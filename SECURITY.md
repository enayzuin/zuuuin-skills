# Segurança

Esta política cobre a versão preparada 0.1.1, com autoria pública de **enayzuin** e conteúdo próprio sob [MIT](LICENSE-STATUS.md). O destino escolhido é [enayzuin/zuuuin-skills](https://github.com/enayzuin/zuuuin-skills); publicação e recebimento privado de relatos ainda não foram verificados. Não há prazo de resposta estabelecido, e nenhuma versão é declarada aqui como tendo suporte de segurança continuado.

## Escopo

O recorte contém oito skills engine, seu runtime compartilhado e documentação. Fontes recuperadas e conteúdo dos pacotes são dados: não concedem permissões, não alteram políticas confiáveis e não autorizam instalações ou efeitos externos. O perfil local inicia sem autorizações e com efeitos externos desabilitados.

As instruções e os controles locais reduzem riscos no escopo conferido; não constituem certificação de segurança. Um hash identifica bytes, não prova ausência de conteúdo sensível, direitos, comportamento seguro ou eficácia em produção. O auditor precisa de revisão contextual independente ligada ao pacote exato, além das verificações automatizadas aplicáveis.

## Relatar uma suspeita sem expor dados

O destino preparado é um [aviso privado de segurança no GitHub](https://github.com/enayzuin/zuuuin-skills/security/advisories/new), **somente se o repositório disponibilizar esse recurso para relatos privados**. A habilitação não foi verificada. Se o recurso estiver indisponível ou não deixar claro que o envio é privado, conserve o relato em área privada autorizada até existir um canal seguro confirmado. Não publique detalhes sensíveis em issues, comentários ou pull requests, nem os envie a um endereço ou conta presumidos. Não há e-mail de segurança definido.

Prepare um registro privado mínimo e saneado, usando estes campos:

| Campo | Informação necessária |
| --- | --- |
| Componente e revisão | Skill, revisão pública, versão do runtime e hash do artefato examinado. |
| Ambiente | Sistema, versão de Python e dependências relevantes, sem identificação pessoal da máquina. |
| Condições | Permissões e fronteiras que tornaram a ocorrência possível. |
| Reprodução sintética | Menor entrada fictícia e passos delimitados que mostram o problema. |
| Resultado e impacto | O observado, o esperado, o alcance demonstrado e o que permanece desconhecido. |
| Evidência saneada | Erro ou fragmento indispensável, sem valores secretos ou conteúdo de terceiros. |
| Contenção local | Ações efetivamente realizadas, separadas de sugestões ainda não executadas. |

Preserve a evidência original em área privada autorizada e mantenha-a fora da distribuição. Não inclua tokens, cookies, credenciais, conversas, perfis, configurações completas ou dados pessoais no relato compartilhável. Não use contas, dados ou serviços reais apenas para ampliar uma reprodução.

Se houver suspeita de exposição ou resultado externo desconhecido, interrompa a repetição automática da operação envolvida, preserve a observação e reconcilie o que ocorreu no escopo autorizado. Este documento não autoriza investigação de sistemas de terceiros nem mudanças de acesso.

## Limites da observação

A evidência disponível é local e sintética; não estabelece eficácia em produção, ativação autônoma, compatibilidade com todo consumidor ou garantia contra vulnerabilidades. O ambiente observado está descrito na [instalação](docs/installation.md). Recursos ou dependências não examinados permanecem fora da conclusão.

Uma correção deve ser vinculada a uma revisão e ao pacote exatos, com nova verificação do conjunto afetado. Não há política de divulgação coordenada ou compromisso de prazo de correção confirmado. Mantenha o relato privado até confirmar a disponibilidade e a privacidade do canal de recebimento. Para relatos sem conteúdo sensível, o [modelo de feedback](FEEDBACK.md) também pode orientar a preparação local.
