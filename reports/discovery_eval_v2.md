# Relatório de Avaliação — Discovery Agent

**Data:** 20260611_185417  
**Cenários testados:** 5  
**Pontuação máxima por cenário:** 100 pts  

## Sumário Executivo

| Cenário | Segmento | Blueprint | Score | Nota |
|---------|----------|-----------|-------|------|
| Loja Virtual de Roupas | ✅ | ✅ | 100/100 (100%) | A — Excelente |
| Restaurante Familiar | ✅ | ✅ | 100/100 (100%) | A — Excelente |
| Clínica Médica | ✅ | ✅ | 100/100 (100%) | A — Excelente |
| Escola de Idiomas | ✅ | ✅ | 100/100 (100%) | A — Excelente |
| Salão de Beleza | ✅ | ✅ | 100/100 (100%) | A — Excelente |

**Média geral:** 100.0% — A — Excelente

---

## Cenário: Loja Virtual de Roupas

- **Descrição:** E-commerce de moda feminina, vende pelo Instagram e site próprio
- **Segmento esperado:** `ecommerce`
- **Segmento detectado:** `ecommerce`
- **Blueprint emitido:** ✅ Sim
- **Score:** 100/100 (100%) — A — Excelente

```
Score  [████████████████████] 100/100
```

### Pontuação por critério

| Critério | Score | Máx | Barra | Observação |
|----------|------:|----:|-------|------------|
| Segmento | 20 | 20 | `██████████` | Correto: `ecommerce` |
| Blueprint gerado | 20 | 20 | `██████████` | Emitido com sucesso |
| Agentes propostos | 15 | 15 | `██████████` | 4 agentes — equipe completa |
| Roadmap | 10 | 10 | `██████████` | 4 etapas — detalhado |
| Mapa de processos | 10 | 10 | `██████████` | 5 processos mapeados |
| Perguntas em aberto | 5 | 5 | `██████████` | 5 perguntas documentadas |
| Integrações detectadas | 10 | 10 | `██████████` | 5 integrações |
| Profundidade da entrevista | 10 | 10 | `██████████` | 7 turnos do usuário |

### ✅ Pontos positivos

- Segmento detectado corretamente: `ecommerce`
- Blueprint gerado e salvo com sucesso
- Time com 4 agentes propostos
- Roadmap com 4 etapas bem definidas
- 5 processos mapeados no blueprint
- 5 perguntas em aberto documentadas (boa prática)
- 5 integrações detectadas corretamente
- Entrevista aprofundada: 7 turnos do empresário

### Transcrição da entrevista

> _Olá! Seja muito bem-vindo(a). 🤝_

> _Meu nome é Orbe e sou especialista em implementação de inteligência artificial para negócios. Já ajudei dezenas de empresas brasileiras a montar times de agentes que trabalham 24 horas por dia — atendendo clientes, criando conteúdo para redes sociais, gerenciando pedidos, automatizando orçamentos e muito mais._

> _Antes de qualquer proposta, quero entender bem a sua realidade. Não existe solução pronta: o plano certo depende do que você faz, de como você opera e de onde você quer chegar._

> _Então me conta: **o que a sua empresa faz** e qual é o maior desafio que você enfrenta hoje no dia a dia?_
> **🧑 Empresário:** Tenho uma loja virtual de roupas femininas. Vendemos pelo Instagram e site próprio.

> **🤖 Consultor:** Opa, tudo bem? Legal saber que você tem uma loja virtual de roupas femininas — e já está vendendo tanto pelo Instagram quanto pelo site próprio. Isso mostra que você já entendeu a importância de estar onde sua cliente está!

> _Antes de sugerir qualquer automação, quero entender melhor como funciona hoje o dia a dia da sua operação. Vamos começar pelo **atendimento**, que costuma ser um dos maiores gargalos em e-commerces:_

> _**Como você responde hoje às mensagens dos clientes?**_
> _Você usa WhatsApp? Direto no Instagram? Ou os dois? E quantas mensagens por dia, mais ou menos, você recebe só com dúvidas sobre produtos, tamanhos, estoque ou entrega?_

> _(Se for mais fácil, pode me contar como foi ontem: quantas pessoas te procuraram e por onde?)_
> **🧑 Empresário:** O maior problema é o atendimento. Recebo mais de 100 mensagens por dia no WhatsApp e não consigo responder todas.

> **🤖 Consultor:** Entendi perfeitamente — mais de 100 mensagens por dia no WhatsApp é inviável de responder sozinha(o), e isso acaba fazendo você perder vendas (além de deixar clientes frustradas).

> _Antes de sugerir um agente de atendimento inteligente, preciso entender **quais são as perguntas que mais se repetem**. Isso vai me ajudar a treinar o agente para resolver o máximo possível sozinho._

> _Das mensagens que você recebe, **quais são os 3 tipos de pergunta que mais aparecem?**_
> _Por exemplo:_
> _- “Tem estoque desse vestido?”_
> _- “Qual o valor com frete para SP?”_
> _- “Qual tamanho uso se calço 38?”_
> _- “Meu pedido já foi enviado?”_

> _Me conta as que mais te consomem tempo!_
> **🧑 Empresário:** Uso WhatsApp Business e uma planilha Excel para controlar os pedidos. Não tenho CRM.

> **🤖 Consultor:** Show! Usar WhatsApp Business já é um ótimo começo, e a planilha no Excel mostra que você tem disciplina para registrar os pedidos — mesmo sem um sistema mais robusto.

> _Agora, voltando às **perguntas repetitivas no atendimento**: como você não consegue responder todas as 100+ mensagens por dia, é provável que muitas sejam sobre coisas que você já responde dezenas de vezes._

> _Pra eu desenhar um agente que realmente alivie seu dia a dia, me ajuda com isso:_

> _**Quais são as 3 perguntas que mais aparecem nas mensagens?**_
> _(Por exemplo: estoque, frete, troca, status do pedido, dúvidas de tamanho etc.)_

> _Se quiser, pode até copiar aqui algumas mensagens reais que recebeu hoje ou ontem — isso ajuda demais!_
> **🧑 Empresário:** Faturamos em torno de R$ 30 mil por mês. Somos 3 pessoas: eu, uma assistente e uma responsável pelo estoque.

> **🤖 Consultor:** Entendi! Com R$ 30 mil/mês e um time de 3 pessoas, cada minuto conta — e perder tempo respondendo mensagens repetidas no WhatsApp realmente atrapalha o crescimento.

> _Como você mencionou que **não consegue responder todas as mensagens**, imagino que muitas clientes acabam desistindo ou comprando em outro lugar. Por isso, quero focar agora exatamente no que mais te consome tempo:_

> _**Quais são as 3 perguntas que mais aparecem no seu WhatsApp?**_
> _(Por exemplo: “tem estoque?”, “quanto fica o frete para...?”, “meu pedido já saiu?”, “qual tamanho uso?”, “aceita parcelamento?” etc.)_

> _Se você me der essas 3 perguntas mais comuns, consigo propor um agente que responda **automaticamente e com qualidade** — liberando você e sua assistente pra focar só nas conversas que realmente viram venda. Pode ser bem direto, sem firula!_
> **🧑 Empresário:** Vendo também na Shopee e no Mercado Livre. Tenho problemas com devoluções que ficam sem resposta.

> **🤖 Consultor:** Ah, agora faz ainda mais sentido! Você não está só no Instagram e site — está também no **Mercado Livre e Shopee**, o que aumenta muito o volume de pedidos… e, consequentemente, de **devoluções e trocas**. E se essas devoluções ficam sem resposta, isso pode afetar sua reputação nos marketplaces (além de deixar a cliente frustrada).

> _Dá pra ver que seu negócio já tem uma operação multicanal sólida — mas o atendimento manual não está dando conta._

> _Voltando à pergunta-chave:_
> _**Quais são as 3 perguntas que mais aparecem no WhatsApp (ou nos marketplaces) sobre devolução, troca ou pós-venda?**_
> _Por exemplo:_
> _- “Como faço para devolver?”_
> _- “Já enviei a devolução, quando recebo o estorno?”_
> _- “Posso trocar o tamanho?”_

