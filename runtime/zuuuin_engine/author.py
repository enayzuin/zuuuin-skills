"""Prepare a private reusable method candidate, never a transcript dump."""
import re
import json
from .state import ControlError
from .util import response, scan_value


def run(request, context=None):
    if any(k in request for k in ("raw_transcript", "full_prompt", "vault_payload", "credentials")):
        raise ControlError("Raw private conversational material is not an authoring input")
    if request.get("existing_solution") is True or request.get("repeatable") is not True:
        return response("author", "no_candidate_needed", reason="Existing method or no justified reusable gap", changes_applied=False)
    method = request.get("method", {})
    if not request.get("evidence_refs") or not all(method.get(k) for k in ("name", "description", "triggers", "exclusions", "steps", "inputs", "outputs")):
        raise ControlError("Provide evidence and a complete reusable method contract")
    name = method["name"]
    if not all(isinstance(method[k],str) for k in ("description","triggers","exclusions","inputs","outputs")) or not isinstance(method["steps"],list) or not all(isinstance(x,str) and x.strip() for x in method["steps"]):
        raise ControlError("Method prose fields must be text and steps a list of nonempty texts")
    if not isinstance(name, str) or len(name) > 64 or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
        raise ControlError("Invalid skill name")
    findings = scan_value(method, private_identifiers=request.get("private_identifiers", []))
    if findings:
        return response("author", "blocked", reason="Potentially private method content; generalize before drafting", findings=findings)
    description = " ".join(method["description"].split())
    if len(description) > 1024:
        raise ControlError("Description exceeds Agent Skills limit")
    steps = "\n".join(f"{i}. {v}" for i, v in enumerate(method["steps"], 1))
    content = f"---\nname: {name}\ndescription: {json.dumps(description,ensure_ascii=False)}\n---\n# {name}\n\n## Uso\n{method['triggers']}\n\n## Não usar\n{method['exclusions']}\n\n## Entradas\n{method['inputs']}\n\n## Resultado\n{method['outputs']}\n\n## Método\n{steps}\n\n## Limites\nUse somente ferramentas autorizadas e pare quando entradas ou permissões forem insuficientes. Não publique dados do caso original.\n"
    tests = request.get("test_cases", [])
    kinds = {t.get("kind") for t in tests if t.get("input") and t.get("expected")}
    ready = {"positive", "negative", "boundary"} <= kinds
    return response("author", "candidate_private" if ready else "needs_test_cases", candidate={"name": name, "content": content, "classification": request.get("classification"), "visibility": "private", "maturity": "draft", "validation": "not_tested", "dependencies": method.get("tools", []), "test_cases": tests}, evidence_refs=request["evidence_refs"], publication_performed=False, changes_applied=False)
