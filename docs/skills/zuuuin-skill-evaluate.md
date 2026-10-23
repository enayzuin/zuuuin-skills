# Avaliar uma revisão por casos

Conferir observações contra critérios previamente fixados, preservando casos não executados e métricas desconhecidas.

Coleção: engine. Skill pública `5d552bc8-026b-47a0-ace9-d9171da95d9a`; revisão pública `80651c06-52f7-4bb2-b4fe-9e591228b2cb`. Esta entrega reúne oito skills engine e nenhuma implementação de skill de domínio.

## Quando usar

Use quando já há revisão identificada, casos, critérios e evidência observada atribuída de uma execução autorizada.

## Quando não usar

Não edite automaticamente a skill, aprove a própria mudança ou transforme casos não executados em sucesso.

## Entradas e resultado

Cada caso informa case_id, executed, expected por caminho de campo, observed_output e evidence_ref. Campos de ativação são opcionais; métricas só entram com a fonte e a evidência exigidas. O helper compara os dados fornecidos: não executa a tarefa, não executa braços com/sem skill e não abre nem autentica a origem de evidence_ref.

## Objetos e capacidade

Capacidade: **Avaliar uma revisão por casos** — `9c161232-89d9-4995-941e-bc24687ffcb7`. Executar casos autorizados e registrar resultados, métricas e desconhecidos da revisão.

| Objeto | ID público |
| --- | --- |
| Caso de avaliação | `8cb878cb-6bfb-43ff-90e3-e2348eee474f` |
| Contexto de trabalho | `f7aea95d-d562-40fb-b875-8676976869b7` |
| Revisão de skill | `e952a79d-b827-4446-a339-8e873de2e47a` |
| Avaliação | `2e6cd3ac-b8bc-4d39-b1a0-d90a50a7f550` |
| Evidência | `9069df1e-5e25-4ef3-8d0e-fb3ebc2f343c` |

Os nomes, IDs e relações deste recorte estão no [modelo público](../../catalog/model.json); a revisão e os hashes estão no [catálogo de skills](../../catalog/skills.json). A associação conceitual não prova cobertura operacional dos objetos.

## Dependências e revisão

Runtime compartilhado **0.1.1**, entregue separadamente no [wheel local](../../dist/zuuuin_engine-0.1.1-py3-none-any.whl). Requer Python >=3.10 e POSIX com fcntl e O_NOFOLLOW; não possui dependências Python externas. Copiar só a pasta da skill não instala o runtime. Se faltar, declare dependency_missing e confira a [instalação](../installation.md), sem buscar pacote homônimo ou instalar globalmente.

Consulte as [instruções da skill](../../skills/zuuuin-skill-evaluate/SKILL.md) e a [referência de runtime](../../skills/zuuuin-skill-evaluate/references/runtime.md). A revisão pública identifica o conteúdo da skill; 0.1.1 é a versão separada do motor.

## Exemplo sintético

A entrada contém um caso demonstrativo com duas fixtures inline iguais: without_skill.result e with_skill.result valem synthetic-equal. Os UUIDs de revisão e caso desse pedido são fictícios e não identificam a revisão pública desta página. A flag executed=true pertence exclusivamente à observação fictícia fornecida, não relata execução real de uma skill. Ao executar o exemplo, o que se testa é a comparação desses dados pelo avaliador. Os dois critérios fixos devem passar, ambos os braços ficam iguais, tokens/duração/custo e taxas de ativação permanecem null. Não há medições reais nem ganho demonstrado.

Entrada: [evaluate.request.json](../../examples/evaluate.request.json). Fragmento esperado: [evaluate.expected.json](../../examples/evaluate.expected.json). Os fragmentos fixam somente campos estáveis; preserve os demais campos da resposta e não compare IDs/horários gerados como se fossem constantes.

Conclua a instalação e use um perfil privado novo conforme o [guia de uso](../usage.md). Copie o pedido demonstrativo para private/requests do perfil; escolha uma saída nova em private/outputs. Não grave resultados nesta entrega.

Partindo da raiz da entrega, com os destinos irmãos indicados no guia:

```sh
cp examples/evaluate.request.json ../zuuuin-local-profile/private/requests/evaluate.request.json
../zuuuin-runtime-env/bin/python -I -B -m zuuuin_engine evaluate --request ../zuuuin-local-profile/private/requests/evaluate.request.json --output ../zuuuin-local-profile/private/outputs/evaluate.result.json --private-root ../zuuuin-local-profile/private
```

O CLI recusa saída existente. Para outra observação, use um nome novo e preserve a anterior. Em caso de recusa, confira dependências, dados e fronteiras do perfil antes de tentar novamente.

## Evidência disponível e limites

A evidência disponível limita-se a observações locais e sintéticas da revisão e do runtime em laboratório. Isso não comprova eficácia em produção, ativação autônoma pelo cliente, adoção ou ganho de produtividade. Estes arquivos de exemplo são contratos demonstrativos; sua presença não é um recibo de execução.

Status passed valida a comparação dos campos fornecidos, não a autenticidade das observações, uma execução anterior de braços ou eficácia em produção. Critério ausente falha; caso não executado permanece not_run.

Maturidade: experimental. Conteúdo próprio sob [MIT](../../LICENSE), com **enayzuin** como titular indicado; veja o [escopo da licença](../../LICENSE-STATUS.md). A licença não concede acesso a dados ou contas nem autoriza efeitos externos de uma execução. Mantenha perfis, políticas, entradas reais, resultados e registros privados fora da entrega.
