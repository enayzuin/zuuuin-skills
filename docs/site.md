# Site estático e prévia local

O site usa apenas a biblioteca padrão de Python. O gerador não envia arquivos, contrata hospedagem, compra domínio ou acessa contas. A entrega contém oito skills engine, zero implementações de skills de domínio e runtime separado 0.1.1. O destino escolhido é [GitHub Pages](https://enayzuin.github.io/zuuuin-skills/), associado a [enayzuin/zuuuin-skills](https://github.com/enayzuin/zuuuin-skills). O conteúdo próprio está sob [MIT](../LICENSE), com **enayzuin** como titular indicado.

## Preparar uma cópia para leitura

Na raiz da entrega, escolha um diretório novo fora dela, com pai existente:

```sh
python3 -I -B tools/build_site.py --output ../zuuuin-site-preview
```

Abra `index.html` do resultado local. O site mantém os arquivos Markdown originais, recursos de instalação e índices, acrescentando páginas HTML, estilos locais e navegação. O renderizador cobre títulos, links, tabelas, listas e blocos de código usados nesta entrega; não executa HTML embutido nem scripts. Não é um renderizador Markdown completo.

Cada página HTML aponta para sua versão Markdown com `rel="alternate"` e para `llms.txt` com `rel="describedby"`. A cópia conserva o diretório [.well-known](consumer-discovery.md) e seus recursos e inclui `.nojekyll` na raiz da árvore estática para GitHub Pages. Documentação legível não fornece o runtime, instala instruções ou garante ativação por um cliente.

## Endereço e acesso

Para conferir canonical e sitemap com o endereço escolhido, gere outra pasta nova:

```sh
python3 -I -B tools/build_site.py --output ../zuuuin-site-target-preview --base-url https://enayzuin.github.io/zuuuin-skills/
```

O parâmetro exige HTTPS, aceita um prefixo de caminho e não realiza deploy. Sem `--base-url`, a prévia omite canonical e sitemap; com o endereço explícito, ambos são gerados para esse prefixo. Os metadados preparados não comprovam que o site esteja publicado ou acessível.

Todas as páginas incluem `noindex,nofollow`, e `robots.txt` contém `Disallow: /`, inclusive quando o endereço escolhido é fornecido. Essas regras orientam robôs; não são autenticação ou controle de acesso. Mantenha a prévia em armazenamento privado até a autorização do pacote e destino exatos. Uma eventual exposição não garante indexação, e qualquer mudança dessas regras exige revisão própria.

A publicação futura deve usar a árvore estática exata revisada para GitHub Pages. A CI incluída executa somente [verificação](validation.md); não publica ou ativa o site automaticamente. O gerador recusa saída dentro da entrega ou em pasta já existente, preservando cópias anteriores.

Veja [índice](index.md), [instalação](installation.md) e [escopo da licença](../LICENSE-STATUS.md). A preparação do endereço e dos arquivos não é um recibo de publicação.
