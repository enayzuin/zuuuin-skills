# Catalogar revisões e instalações

Descrever as pastas de skills e seus recursos sem confundir arquivos presentes, revisões, instalações, ferramentas disponíveis e execução validada.

Coleção: engine. Skill pública `c08b3153-1a28-42bb-bbd0-d5c1731de42c`; revisão pública `487b80d4-1f9d-4cd0-a063-9a8b22518c61`. Esta entrega reúne oito skills engine e nenhuma implementação de skill de domínio.

## Quando usar

Use em raízes de leitura explicitamente autorizadas, com relações do modelo já recebidas, para obter um inventário físico e conflitos.

## Quando não usar

Não mova, renomeie, instale, remova nem substitua skills. Sem modelo aprovado recebido, limite-se à descrição física.

## Entradas e resultado

O pedido informa roots, available_tools observadas e model_links. As fronteiras allowed_read_roots vêm do perfil confiável. O resultado inclui entradas, manifestos, links não seguidos, conflitos, erros, cobertura e mutations vazio. Model_links são relações recebidas, sem descoberta semântica automática.

## Objetos e capacidade

Capacidade: **Catalogar revisões e instalações** — `c1003b8d-a857-421a-be24-143a4bc297d0`. Registrar acervo e suas revisões/instalações preservando originais e limites de leitura.

| Objeto | ID público |
| --- | --- |
| Skill | `ab72be05-2d41-4985-875d-60109f84c02e` |
| Contexto de trabalho | `f7aea95d-d562-40fb-b875-8676976869b7` |
| Revisão de skill | `e952a79d-b827-4446-a339-8e873de2e47a` |
| Evidência | `9069df1e-5e25-4ef3-8d0e-fb3ebc2f343c` |
| Instalação | `0b8b9744-bcf2-4c3d-b4b6-07b35daaa101` |

Os nomes, IDs e relações deste recorte estão no [modelo público](../../catalog/model.json); a revisão e os hashes estão no [catálogo de skills](../../catalog/skills.json). A associação conceitual não prova cobertura operacional dos objetos.

## Dependências e revisão

Runtime compartilhado **0.1.1**, entregue separadamente no [wheel local](../../dist/zuuuin_engine-0.1.1-py3-none-any.whl). Requer Python >=3.10 e POSIX com fcntl e O_NOFOLLOW; não possui dependências Python externas. Copiar só a pasta da skill não instala o runtime. Se faltar, declare dependency_missing e confira a [instalação](../installation.md), sem buscar pacote homônimo ou instalar globalmente.

Consulte as [instruções da skill](../../skills/zuuuin-skill-catalog/SKILL.md) e a [referência de runtime](../../skills/zuuuin-skill-catalog/references/runtime.md). A revisão pública identifica o conteúdo da skill; 0.1.1 é a versão separada do motor.

## Exemplo sintético

Prepare uma pasta nova PROFILE/source/engine-fixture e copie para ela somente as oito pastas de skills desta entrega, como dados; não é instalação no cliente. Pare se o destino já existir e confira o conteúdo antes de reutilizar qualquer observação. A entrada roots=["."] usa como CWD exatamente essa pasta. O fragmento espera cataloged, uma raiz, cobertura completa e nenhum erro, link, conflito ou mutação. As oito entradas devem corresponder às oito pastas copiadas.

Entrada: [catalog.request.json](../../examples/catalog.request.json). Fragmento esperado: [catalog.expected.json](../../examples/catalog.expected.json). Os fragmentos fixam somente campos estáveis; preserve os demais campos da resposta e não compare IDs/horários gerados como se fossem constantes.

Conclua a instalação e use um perfil privado novo conforme o [guia de uso](../usage.md). Copie o pedido demonstrativo para private/requests do perfil; escolha uma saída nova em private/outputs. Não grave resultados nesta entrega.

**CWD obrigatório para este pedido:** a pasta `source/engine-fixture` do perfil, preparada e conferida acima. O ponto em JSON é resolvido a partir desse diretório, não da entrega, da pasta do request ou de private/.

Partindo da raiz da entrega, copie `examples/catalog.request.json` para `../zuuuin-local-profile/private/requests/catalog.request.json`. Depois, a partir de `../zuuuin-local-profile/source/engine-fixture`, execute:

```sh
../../../zuuuin-runtime-env/bin/python -I -B -m zuuuin_engine catalog --request ../../private/requests/catalog.request.json --output ../../private/outputs/catalog.result.json --private-root ../../private
```

O CLI recusa saída existente. Para outra observação, use um nome novo e preserve a anterior. Em caso de recusa, confira dependências, dados e fronteiras do perfil antes de tentar novamente.

## Evidência disponível e limites

A evidência disponível limita-se a observações locais e sintéticas da revisão e do runtime em laboratório. Isso não comprova eficácia em produção, ativação autônoma pelo cliente, adoção ou ganho de produtividade. Estes arquivos de exemplo são contratos demonstrativos; sua presença não é um recibo de execução.

Ferramentas ausentes só podem ser inferidas do manifesto declarado e das ferramentas informadas. O parser de metadados possui escopo limitado; recusa não prova defeito de toda skill ou obsolescência. Não executa recursos do pacote.

Maturidade: experimental. Conteúdo próprio sob [MIT](../../LICENSE), com **enayzuin** como titular indicado; veja o [escopo da licença](../../LICENSE-STATUS.md). A licença não concede acesso a dados ou contas nem autoriza efeitos externos de uma execução. Mantenha perfis, políticas, entradas reais, resultados e registros privados fora da entrega.
