# Preparar um pacote sem exposição

Vincular preparação e eventual efeito externo a um pacote exato, autorização específica e recibo verificável, sem publicar por consequência da criação de uma skill.

Coleção: engine. Skill pública `566240cd-ae0f-41ee-8f88-cfa3af0965a9`; revisão pública `2f6c07e2-82cb-4e11-b530-d22d6ae65db0`. Esta entrega reúne oito skills engine e nenhuma implementação de skill de domínio.

## Quando usar

Use mode=prepare para obter manifesto local sem destino ou efeito externo. Um uso posterior com exposição exige políticas, revisão, autorização e destino efetivos conferidos no controle privado.

## Quando não usar

Não escolha conteúdo por conta própria, altere bytes aprovados ou publique automaticamente. Resultado externo desconhecido exige reconciliação antes de qualquer repetição.

## Entradas e resultado

O exemplo aceita package e mode=prepare. Esse ramo retorna antes de exigir destino ou autorização de efeito externo. Preparação não é publicação. Na operação de exposição, o runtime exige pacote e auditoria atuais, autorização delimitada e confirmação do efeito; esses controles vêm do perfil confiável.

## Objetos e capacidade

Capacidade: **Publicar pacote autorizado** — `e68f24ed-d351-422c-b35b-979485308332`. Expor somente o pacote aprovado e registrar efeito/destino com idempotência e verificação.

| Objeto | ID público |
| --- | --- |
| Autorização | `9f2dfa2d-437f-47d8-95ae-360e0dc2344b` |
| Publicação | `a2bd89f7-2a1e-4653-a4ff-adc07170105c` |
| Pacote selecionado | `7d929b0a-e83b-466a-bbbb-fa33ea8f8ffc` |
| Evidência | `9069df1e-5e25-4ef3-8d0e-fb3ebc2f343c` |
| Decisão | `882a93cf-8d72-4811-9067-d333ab0a5dfd` |

Os nomes, IDs e relações deste recorte estão no [modelo público](../../catalog/model.json); a revisão e os hashes estão no [catálogo de skills](../../catalog/skills.json). A associação conceitual não prova cobertura operacional dos objetos.

## Dependências e revisão

Runtime compartilhado **0.1.1**, entregue separadamente no [wheel local](../../dist/zuuuin_engine-0.1.1-py3-none-any.whl). Requer Python >=3.10 e POSIX com fcntl e O_NOFOLLOW; não possui dependências Python externas. Copiar só a pasta da skill não instala o runtime. Se faltar, declare dependency_missing e confira a [instalação](../installation.md), sem buscar pacote homônimo ou instalar globalmente.

Consulte as [instruções da skill](../../skills/zuuuin-skill-publish/SKILL.md) e a [referência de runtime](../../skills/zuuuin-skill-publish/references/runtime.md). A revisão pública identifica o conteúdo da skill; 0.1.1 é a versão separada do motor.

## Exemplo sintético

Use o mesmo tipo de fixture mínima descrita na auditoria: uma pasta nova PROFILE/source/demo-package com somente README.md sintético, sem Git ou links. Se já foi preparada para auditoria, confira os bytes e reutilize apenas para leitura, sem sobrescrever. O CWD é essa pasta. O pedido package=".", mode="prepare" deve produzir prepared_only e external_effects=false. Não há destino, push, aprovação ou recibo de publicação neste exemplo.

Entrada: [publish.request.json](../../examples/publish.request.json). Fragmento esperado: [publish.expected.json](../../examples/publish.expected.json). Os fragmentos fixam somente campos estáveis; preserve os demais campos da resposta e não compare IDs/horários gerados como se fossem constantes.

Conclua a instalação e use um perfil privado novo conforme o [guia de uso](../usage.md). Copie o pedido demonstrativo para private/requests do perfil; escolha uma saída nova em private/outputs. Não grave resultados nesta entrega.

**CWD obrigatório para este pedido:** a pasta `source/demo-package` do perfil, preparada e conferida acima. O ponto em JSON é resolvido a partir desse diretório, não da entrega, da pasta do request ou de private/.

Partindo da raiz da entrega, copie `examples/publish.request.json` para `../zuuuin-local-profile/private/requests/publish.request.json`. Depois, a partir de `../zuuuin-local-profile/source/demo-package`, execute:

```sh
../../../zuuuin-runtime-env/bin/python -I -B -m zuuuin_engine publish --request ../../private/requests/publish.request.json --output ../../private/outputs/publish.result.json --private-root ../../private
```

O CLI recusa saída existente. Para outra observação, use um nome novo e preserve a anterior. Em caso de recusa, confira dependências, dados e fronteiras do perfil antes de tentar novamente.

## Evidência disponível e limites

A evidência disponível limita-se a observações locais e sintéticas da revisão e do runtime em laboratório. Isso não comprova eficácia em produção, ativação autônoma pelo cliente, adoção ou ganho de produtividade. Estes arquivos de exemplo são contratos demonstrativos; sua presença não é um recibo de execução.

Preparação não concede direitos, não abre permissões do perfil e não confirma publicação. Para histórico Git ou transporte Git, Git local é dependência adicional; este exemplo sem Git não usa transporte. Se o resultado de uma tentativa externa for desconhecido, preserve a evidência e reconcilie.

Maturidade: experimental. Conteúdo próprio sob [MIT](../../LICENSE), com **enayzuin** como titular indicado; veja o [escopo da licença](../../LICENSE-STATUS.md). A licença não concede acesso a dados ou contas nem autoriza efeitos externos de uma execução. Mantenha perfis, políticas, entradas reais, resultados e registros privados fora da entrega.