> _E, se possível, me confirma também:_
> _**As devoluções dos marketplaces você gerencia separadamente, ou tudo vai parar na mesma planilha do Excel?**_

> _Essas respostas vão me ajudar a desenhar um agente que não só responda automaticamente, mas também **atualize o status da devolução** e evite que fiquem esquecidas._
> **🧑 Empresário:** Meu sonho é conseguir vender enquanto durmo — automação total do atendimento e rastreio de pedidos.

> **🤖 Consultor:** Esse é um sonho **totalmente realizável** — e, na verdade, bem comum entre lojistas que já vendem em múltiplos canais como você. Com a automação certa, dá pra ter um “vendedor virtual” funcionando 24h, respondendo dúvidas, atualizando status de pedidos e até recuperando carrinhos abandonados.

> _Mas pra chegar nisso com segurança, preciso entender **como você rastreia hoje os pedidos depois que são feitos**._

> _Você me contou que usa uma planilha do Excel… então pergunto:_

> _**Quando um pedido é enviado (pelo Correios, transportadora ou motoboy), você atualiza manualmente na planilha? E os clientes perguntam muito “onde está meu pedido?”**_

> _Além disso:_
> _**Você tem um processo definido para avisar a cliente quando o pedido é despachado?** (Por exemplo: manda um print do código de rastreio no WhatsApp?)_

> _Essas respostas vão me ajudar a desenhar um agente que **automatize o rastreio e a comunicação**, reduzindo drasticamente as mensagens repetidas sobre “cadê meu pedido?”._
> **🧑 Empresário:** /fim

> **🤖 Consultor:** Pronto! Acabei de gerar o seu **blueprint personalizado** com um time de **4 agentes inteligentes** pensados especialmente para sua loja de roupas femininas multicanal.

> _### 🎯 O que você vai ganhar:_
> _- **Atendimento 24/7 no WhatsApp** que responde automaticamente às perguntas repetitivas (estoque, frete, tamanhos etc.)_
> _- **Rastreio automático de pedidos** que avisa a cliente quando o pedido é enviado — reduzindo mensagens do tipo “cadê meu pedido?”_
> _- **Gestão proativa de devoluções**, evitando que fiquem esquecidas nos marketplaces_
> _- **Marketing consistente no Instagram**, reforçando seus lançamentos e avaliações_

> _### 🚀 Primeiro passo (semana 1):_
> _Começamos pelo **Agente de Atendimento WhatsApp**, pois é onde está sua maior dor hoje: mais de 100 mensagens por dia que você não consegue responder. Esse agente sozinho já pode recuperar vendas perdidas e liberar horas do seu dia._

> _---_

> _✅ O plano completo está salvo nos arquivos `blueprint.json` e `blueprint.md` na pasta da sessão._

> _Se quiser avançar com a implementação ou tirar dúvidas sobre algum agente, é só chamar! E lembre-se: **vender enquanto você dorme não é sonho — é só uma boa automação bem desenhada.** 💤🛍️_

### Blueprint gerado

<details>
<summary>Expandir blueprint completo</summary>

# Blueprint do Time de Agentes

## Perfil da empresa
- Segmento: ecommerce
- Porte: pequeno
- Modelo de negócio: e-commerce multicanal (site próprio + Instagram + marketplaces)
- Dores: atendimento lento, não consegue responder todas as mensagens no WhatsApp, devoluções sem resposta, abandono de carrinho, dúvidas repetitivas sobre entrega

## Mapa de processos
- **Atendimento ao cliente**: Resposta a dúvidas sobre produtos, estoque, frete, tamanhos e status de pedidos via WhatsApp e marketplaces.
- **Gestão de pedidos**: Registro e acompanhamento de pedidos em planilha Excel, com atualização manual de status.
- **Pós-venda e devoluções**: Processo de trocas e devoluções, especialmente nos marketplaces, frequentemente sem follow-up.
- **Rastreio e comunicação logística**: Informar clientes sobre o status de entrega; atualmente feito de forma manual ou inconsistente.
- **Marketing e vendas multicanal**: Vendas pelo site próprio, Instagram, Mercado Livre e Shopee, sem integração centralizada.

## Integrações detectadas
- messaging — WhatsApp Business (dados em: aplicativo WhatsApp Business)
- spreadsheet — Planilha Excel (dados em: arquivo local ou Google Sheets)
- marketplace — Mercado Livre (dados em: painel do vendedor)
- marketplace — Shopee (dados em: painel do vendedor)

## Time de agentes proposto
### Agente de Atendimento WhatsApp — Atendente WhatsApp
- Objetivo: Responder automaticamente às mensagens mais comuns no WhatsApp 24/7, triando leads e resolvendo dúvidas frequentes.
- Tarefas: Responder perguntas sobre estoque, frete, tamanhos e políticas de troca, Verificar disponibilidade do produto consultando a planilha ou sistema, Encaminhar casos complexos para a equipe humana, Coletar dados de contato para follow-up
- Integrações: WhatsApp Business, Planilha Excel
- Conversa com: Agente de Logística, Agente de Pós-Venda
### Agente de Logística e Rastreio — Agente de Logística
- Objetivo: Automatizar o envio de atualizações de status de pedidos e reduzir mensagens sobre 'cadê meu pedido?'.
- Tarefas: Monitorar status de envio na planilha, Enviar automaticamente mensagem no WhatsApp com código de rastreio, Notificar cliente em caso de atraso ou problema na entrega, Atualizar status do pedido após confirmação de entrega
- Integrações: Planilha Excel, WhatsApp Business, API dos Correios (futuro)
- Conversa com: Agente de Atendimento WhatsApp, Responsável pelo estoque
### Agente de Pós-Venda e Devoluções — Coordenador de Pós-Venda
- Objetivo: Garantir que nenhuma devolução fique sem resposta e recuperar relacionamento com clientes insatisfeitas.
- Tarefas: Monitorar solicitações de devolução nos marketplaces e WhatsApp, Enviar instruções claras de devolução/troca, Acompanhar recebimento da devolução e estorno/reembolso, Pedir feedback após resolução e oferecer cupom de retorno
- Integrações: Mercado Livre, Shopee, Planilha Excel, WhatsApp Business
- Conversa com: Agente de Atendimento WhatsApp, Proprietário
### Agente de Marketing Multicanal — Gerente de Redes Sociais
- Objetivo: Manter presença ativa e consistente no Instagram e apoiar vendas com conteúdo atrativo.
- Tarefas: Criar posts e stories com looks do catálogo, Destacar avaliações positivas e depoimentos, Promover campanhas de recuperação de carrinho, Sincronizar mensagens de lançamento entre canais
- Integrações: Instagram, Site próprio, Planilha de produtos
- Conversa com: Agente de Atendimento WhatsApp

## Roadmap
1. **Implantar Agente de Atendimento WhatsApp** — Maior impacto imediato: resolve o gargalo principal (100+ mensagens/dia) e libera tempo da equipe.
2. **Implantar Agente de Logística e Rastreio** — Reduz drasticamente mensagens repetidas sobre status de entrega e melhora experiência pós-compra.
3. **Implantar Agente de Pós-Venda e Devoluções** — Evita perda de reputação nos marketplaces e transforma experiências negativas em oportunidades de fidelização.
4. **Implantar Agente de Marketing Multicanal** — Aumenta conversão orgânica e reforça consistência da marca em todos os canais.

## Perguntas em aberto
- Quais são as 3 perguntas mais frequentes recebidas no WhatsApp?
- Como é feito hoje o envio de atualizações de rastreio aos clientes?
- As devoluções dos marketplaces são registradas na mesma planilha do Excel?
- Existe catálogo digital estruturado (com fotos, descrições e tamanhos)?
- Há uso de gateway de pagamento com API (como Stripe, Pagarme) que permita integração futura?

