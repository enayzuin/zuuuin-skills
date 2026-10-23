# Descoberta pelo consumidor identificado

Esta candidata prepara somente o formato legado de diretório em `.well-known/skills/`, para o consumidor identificado **skills CLI 1.7.4**. É um contrato específico, não uma promessa de descoberta universal ou ativação no cliente. O recorte continua com oito skills engine, zero implementações de skills de domínio e runtime separado 0.1.1.

O [índice legado](../.well-known/skills/index.json) descreve cada skill por name, description e files. Cada entrada lista `SKILL.md` e `references/runtime.md`; os dois recursos são cópias dos bytes da pasta pública correspondente. `references/runtime.md` leva o aviso MIT completo de cada unidade. O nome da skill determina seu subdiretório. São oito entradas, dezesseis recursos e um índice. O destino escolhido para essa árvore é [GitHub Pages](https://enayzuin.github.io/zuuuin-skills/), com índice em [.well-known/skills/index.json](https://enayzuin.github.io/zuuuin-skills/.well-known/skills/index.json); esses URLs não comprovam disponibilidade externa.

O formato foi escolhido pela [documentação do endpoint legado](https://www.mintlify.com/docs/ai/skillmd#skills-index) e pelo [provedor da versão 1.7.4](https://raw.githubusercontent.com/vercel-labs/skills/v1.7.4/src/providers/wellknown.ts). Esse consumidor pode consultar o caminho de agent-skills antes do legado. Esta entrega prepara apenas o legado; não implementa um segundo formato, um servidor MCP ou uma integração Mintlify.

## O que o diretório entrega

O gerador lê o [catálogo público](../catalog/skills.json), confere as revisões e hashes e copia os recursos selecionados. Não altera os [originais de skills](index.md), não inclui perfis ou políticas e não instala o runtime. O wheel local continua separado, com as dependências descritas na [instalação](installation.md).

O provedor identificado obtém o arquivo `SKILL.md` e busca os demais caminhos de files sob o mesmo subdiretório. Sua leitura do índice não garante que todos os recursos auxiliares chegaram; qualquer teste de consumo deve conferir também `references/runtime.md` de cada skill.

## Regeneração local

Partindo da raiz da entrega, confira os dezessete arquivos com:

```sh
python3 -I -B tools/build_well_known.py --check
```

Sem `--check`, o gerador cria arquivos ausentes e aceita os existentes somente quando os bytes são iguais; não substitui recursos divergentes. A lista de saída é determinada pelo catálogo e seus hashes. Ele usa a biblioteca padrão e não realiza rede, instalação, publicação ou chamadas ao motor.

## Limites de consumo e exposição

O repositório escolhido é [enayzuin/zuuuin-skills](https://github.com/enayzuin/zuuuin-skills). A disponibilidade pública do repositório, do site e do índice ainda não foi verificada. Arquivo presente e `--check` aprovado demonstram apenas preparação local. Uma observação de consumo precisa identificar o consumidor, o ambiente e os recursos efetivamente recuperados; não prova instalação, recarga, uso na próxima mensagem ou eficácia em produção.

As instruções continuam em português. Leitura HTTP das pastas não fornece Python nem o wheel e não configura o perfil privado. Métricas e disponibilidade não observadas permanecem desconhecidas.

O conteúdo próprio usa MIT, com **enayzuin** como titular indicado; veja o [escopo da licença](../LICENSE-STATUS.md). Um índice técnico ou um teste local não substitui a revisão e a autorização de uma operação de publicação sobre pacote e destino exatos. Dados e contas de terceiros exigem permissões próprias.
