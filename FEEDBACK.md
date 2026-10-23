# Feedback

O destino preparado para relatos sem conteúdo sensível é [criar uma issue em enayzuin/zuuuin-skills](https://github.com/enayzuin/zuuuin-skills/issues/new). A disponibilidade do repositório e desse canal ainda não foi verificada. Prepare um registro com a estrutura abaixo e preserve-o localmente se o canal estiver indisponível. Este documento não envia mensagens nem ativa um serviço. Suspeitas de segurança ou conteúdo privado devem seguir [segurança](SECURITY.md), sem expor detalhes em uma issue pública.

## Modelo de registro

Copie os nomes dos campos para um documento privado e preencha somente o que foi observado. Informação indisponível deve ficar identificada como desconhecida, sem estimativas apresentadas como medição.

| Campo | O que registrar |
| --- | --- |
| Tipo | Defeito, mudança de escopo, preferência ou dúvida de uso. |
| Componente | Nome da skill, revisão pública do catálogo e versão separada do runtime. |
| Objetivo | Resultado concreto pretendido e contexto mínimo, sem identificar projetos ou pessoas reais. |
| Ambiente | Sistema e versões relevantes, método de instalação e dependências disponíveis. |
| Entrada sintética | Caso mínimo autorizado, sem credenciais, contas, transcrições ou dados pessoais. |
| Critério anterior | Resultado esperado e critério definido antes da observação; informe se isso não foi fixado. |
| Resultado observado | Saída ou erro indispensável, com campos sensíveis removidos e limite da evidência. |
| Reprodução | Passos realmente executados, separados de passos sugeridos ou ainda não testados. |
| Impacto | Consequência demonstrada, frequência observada e alcance desconhecido. |
| Medições | Fonte e evidência de duração, tokens ou custo, quando existirem; caso contrário, desconhecido. |
| Proposta | Alteração sugerida e eventuais perdas ou alternativas; proposta não equivale a decisão de adoção. |

Identifique revisões no [catálogo](catalog/skills.json) e conceitos no [modelo](catalog/model.json). Se o relato envolver conteúdo sensível ou falha de segurança, siga [segurança](SECURITY.md) e preserve a evidência original apenas em área privada autorizada.

## Como interpretar os resultados

Instalação de arquivos, execução de helper, acionamento pelo cliente e satisfação de critérios são fatos distintos. Um status nominal não comprova a tarefa inteira. Os [exemplos](examples/README.md) são sintéticos; seus fragmentos esperados não são depoimentos ou medições de uso real.

O recorte atual tem oito skills engine, zero implementações de skills de domínio e runtime 0.1.1 em condição de candidata local. Não há ganho comparativo comprovado ou eficácia em produção estabelecida. Relatos devem manter esses limites e não inferir adoção, produtividade ou ativação autônoma.

Ainda não há compromisso de triagem, atendimento ou prazo de resposta. Para preparar uma alteração, consulte [contribuições](CONTRIBUTING.md). O conteúdo próprio está sob MIT, com **enayzuin** como titular indicado; veja o [escopo da licença](LICENSE-STATUS.md). Essa licença não concede permissões sobre dados, contas ou operações externas.
