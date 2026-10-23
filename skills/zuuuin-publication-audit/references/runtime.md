O runtime zuuuin_engine acompanha a distribuição do motor como artefato local separado, construído do pyproject.toml fornecido. Não resolver esse nome em registries públicos. Em laboratório, execute com PYTHONPATH apontando para a pasta runtime da fonte aprovada; na distribuição, use o wheel local aprovado com pip --no-index --no-deps. Nunca referenciar um arquivo do repositório pai como se o instalador da skill o entregasse. Se o runtime não estiver disponível, parar com dependency_missing. Operações retornam JSON e erros explícitos; modos de simulação não efetuam escrita externa. O CLI não consulta contas sozinho.
Requer POSIX (macOS/Linux): o runtime usa flock/fcntl e O_NOFOLLOW. Sua instalação deve ser verificada no cliente-alvo.

Esta revisão do motor requer o runtime local Zuuuin Engine 0.1.1, construído da fonte entregue.

## Licença do conteúdo desta unidade

MIT License

Copyright (c) 2026 enayzuin

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
