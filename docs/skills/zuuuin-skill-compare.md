# Comparar alternativas por necessidade

Confrontar revisões para uma necessidade e contexto concretos, sem converter popularidade, score sem evidência ou recomendação em autorização de adoção.

Coleção: engine. Skill pública `7362fbbe-51c8-4753-9219-06342aecc5f1`; revisão pública `4b742972-7df1-4c6b-8145-b89bfde14991`. Esta entrega reúne oito skills engine e nenhuma implementação de skill de domínio.

## Quando usar

Use após resolver a necessidade e reunir alternativas elegíveis, eliminatórios, recursos comparáveis e resultados observados.

## Quando não usar

Não instale, aprove mudanças globais ou atribua eficácia à leitura estática. Métodos protegidos e perdas relevantes precisam de decisão atribuída.

## Entradas e resultado

O pedido operacional usa need_id, context_key, cinco criteria e local/candidates. Uma medição utilizável exige valor de 0 a 4, source_kind de execução aceito e evidence_refs; sem os cinco critérios comparáveis, o índice permanece null. A saída contém avaliações das alternativas e propostas contextuais, sem adoção automática.

## Objetos e capacidade

Capacidade: **Comparar alternativas por necessidade** — `25f3bcff-d07b-43b3-9217-bf6af16b904f`. Comparar revisões em critérios contextualizados, com ganhos, perdas e confiança.

| Objeto | ID público |
| --- | --- |
| Caso de avaliação | `8cb878cb-6bfb-43ff-90e3-e2348eee474f` |
| Comparação | `62031be1-a10b-4f87-9033-3c5e4ad2498a` |
| Revisão de skill | `e952a79d-b827-4446-a339-8e873de2e47a` |
| Evidência | `9069df1e-5e25-4ef3-8d0e-fb3ebc2f343c` |
| Decisão | `882a93cf-8d72-4811-9067-d333ab0a5dfd` |

Os nomes, IDs e relações deste recorte estão no [modelo público](../../catalog/model.json); a revisão e os hashes estão no [catálogo de skills](../../catalog/skills.json). A associação conceitual não prova cobertura operacional dos objetos.

## Dependências e revisão

Runtime compartilhado **0.1.1**, entregue separadamente no [wheel local](../../dist/zuuuin_engine-0.1.1-py3-none-any.whl). Requer Python >=3.10 e POSIX com fcntl e O_NOFOLLOW; não possui dependências Python externas. Copiar só a pasta da skill não instala o runtime. Se faltar, declare dependency_missing e confira a [instalação](../installation.md), sem buscar pacote homônimo ou instalar globalmente.

Consulte as [instruções da skill](../../skills/zuuuin-skill-compare/SKILL.md) e a [referência de runtime](../../skills/zuuuin-skill-compare/references/runtime.md). A revisão pública identifica o conteúdo da skill; 0.1.1 é a versão separada do motor.

## Exemplo sintético

A necessidade e a revisão local têm UUIDs novos exclusivamente sintéticos. O contexto é synthetic-example:compare-empty:v1, a lista candidates é vazia e não há medições. O fragmento exige inconclusive, scores/index null, comparisons vazio e nenhuma substituição global ou mutação. O vínculo conceitual deste exemplo é a capacidade pública desta página; compare não consome nem valida capability_ids, portanto não se deve inferir validação desse vínculo pelo CLI.

Entrada: [compare.request.json](../../examples/compare.request.json). Fragmento esperado: [compare.expected.json](../../examples/compare.expected.json). Os fragmentos fixam somente campos estáveis; preserve os demais campos da resposta e não compare IDs/horários gerados como se fossem constantes.

Conclua a instalação e use um perfil privado novo conforme o [guia de uso](../usage.md). Copie o pedido demonstrativo para private/requests do perfil; escolha uma saída nova em private/outputs. Não grave resultados nesta entrega.

Partindo da raiz da entrega, com os destinos irmãos indicados no guia:

```sh
cp examples/compare.request.json ../zuuuin-local-profile/private/requests/compare.request.json
../zuuuin-runtime-env/bin/python -I -B -m zuuuin_engine compare --request ../zuuuin-local-profile/private/requests/compare.request.json --output ../zuuuin-local-profile/private/outputs/compare.result.json --private-root ../zuuuin-local-profile/private
```

O CLI recusa saída existente. Para outra observação, use um nome novo e preserve a anterior. Em caso de recusa, confira dependências, dados e fronteiras do perfil antes de tentar novamente.

## Evidência disponível e limites

A evidência disponível limita-se a observações locais e sintéticas da revisão e do runtime em laboratório. Isso não comprova eficácia em produção, ativação autônoma pelo cliente, adoção ou ganho de produtividade. Estes arquivos de exemplo são contratos demonstrativos; sua presença não é um recibo de execução.

Este é um pedido operacional de comparação, não um registro tipado completo. Candidata inelegível presente produz not_eligible dentro de compared; lista vazia produz inconclusive. O exemplo não demonstra superioridade de alternativa alguma.

Maturidade: experimental. Conteúdo próprio sob [MIT](../../LICENSE), com **enayzuin** como titular indicado; veja o [escopo da licença](../../LICENSE-STATUS.md). A licença não concede acesso a dados ou contas nem autoriza efeitos externos de uma execução. Mantenha perfis, políticas, entradas reais, resultados e registros privados fora da entrega.
