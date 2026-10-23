# Preparar uma candidata privada

Extrair um método reutilizável de uma lacuna comprovada, evitando duplicatas e a cópia de conversas ou configuração privada.

Coleção: engine. Skill pública `6061d0a0-5cd3-4118-bcac-5c10f864a449`; revisão pública `3b7a4127-7e67-4d4b-93a0-83a758ea541e`. Esta entrega reúne oito skills engine e nenhuma implementação de skill de domínio.

## Quando usar

Use quando há repetição justificada, evidências autorizadas e ausência de solução existente adequada.

## Quando não usar

Não publique, copie transcrições ou crie uma skill só porque uma conversa terminou. Não gere outra candidata para uma solução existente.

## Entradas e resultado

Para criar, informe repeatable, existing_solution, evidence_refs e um método com nome, descrição, gatilhos, exclusões, passos, entradas e saídas. Casos positive, negative e boundary deixam explícito o contrato preparado; não equivalem a testes executados. Conteúdo potencialmente privado bloqueia a preparação.

## Objetos e capacidade

Capacidade: **Criar ou melhorar revisão de skill** — `9032b66e-56f1-4a51-bd4b-8e5d5ccccd0d`. Transformar lacuna comprovada em candidata privada com contrato e recursos proporcionais.

| Objeto | ID público |
| --- | --- |
| Skill | `ab72be05-2d41-4985-875d-60109f84c02e` |
| Contexto de trabalho | `f7aea95d-d562-40fb-b875-8676976869b7` |
| Pacote selecionado | `7d929b0a-e83b-466a-bbbb-fa33ea8f8ffc` |
| Revisão de skill | `e952a79d-b827-4446-a339-8e873de2e47a` |
| Evidência | `9069df1e-5e25-4ef3-8d0e-fb3ebc2f343c` |

Os nomes, IDs e relações deste recorte estão no [modelo público](../../catalog/model.json); a revisão e os hashes estão no [catálogo de skills](../../catalog/skills.json). A associação conceitual não prova cobertura operacional dos objetos.

## Dependências e revisão

Runtime compartilhado **0.1.1**, entregue separadamente no [wheel local](../../dist/zuuuin_engine-0.1.1-py3-none-any.whl). Requer Python >=3.10 e POSIX com fcntl e O_NOFOLLOW; não possui dependências Python externas. Copiar só a pasta da skill não instala o runtime. Se faltar, declare dependency_missing e confira a [instalação](../installation.md), sem buscar pacote homônimo ou instalar globalmente.

Consulte as [instruções da skill](../../skills/zuuuin-skill-author/SKILL.md) e a [referência de runtime](../../skills/zuuuin-skill-author/references/runtime.md). A revisão pública identifica o conteúdo da skill; 0.1.1 é a versão separada do motor.

## Exemplo sintético

A entrada mínima demonstra existing_solution=true. O fragmento exige no_candidate_needed e changes_applied=false: não há razão para redigir uma duplicata nem um arquivo de candidata.

Entrada: [author.request.json](../../examples/author.request.json). Fragmento esperado: [author.expected.json](../../examples/author.expected.json). Os fragmentos fixam somente campos estáveis; preserve os demais campos da resposta e não compare IDs/horários gerados como se fossem constantes.

Conclua a instalação e use um perfil privado novo conforme o [guia de uso](../usage.md). Copie o pedido demonstrativo para private/requests do perfil; escolha uma saída nova em private/outputs. Não grave resultados nesta entrega.

Partindo da raiz da entrega, com os destinos irmãos indicados no guia:

```sh
cp examples/author.request.json ../zuuuin-local-profile/private/requests/author.request.json
../zuuuin-runtime-env/bin/python -I -B -m zuuuin_engine author --request ../zuuuin-local-profile/private/requests/author.request.json --output ../zuuuin-local-profile/private/outputs/author.result.json --private-root ../zuuuin-local-profile/private
```

O CLI recusa saída existente. Para outra observação, use um nome novo e preserve a anterior. Em caso de recusa, confira dependências, dados e fronteiras do perfil antes de tentar novamente.

## Evidência disponível e limites

A evidência disponível limita-se a observações locais e sintéticas da revisão e do runtime em laboratório. Isso não comprova eficácia em produção, ativação autônoma pelo cliente, adoção ou ganho de produtividade. Estes arquivos de exemplo são contratos demonstrativos; sua presença não é um recibo de execução.

Uma candidata preparada continua privada, draft e not_tested. Autoria técnica, classificação e casos escritos não comprovam direitos ou eficácia.

Maturidade: experimental. Conteúdo próprio sob [MIT](../../LICENSE), com **enayzuin** como titular indicado; veja o [escopo da licença](../../LICENSE-STATUS.md). A licença não concede acesso a dados ou contas nem autoriza efeitos externos de uma execução. Mantenha perfis, políticas, entradas reais, resultados e registros privados fora da entrega.
