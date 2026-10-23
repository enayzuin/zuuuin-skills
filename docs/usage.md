# Uso com perfil privado

Conclua a [instalação](installation.md) antes destes passos. Os comandos abaixo partem da raiz da entrega, com venv em `../zuuuin-runtime-env` e perfil novo em `../zuuuin-local-profile`. O inicializador já criou `private/requests` e `private/outputs`.

O CLI exige `--private-root` e lê checkpoint, políticas e raízes do perfil. Entradas precisam estar nas raízes autorizadas desse perfil. Por isso, copie as entradas demonstrativas antes de executar:

```sh
cp examples/project-map.request.json ../zuuuin-local-profile/private/requests/project-map.request.json
cp examples/router.request.json ../zuuuin-local-profile/private/requests/router.request.json
../zuuuin-runtime-env/bin/python -I -B -m zuuuin_engine project-map --request ../zuuuin-local-profile/private/requests/project-map.request.json --output ../zuuuin-local-profile/private/outputs/project-map.result.json --private-root ../zuuuin-local-profile/private
../zuuuin-runtime-env/bin/python -I -B -m zuuuin_engine router --request ../zuuuin-local-profile/private/requests/router.request.json --output ../zuuuin-local-profile/private/outputs/router.result.json --private-root ../zuuuin-local-profile/private
```

Essas entradas descrevem apenas dados sintéticos. Nenhum projeto real, conta ou fonte externa é consultado. Os resultados ficam no perfil privado, fora da entrega. O CLI recusa saída existente: para uma nova execução, escolha outro nome de resultado e preserve a observação anterior.

Compare os resultados com os fragmentos [project-map.expected.json](../examples/project-map.expected.json) e [router.expected.json](../examples/router.expected.json). Cada campo do fragmento precisa existir e coincidir. Objetos podem ter campos adicionais; IDs e horários novos não precisam ser iguais entre execuções. Não transforme saída nominal em aceite de critérios que você não conferiu. Veja o [contrato dos exemplos](../examples/README.md).

## Entradas e limites

Escolha a skill pela transformação pretendida e leia seu `SKILL.md`, inclusive não uso, entradas, recursos e autorizações. O runtime aceita pedidos explícitos; não pesquisa contas automaticamente e não substitui o método do projeto. O perfil inicial tem `source/`, `test/` e `release/` próprios e vazios. Autorizar uma fonte fora deles exige uma decisão explícita sobre o escopo; não amplie raízes para contornar uma recusa.

Mantenha cópias de trabalho, políticas, configurações, saídas e evidências privadas fora desta entrega e de qualquer repositório público. A ausência de Obsidian ou Linear não impede esses exemplos. Conectores e dados reais exigem permissões e verificação próprias.

A evidência disponível é local e sintética. Descoberta no cliente, recarga, acionamento na próxima mensagem e eficácia em produção permanecem desconhecidos quando não observados. Métricas sem medição ficam desconhecidas; não estime custo ou taxa de ativação a partir do status de uma API.

O perfil começa sem autorizações ou aprovações e com efeitos externos desabilitados. Não edite o checkpoint para aparentar avanço, aprovação ou publicação. Preparação de pacote e simulação exigem sua própria conferência; publicação real depende das permissões e políticas efetivas. O conteúdo próprio está sob [MIT](../LICENSE), com **enayzuin** como titular indicado; a licença não fornece autorização para acessar contas ou dados privados, nem para publicar resultados de terceiros.

Em uma falha, preserve o pedido e a mensagem de erro, confira pré-requisitos e limites e escolha um caminho de saída novo ao tentar novamente. Para desfazer uma instalação local ou retornar a revisão anterior, siga os limites de [remoção e rollback](installation.md#atualização-remoção-e-rollback).