</details>

---

## Cenário: Restaurante Familiar

- **Descrição:** Restaurante de comida caseira com salão e delivery pelo iFood
- **Segmento esperado:** `alimentacao`
- **Segmento detectado:** `alimentacao`
- **Blueprint emitido:** ✅ Sim
- **Score:** 100/100 (100%) — A — Excelente

```
Score  [████████████████████] 100/100
```

### Pontuação por critério

| Critério | Score | Máx | Barra | Observação |
|----------|------:|----:|-------|------------|
| Segmento | 20 | 20 | `██████████` | Correto: `alimentacao` |
| Blueprint gerado | 20 | 20 | `██████████` | Emitido com sucesso |
| Agentes propostos | 15 | 15 | `██████████` | 3 agentes — equipe completa |
| Roadmap | 10 | 10 | `██████████` | 3 etapas — detalhado |
| Mapa de processos | 10 | 10 | `██████████` | 3 processos mapeados |
| Perguntas em aberto | 5 | 5 | `██████████` | 5 perguntas documentadas |
| Integrações detectadas | 10 | 10 | `██████████` | 5 integrações |
| Profundidade da entrevista | 10 | 10 | `██████████` | 6 turnos do usuário |

### ✅ Pontos positivos

- Segmento detectado corretamente: `alimentacao`
- Blueprint gerado e salvo com sucesso
- Time com 3 agentes propostos
- Roadmap com 3 etapas bem definidas
- 3 processos mapeados no blueprint
- 5 perguntas em aberto documentadas (boa prática)
- 5 integrações detectadas corretamente
- Entrevista aprofundada: 6 turnos do empresário

### Transcrição da entrevista

> _Olá! Seja muito bem-vindo(a). 🤝_

> _Meu nome é Orbe e sou especialista em implementação de inteligência artificial para negócios. Já ajudei dezenas de empresas brasileiras a montar times de agentes que trabalham 24 horas por dia — atendendo clientes, criando conteúdo para redes sociais, gerenciando pedidos, automatizando orçamentos e muito mais._

> _Antes de qualquer proposta, quero entender bem a sua realidade. Não existe solução pronta: o plano certo depende do que você faz, de como você opera e de onde você quer chegar._

> _Então me conta: **o que a sua empresa faz** e qual é o maior desafio que você enfrenta hoje no dia a dia?_
> **🧑 Empresário:** Tenho um restaurante de comida caseira. Atendo no salão e faço delivery pelo iFood.

> **🤖 Consultor:** Entendi! Você tem um restaurante de comida caseira com atendimento no salão e também faz delivery pelo iFood — ótimo começo.

> _Antes de mergulhar nas soluções, quero entender melhor como você lida com os pedidos **fora do iFood**. Muitos restaurantes recebem pedidos diretos por WhatsApp, Instagram ou até telefone._

> _Você recebe pedidos por outros canais além do iFood? Se sim, quais? E como você organiza esses pedidos hoje (planilha, papel, app)?_
> **🧑 Empresário:** O maior problema é a gestão: pedidos do iFood chegam misturados com os do salão. Muito caos na cozinha.

> **🤖 Consultor:** Esse caos na cozinha é uma dor **muito comum** em restaurantes que operam salão e delivery ao mesmo tempo — e é justamente aí que a IA pode trazer clareza e ordem.

> _Antes de propor soluções, preciso entender melhor como você **recebe e organiza os pedidos hoje**:_

> _- Os pedidos do iFood chegam impressos? No celular? Em um tablet?_
> _- E os pedidos do salão — como são registrados? (comanda, planilha, de cabeça?)_
> _- Você ou sua equipe usam alguma ferramenta (mesmo que simples, como uma planilha do Excel ou Google Sheets) para tentar separar esses fluxos?_

> _Essas respostas vão me ajudar a desenhar um sistema que realmente resolva o caos sem complicar ainda mais o seu dia a dia._
> **🧑 Empresário:** Uso o iFood, WhatsApp para delivery próprio, e o sistema da operadora de cartão. Tudo separado.

> **🤖 Consultor:** Perfeito — agora ficou claro: você tem **três fluxos paralelos** (iFood, WhatsApp e salão) que não conversam entre si, e isso gera o caos na cozinha. Isso é exatamente o tipo de problema que um time de agentes inteligentes resolve com elegância.

> _Vamos focar no **delivery via WhatsApp**, já que é o canal que você controla diretamente (ao contrário do iFood)._

> _Quando alguém pede pelo WhatsApp:_
> _- Você manda o cardápio manualmente?_
> _- O cliente escreve o pedido por texto?_
> _- Depois, como esse pedido chega à cozinha? Você repassa por voz, manda print, ou anota em algum lugar?_

> _Essa resposta vai me ajudar a desenhar um agente que **padronize e automatize** esse fluxo — sem você precisar digitar nada repetido._
> **🧑 Empresário:** Faturamos em torno de R$ 60 mil por mês. Temos 8 funcionários incluindo cozinha e salão.

> **🤖 Consultor:** Ótimo — com R$ 60 mil de faturamento e 8 funcionários, você já tem escala suficiente para **ganhar muito tempo e reduzir erros** com automação inteligente, sem precisar de sistemas caros.

> _Volto à pergunta anterior, porque ela é chave para resolver o caos:_

> _Quando um cliente faz um pedido **pelo WhatsApp**, como funciona hoje?_
> _- Você envia o cardápio manualmente (foto, lista de texto)?_
> _- O cliente responde escrevendo o que quer?_
> _- Depois, como esse pedido chega para a cozinha? Você repassa verbalmente, manda um print, ou anota em papel/planilha?_

> _Essa etapa é crítica: se conseguirmos **automatizar o recebimento, confirmação e encaminhamento do pedido do WhatsApp direto para a cozinha**, já eliminamos uma fonte grande de confusão — e ainda melhoramos a experiência do cliente._
> **🧑 Empresário:** Quero um agente que responda clientes no WhatsApp sobre cardápio, horários e reservas automaticamente.

> **🤖 Consultor:** Excelente! Um **agente de atendimento no WhatsApp** é um ótimo ponto de partida — e vai resolver justamente a sobrecarga de responder repetidamente "qual o cardápio?", "que horas abre?" ou "dá pra reservar?".

> _Para montar esse agente com precisão, preciso de duas informações rápidas:_

> _1. **Cardápio**: você já tem um cardápio digital (foto atualizada, PDF, link do iFood, site)? Ou ele existe só em papel/na memória?_
> _2. **Reservas**: hoje, quando alguém quer reservar mesa, como você faz? Anota em agenda, planilha, Google Calendar?_

> _Com essas respostas, consigo propor um agente que não só responda automaticamente, mas também **registre reservas e envie o cardápio certo** — tudo integrado ao seu fluxo atual._
> **🧑 Empresário:** /fim

> **🤖 Consultor:** Pronto! Com base nas informações que você compartilhou, elaborei um **plano de transformação digital com agentes de IA** especialmente para o seu restaurante de comida caseira.

> _### 📌 O que foi entregue:_
> _- **3 agentes inteligentes** focados em resolver suas maiores dores:_
> _1. **Atendente WhatsApp** – responde automaticamente sobre cardápio, horários e reservas._
> _2. **Coordenador de Pedidos** – unifica iFood, WhatsApp e salão em um único fluxo para a cozinha._
> _3. **Gerente de Redes Sociais** – cria conteúdo para atrair mais pedidos diretos (e reduzir dependência do iFood)._

> _- **Roadmap por etapas**, começando pelo que traz resultado mais rápido com menos esforço._

> _- **Perguntas em aberto** listadas, caso queira refinar depois._

> _O blueprint completo está disponível nos arquivos `blueprint.json` e `blueprint.md` na pasta da sessão._

> _Se quiser avançar com a implementação ou ajustar algo, é só dizer! Boa sorte com o restaurante — comida caseira merece brilhar. 🍲✨_

### Blueprint gerado

