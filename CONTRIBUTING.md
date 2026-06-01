<!-- omit in toc -->
# Contribuindo para o Taggy green

Antes de mais nada, obrigado por dedicar seu tempo para contribuir! ❤️

Todos os tipos de contribuição são encorajados e valorizados. Consulte o [Sumário](#sumário) para conhecer as diferentes maneiras de ajudar e os detalhes sobre como este projeto as gerencia. Certifique-se de ler a seção relevante antes de fazer sua contribuição. Isso facilitará muito o trabalho de nós, mantenedores, e tornará a experiência mais fluida para todos os envolvidos. A comunidade aguarda ansiosamente por suas contribuições. 🎉

> E se você gosta do projeto, mas não tem tempo para contribuir, tudo bem. Existem outras formas fáceis de apoiar o projeto e demonstrar sua consideração, pelas quais também ficaríamos muito felizes:
> - Dê uma estrela (Star) no projeto
> - Faça um tweet sobre ele
> - Mencione este projeto no readme do seu próprio projeto
> - Cite o projeto em encontros (meetups) locais e conte para seus amigos/colegas

<!-- omit in toc -->
## Sumário

- [Código de Conduta](#código-de-conduta)
- [Eu Tenho uma Pergunta](#eu-tenho-uma-pergunta)
  - [Eu Quero Contribuir](#eu-quero-contribuir)
  - [Reportando Bugs](#reportando-bugs)
  - [Sugerindo Melhorias](#sugerindo-melhorias)
  - [Sua Primeira Contribuição de Código](#sua-primeira-contribuição-de-código)
  - [Melhorando a Documentação](#melhorando-a-documentação)
- [Guias de Estilo](#guias-de-estilo)
  - [Mensagens de Commit](#mensagens-de-commit)
- [Junte-se à Equipe do Projeto](#junte-se-à-equipe-do-projeto)


## Código de Conduta

Este projeto e todos os que nele participam são regidos pelo [Código de Conduta do Taggy green](https://github.com/e1-taggy-green/taggygreen.api/blob/main/CODE_OF_CONDUCT.md). Ao participar, espera-se que você respeite este código. Por favor, denuncie comportamentos inaceitáveis para <>.


## Eu Tenho uma Pergunta

> Se você deseja fazer uma pergunta, presumimos que você já tenha lido a [Documentação]() disponível.

Antes de fazer uma pergunta, o melhor é pesquisar por [Issues](https://github.com/e1-taggy-green/taggygreen.api/issues) existentes que possam ajudá-lo. Caso encontre uma issue adequada e ainda precise de esclarecimentos, você pode deixar sua pergunta nela. Também é recomendável pesquisar na internet por respostas primeiro.

Se, depois disso, você ainda sentir necessidade de fazer uma pergunta e precisar de esclarecimentos, recomendamos o seguinte:

- Abra uma [Issue](https://github.com/e1-taggy-green/taggygreen.api/issues/new).
- Forneça o máximo de contexto possível sobre o problema que está enfrentando.
- Informe as versões do projeto e da plataforma (nodejs, npm, etc.), dependendo do que parecer relevante.

Nós cuidaremos da issue o mais rápido possível.

<!--
Você pode querer criar uma tag de issue separada para perguntas e incluí-la nesta descrição. As pessoas devem então marcar suas issues de acordo.

Dependendo do tamanho do projeto, você pode querer terceirizar as perguntas, por exemplo, para o Stack Overflow ou Gitter. Você pode adicionar canais adicionais de contato e informação:
- IRC
- Slack
- Gitter
- Tag no Stack Overflow
- Blog
- FAQ
- Roadmap
- Lista de E-mail
- Fórum
-->

## Eu Quero Contribuir

> ### Aviso Legal <!-- omit in toc -->
> Ao contribuir com este projeto, você deve concordar que é o autor de 100% do conteúdo, que possui os direitos necessários sobre ele e que o conteúdo que você contribui pode ser fornecido sob a licença do projeto.

### Reportando Bugs

<!-- omit in toc -->
#### Antes de Enviar um Relatório de Bug

Um bom relatório de bug não deve deixar os outros precisando correr atrás de você para obter mais informações. Portanto, pedimos que você investigue cuidadosamente, colete informações e descreva o problema detalhadamente em seu relatório. Por favor, conclua as etapas a seguir com antecedência para nos ajudar a corrigir qualquer bug potencial o mais rápido possível.

- Certifique-se de que está usando la versão mais recente.
- Determine se o seu bug é realmente um bug e não um erro da sua parte, por exemplo, uso de componentes/versões de ambiente incompatíveis (Certifique-se de ter lido a [documentação](). Se estiver procurando por suporte, você pode verificar [esta seção](#eu-tenho-uma-pergunta)).
- Para ver se outros usuários passaram (e potencialmente já resolveram) pelo mesmo problema que você, verifique se já não existe um relatório para o seu bug ou erro no [rastreador de bugs](https://github.com/e1-taggy-green/taggygreen.api/issues?q=label%3Abug).
- Certifique-se também de pesquisar na internet (incluindo o Stack Overflow) para ver se usuários fora da comunidade do GitHub já discutiram o assunto.
- Colete informações sobre o bug:
  - Stack trace (Rastreamento de pilha/Traceback)
  - Sistema Operacional, Plataforma e Versão (Windows, Linux, macOS, x86, ARM)
  - Versão do interpretador, compilador, SDK, ambiente de execução (runtime), gerenciador de pacotes, dependendo do que for relevante.
  - Possivelmente a sua entrada (input) e a saída (output)
  - Você consegue reproduzir o problema de forma confiável? E também consegue reproduzi-lo em versões anteriores?

<!-- omit in toc -->
#### Como Envio um Bom Relatório de Bug?

> Você nunca deve reportar problemas de segurança, vulnerabilidades ou bugs que incluam informações sensíveis no rastreador de issues ou em qualquer outro lugar público. Em vez disso, bugs sensíveis devem ser enviados por e-mail para <>.
<!-- Você pode adicionar uma chave PGP para permitir que as mensagens também sejam enviadas criptografadas. -->

Usamos as issues do GitHub para rastrear bugs e erros. Se você encontrar um problema no projeto:

- Abra uma [Issue](https://github.com/e1-taggy-green/taggygreen.api/issues/new). (Como não podemos ter certeza neste momento se trata-se de um bug ou não, pedimos que ainda não fale em bug e não adicione etiquetas/labels à issue).
- Explique o comportamento esperado e o comportamento real observado.
- Por favor, forneça o máximo de contexto possível e descreva os *passos para reprodução* para que outra pessoa possa segui-los e recriar o problema por conta própria. Isso geralmente inclui o seu código. Para bons relatórios de bug, você deve isolar o problema e criar um caso de teste reduzido.
- Forneça as informações que você coletou na seção anterior.

Assim que for enviada:

- A equipe do projeto categorizará a issue com as etiquetas correspondentes.
- Um membro da equipe tentará reproduzir o problema com os passos fornecidos. Se não houver passos de reprodução ou uma maneira óbvia de reproduzir o problema, a equipe solicitará esses passos e marcará a issue como `needs-repro` (precisa de reprodução). Bugs com a etiqueta `needs-repro` não serão analisados até que sejam reproduzidos.
- Se a equipe conseguir reproduzir o problema, ele será marcado como `needs-fix` (precisa de correção), além de possivelmente outras etiquetas (como `critical`), e a issue ficará disponível para ser [implementada por alguém](#sua primeira-contribuição-de-código).

<!-- Você pode querer criar um modelo (template) de issue para bugs e erros que sirva como guia e defina a estrutura das informações a serem incluídas. Se fizer isso, faça uma referência a ele aqui na descrição. -->


### Sugerindo Melhorias

Esta seção orienta você no envio de uma sugestão de melhoria para o Taggy green, **incluindo funcionalidades totalmente novas e pequenas melhorias em recursos existentes**. Seguir estas diretrizes ajudará os mantenedores e a comunidade a entender a sua sugestão e a encontrar sugestões relacionadas.

<!-- omit in toc -->
#### Antes de Enviar uma Melhoria

- Certifique-se de que está usando a versão mais recente.
- Leia a [documentação]() cuidadosamente e descubra se a funcionalidade já não é atendida, talvez por meio de uma configuração específica.
- Faça uma [pesquisa](https://github.com/e1-taggy-green/taggygreen.api/issues) para ver se a melhoria já não foi sugerida. Se já foi, adicione um comentário na issue existente em vez de abrir uma nova.
- Avalie se a sua ideia se encaixa no escopo e nos objetivos do projeto. Cabe a você apresentar argumentos sólidos para convencer os desenvolvedores do projeto sobre os méritos dessa funcionalidade. Tenha em mente que queremos recursos que sejam úteis para a maioria dos nossos usuários e não apenas para um pequeno grupo. Se o seu objetivo atende apenas a uma minoria, considere criar uma biblioteca de extensão/plugin.

<!-- omit in toc -->
#### Como Envio uma Boa Sugestão de Melhoria?

As sugestões de melhorias são rastreadas como [issues do GitHub](https://github.com/e1-taggy-green/taggygreen.api/issues).

- Use um **título claro e descritivo** para a issue para identificar a sugestão.
- Forneça uma **descrição passo a passo da melhoria sugerida** com o máximo de detalhes possível.
- **Descreva o comportamento atual** e **explique qual comportamento você esperava ver em vez disso** e o porquê. Neste ponto, você também pode informar quais alternativas não funcionaram para você.
- Você pode **incluir capturas de tela ou gravações de tela** que ajudem a demonstrar os passos ou apontar a parte com a qual a sugestão está relacionada. Você pode usar o [LICEcap](https://www.cockos.com/licecap/) para gravar GIFs no macOS e Windows, e o [gravador de tela integrado do GNOME](https://help.gnome.org/users/gnome-help/stable/screen-shot-record.html.en) ou o [SimpleScreenRecorder](https://github.com/MaartenBaert/ssr) no Linux. <!-- isso só deve ser incluído se o projeto tiver uma interface gráfica (GUI) -->
- **Explique por que essa melhoria seria útil** para a maioria dos usuários do Taggy green. Você também pode apontar outros projetos que resolveram isso melhor e que poderiam servir de inspiração.

<!-- Você pode querer criar um modelo (template) de issue para sugestões de melhorias que sirva como guia e defina a estrutura das informações a serem incluídas. Se fizer isso, faça uma referência a ele aqui na descrição. -->

### Sua Primeira Contribuição de Código
<!-- TODO
incluir configuração do ambiente, IDE e instruções típicas de introdução?
-->

### Melhorando a Documentação
<!-- TODO
Atualização, melhoria e correção da documentação
-->

## Guias de Estilo
### Mensagens de Commit
<!-- TODO
-->

## Junte-se à Equipe do Projeto
<!-- TODO -->

<!-- omit in toc -->
## Atribuição
Este guia é baseado no [contributing.md](https://contributing.md/generator)!
