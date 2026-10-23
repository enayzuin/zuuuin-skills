# Zuuuin Skills

Instruções reutilizáveis para mapear necessidades, organizar skills, comparar alternativas e registrar decisões com evidências. O runtime local executa operações explícitas em JSON; as skills orientam o trabalho do agente.

O recorte atual contém **oito skills de motor** e o runtime **0.1.1**. Não contém skills de domínio: o catálogo público tem zero implementações de trabalho específico de um produto. Conceitos compartilhados de contexto, evidência e autorização apoiam o motor. O router usa o método aplicável ao trabalho e não cria outro SDLC.

A versão preparada é **0.1.1**, com conteúdo próprio sob a [licença MIT](LICENSE) e autoria pública de **enayzuin**. O destino escolhido é [enayzuin/zuuuin-skills](https://github.com/enayzuin/zuuuin-skills), com documentação em [GitHub Pages](https://enayzuin.github.io/zuuuin-skills/). Esses endereços identificam os destinos planejados; esta cópia local não comprova publicação, disponibilidade ou aprovação de exposição do pacote exato. O [catálogo](catalog/skills.json) e o [modelo selecionado](catalog/model.json) descrevem o recorte. As instruções das skills estão em português.

## Escolher uma skill

| Quando usar | Skill |
| --- | --- |
| Entender projetos e resultados necessários a partir de fontes autorizadas | [project-skill-map](skills/zuuuin-project-skill-map/SKILL.md) |
| Inventariar pacotes, revisões e dependências sem alterar o acervo | [skill-catalog](skills/zuuuin-skill-catalog/SKILL.md) |
| Comparar alternativas para uma necessidade e um contexto | [skill-compare](skills/zuuuin-skill-compare/SKILL.md) |
| Confrontar saídas observadas com casos e critérios explícitos | [skill-evaluate](skills/zuuuin-skill-evaluate/SKILL.md) |
| Preparar uma candidata privada para um método reutilizável | [skill-author](skills/zuuuin-skill-author/SKILL.md) |
| Conferir o conteúdo e os limites de exposição de um pacote exato | [publication-audit](skills/zuuuin-publication-audit/SKILL.md) |
| Preparar ou simular uma publicação com escopo explícito | [skill-publish](skills/zuuuin-skill-publish/SKILL.md) |
| Encaminhar uma tarefa para revisões pertinentes já disponíveis | [skill-router](skills/zuuuin-skill-router/SKILL.md) |

Leia o contrato e as exclusões da skill escolhida. A presença de uma pasta, uma instalação, uma execução e uma aprovação são fatos distintos.

## Começar localmente

Requer Python **3.10 ou superior**, POSIX (macOS/Linux), `fcntl` e `O_NOFOLLOW`. O ambiente observado foi **Python 3.14.8 em macOS**; outras versões e sistemas compatíveis não foram todos testados. O runtime usa apenas a biblioteca padrão.

Para obter a futura tag `v0.1.1` do repositório escolhido, siga [obter a versão](docs/installation.md#obter-a-versão-011). A instrução de download depende da publicação dessa tag e não afirma que ela já existe.

Partindo da raiz desta entrega, use dois destinos novos e irmãos. O ambiente virtual precisa existir antes de criar o perfil:

```sh
python3 -I -B -m venv ../zuuuin-runtime-env
../zuuuin-runtime-env/bin/python -I -B -m pip install --no-index --no-deps --disable-pip-version-check dist/zuuuin_engine-0.1.1-py3-none-any.whl
../zuuuin-runtime-env/bin/python -I -B tools/init_profile.py --root ../zuuuin-local-profile
```

O perfil é privado, começa sem ações concluídas ou autorizações e recusa destino existente. Nenhum perfil ou resultado deve ser criado dentro desta entrega. Continue em [instalação](docs/installation.md) e [uso](docs/usage.md), que copiam as entradas demonstrativas para o perfil antes de chamar o CLI.

A instalação das instruções no projeto pode usar cópia manual ou o CLI opcional `skills@1.7.4`. Esse CLI exige Node **22.20 ou superior**; a combinação observada usou Node **24.19.0**. Node/npm não são necessários para a cópia manual ou para o runtime Python.

## Limites de uso

Os [exemplos](examples/README.md) são inteiramente sintéticos. A evidência disponível é local e limitada; não estabelece eficácia em produção, descoberta universal no cliente ou ativação autônoma. Instalar arquivos não garante recarga nem uso na próxima mensagem. Verifique o comportamento no cliente escolhido e mantenha como desconhecido o que não foi observado.

O perfil não depende de Obsidian, Linear, contas ou credenciais. Fontes reais exigem autorização própria. Saídas e políticas privadas ficam no perfil, fora da distribuição. O estado inicial mantém efeitos externos desabilitados; preparação e simulação não concedem autorização para publicar.

Antes de uma atualização, confira a unidade escolhida e preserve o destino anterior. A [instalação](docs/installation.md) descreve remoção local e rollback sem apagar acervo global ou atualizar tudo em lote. A licença de uso do conteúdo próprio está em [LICENSE](LICENSE); permissões sobre dados, contas e efeitos externos são específicas de cada execução.

[English entry](README.en.md)