<details>
<summary>Expandir blueprint completo</summary>

# Blueprint do Time de Agentes

## Perfil da empresa
- Segmento: alimentacao
- Porte: pequeno (R$60k/mês, 8 funcionários)
- Modelo de negócio: restaurante com salão + delivery
- Dores: gestão caótica de pedidos, mistura de pedidos do iFood com os do salão, confusão na cozinha, canais de pedido desconectados

## Mapa de processos
- **Atendimento no WhatsApp**: Resposta a clientes sobre cardápio, horários e reservas.
- **Gestão de pedidos**: Recebimento e organização de pedidos do iFood, WhatsApp e salão.
- **Operações de cozinha**: Preparo dos pedidos com separação clara entre salão e delivery.

## Integrações detectadas
- delivery_platform — iFood (dados em: —)
- messaging — WhatsApp (dados em: —)
- payment_system — Sistema da operadora de cartão (dados em: —)

## Time de agentes proposto
### Atendente WhatsApp — Atendimento & Vendas
- Objetivo: Responder automaticamente perguntas frequentes sobre cardápio, horários e reservas, melhorando a experiência do cliente e liberando tempo da equipe.
- Tarefas: Enviar cardápio digital atualizado ao cliente, Informar horário de funcionamento, Registrar e confirmar reservas de mesa, Encaminhar dúvidas complexas para humano quando necessário
- Integrações: WhatsApp Business API
- Conversa com: Cliente, Coordenador de Pedidos
### Coordenador de Pedidos — Operações & Logística
- Objetivo: Unificar e organizar todos os pedidos (iFood, WhatsApp e salão) em um único fluxo claro para a cozinha.
- Tarefas: Receber pedidos do WhatsApp e formatá-los, Integrar pedidos do iFood com os demais canais, Gerar comandas padronizadas para a cozinha, Notificar status de preparo quando relevante
- Integrações: iFood, WhatsApp, Impressora de comandas ou sistema interno
- Conversa com: Atendente WhatsApp, Cozinha, Cliente (via WhatsApp)
### Gerente de Redes Sociais — Marketing & Conteúdo
- Objetivo: Criar conteúdo atrativo para promover o restaurante e impulsionar pedidos diretos (fora do iFood).
- Tarefas: Criar posts e stories com pratos do dia, Divulgar promoções e horários de funcionamento, Incentivar pedidos via WhatsApp com link direto, Destacar diferenciais da comida caseira
- Integrações: Instagram, Canva, Link de WhatsApp
- Conversa com: Atendente WhatsApp, Cliente potencial

## Roadmap
1. **Implantar Atendente WhatsApp** — Alto impacto imediato com baixa complexidade: resolve perguntas repetitivas e inicia a automação sem depender de integração profunda.
2. **Implantar Coordenador de Pedidos** — Resolve a dor central do negócio: o caos na cozinha. Centraliza todos os pedidos em um fluxo unificado.
3. **Implantar Gerente de Redes Sociais** — Gera pedidos diretos, reduzindo dependência do iFood e aumentando margem de lucro.

## Perguntas em aberto
- O cardápio já existe em formato digital estruturado (foto, PDF, site)?
- Qual é o processo atual de reservas (agenda, planilha, Google Calendar)?
- Os pedidos do WhatsApp são escritos livremente ou seguem algum padrão?
- Há uso de impressora de comandas ou sistema interno para pedidos do salão?
- Existe presença ativa no Instagram ou outra rede social?

</details>

---

## Cenário: Clínica Médica

- **Descrição:** Clínica com 3 especialistas, atende convênios e particular
- **Segmento esperado:** `saude`
- **Segmento detectado:** `saude`
- **Blueprint emitido:** ✅ Sim
- **Score:** 100/100 (100%) — A — Excelente

```
Score  [████████████████████] 100/100
```

### Pontuação por critério

| Critério | Score | Máx | Barra | Observação |
|----------|------:|----:|-------|------------|
| Segmento | 20 | 20 | `██████████` | Correto: `saude` |
| Blueprint gerado | 20 | 20 | `██████████` | Emitido com sucesso |
| Agentes propostos | 15 | 15 | `██████████` | 3 agentes — equipe completa |
| Roadmap | 10 | 10 | `██████████` | 3 etapas — detalhado |
| Mapa de processos | 10 | 10 | `██████████` | 4 processos mapeados |
| Perguntas em aberto | 5 | 5 | `██████████` | 4 perguntas documentadas |
| Integrações detectadas | 10 | 10 | `██████████` | 7 integrações |
| Profundidade da entrevista | 10 | 10 | `██████████` | 6 turnos do usuário |

### ✅ Pontos positivos

- Segmento detectado corretamente: `saude`
- Blueprint gerado e salvo com sucesso
- Time com 3 agentes propostos
- Roadmap com 3 etapas bem definidas
- 4 processos mapeados no blueprint
- 4 perguntas em aberto documentadas (boa prática)
- 7 integrações detectadas corretamente
- Entrevista aprofundada: 6 turnos do empresário

### Transcrição da entrevista

> _Olá! Seja muito bem-vindo(a). 🤝_

> _Meu nome é Orbe e sou especialista em implementação de inteligência artificial para negócios. Já ajudei dezenas de empresas brasileiras a montar times de agentes que trabalham 24 horas por dia — atendendo clientes, criando conteúdo para redes sociais, gerenciando pedidos, automatizando orçamentos e muito mais._

> _Antes de qualquer proposta, quero entender bem a sua realidade. Não existe solução pronta: o plano certo depende do que você faz, de como você opera e de onde você quer chegar._

> _Então me conta: **o que a sua empresa faz** e qual é o maior desafio que você enfrenta hoje no dia a dia?_
> **🧑 Empresário:** Tenho uma clínica médica com 3 médicos: clínico geral, dermatologista e ortopedista.

> **🤖 Consultor:** Obrigado pela descrição! Clínicas médicas têm desafios bem específicos — e boas oportunidades para automatizar o dia a dia sem perder o toque humano.

> _Antes de tudo, quero entender melhor como funciona o **atendimento aos pacientes hoje**. Por exemplo:_

> _- Vocês recebem muitos contatos por WhatsApp, telefone ou outro canal?_
> _- Quem responde essas mensagens: uma recepcionista, os próprios médicos ou alguém da equipe administrativa?_

> _Essa resposta já vai me ajudar a mapear a primeira grande área: **atendimento e agendamento**._
> **🧑 Empresário:** A recepção gasta o dia inteiro agendando e desmarcando consultas. Pacientes ligam para confirmar, remarcar.

> **🤖 Consultor:** Entendi perfeitamente — e é super comum clínicas médicas ficarem nesse “fogo cruzado” de ligações e mensagens o dia todo. Isso tira o foco da recepção de outras tarefas importantes e ainda gera risco de erros ou esquecimentos.

> _Vamos agora olhar para a **operação interna**:_
> _**Que sistema vocês usam hoje para gerenciar a agenda dos médicos?**_

> _É uma planilha (Excel/Google Sheets), um software específico de clínica (como o iClinic, Agendor, Doctoralia etc.), ou algo mais simples como o próprio calendário do celular?_

> _Essa resposta vai me ajudar a entender se conseguimos conectar um agente inteligente diretamente à sua agenda — pra ele poder mostrar horários disponíveis, bloquear datas, confirmar consultas etc., sem precisar que alguém digite tudo na mão._
> **🧑 Empresário:** Usamos um software de clínica chamado Nuvem, integrado com Google Calendar. Também WhatsApp para confirmações.

> **🤖 Consultor:** Ótimo! O fato de vocês já usarem o **Nuvem + Google Calendar** é uma excelente notícia — isso significa que dá pra conectar um agente inteligente diretamente à agenda e automatizar respostas em tempo real, sem precisar recriar nada.

> _Agora, quero entender melhor o **volume e o tipo de contato que chega no WhatsApp da clínica**:_

