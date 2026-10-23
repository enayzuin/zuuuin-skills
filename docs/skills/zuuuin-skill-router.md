# Selecionar uma capacidade pertinente

Relacionar uma tarefa ao mapa recebido e a revisões aprovadas no contexto correto, sem instalar, criar ou iniciar descobertas sem vínculo.

Coleção: engine. Skill pública `836f06da-a10a-46a2-b5d2-bdbc4d78cc7e`; revisão pública `6bdc643d-0e55-4e62-8224-d67e19405c78`. Esta entrega reúne oito skills engine e nenhuma implementação de skill de domínio.

## Quando usar

Use em tarefa relacionada a skills quando context_key, need_id e capability_ids estiverem resolvidos por evidência confiável, ou quando o mapa autorizado disponível puder resolver a lacuna.

## Quando não usar

Não use como novo método de desenvolvimento, catálogo global a cada mensagem ou autorização para instalar, criar ou publicar. Conversa fora do escopo não inicia descoberta.

## Entradas e resultado

O pedido pode informar task, context_key, need_id, capability_ids e identidades de sessão/tarefa/evento. Catálogo, ferramentas, decisões e deduplicação precisam pertencer ao contexto. Um vínculo já resolvido não exige outro documento para validá-lo novamente; lacuna não recuperável produz needs_mapping sem recomendar revisão.

## Objetos e capacidade

Capacidade: **Selecionar capacidade pertinente** — `76ff1fa6-245b-46ac-9594-d765d493f695`. Selecionar implementação pertinente ao contexto e registrar decisão sem reentrada ou adoção ilimitada.

| Objeto | ID público |
| --- | --- |
| Checkpoint | `de1a6298-7289-4b82-b0eb-60114eaf943e` |
| Contexto de trabalho | `f7aea95d-d562-40fb-b875-8676976869b7` |
| Revisão de skill | `e952a79d-b827-4446-a339-8e873de2e47a` |
| Decisão | `882a93cf-8d72-4811-9067-d333ab0a5dfd` |

Os nomes, IDs e relações deste recorte estão no [modelo público](../../catalog/model.json); a revisão e os hashes estão no [catálogo de skills](../../catalog/skills.json). A associação conceitual não prova cobertura operacional dos objetos.

## Dependências e revisão

Runtime compartilhado **0.1.1**, entregue separadamente no [wheel local](../../dist/zuuuin_engine-0.1.1-py3-none-any.whl). Requer Python >=3.10 e POSIX com fcntl e O_NOFOLLOW; não possui dependências Python externas. Copiar só a pasta da skill não instala o runtime. Se faltar, declare dependency_missing e confira a [instalação](../installation.md), sem buscar pacote homônimo ou instalar globalmente.

Consulte as [instruções da skill](../../skills/zuuuin-skill-router/SKILL.md) e a [referência de runtime](../../skills/zuuuin-skill-router/references/runtime.md). A revisão pública identifica o conteúdo da skill; 0.1.1 é a versão separada do motor.

## Exemplo sintético

A entrada related=false descreve uma conversa fictícia fora de uma tarefa de skills. O fragmento exige out_of_scope, selected vazio, discovery_performed=false e created_skill=false. O exemplo verifica a recusa de reentrada, não seleção contextual ou descoberta em conta real.

Entrada: [router.request.json](../../examples/router.request.json). Fragmento esperado: [router.expected.json](../../examples/router.expected.json). Os fragmentos fixam somente campos estáveis; preserve os demais campos da resposta e não compare IDs/horários gerados como se fossem constantes.

Conclua a instalação e use um perfil privado novo conforme o [guia de uso](../usage.md). Copie o pedido demonstrativo para private/requests do perfil; escolha uma saída nova em private/outputs. Não grave resultados nesta entrega.

Partindo da raiz da entrega, com os destinos irmãos indicados no guia:

```sh
cp examples/router.request.json ../zuuuin-local-profile/private/requests/router.request.json
../zuuuin-runtime-env/bin/python -I -B -m zuuuin_engine router --request ../zuuuin-local-profile/private/requests/router.request.json --output ../zuuuin-local-profile/private/outputs/router.result.json --private-root ../zuuuin-local-profile/private
```

O CLI recusa saída existente. Para outra observação, use um nome novo e preserve a anterior. Em caso de recusa, confira dependências, dados e fronteiras do perfil antes de tentar novamente.

## Evidência disponível e limites

A evidência disponível limita-se a observações locais e sintéticas da revisão e do runtime em laboratório. Isso não comprova eficácia em produção, ativação autônoma pelo cliente, adoção ou ganho de produtividade. Estes arquivos de exemplo são contratos demonstrativos; sua presença não é um recibo de execução.

Ferramenta disponível e revisão aprovada não resolvem identidade ausente. Busca com erro não significa ausência. Seleção do helper não comprova acionamento autônomo pelo cliente nem autoriza adoção.

Maturidade: experimental. Conteúdo próprio sob [MIT](../../LICENSE), com **enayzuin** como titular indicado; veja o [escopo da licença](../../LICENSE-STATUS.md). A licença não concede acesso a dados ou contas nem autoriza efeitos externos de uma execução. Mantenha perfis, políticas, entradas reais, resultados e registros privados fora da entrega.
