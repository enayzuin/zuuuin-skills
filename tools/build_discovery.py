"""Build local discovery files from the two public catalogs, without network.

Observed contracts: skills.sh/docs/customize and its official JSON schema;
llmstxt.org proposal v2, modified 2026-08-10. Validation here covers the
generated subset, not arbitrary JSON Schema documents or client activation.
"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import posixpath
import re
import sys
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_URL = "https://skills.sh/schemas/skills.sh.schema.json"
PUBLIC_METADATA = {
    "owner": "enayzuin",
    "license": "MIT",
    "distribution_version": "0.1.1",
    "repository_url": "https://github.com/enayzuin/zuuuin-skills",
    "site_url": "https://enayzuin.github.io/zuuuin-skills/",
}
REFERENCE_URLS = {
    "https://www.skills.sh/docs/customize",
    SCHEMA_URL,
    "https://llmstxt.org/",
    PUBLIC_METADATA["repository_url"],
    PUBLIC_METADATA["site_url"],
}
OUTPUTS = ("docs/index.md", "llms.txt", "skills.sh.json")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def local(path):
    value = PurePosixPath(path)
    require(not value.is_absolute() and ".." not in value.parts, "Unsafe local path")
    current = ROOT
    for part in value.parts:
        current = current / part
        require(not current.is_symlink(), "Local symlink refused")
    return current


def read_catalog(path):
    file = local(path)
    require(file.is_file(), "Public catalog missing")
    return json.loads(file.read_text(encoding="utf-8"))


def text(value):
    require(isinstance(value, str) and value.strip(), "Nonempty catalog text required")
    require("\n" not in value and "\r" not in value, "Multiline inline text refused")
    return value.replace("\\", "\\\\").replace("[", "\\[").replace("]", "\\]").replace("|", "\\|").replace("<", "&lt;").replace(">", "&gt;")


def load_inputs():
    catalog = read_catalog("catalog/skills.json")
    model = read_catalog("catalog/model.json")
    skills = sorted(catalog["skills"], key=lambda item: item["slug"])
    require(len(skills) == 8, "This candidate expects exactly eight skills")
    require(catalog["runtime"]["version"] == "0.1.1", "Runtime candidate changed")
    require(all(s["collection"] == "engine" for s in skills), "Only engine skills selected")
    require(all(catalog.get(key) == value for key, value in PUBLIC_METADATA.items()),
            "Selected public metadata changed; review discovery wording")
    records = [catalog] + skills + catalog["skill_revisions"]
    require(all(item.get("owner") == PUBLIC_METADATA["owner"]
                and item.get("license") == PUBLIC_METADATA["license"] for item in records),
            "Selected public owner/license changed")
    require(all("rights_pending" not in item and "public_exposure_cleared" not in item
                for item in records), "Instance authorizations are not public catalog metadata")
    modules = {item["id"]: item for item in model["modules"]}
    caps = {item["id"]: item for item in model["capabilities"]}
    revisions = {item["id"]: item for item in catalog["skill_revisions"]}
    seen, groups = set(), {}
    for skill in skills:
        slug = skill["slug"]
        require(isinstance(slug, str) and re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug), "Invalid slug")
        require(slug == skill["name"] and slug not in seen and skill["path"] == "skills/" + slug, "Skill identity/path mismatch")
        seen.add(slug)
        require(len(skill["capability_ids"]) == 1, "Primary capability must be unambiguous")
        cap = caps[skill["capability_ids"][0]]
        module = modules[cap["primary_module_id"]]
        require(cap["collection"] == "engine" and module["collection"] == "engine", "Unexpected primary collection")
        require(revisions[skill["current_revision_id"]]["skill_id"] == skill["id"], "Revision binding mismatch")
        require(local("docs/skills/" + slug + ".md").is_file(), "Skill documentation missing")
        require(local(skill["path"] + "/SKILL.md").is_file(), "SKILL entry missing")
        groups.setdefault(module["id"], []).append(skill)
    ordered = [(module, groups[module["id"]]) for module in model["modules"] if module["id"] in groups]
    support = [module for module in model["modules"] if module["collection"] == "shared"]
    require(len(ordered) == 3 and [len(members) for _, members in ordered] == [4, 2, 2]
            and len(support) == 2, "Selected taxonomy/group sizes changed")
    return catalog, model, skills, caps, ordered, support


def validate_groupings(value, slugs):
    """All applicable constraints of the observed schema for this output shape."""
    require(isinstance(value, dict) and set(value) <= {"$schema", "schema", "notGrouped", "groupings"}, "Unexpected config field")
    for key in ("$schema", "schema"):
        if key in value:
            require(isinstance(value[key], str) and bool(urlsplit(value[key]).scheme), "Schema URI required")
    require(value.get("notGrouped", "bottom") in ("top", "bottom"), "Invalid notGrouped")
    groups = value.get("groupings")
    require(isinstance(groups, list) and 1 <= len(groups) <= 50, "Group count out of range")
    covered = []
    for group in groups:
        require(isinstance(group, dict) and set(group) <= {"title", "description", "skills"}, "Unexpected group field")
        require(isinstance(group.get("title"), str) and 1 <= len(group["title"]) <= 120, "Invalid title")
        if "description" in group:
            require(isinstance(group["description"], str) and len(group["description"]) <= 500, "Invalid description")
        names = group.get("skills")
        require(isinstance(names, list) and 1 <= len(names) <= 500, "Invalid group size")
        require(all(isinstance(name, str) and 1 <= len(name) <= 120 for name in names), "Invalid skill string")
        covered.extend(names)
    require(len(covered) == len(set(covered)) and set(covered) == set(slugs), "Skill coverage must be exact and unique")


def render():
    catalog, model, skills, caps, groups, support = load_inputs()
    grouping = {"$schema": SCHEMA_URL, "notGrouped": "bottom", "groupings": [
        {"title": module["name"], "description": module["definition"], "skills": [s["slug"] for s in members]}
        for module, members in groups
    ]}
    validate_groupings(grouping, [s["slug"] for s in skills])
    index = ["# Índice do Zuuuin Skills", "",
             "Distribuição **0.1.1**: **8 skills engine**, **0 implementações de skills de domínio** e runtime separado **0.1.1**.", "",
             "Conteúdo próprio de **enayzuin**, sob a [licença MIT](../LICENSE). [Repositório selecionado](https://github.com/enayzuin/zuuuin-skills) e [endereço selecionado da documentação](https://enayzuin.github.io/zuuuin-skills/); a presença destes links não comprova publicação ou hospedagem.", "",
             "Leia o [README](../README.md), a [instalação](installation.md), o [uso](usage.md) e os [exemplos sintéticos](../examples/README.md). [Entrada em inglês](../README.en.md).", "",
             "Os grupos abaixo vêm do módulo primário de cada capacidade no [modelo público](../catalog/model.json). IDs e revisões vêm do [catálogo](../catalog/skills.json); não há seleção por popularidade ou adoção implícita."]
    llms = ["# Zuuuin Skills", "",
            "> Zuuuin Skills 0.1.1: oito skills engine, runtime separado 0.1.1 e zero implementações de skills de domínio; conteúdo próprio de enayzuin sob MIT.", "",
            "Evidência apenas local e sintética; leitura de documentação não instala, recarrega ou ativa skills e não comprova eficácia em produção ou ganho comparativo.", "",
            "Os links locais são relativos a este arquivo. O endereço selecionado da documentação é https://enayzuin.github.io/zuuuin-skills/. A resolução no destino e o comportamento de cada consumidor precisam de verificação própria; este arquivo não comprova hospedagem ou listagem.", "",
            "## Começar", "",
            "- [Visão geral](README.md): Escopo, escolha de skill e limites.",
            "- [Índice navegável](docs/index.md): Grupos, capacidades e revisões públicas.",
            "- [Instalação](docs/installation.md): Runtime separado e perfil local novo.",
            "- [Uso](docs/usage.md): Pedidos explícitos e saídas privadas.",
            "- [Exemplos sintéticos](examples/README.md): Entradas e fragmentos esperados."]
    for module, members in groups:
        index += ["", "## " + text(module["name"]), "", text(module["definition"]), "",
                  "| Skill e documentação | Descrição | Capacidade | Revisão pública | Instruções |",
                  "| --- | --- | --- | --- | --- |"]
        llms += ["", "## " + text(module["name"]), ""]
        for skill in members:
            cap = caps[skill["capability_ids"][0]]
            slug = skill["slug"]
            index += ["| [" + slug + "](skills/" + slug + ".md) | " + text(skill["description"]) + " | " + text(cap["name"]) + " | `" + skill["current_revision_id"] + "` | [SKILL.md](../" + skill["path"] + "/SKILL.md) |"]
            llms += ["- [" + slug + "](docs/skills/" + slug + ".md): " + text(skill["description"])]
    index += ["", "## Módulos compartilhados de apoio", "",
              "Estes módulos pertencem ao modelo selecionado e não recebem grupo vazio de skills. Apoiá-los conceitualmente não demonstra uma implementação independente nem cobertura operacional."]
    for module in support:
        index += ["", "- **" + text(module["name"]) + "**: " + text(module["definition"])]
    index += ["", "## Formatos de descoberta", "",
              "[llms.txt](../llms.txt) é uma entrada Markdown com links relativos. A [proposta v2](https://llmstxt.org/) orienta o formato; não garante descoberta, instalação ou ativação por todo consumidor. Resolução HTTP e comportamento no destino ainda dependem de verificação própria.", "",
              "[skills.sh.json](../skills.sh.json) agrupa os oito nomes em três módulos primários não vazios. O arquivo segue o [schema oficial](https://skills.sh/schemas/skills.sh.schema.json) no formato gerado. Segundo a [documentação de personalização](https://www.skills.sh/docs/customize), esse agrupamento trata da apresentação de uma página de repositório; não altera a instalação pelo CLI. Sua presença local não comprova listagem ou consumo pelo serviço.", "",
              "As [páginas Markdown por skill](skills/" + skills[0]["slug"] + ".md) já fazem parte da entrega. O índice apenas as referencia. Para conferir os três arquivos gerados, execute `python3 -I -B tools/build_discovery.py --check` a partir da raiz da entrega. O gerador usa somente os dois catálogos públicos como dados e não faz chamadas de rede.", "",
              "## Governança e limites", "",
              "- [Contribuições](../CONTRIBUTING.md)",
              "- [Segurança](../SECURITY.md)",
              "- [Feedback](../FEEDBACK.md)",
              "- [Histórico da candidata](../CHANGELOG.md)",
              "- [Licença MIT](../LICENSE)",
              "- [Titularidade e escopo da licença](../LICENSE-STATUS.md)", "",
              "Arquivo presente, instalação, execução, decisão e efeito externo são fatos distintos. A evidência sintética disponível não comprova eficácia em produção, ativação autônoma, adoção ou produtividade.", ""]
    llms += ["", "## Optional", "",
             "- [Contribuições](CONTRIBUTING.md): Fluxo proposto e situação dos canais.",
             "- [Segurança](SECURITY.md): Relato privado saneado, canais e limites.",
             "- [Feedback](FEEDBACK.md): Estrutura para relatos e destino selecionado.",
             "- [Histórico](CHANGELOG.md): Conteúdo da candidata, sem anúncio de lançamento.",
             "- [Licença MIT](LICENSE): Termos do conteúdo próprio de enayzuin.",
             "- [Escopo da licença](LICENSE-STATUS.md): Titularidade indicada e limites para terceiros.",
             "- [Entrada em inglês](README.en.md): Apresentação internacional; instruções permanecem em português.", ""]
    return {"docs/index.md": "\n".join(index).encode("utf-8"),
            "llms.txt": "\n".join(llms).encode("utf-8"),
            "skills.sh.json": (json.dumps(grouping, ensure_ascii=False, indent=2) + "\n").encode("utf-8")}


def validate_links(outputs):
    count = 0
    for source in ("docs/index.md", "llms.txt"):
        value = outputs[source].decode("utf-8")
        require(value.startswith("# ") and len(re.findall(r"^# ", value, re.M)) == 1, "One H1 required")
        if source == "llms.txt":
            require(value.splitlines()[2].startswith("> "), "Summary blockquote required for this subset")
            in_sections = False
            for line in value.splitlines():
                if line.startswith("## "):
                    in_sections = True
                elif in_sections and line:
                    require(bool(re.fullmatch(r"- \[[^\]]+\]\([^)]+\)(?:: .+)?", line)), "Invalid llms file-list item")
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", value):
            if urlsplit(target).scheme:
                require(target in REFERENCE_URLS, "Unknown external reference")
            else:
                normalized = posixpath.normpath(posixpath.join(posixpath.dirname(source), target))
                require(not normalized.startswith("../"), "Link escapes delivery")
                file = local(normalized)
                require(normalized in outputs or file.is_file(), "Linked local file missing")
                if file.exists():
                    current = ROOT
                    for part in PurePosixPath(normalized).parts:
                        require(part in {p.name for p in current.iterdir()}, "Case-sensitive path mismatch")
                        current = current / part
            count += 1
    return count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Read-only comparison with deterministic output")
    args = parser.parse_args()
    try:
        outputs = render()
        count = validate_links(outputs)
        # Preflight all outputs before creating any. Existing files are never replaced.
        for name, value in outputs.items():
            file = local(name)
            if file.exists():
                require(file.is_file() and file.read_bytes() == value, "Generated file differs: " + name)
            else:
                require(not args.check and file.parent.is_dir(), "Generated file missing: " + name)
        if not args.check:
            for name, value in outputs.items():
                file = local(name)
                if not file.exists():
                    with file.open("xb") as stream:
                        stream.write(value)
        print(json.dumps({"status": "checked" if args.check else "generated", "skills": 8,
                          "domain_skill_implementations": 0, "runtime_version": "0.1.1",
                          "distribution_version": PUBLIC_METADATA["distribution_version"], "groups": 3,
                          "supporting_shared_modules": 2, "links": count,
                          "outputs": {name: hashlib.sha256(value).hexdigest() for name, value in outputs.items()}}, sort_keys=True))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(json.dumps({"status": "refused", "error": str(error)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