> _- Em média, quantas mensagens ou ligações vocês recebem por dia só sobre agendamento (marcar, desmarcar, confirmar)?_
> _- Quais são as **perguntas mais repetidas**? Por exemplo: “tem horário com o ortopedista?”, “quanto custa a consulta?”, “posso remarcar?” etc._

> _Com isso, consigo desenhar um agente que responda 80% dessas mensagens sozinho — liberando sua recepção para cuidar do que realmente precisa de atenção humana._
> **🧑 Empresário:** Atendemos convênios Unimed e Bradesco Saúde, e particular. Faturamos R$ 120 mil por mês.

> **🤖 Consultor:** Entendi! Com esse faturamento e atendimento a convênios, dá pra ver que vocês já têm uma base sólida de pacientes — o que reforça ainda mais a importância de **otimizar o atendimento e reduzir faltas**, já que cada consulta perdida impacta diretamente na receita.

> _Voltando ao WhatsApp (que é o coração do contato com o paciente), preciso de um último detalhe para desenhar bem o agente de atendimento:_

> _**Quais são as 3 perguntas mais repetidas que chegam no WhatsApp da clínica?**_
> _(ex: “tem horário com o dermatologista?”, “vocês aceitam Unimed?”, “quanto custa a consulta particular?”)_

> _Essa resposta vai me permitir montar respostas automáticas precisas e naturais — quase como se fosse a própria recepção respondendo._
> **🧑 Empresário:** Quero automação de agendamento pelo WhatsApp com confirmação automática 24 horas antes da consulta.

> **🤖 Consultor:** Perfeito! Com essa demanda clara — **agendamento pelo WhatsApp + confirmação automática 24h antes** — já dá pra desenhar um agente de alto impacto que resolve a maior dor da sua recepção e reduz bastante as faltas.

> _Antes de fechar o plano, quero explorar uma oportunidade que muitas clínicas perdem: **o pós-consulta**._

> _Vocês fazem algum tipo de **acompanhamento após a consulta**? Por exemplo:_
> _- Enviam receitas ou exames por e-mail/WhatsApp?_
> _- Marcam retorno automaticamente?_
> _- Pedem para o paciente deixar uma avaliação no Google?_

> _Isso é importante porque, com os mesmos dados do agendamento, dá pra ativar um segundo agente que cuida justamente disso — aumentando a satisfação do paciente e gerando mais indicações (sem trabalho extra pra equipe)._
> **🧑 Empresário:** /fim

> **🤖 Consultor:** Pronto! Acabei de gerar o **blueprint completo** para transformar sua clínica com agentes inteligentes.

> _### 🎯 O que foi entregue:_
> _- **3 agentes especializados** (mínimo recomendado) focados exatamente nas suas dores:_
> _1. **Agente de Atendimento Médico** → automatiza agendamento e confirmação pelo WhatsApp_
> _2. **Agente de Pós-Consulta** → cuida do follow-up e pede avaliações_
> _3. **Agente de Operações Clínicas** → garante que tudo esteja sincronizado e gera relatórios_

> _- **Roadmap por etapas**, começando pelo que traz resultado mais rápido: o agente de WhatsApp + agenda._

> _- **Integrações reais**: usa seu Nuvem, Google Calendar e WhatsApp — nada de mudar sistemas._

> _- **Perguntas em aberto** listadas, caso queira evoluir depois para marketing ou reativação de pacientes._

> _Os arquivos `blueprint.json` e `blueprint.md` estão salvos na pasta da sessão — prontos para você compartilhar com sua equipe ou com um desenvolvedor._

> _Se quiser avançar com a implementação ou esclarecer alguma das perguntas pendentes, é só chamar!_

### Blueprint gerado

<details>
<summary>Expandir blueprint completo</summary>

# Blueprint do Time de Agentes

## Perfil da empresa
- Segmento: saude
- Porte: pequeno
- Modelo de negócio: consultórios médicos presenciais com atendimento a convênios e particulares
- Dores: agenda manual, faltas (no-show), sobrecarga da recepção

## Mapa de processos
- **Agendamento de consultas**: Receber solicitações de agendamento via WhatsApp, verificar disponibilidade e reservar horário.
- **Confirmação e lembrete**: Confirmar consulta com o paciente e enviar lembrete automático 24h antes.
- **Remarcação e cancelamento**: Processar pedidos de remarcação ou cancelamento via WhatsApp e atualizar agenda.
- **Pós-consulta**: Enviar receitas, marcar retorno e/ou solicitar avaliação (parcialmente explorado).

## Integrações detectadas
- scheduling — Nuvem + Google Calendar (dados em: agenda sincronizada)
- communication — WhatsApp (dados em: número oficial da clínica)
- insurance — Unimed (dados em: dados de atendimento no Nuvem)
- insurance — Bradesco Saúde (dados em: dados de atendimento no Nuvem)

## Time de agentes proposto
### Agente de Atendimento Médico — Atendente WhatsApp
- Objetivo: Automatizar agendamento, confirmação e remarcação de consultas via WhatsApp, integrado à agenda da clínica.
- Tarefas: Responder automaticamente às mensagens de agendamento no WhatsApp, Consultar disponibilidade em tempo real na agenda do Nuvem/Google Calendar, Reservar horário e enviar confirmação imediata ao paciente, Enviar lembrete automático 24h antes da consulta, Processar pedidos de cancelamento ou remarcação e atualizar agenda
- Integrações: WhatsApp Business API, Nuvem, Google Calendar
- Conversa com: Pacientes, Agente de Pós-Consulta
### Agente de Pós-Consulta — Coordenador de Pós-Venda
- Objetivo: Garantir acompanhamento após a consulta e estimular avaliações positivas.
- Tarefas: Enviar receitas ou laudos por WhatsApp/e-mail após consulta, Solicitar avaliação no Google Meu Negócio, Oferecer agendamento de retorno quando aplicável
- Integrações: WhatsApp, Nuvem, Google Meu Negócio
- Conversa com: Pacientes, Agente de Atendimento Médico
### Agente de Operações Clínicas — Coordenador de Pedidos
- Objetivo: Sincronizar e monitorar todos os agendamentos e status de consultas.
- Tarefas: Monitorar integridade dos dados entre Nuvem e Google Calendar, Gerar relatórios semanais de faltas e remarcações, Alertar equipe sobre inconsistências ou duplicações
- Integrações: Nuvem, Google Calendar, Planilha de controle
- Conversa com: Recepção, Agente de Atendimento Médico

## Roadmap
1. **Implantar Agente de Atendimento Médico (WhatsApp + Agenda)** — Resolve a dor principal (sobrecarga da recepção e faltas) com integração já possível via Nuvem + WhatsApp.
2. **Ativar Agente de Pós-Consulta** — Aproveita os mesmos dados para aumentar satisfação e reputação online com baixo esforço adicional.
3. **Implantar Agente de Operações Clínicas** — Garante qualidade operacional e fornece insights para reduzir ainda mais as faltas.

## Perguntas em aberto
- Como os novos pacientes chegam à clínica? (indicação, Google Meu Negócio, Instagram etc.)
- Existe processo formal de envio de receitas ou exames após consulta?
- A clínica utiliza Google Meu Negócio ou outro canal para avaliações online?
- Há interesse em campanhas de reativação de pacientes inativos?

</details>

---

## Cenário: Escola de Idiomas

- **Descrição:** Escola de inglês e espanhol presencial e online, 120 alunos
- **Segmento esperado:** `educacao`
- **Segmento detectado:** `educacao`
- **Blueprint emitido:** ✅ Sim
- **Score:** 100/100 (100%) — A — Excelente

```
Score  [████████████████████] 100/100
```

### Pontuação por critério

