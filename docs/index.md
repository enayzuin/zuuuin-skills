# Índice do Zuuuin Skills

Distribuição **0.1.1**: **8 skills engine**, **0 implementações de skills de domínio** e runtime separado **0.1.1**.

Conteúdo próprio de **enayzuin**, sob a [licença MIT](../LICENSE). [Repositório selecionado](https://github.com/enayzuin/zuuuin-skills) e [endereço selecionado da documentação](https://enayzuin.github.io/zuuuin-skills/); a presença destes links não comprova publicação ou hospedagem.

Leia o [README](../README.md), a [instalação](installation.md), o [uso](usage.md) e os [exemplos sintéticos](../examples/README.md). [Entrada em inglês](../README.en.md).

Os grupos abaixo vêm do módulo primário de cada capacidade no [modelo público](../catalog/model.json). IDs e revisões vêm do [catálogo](../catalog/skills.json); não há seleção por popularidade ou adoção implícita.

## Descoberta e seleção

Mapear necessidades, catalogar, comparar e rotear revisões pertinentes.

| Skill e documentação | Descrição | Capacidade | Revisão pública | Instruções |
| --- | --- | --- | --- | --- |
| [zuuuin-project-skill-map](skills/zuuuin-project-skill-map.md) | Mapear projetos e necessidades a partir de fontes autorizadas, quando for preciso compreender o trabalho antes de selecionar skills. | Levantar projetos e necessidades | `bd123fb8-238a-451f-9ef4-13e3d341adc6` | [SKILL.md](../skills/zuuuin-project-skill-map/SKILL.md) |
| [zuuuin-skill-catalog](skills/zuuuin-skill-catalog.md) | Inventariar raízes de skills explicitamente autorizadas e aplicar um modelo recebido, preservando instalações e revisões. | Catalogar revisões e instalações | `487b80d4-1f9d-4cd0-a063-9a8b22518c61` | [SKILL.md](../skills/zuuuin-skill-catalog/SKILL.md) |
| [zuuuin-skill-compare](skills/zuuuin-skill-compare.md) | Comparar a skill local e candidatas elegíveis para uma necessidade e contexto concretos, mostrando evidências, ganhos, perdas e incerteza. | Comparar alternativas por necessidade | `4b742972-7df1-4c6b-8145-b89bfde14991` | [SKILL.md](../skills/zuuuin-skill-compare/SKILL.md) |
| [zuuuin-skill-router](skills/zuuuin-skill-router.md) | Relacionar uma tarefa a necessidades e capacidades mapeadas e selecionar revisões já aprovadas no contexto correto, encaminhando lacunas para comparação. | Selecionar capacidade pertinente | `6bdc643d-0e55-4e62-8224-d67e19405c78` | [SKILL.md](../skills/zuuuin-skill-router/SKILL.md) |

## Avaliação e evolução

Casos, avaliações e autoria de revisões com evidência.

| Skill e documentação | Descrição | Capacidade | Revisão pública | Instruções |
| --- | --- | --- | --- | --- |
| [zuuuin-skill-author](skills/zuuuin-skill-author.md) | Extrair de evidências autorizadas um método reutilizável e preparar uma candidata privada com contratos, classificação recebida e casos de teste. | Criar ou melhorar revisão de skill | `3b7a4127-7e67-4d4b-93a0-83a758ea541e` | [SKILL.md](../skills/zuuuin-skill-author/SKILL.md) |
| [zuuuin-skill-evaluate](skills/zuuuin-skill-evaluate.md) | Avaliar ativação e resultados observados de uma revisão de skill com casos e critérios prévios, registrando limitações e propostas de melhoria. | Avaliar uma revisão por casos | `80651c06-52f7-4bb2-b4fe-9e591228b2cb` | [SKILL.md](../skills/zuuuin-skill-evaluate/SKILL.md) |

## Auditoria e publicação

Pacote exato, direitos, auditoria, autorização e recibo de publicação.

| Skill e documentação | Descrição | Capacidade | Revisão pública | Instruções |
| --- | --- | --- | --- | --- |
| [zuuuin-publication-audit](skills/zuuuin-publication-audit.md) | Auditar um pacote exato e seu histórico de saída antes da exposição, combinando verificações automatizadas e revisão contextual independente. | Auditar pacote para exposição | `56f2c90d-42ab-4753-9fa2-a216a7353996` | [SKILL.md](../skills/zuuuin-publication-audit/SKILL.md) |
| [zuuuin-skill-publish](skills/zuuuin-skill-publish.md) | Preparar ou publicar somente um pacote auditado e imutável, com destino e autorização específicos conferidos no controle privado. | Publicar pacote autorizado | `2f6c07e2-82cb-4e11-b530-d22d6ae65db0` | [SKILL.md](../skills/zuuuin-skill-publish/SKILL.md) |

## Módulos compartilhados de apoio

Estes módulos pertencem ao modelo selecionado e não recebem grupo vazio de skills. Apoiá-los conceitualmente não demonstra uma implementação independente nem cobertura operacional.

- **Contexto e continuidade**: Recuperar fontes e estado retomável sem depender da narrativa de um chat.

- **Evidência e limites de atuação**: Proveniência, autorização e recibos de efeitos observados.

## Formatos de descoberta

[llms.txt](../llms.txt) é uma entrada Markdown com links relativos. A [proposta v2](https://llmstxt.org/) orienta o formato; não garante descoberta, instalação ou ativação por todo consumidor. Resolução HTTP e comportamento no destino ainda dependem de verificação própria.

[skills.sh.json](../skills.sh.json) agrupa os oito nomes em três módulos primários não vazios. O arquivo segue o [schema oficial](https://skills.sh/schemas/skills.sh.schema.json) no formato gerado. Segundo a [documentação de personalização](https://www.skills.sh/docs/customize), esse agrupamento trata da apresentação de uma página de repositório; não altera a instalação pelo CLI. Sua presença local não comprova listagem ou consumo pelo serviço.

As [páginas Markdown por skill](skills/zuuuin-project-skill-map.md) já fazem parte da entrega. O índice apenas as referencia. Para conferir os três arquivos gerados, execute `python3 -I -B tools/build_discovery.py --check` a partir da raiz da entrega. O gerador usa somente os dois catálogos públicos como dados e não faz chamadas de rede.

## Governança e limites

- [Contribuições](../CONTRIBUTING.md)
- [Segurança](../SECURITY.md)
- [Feedback](../FEEDBACK.md)
- [Histórico da candidata](../CHANGELOG.md)
- [Licença MIT](../LICENSE)
- [Titularidade e escopo da licença](../LICENSE-STATUS.md)

Arquivo presente, instalação, execução, decisão e efeito externo são fatos distintos. A evidência sintética disponível não comprova eficácia em produção, ativação autônoma, adoção ou produtividade.
