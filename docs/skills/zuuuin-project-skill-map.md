# Mapear projetos e necessidades

Transformar fontes autorizadas em projetos reconhecíveis e necessidades descritas por resultados, sem preencher lacunas a partir do nome.

Coleção: engine. Skill pública `3053093f-1185-4d2e-b25e-2befc4435056`; revisão pública `bd123fb8-238a-451f-9ef4-13e3d341adc6`. Esta entrega reúne oito skills engine e nenhuma implementação de skill de domínio.

## Quando usar

Use antes de escolher skills quando o trabalho, as fontes, os critérios ou a cobertura ainda precisam ser explicitados.

## Quando não usar

Não implemente backlog, infira requisitos por nomes ou escolha uma skill vencedora com este mapeamento.

## Entradas e resultado

A entrada contém sources autorizadas, estado de paginação e projetos com canonical_key. Necessidades informam entrada, resultado desejado, critérios, restrições e desconhecidos. A saída preserva IDs, referências, conflitos, lacunas e cobertura; complete só é verdadeiro quando todas as fontes estão completas e sem páginas restantes.

## Objetos e capacidade

Capacidade: **Levantar projetos e necessidades** — `23f6f714-9ca8-40c4-8c2b-85432376c4d7`. Transformar fontes autorizadas em identidades, necessidades por resultado e cobertura explícita.

| Objeto | ID público |
| --- | --- |
| Contexto de trabalho | `f7aea95d-d562-40fb-b875-8676976869b7` |
| Evidência | `9069df1e-5e25-4ef3-8d0e-fb3ebc2f343c` |

Os nomes, IDs e relações deste recorte estão no [modelo público](../../catalog/model.json); a revisão e os hashes estão no [catálogo de skills](../../catalog/skills.json). A associação conceitual não prova cobertura operacional dos objetos.

## Dependências e revisão

Runtime compartilhado **0.1.1**, entregue separadamente no [wheel local](../../dist/zuuuin_engine-0.1.1-py3-none-any.whl). Requer Python >=3.10 e POSIX com fcntl e O_NOFOLLOW; não possui dependências Python externas. Copiar só a pasta da skill não instala o runtime. Se faltar, declare dependency_missing e confira a [instalação](../installation.md), sem buscar pacote homônimo ou instalar globalmente.

Consulte as [instruções da skill](../../skills/zuuuin-project-skill-map/SKILL.md) e a [referência de runtime](../../skills/zuuuin-project-skill-map/references/runtime.md). A revisão pública identifica o conteúdo da skill; 0.1.1 é a versão separada do motor.

## Exemplo sintético

A entrada demonstra uma fonte completa, um projeto fictício e um requisito observável. O fragmento esperado exige mapped, cobertura completa, um projeto observado e ausência de lacunas/conflitos. Frequência e prioridade desconhecidas continuam null.

Entrada: [project-map.request.json](../../examples/project-map.request.json). Fragmento esperado: [project-map.expected.json](../../examples/project-map.expected.json). Os fragmentos fixam somente campos estáveis; preserve os demais campos da resposta e não compare IDs/horários gerados como se fossem constantes.

Conclua a instalação e use um perfil privado novo conforme o [guia de uso](../usage.md). Copie o pedido demonstrativo para private/requests do perfil; escolha uma saída nova em private/outputs. Não grave resultados nesta entrega.

Partindo da raiz da entrega, com os destinos irmãos indicados no guia:

```sh
cp examples/project-map.request.json ../zuuuin-local-profile/private/requests/project-map.request.json
../zuuuin-runtime-env/bin/python -I -B -m zuuuin_engine project-map --request ../zuuuin-local-profile/private/requests/project-map.request.json --output ../zuuuin-local-profile/private/outputs/project-map.result.json --private-root ../zuuuin-local-profile/private
```

O CLI recusa saída existente. Para outra observação, use um nome novo e preserve a anterior. Em caso de recusa, confira dependências, dados e fronteiras do perfil antes de tentar novamente.

## Evidência disponível e limites

A evidência disponível limita-se a observações locais e sintéticas da revisão e do runtime em laboratório. Isso não comprova eficácia em produção, ativação autônoma pelo cliente, adoção ou ganho de produtividade. Estes arquivos de exemplo são contratos demonstrativos; sua presença não é um recibo de execução.

A consolidação depende da identidade canônica e dos fatos fornecidos. Fonte incompleta ou erro não prova ausência. O helper não lê contas nem interpreta sozinho novas fontes.

Maturidade: experimental. Conteúdo próprio sob [MIT](../../LICENSE), com **enayzuin** como titular indicado; veja o [escopo da licença](../../LICENSE-STATUS.md). A licença não concede acesso a dados ou contas nem autoriza efeitos externos de uma execução. Mantenha perfis, políticas, entradas reais, resultados e registros privados fora da entrega.