| Critério | Score | Máx | Barra | Observação |
|----------|------:|----:|-------|------------|
| Segmento | 20 | 20 | `██████████` | Correto: `educacao` |
| Blueprint gerado | 20 | 20 | `██████████` | Emitido com sucesso |
| Agentes propostos | 15 | 15 | `██████████` | 3 agentes — equipe completa |
| Roadmap | 10 | 10 | `██████████` | 3 etapas — detalhado |
| Mapa de processos | 10 | 10 | `██████████` | 4 processos mapeados |
| Perguntas em aberto | 5 | 5 | `██████████` | 6 perguntas documentadas |
| Integrações detectadas | 10 | 10 | `██████████` | 4 integrações |
| Profundidade da entrevista | 10 | 10 | `██████████` | 6 turnos do usuário |

### ✅ Pontos positivos

- Segmento detectado corretamente: `educacao`
- Blueprint gerado e salvo com sucesso
- Time com 3 agentes propostos
- Roadmap com 3 etapas bem definidas
- 4 processos mapeados no blueprint
- 6 perguntas em aberto documentadas (boa prática)
- 4 integrações detectadas corretamente
- Entrevista aprofundada: 6 turnos do empresário

### Transcrição da entrevista

> _Olá! Seja muito bem-vindo(a). 🤝_

> _Meu nome é Orbe e sou especialista em implementação de inteligência artificial para negócios. Já ajudei dezenas de empresas brasileiras a montar times de agentes que trabalham 24 horas por dia — atendendo clientes, criando conteúdo para redes sociais, gerenciando pedidos, automatizando orçamentos e muito mais._

> _Antes de qualquer proposta, quero entender bem a sua realidade. Não existe solução pronta: o plano certo depende do que você faz, de como você opera e de onde você quer chegar._

> _Então me conta: **o que a sua empresa faz** e qual é o maior desafio que você enfrenta hoje no dia a dia?_
> **🧑 Empresário:** Tenho uma escola de idiomas. Inglês e espanhol, aulas presenciais e online pelo Zoom.

> **🤖 Consultor:** Obrigado pela descrição! Escolas de idiomas têm um modelo muito interessante — e ao mesmo tempo desafiador, especialmente quando combinam presencial e online. Antes de tudo, quero entender melhor como vocês estão hoje.

> _Vamos começar pelo **atendimento**:_
> _Atualmente, por quais canais os alunos ou pais entram em contato com a escola? (WhatsApp, Instagram, telefone, e-mail?) E quantas mensagens ou ligações vocês recebem por dia, em média?_
> **🧑 Empresário:** Tenho dificuldade em converter leads que chegam pelo Instagram em alunos matriculados. Muitos somem.

> **🤖 Consultor:** Entendi — e isso é **muito comum** em escolas de idiomas. O Instagram traz o lead, mas sem um acompanhamento rápido e estruturado, ele esfria e some.

> _Antes de mergulhar nas soluções, preciso entender melhor como vocês **captam e qualificam esses leads hoje**:_

> _1. Quando alguém manda mensagem no Instagram interessado, **vocês respondem manualmente?**_
> _2. Existe algum **roteiro ou checklist** que vocês seguem para apresentar os cursos, preços, horários etc.?_
> _3. Depois da primeira resposta, **vocês fazem follow-up** (por exemplo, no dia seguinte ou dois dias depois) se a pessoa não responder?_

> _Essas respostas vão me ajudar a ver onde está o gargalo — e como um agente de IA pode fechar essa brecha._
> **🧑 Empresário:** Uso Instagram para captar alunos, WhatsApp para contato, e planilhas Google para controle de matrículas.

> **🤖 Consultor:** Ótimo — agora já tenho um panorama mais claro: você atrai pelo Instagram, converte (ou tenta) pelo WhatsApp e registra tudo em planilhas do Google. É um fluxo comum em escolas pequenas, mas justamente por ser manual, **vaza muita oportunidade**.

> _Vamos olhar para o **processo de matrícula** em si:_

> _- Quando alguém demonstra interesse, **como você apresenta os cursos?** Manda fotos de turmas? Um PDF com valores e horários? Link do site?_
> _- Existe alguma **etapa de agendamento de aula experimental ou teste de nivelamento?**_
> _- E depois que a pessoa se matricula: **como você confirma pagamento, envia link da primeira aula (se for online) e dá as boas-vindas?**_

> _Esses detalhes me ajudam a entender se falta um “empurrãozinho” automatizado nessa jornada — algo que mantenha o lead engajado até fechar._
> **🧑 Empresário:** Tenho 120 alunos ativos e 5 professores. Faturamento de R$ 45 mil por mês.

> **🤖 Consultor:** Com 120 alunos e 5 professores, você já tem uma base sólida — mas provavelmente **gasta tempo demais com tarefas repetitivas** que poderiam ser automatizadas.

> _Vamos focar agora nas **operações internas**:_

> _- Além da planilha de matrículas, você usa **algum sistema para controlar pagamentos, vencimentos ou inadimplência?**_
> _- Quando um aluno falta ou cancela, **como você registra isso?** Isso impacta na reposição de aulas?_
> _- E os **horários das turmas**: são fixos ou flexíveis? Como você organiza a agenda dos professores?_

> _Essas informações vão me ajudar a propor um agente que não só melhore sua conversão, mas também **libere sua equipe do trabalho braçal** com planilhas e lembretes manuais._
> **🧑 Empresário:** Quero um agente que qualifique os leads automaticamente e agende a aula experimental.

> **🤖 Consultor:** Perfeito! Você já identificou exatamente o ponto crítico: **qualificar e agendar a aula experimental** — que é o momento decisivo para transformar um lead em aluno.

> _Agora, só preciso de mais um detalhe sobre seu **marketing atual**:_

> _- Você posta conteúdo no Instagram com que frequência? (ex: todo dia, 3x por semana?)_
> _- Usa **campanhas pagas** (anúncios no Instagram ou Facebook) ou só postagens orgânicas?_
> _- Tem algum **link na bio** (tipo Linktree) com informações sobre os cursos, preços ou como falar com você?_

> _Isso vai me dizer se há oportunidade de **automatizar também a geração de leads qualificados**, não só o atendimento depois._
> **🧑 Empresário:** /fim

> **🤖 Consultor:** Pronto! Acabei de gerar o **blueprint completo** para transformar sua escola de idiomas com um time de agentes inteligentes.

> _### 🎯 O que você vai ganhar:_
> _- **Menos leads perdidos**: Um agente (SDR) vai qualificar automaticamente quem chega pelo Instagram e agendar a aula experimental — com follow-up se não responderem._
> _- **Mais tempo livre**: Um atendente 24/7 no WhatsApp responde dúvidas repetitivas (preços, horários, política de reposição)._
> _- **Matrículas mais rápidas**: Após a aula experimental, outro agente cuida do onboarding: envia boas-vindas, link do Zoom, registra na planilha e até avisa sobre pagamento._

> _### 🚀 Primeiro passo recomendado:_
> _Começar pelo **SDR de pré-vendas**, porque é onde está sua maior dor hoje — e ele usa só o WhatsApp e o Google Calendar, ferramentas que você já domina._

> _---_

> _📌 **O que ficou em aberto** (para refinamento futuro):_
> _- Frequência de posts no Instagram e uso de anúncios pagos_
> _- Estrutura atual de pagamentos e inadimplência_
> _- Disponibilidade dos professores para aulas experimentais_
> _- Possibilidade de integrar gateway de pagamento_

> _Se quiser, posso te ajudar a implementar o primeiro agente passo a passo — é mais simples do que parece! É só dizer._

### Blueprint gerado

<details>
<summary>Expandir blueprint completo</summary>

# Blueprint do Time de Agentes

## Perfil da empresa
- Segmento: educacao
- Porte: pequeno
- Modelo de negócio: aulas presenciais e online de inglês e espanhol
- Dores: dificuldade em converter leads do Instagram, evasão de leads antes da matrícula, processos manuais em planilhas, falta de follow-up estruturado com leads

## Mapa de processos
- **Captação de Leads**: Atração via Instagram (orgânico), sem campanhas pagas confirmadas.
- **Qualificação e Agendamento**: Contato inicial via WhatsApp, sem roteiro ou automação; agendamento manual de aula experimental.
- **Matrícula e Onboarding**: Registro em planilha do Google; confirmação de pagamento e acesso às aulas feitos manualmente.
- **Atendimento ao Aluno**: Suporte reativo via WhatsApp; sem sistema de acompanhamento proativo.

