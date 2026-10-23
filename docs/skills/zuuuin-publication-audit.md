# Auditar um pacote exato

Examinar bytes, auxiliares e histórico aplicável antes da exposição, sem confundir hash correspondente com segurança, direitos ou autorização.

Coleção: engine. Skill pública `c4d06892-9296-45b5-8336-fc34b71f0de7`; revisão pública `56f2c90d-42ab-4753-9fa2-a216a7353996`. Esta entrega reúne oito skills engine e nenhuma implementação de skill de domínio.

## Quando usar

Use com pacote autorizado e congelado, identificadores privados conhecidos, histórico aplicável e revisão contextual independente ligada ao digest exato.

## Quando não usar

Não escolha destino, conceda permissão de publicação ou aprove binários não examinados. O parecer não publica nada.

## Entradas e resultado

A entrada informa package e, conforme o caso, private_identifiers, snapshots de histórico, direitos e contextual_review. A saída pode ser approved_in_scope, blocked ou review_required, com manifesto, cobertura, achados redigidos e limitações. Histórico Git presente é inspecionado automaticamente dentro dos limites do runtime.

## Objetos e capacidade

Capacidade: **Auditar pacote para exposição** — `99c2045c-ad0b-4a4c-ac22-6532b1df90c3`. Examinar conteúdo, auxiliares, metadados, histórico e artefatos do pacote exato.

| Objeto | ID público |
| --- | --- |
| Autorização | `9f2dfa2d-437f-47d8-95ae-360e0dc2344b` |
| Pacote selecionado | `7d929b0a-e83b-466a-bbbb-fa33ea8f8ffc` |
| Evidência | `9069df1e-5e25-4ef3-8d0e-fb3ebc2f343c` |
| Decisão | `882a93cf-8d72-4811-9067-d333ab0a5dfd` |

Os nomes, IDs e relações deste recorte estão no [modelo público](../../catalog/model.json); a revisão e os hashes estão no [catálogo de skills](../../catalog/skills.json). A associação conceitual não prova cobertura operacional dos objetos.

## Dependências e revisão

Runtime compartilhado **0.1.1**, entregue separadamente no [wheel local](../../dist/zuuuin_engine-0.1.1-py3-none-any.whl). Requer Python >=3.10 e POSIX com fcntl e O_NOFOLLOW; não possui dependências Python externas. Copiar só a pasta da skill não instala o runtime. Se faltar, declare dependency_missing e confira a [instalação](../installation.md), sem buscar pacote homônimo ou instalar globalmente.

Git local também é necessário quando o pacote possui histórico Git aplicável. A fixture demonstrativa sem Git dispensa essa parte.

Consulte as [instruções da skill](../../skills/zuuuin-publication-audit/SKILL.md) e a [referência de runtime](../../skills/zuuuin-publication-audit/references/runtime.md). A revisão pública identifica o conteúdo da skill; 0.1.1 é a versão separada do motor.

## Exemplo sintético

Prepare uma pasta nova PROFILE/source/demo-package contendo somente README.md com a frase "Pacote sintético para revisão local." e uma quebra de linha, sem Git, links ou arquivos adicionais. Pare se a pasta já existir; nunca sobrescreva um pacote existente. O CWD é exatamente essa pasta e package=".". rights_confirmed=false e ausência de revisão contextual devem produzir review_required, duas limitações explícitas, findings vazio e exposure_performed=false.

Entrada: [audit.request.json](../../examples/audit.request.json). Fragmento esperado: [audit.expected.json](../../examples/audit.expected.json). Os fragmentos fixam somente campos estáveis; preserve os demais campos da resposta e não compare IDs/horários gerados como se fossem constantes.

Conclua a instalação e use um perfil privado novo conforme o [guia de uso](../usage.md). Copie o pedido demonstrativo para private/requests do perfil; escolha uma saída nova em private/outputs. Não grave resultados nesta entrega.

**CWD obrigatório para este pedido:** a pasta `source/demo-package` do perfil, preparada e conferida acima. O ponto em JSON é resolvido a partir desse diretório, não da entrega, da pasta do request ou de private/.

Partindo da raiz da entrega, copie `examples/audit.request.json` para `../zuuuin-local-profile/private/requests/audit.request.json`. Depois, a partir de `../zuuuin-local-profile/source/demo-package`, execute:

```sh
../../../zuuuin-runtime-env/bin/python -I -B -m zuuuin_engine audit --request ../../private/requests/audit.request.json --output ../../private/outputs/audit.result.json --private-root ../../private
```

O CLI recusa saída existente. Para outra observação, use um nome novo e preserve a anterior. Em caso de recusa, confira dependências, dados e fronteiras do perfil antes de tentar novamente.

## Evidência disponível e limites

A evidência disponível limita-se a observações locais e sintéticas da revisão e do runtime em laboratório. Isso não comprova eficácia em produção, ativação autônoma pelo cliente, adoção ou ganho de produtividade. Estes arquivos de exemplo são contratos demonstrativos; sua presença não é um recibo de execução.

Ausência de achados automatizados não elimina a revisão contextual nem confirma direitos. Binários, cobertura de histórico e limites de leitura precisam ser examinados. Qualquer alteração de bytes invalida o vínculo do parecer.

Maturidade: experimental. Conteúdo próprio sob [MIT](../../LICENSE), com **enayzuin** como titular indicado; veja o [escopo da licença](../../LICENSE-STATUS.md). A licença não concede acesso a dados ou contas nem autoriza efeitos externos de uma execução. Mantenha perfis, políticas, entradas reais, resultados e registros privados fora da entrega.
