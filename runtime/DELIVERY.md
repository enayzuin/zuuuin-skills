# Runtime local do motor

Requer Python >=3.10 em POSIX (macOS/Linux, `fcntl` e `O_NOFOLLOW`). Nenhuma biblioteca de terceiros é necessária. As oito skills de motor dependem deste runtime; skills de domínio independentes não dependem dele.

Construa o wheel somente da fonte aprovada: no diretório `runtime`, execute `python3 -c 'import zuuuin_build; print(zuuuin_build.build_wheel("dist"))'`. A saída é `dist/zuuuin_engine-0.1.1-py3-none-any.whl`.

Em um ambiente virtual de laboratório ou outro destino explicitamente autorizado, instale o arquivo local com `python -m pip install --no-index --no-deps /caminho/real/do/artefato.whl`. O caminho ilustrativo precisa ser substituído pelo artefato realmente construído e verificado. Não consultar PyPI por um nome homônimo e não instalar globalmente por padrão.

Durante desenvolvimento, `PYTHONPATH` pode apontar à pasta `runtime` aprovada. O CLI é `python -m zuuuin_engine OPERATION --request REQUEST.json --output OUTPUT.json --private-root PRIVATE_ROOT`. O checkpoint, políticas e autorizações são privados e nunca acompanham uma skill pública.

O wheel contém todos os módulos chamados pelas oito operações. Instalar uma pasta de skill sem esse artefato deixa uma dependência ausente explícita; não é considerado instalação funcional. A distribuição 0.1.1 fornece o wheel junto às skills do motor. O uso observado é local e sintético; instalação não comprova ativação autônoma ou eficácia em produção.

O conteúdo próprio está sob a licença [MIT](LICENSE), com aviso de copyright de enayzuin. O wheel inclui os mesmos termos em `zuuuin_engine-0.1.1.dist-info/licenses/LICENSE`, declarados nos metadados do pacote. A fonte escolhida é [enayzuin/zuuuin-skills](https://github.com/enayzuin/zuuuin-skills) e a documentação tem como destino [GitHub Pages](https://enayzuin.github.io/zuuuin-skills/). A construção local não envia arquivos nem ativa esses destinos.

O validador de frontmatter cobre os formatos gerados e blocos de texto suportados; não é parser YAML universal. `quick_validate.py` do criador requer PyYAML no interpretador usado para validação. Se essa dependência faltar, registrar a limitação ou usar um runtime autorizado que já a forneça; não instalar dependências globalmente para contornar isso.

A inspeção Git aceita somente raiz dedicada com `.git` local e configuração no subconjunto conservador documentado em `util.py`. Includes, filtros, callbacks, worktrees, metadados externos e históricos acima dos limites são recusados; a recusa não significa conteúdo vazio ou auditado. Binários atuais ou históricos exigem revisão explícita pelo digest. Transporte usa destino explícito `https://` ou `ssh://`, sem alias remoto, e SHA aprovado no refspec. A política de bootstrap mantém efeitos externos bloqueados; o laboratório usa transporte falso.