## Integrações detectadas
- social_media — Instagram (dados em: mensagens diretas)
- messaging — WhatsApp (dados em: conversas com leads e alunos)
- spreadsheet — Google Sheets (dados em: planilha de matrículas)

## Time de agentes proposto
### SDR - Pré-Vendas — Qualificação de Leads e Agendamento
- Objetivo: Converter leads do Instagram em aulas experimentais agendadas, com follow-up automatizado.
- Tarefas: Responder automaticamente mensagens do Instagram repassadas para o WhatsApp, Qualificar lead: nível de interesse, idioma desejado, disponibilidade, Apresentar opções de horário com base na agenda dos professores, Agendar aula experimental diretamente no Google Calendar, Enviar lembrete 1h antes da aula via WhatsApp, Fazer follow-up em 24h se lead não responder
- Integrações: WhatsApp Business API, Google Calendar, Google Sheets
- Conversa com: Lead, Coordenador de Pedidos
### Atendente WhatsApp — Atendimento 24/7
- Objetivo: Responder dúvidas frequentes de alunos e pais, liberando tempo da equipe.
- Tarefas: Responder perguntas sobre valores, horários, metodologia, Informar políticas de reposição, cancelamento e pagamento, Encaminhar casos complexos para humano, Atualizar status do aluno na planilha (ex: 'aguardando matrícula')
- Integrações: WhatsApp Business API, Google Sheets
- Conversa com: Aluno, SDR - Pré-Vendas
### Coordenador de Pedidos — Operações e Onboarding
- Objetivo: Automatizar matrícula, pagamento e boas-vindas após aula experimental.
- Tarefas: Registrar matrícula na planilha ao receber confirmação, Gerar boleto ou link de pagamento (via integração futura), Enviar mensagem de boas-vindas com link da primeira aula (Zoom) e materiais, Adicionar aluno ao grupo de turma (se aplicável), Monitorar inadimplência e enviar aviso automático
- Integrações: Google Sheets, WhatsApp Business API
- Conversa com: Aluno, SDR - Pré-Vendas

## Roadmap
1. **Implantar SDR - Pré-Vendas no WhatsApp** — Maior impacto imediato: converte leads que hoje somem. Baixa complexidade: usa ferramentas já existentes (WhatsApp + Google Calendar).
2. **Lançar Atendente WhatsApp para FAQ** — Reduz carga da equipe com perguntas repetitivas e melhora tempo de resposta.
3. **Automatizar onboarding com Coordenador de Pedidos** — Fecha o ciclo: transforma aula experimental em matrícula ativa com mínimo esforço humano.

## Perguntas em aberto
- Com que frequência são postadas atualizações no Instagram?
- Há uso de campanhas pagas (Meta Ads)?
- Existe link na bio com informações ou formulário de contato?
- Como é feito hoje o controle de pagamentos e inadimplência?
- Os horários das turmas são fixos ou flexíveis? Há disponibilidade pré-definida dos professores?
- Há interesse em integrar um sistema de pagamentos (ex: Stripe, PagSeguro) no futuro?

</details>

---

## Cenário: Salão de Beleza

- **Descrição:** Salão com 5 profissionais, problema grave de no-shows
- **Segmento esperado:** `beleza`
- **Segmento detectado:** `beleza`
- **Blueprint emitido:** ✅ Sim
- **Score:** 100/100 (100%) — A — Excelente

```
Score  [████████████████████] 100/100
```

### Pontuação por critério

| Critério | Score | Máx | Barra | Observação |
|----------|------:|----:|-------|------------|
| Segmento | 20 | 20 | `██████████` | Correto: `beleza` |
| Blueprint gerado | 20 | 20 | `██████████` | Emitido com sucesso |
| Agentes propostos | 15 | 15 | `██████████` | 3 agentes — equipe completa |
| Roadmap | 10 | 10 | `██████████` | 3 etapas — detalhado |
| Mapa de processos | 10 | 10 | `██████████` | 4 processos mapeados |
| Perguntas em aberto | 5 | 5 | `██████████` | 4 perguntas documentadas |
| Integrações detectadas | 10 | 10 | `██████████` | 3 integrações |
| Profundidade da entrevista | 10 | 10 | `██████████` | 6 turnos do usuário |

### ✅ Pontos positivos

- Segmento detectado corretamente: `beleza`
- Blueprint gerado e salvo com sucesso
- Time com 3 agentes propostos
- Roadmap com 3 etapas bem definidas
- 4 processos mapeados no blueprint
- 4 perguntas em aberto documentadas (boa prática)
- 3 integrações detectadas corretamente
- Entrevista aprofundada: 6 turnos do empresário

### Transcrição da entrevista

> _Olá! Seja muito bem-vindo(a). 🤝_

> _Meu nome é Orbe e sou especialista em implementação de inteligência artificial para negócios. Já ajudei dezenas de empresas brasileiras a montar times de agentes que trabalham 24 horas por dia — atendendo clientes, criando conteúdo para redes sociais, gerenciando pedidos, automatizando orçamentos e muito mais._

> _Antes de qualquer proposta, quero entender bem a sua realidade. Não existe solução pronta: o plano certo depende do que você faz, de como você opera e de onde você quer chegar._

> _Então me conta: **o que a sua empresa faz** e qual é o maior desafio que você enfrenta hoje no dia a dia?_
> **🧑 Empresário:** Tenho um salão de beleza com 5 profissionais: cabelo, manicure e estética.

> **🤖 Consultor:** Opa, que legal! Um salão com 5 profissionais já é um negócio sólido — e ao mesmo tempo complexo de gerenciar, porque cada um pode ter sua própria agenda, clientes fixos e ritmo.

> _Antes de tudo, quero entender melhor **como vocês recebem e gerenciam os agendamentos hoje**. É tudo pelo WhatsApp? Vocês usam alguma agenda digital (tipo Mindbody, Agendor, Google Agenda) ou ainda é no caderno/planilha?_

> _Essa parte é crítica: em salões, o maior gargalo costuma ser justamente a perda de horários por falta de confirmação, remarcações manuais ou até clientes esquecendo do dia/hora._
> **🧑 Empresário:** O maior problema é no-show. Clientes que marcam e não aparecem. Perdemos várias horas por semana.

> **🤖 Consultor:** Entendi perfeitamente — no-show é um dos maiores vilões de salões, e com 5 profissionais, cada horário perdido impacta diretamente na renda do time.

> _Vamos focar nisso. Me conta: **vocês já tentaram confirmar os agendamentos antes do dia?**_
> _Por exemplo, mandam mensagem no dia anterior tipo “amanhã às 15h com a Ana, certo?” — ou isso ainda é feito manualmente (ou nem é feito)?_

> _E aproveitando: **quantos agendamentos vocês recebem por dia, em média?** Isso me ajuda a dimensionar o volume que precisamos automatizar._
> **🧑 Empresário:** Usamos um app de agendamento chamado Booksy e WhatsApp para confirmações manuais.

> **🤖 Consultor:** Ótimo! O fato de vocês já usarem o **Booksy** é uma excelente notícia — porque ele permite integração com sistemas externos, o que abre a porta para **automatizar os lembretes e confirmações sem precisar mudar de ferramenta**.

> _Agora, só pra eu entender melhor o volume:_
> _**Quantas mensagens por dia vocês recebem no WhatsApp só sobre agendamento?** (ex: “tem horário?”, “quero remarcar”, “vou faltar” etc.)_

> _Isso vai me ajudar a ver se vale a pena criar um **atendente automático 24/7** que já responde essas perguntas e até confirma/remarca direto no Booksy — tudo sem ninguém precisar ficar colado no celular._
> **🧑 Empresário:** Faturamos R$ 25 mil por mês. Sou eu mais 4 profissionais autônomos.

