# Verificação local e CI preparada

Esta candidata tem verificações de formatos, links e exemplos sintéticos. O workflow preparado executa somente verificação. Não cria release, faz push, publica site, envia artefatos a um serviço ou instala skills no ambiente pessoal.

## Executar localmente

Na raiz da entrega:

```sh
python3 -I -B tools/verify_delivery.py
```

O comando lê os arquivos JSON sem aceitar chaves duplicadas ou números não finitos, confere a sintaxe Python e o frontmatter selecionado das oito skills, resolve links locais e verifica hashes das revisões e dos quatorze módulos do wheel. Também confere os geradores de descoberta e constrói uma prévia temporária para verificar links HTML e âncoras. O renderizador é o mesmo descrito no [site local](site.md). A verificação de links externos não faz requisições de rede.

Depois de instalar o wheel local em um venv separado, conforme a [instalação](installation.md), acrescente `--examples` com o Python desse venv. Ele cria um perfil temporário novo, executa as oito operações documentadas e compara fragmentos esperados definidos nos [exemplos](../examples/README.md). Os resultados sintéticos vão para stdout; o perfil temporário é removido ao terminar. As autorizações e o pacote devem permanecer iguais. A opção exige o runtime 0.1.1 instalado e não o obtém de um registro público.

Os casos demonstram contratos dos helpers. O caso evaluate recebe observações fictícias já fornecidas; não executa os braços de uma experiência nem mede produtividade. Cópia de instruções, instalação de um consumidor, ativação autônoma e resultados de trabalho real continuam verificações distintas.

## Workflow

O [workflow de verificação](../.github/workflows/verify.yml) está preparado para GitHub Actions com `contents: read`, ações fixadas em commits e credenciais de checkout não persistidas. Usa eventos push e pull_request restritos à branch `main`, além de disparo manual; não usa pull_request_target, segredos de publicação, permissões de escrita, ambiente de produção ou etapa de deploy. Instala somente o wheel local sem índice e sem dependências externas; o provisionamento futuro do runner/Python pelas ações é separado desse passo offline.

Sua existência local não comprova execução hospedada. O ambiente Ubuntu/Python do runner e o acesso ao repositório real ainda precisam ser observados quando houver destino autorizado. Os comandos locais e seus resultados devem ser atribuídos ao ambiente efetivamente testado. Não habilite publicação como consequência de uma contribuição externa aprovada por testes.

O destino preparado é [enayzuin/zuuuin-skills](https://github.com/enayzuin/zuuuin-skills), com [GitHub Pages](https://enayzuin.github.io/zuuuin-skills/) e conteúdo próprio sob MIT, com **enayzuin** como titular indicado; veja o [escopo da licença](../LICENSE-STATUS.md). A escolha desses valores não comprova disponibilidade externa. Verificação técnica não substitui revisão contextual do pacote exato ou autorização operacional de exposição.
