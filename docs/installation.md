# Instalação local

Execute os comandos iniciais a partir da raiz da entrega. Escolha destinos novos; se já existirem, pare e confira seu conteúdo. Não reutilize pastas de um acervo sem revisão e backup.

## Obter a versão 0.1.1

A versão preparada é **0.1.1**, com futura tag **v0.1.1** no repositório escolhido [enayzuin/zuuuin-skills](https://github.com/enayzuin/zuuuin-skills). Quando essa tag estiver publicada, obtenha o [arquivo de código-fonte v0.1.1](https://github.com/enayzuin/zuuuin-skills/archive/refs/tags/v0.1.1.tar.gz) ou consulte a [página da release v0.1.1](https://github.com/enayzuin/zuuuin-skills/releases/tag/v0.1.1). Extraia o arquivo em uma pasta nova, confira a origem e os hashes divulgados junto da versão e execute os próximos passos a partir da raiz extraída. A distribuição contém `skills/`, `docs/`, `tools/` e o wheel em `dist/`.

Esses links são instruções para a publicação futura; esta preparação local não comprova existência da tag, da release ou de assets de download. Se estiverem indisponíveis, não substitua a versão por outro repositório, uma branch mutável ou um pacote homônimo. Uma cópia local recebida para revisão pode ser verificada conforme [validação](validation.md). O conteúdo próprio usa [MIT](../LICENSE), com **enayzuin** como titular indicado; isso não autoriza operações sobre contas, fontes ou dados de terceiros.

## Runtime separado e perfil privado

Cada pasta de skill contém dois Markdown. O aviso MIT completo acompanha `references/runtime.md`, preservando os termos e a autoria na obtenção individual. Copiar essa pasta não instala Python nem fornece o módulo `zuuuin_engine`. As oito skills do motor compartilham o wheel entregue em `dist/`.

Pré-requisitos: Python >=3.10 e POSIX com `fcntl` e `O_NOFOLLOW`. O teste disponível usou Python 3.14.8 em macOS. O runtime não tem dependências Python externas.

```sh
python3 -I -B -m venv ../zuuuin-runtime-env
../zuuuin-runtime-env/bin/python -I -B -m pip install --no-index --no-deps --disable-pip-version-check dist/zuuuin_engine-0.1.1-py3-none-any.whl
../zuuuin-runtime-env/bin/python -I -B tools/init_profile.py --root ../zuuuin-local-profile
```

O ambiente virtual é irmão do perfil: criar a venv dentro do destino antes do inicializador tornaria esse destino existente e ele seria recusado. O diretório pai do perfil deve existir. O inicializador não sobrescreve perfis ou configurações, recusa descendentes da entrega e ancestrais simbólicos de usuário. Aliases POSIX conhecidos do sistema para diretórios temporários são normalizados para seu caminho físico e informados no recibo.

O diretório do perfil e seus subdiretórios usam modo `0700`; os JSONs de controle usam `0600`. Ele contém `private/`, `source/`, `test/` e `release/` próprios. Em `private/` ficam checkpoint, políticas, autorizações vazias, entradas e saídas. O perfil é local e genérico: não contém roteiro de implantação nem aprovações de outra execução. As políticas desabilitam publicação e instalação externas. Não copie estados, modelos pessoais, contas ou segredos de outra execução para iniciar esse perfil.

A falta do runtime é uma dependência ausente. Instale o wheel local com o interpretador que executará o inicializador; não busque um pacote homônimo em registro público. Nenhum ajuste de `HOME` ou `CODEX_HOME` é necessário.

## Instruções no projeto: escolha um método

Use um projeto de teste novo. Estes métodos instalam só a pasta de instruções; o runtime separado continua necessário. O destino Codex observado é `.agents/skills/<nome>` no projeto. Isso não confirma recarga ou ativação pelo cliente.

### Cópia manual

Partindo da raiz da entrega:

```sh
mkdir ../zuuuin-skill-demo
mkdir -p ../zuuuin-skill-demo/.agents/skills
cp -R skills/zuuuin-project-skill-map ../zuuuin-skill-demo/.agents/skills/
```

Confira que a pasta contém `SKILL.md` e `references/runtime.md`, incluindo o aviso MIT completo, com os bytes da entrega. Para outra skill, escolha apenas sua pasta na [tabela](../README.md#escolher-uma-skill). Não mescle um destino existente.

### CLI opcional de obtenção de skills

Foi observado o CLI [Vercel skills 1.7.4](https://github.com/vercel-labs/skills/tree/v1.7.4), com Node 24.19.0. Essa versão exige Node >=22.20. O primeiro uso de `npx` pode obter a ferramenta e suas dependências pela rede; a fonte de skill no comando abaixo é local. Defina ambos os opt-outs para desabilitar telemetria e consultas de auditoria remota.

Em uma sessão separada, ainda partindo da raiz da entrega, use outro destino novo:

```sh
ZUUUIN_DELIVERY_DIR="$(pwd -P)"
mkdir ../zuuuin-cli-demo
cd ../zuuuin-cli-demo
DISABLE_TELEMETRY=1 DO_NOT_TRACK=1 npx --yes skills@1.7.4 add "$ZUUUIN_DELIVERY_DIR/skills/zuuuin-project-skill-map" -a codex --copy -y
```

O escopo padrão é o projeto. `--copy` solicita cópia; `-a codex` seleciona o cliente; `-y` aceita essa instalação explícita. Não acrescente instalação global. Confira a saída real e os dois arquivos no destino. A observação de laboratório usou diretórios/cache temporários e instrumentação adicional; ela não promete comportamento idêntico em todo ambiente.

## Atualização, remoção e rollback

Atualize uma unidade por vez, primeiro em destino novo de teste. Compare arquivos, versão do runtime e requisitos; preserve a revisão e o wheel anteriores antes de autorizar qualquer substituição. Não execute atualização global ou em lote como parte desta receita.

Para remover, identifique o projeto e a pasta exata que você criou. Remova somente essa instalação local depois de conferir seu conteúdo. Não apague diretórios globais de skills nem outras pastas do cliente. Políticas, checkpoint e saídas pertencem ao perfil privado; preserve evidências antes de descartá-lo.

Rollback requer o artefato anterior conservado e verificado. Instale-o em outra venv e outro destino de teste, depois ajuste explicitamente o uso para essa revisão. Sem artefato anterior disponível, não declare rollback realizado. Esses procedimentos não concedem acesso a dados, contas ou serviços. O uso e a redistribuição do conteúdo próprio seguem a [licença MIT](../LICENSE); efeitos externos do runtime continuam sujeitos às políticas e autorizações da execução.