> **🤖 Consultor:** Entendi — com profissionais autônomos, cada um pode ter seu próprio fluxo, e isso realmente dificulta manter uma comunicação uniforme com os clientes (principalmente nas confirmações).

> _Vamos voltar ao ponto mais urgente: **você consegue estimar quantas vezes por semana alguém falta sem avisar?**_
> _Por exemplo: “em média, 8 a 10 faltas por semana” — ou algo assim?_

> _E só pra fechar essa parte: **todas as marcações passam por você, ou os autônomos também marcam diretamente com os clientes no WhatsApp deles?**_

> _Essa resposta vai definir se a automação precisa centralizar tudo num único canal ou se temos que lidar com múltiplos pontos de contato._
> **🧑 Empresário:** Quero confirmação automática 48h e 2h antes pelo WhatsApp, com link para remarcar se necessário.

> **🤖 Consultor:** Perfeito! Você já definiu exatamente o que precisa: **confirmação automática 48h e 2h antes pelo WhatsApp, com link para remarcar**. Isso resolve a raiz do problema de no-show — e ainda dá autonomia ao cliente.

> _Agora, só mais duas perguntas rápidas pra eu fechar o plano completo:_

> _1. **Vocês fazem algum tipo de follow-up depois do atendimento?**_
> _Por exemplo: pedem avaliação no Google, mandam mensagem tipo “como foi seu corte?” ou oferecem cupom para a próxima visita?_

> _2. **Além do agendamento, quais outras perguntas os clientes repetem muito no WhatsApp?**_
> _(ex: “quanto custa tal serviço?”, “vocês abrem aos domingos?”, “onde fica?”)_

> _Essas respostas vão me dizer se dá pra incluir um **agente de pós-venda** e um **atendente 24/7 para FAQ**, aumentando ainda mais o valor da automação — sem aumentar seu trabalho._
> **🧑 Empresário:** /fim

> **🤖 Consultor:** Pronto! Acabei de gerar seu **blueprint personalizado** com um time de 3 agentes inteligentes pensado especialmente para o seu salão:

> _1. **Agente de Confirmação e Lembretes** – vai resolver seu problema de no-show com mensagens automáticas 48h e 2h antes, incluindo link para remarcar._
> _2. **Atendente WhatsApp 24/7** – responde perguntas repetidas (preço, horário, localização) e direciona agendamentos._
> _3. **Agente de Operações** – centraliza tudo, alinha os autônomos e garante que nenhum horário se perca._

> _O plano começa justamente pelo que você pediu: **automação de confirmação via WhatsApp com integração ao Booksy** — o que já deve reduzir drasticamente suas horas ociosas._

> _Deixei algumas perguntas em aberto (como follow-up pós-serviço e conteúdo em redes), porque, se houver interesse futuro, dá pra expandir o time com agentes de marketing e fidelização._

> _Se quiser ajustar algo ou entender como implementar passo a passo, é só chamar! 💇‍♀️✨_

### Blueprint gerado

<details>
<summary>Expandir blueprint completo</summary>

# Blueprint do Time de Agentes

## Perfil da empresa
- Segmento: beleza
- Porte: pequeno (5 profissionais, sendo 4 autônomos)
- Modelo de negócio: serviços presenciais com profissionais autônomos
- Dores: no-show, horários ociosos, confirmação manual de agendamentos, coordenação entre autônomos

## Mapa de processos
- **Agendamento**: Clientes marcam serviços via Booksy ou WhatsApp.
- **Confirmação e lembrete**: Equipe confirma manualmente horários pelo WhatsApp, mas com falhas frequentes.
- **Remarcação**: Clientes precisam remarcar, mas o processo é manual e depende da disponibilidade da equipe.
- **Atendimento inicial**: Clientes entram em contato via WhatsApp para tirar dúvidas, verificar horários e preços.

## Integrações detectadas
- scheduling — Booksy (dados em: agendamentos e cadastro de clientes)
- communication — WhatsApp (dados em: conversas com clientes)

## Time de agentes proposto
### Agente de Confirmação e Lembretes — Coordenador de Agendamentos
- Objetivo: Reduzir no-shows com confirmações automáticas 48h e 2h antes do horário, com opção de remarcar.
- Tarefas: Enviar mensagem automática 48h antes do agendamento confirmando data, horário e profissional, Enviar segundo lembrete 2h antes do horário, Incluir link direto para remarcar no Booksy caso o cliente não possa comparecer, Registrar resposta do cliente (confirmou, cancelou, não respondeu), Notificar equipe internamente sobre cancelamentos
- Integrações: Booksy, WhatsApp Business API
- Conversa com: Cliente, Equipe do salão
### Atendente WhatsApp 24/7 — Atendente de Primeiro Contato
- Objetivo: Responder automaticamente às perguntas mais comuns e liberar tempo da equipe.
- Tarefas: Responder FAQs: horário de funcionamento, localização, preços médios, Mostrar link do Booksy para agendamento, Coletar nome e serviço desejado para repassar à equipe se necessário, Identificar intenção de remarcar e redirecionar ao fluxo correto
- Integrações: WhatsApp Business API
- Conversa com: Cliente
### Agente de Operações — Gestor de Fluxo Interno
- Objetivo: Centralizar e alinhar a comunicação entre os profissionais autônomos e os sistemas.
- Tarefas: Garantir que todos os agendamentos passem pelo Booksy (mesmo que marcados via WhatsApp), Monitorar taxa de no-show por profissional, Gerar relatório semanal de horários ociosos e conversão de leads, Sincronizar dados entre WhatsApp e Booksy
- Integrações: Booksy, Planilha Google ou CRM simples
- Conversa com: Equipe do salão, Agente de Confirmação, Atendente WhatsApp

## Roadmap
1. **Implantar Agente de Confirmação e Lembretes** — Resolve a dor principal (no-show) com alto impacto imediato e complexidade moderada, aproveitando a integração Booksy + WhatsApp.
2. **Lançar Atendente WhatsApp 24/7 para FAQ** — Reduz volume de mensagens repetitivas e melhora a experiência do cliente desde o primeiro contato.
3. **Implementar Agente de Operações para centralização** — Alinha os autônomos e garante consistência nos dados, preparando o salão para escalar.

## Perguntas em aberto
- Vocês fazem follow-up pós-atendimento (NPS, avaliação, cupom de retorno)?
- Quais são as perguntas mais frequentes dos clientes no WhatsApp além de agendamento?
- Os autônomos marcam diretamente com clientes em seus próprios WhatsApps ou tudo passa pelo dono?
- Há interesse em gerar conteúdo para Instagram/TikTok para atrair novos clientes?

</details>

---

## Análise Global e Melhorias Sugeridas

### Recomendações de melhoria

1. **Forçar chamada ao `segment_lookup` na primeira resposta** — o prompt deve instruir o agente a chamar `segment_lookup` imediatamente ao identificar o negócio, antes de prosseguir com perguntas.
2. **Exigir uso de `reflect` após cada resposta** — adicionar ao system prompt: 'VOCÊ DEVE chamar `reflect` após CADA resposta do empresário, sem exceção.'
3. **Aumentar `max_iters`** — sessões com 5+ respostas podem esgotar as iterações antes de emitir o blueprint. Ajustar para `max_iters=10`.
4. **Expandir seed CNAE** — os segmentos 'serviços B2B', 'tecnologia' e 'construção civil' são frequentes mas ainda não têm trilhos curados.
5. **Adicionar exemplos de blueprint no prompt** — o LLM performa melhor quando vê 1-2 exemplos de blueprints bem estruturados no system prompt (few-shot).
6. **Validar integrações no reflect** — o `reflect` deve incluir campo obrigatório `integrations` para garantir captura sistemática.
7. **Teste de regressão automatizado** — integrar este avaliador ao pipeline de CI/CD para detectar regressões de qualidade a cada mudança no prompt.

---

_Relatório gerado por `scripts/eval_discovery.py` em 20260611_185417_
