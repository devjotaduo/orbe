# Relatório de Avaliação — Discovery Agent

**Data:** 20260611_194029  
**Cenários testados:** 8  
**Pontuação máxima por cenário:** 100 pts  

## Sumário Executivo

| Cenário | Segmento | Blueprint | Score | Nota |
|---------|----------|-----------|-------|------|
| Loja Virtual de Roupas | ✅ | ✅ | 100/100 (100%) | A — Excelente |
| Restaurante Familiar | ✅ | ✅ | 100/100 (100%) | A — Excelente |
| Clínica Médica | ✅ | ✅ | 100/100 (100%) | A — Excelente |
| Escola de Idiomas | ✅ | ✅ | 100/100 (100%) | A — Excelente |
| Salão de Beleza | ✅ | ✅ | 100/100 (100%) | A — Excelente |
| Software House B2B | ✅ | ✅ | 100/100 (100%) | A — Excelente |
| Construtora de Reformas | ✅ | ✅ | 100/100 (100%) | A — Excelente |
| Escritório de Advocacia | ✅ | ✅ | 100/100 (100%) | A — Excelente |

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
| Mapa de processos | 10 | 10 | `██████████` | 4 processos mapeados |
| Perguntas em aberto | 5 | 5 | `██████████` | 5 perguntas documentadas |
| Integrações detectadas | 10 | 10 | `██████████` | 5 integrações |
| Profundidade da entrevista | 10 | 10 | `██████████` | 7 turnos do usuário |

### ✅ Pontos positivos

- Segmento detectado corretamente: `ecommerce`
- Blueprint gerado e salvo com sucesso
- Time com 4 agentes propostos
- Roadmap com 4 etapas bem definidas
- 4 processos mapeados no blueprint
- 5 perguntas em aberto documentadas (boa prática)
- 5 integrações detectadas corretamente
- Entrevista aprofundada: 7 turnos do empresário

### Transcrição da entrevista

> _Olá! Seja muito bem-vindo(a). 🤝_

> _Meu nome é Orbe e sou especialista em implementação de inteligência artificial para negócios. Já ajudei dezenas de empresas brasileiras a montar times de agentes que trabalham 24 horas por dia — atendendo clientes, criando conteúdo para redes sociais, gerenciando pedidos, automatizando orçamentos e muito mais._

> _Antes de qualquer proposta, quero entender bem a sua realidade. Não existe solução pronta: o plano certo depende do que você faz, de como você opera e de onde você quer chegar._

> _Então me conta: **o que a sua empresa faz** e qual é o maior desafio que você enfrenta hoje no dia a dia?_
> **🧑 Empresário:** Tenho uma loja virtual de roupas femininas. Vendemos pelo Instagram e site próprio.

> **🤖 Consultor:** Ótimo! Loja virtual de roupas femininas com vendas pelo Instagram e site próprio — um modelo bem comum, mas cheio de oportunidades para escalar com IA.

> _Antes de tudo: **vocês usam WhatsApp para atendimento?**_
> _(Se sim: é WhatsApp pessoal ou Business? Quantas mensagens em média por dia?)_
> **🧑 Empresário:** O maior problema é o atendimento. Recebo mais de 100 mensagens por dia no WhatsApp e não consigo responder todas.

> **🤖 Consultor:** Entendi perfeitamente — mais de 100 mensagens por dia no WhatsApp e não dá tempo de responder tudo. Isso faz com que você perca vendas e clientes fiquem frustrados.

> _Agora, para montar um plano completo, preciso entender melhor **como funciona seu marketing e vendas hoje**:_

> _Você cria posts ou reels no Instagram com frequência? Tem campanhas pagas (anúncios no Instagram ou Facebook)? E o site: ele tem um catálogo completo das roupas com fotos, descrições e preços atualizados?_
> **🧑 Empresário:** Uso WhatsApp Business e uma planilha Excel para controlar os pedidos. Não tenho CRM.

> **🤖 Consultor:** Show! WhatsApp Business + planilha Excel — combinação super comum, mas que consome muito tempo e dá brecha para erros.

> _Vamos agora entender melhor **a parte de logística e pós-venda**, que costuma gerar muitas mensagens repetidas no WhatsApp:_

> _1. Como você entrega os pedidos? (Correios, motoboy, transportadora?)_
> _2. Os clientes costumam perguntar sobre o status do pedido ou prazo de entrega?_
> _3. Depois da venda, você faz algum tipo de follow-up? Por exemplo: pede avaliação, envia cupom de desconto para a próxima compra ou tenta reativar quem não compra há um tempo?_

> _Essas respostas vão me ajudar a ver se podemos automatizar também essa parte — e aliviar ainda mais sua caixa de mensagens._
> **🧑 Empresário:** Faturamos em torno de R$ 30 mil por mês. Somos 3 pessoas: eu, uma assistente e uma responsável pelo estoque.

> **🤖 Consultor:** Perfeito — time enxuto, faturamento sólido para o tamanho e operação totalmente manual. Isso reforça que **automatizar o atendimento vai liberar horas valiosas** da sua semana.

> _Voltando à logística e pós-venda (áreas que geram muitas mensagens no WhatsApp):_

> _1. **Como você entrega os pedidos?** (Correios, motoboy, transportadora?)_
> _2. **Clientes perguntam muito sobre “onde está meu pedido?” ou prazo de entrega?**_
> _3. **Depois da venda, você faz follow-up?** Por exemplo:_
> _- Pede avaliação no Google ou Instagram?_
> _- Envia cupom para próxima compra?_
> _- Tenta reativar quem não compra há um tempo?_

> _Essas respostas vão me ajudar a propor agentes que não só respondem, mas **evitam que as mesmas perguntas se repitam todo dia**._
> **🧑 Empresário:** Vendo também na Shopee e no Mercado Livre. Tenho problemas com devoluções que ficam sem resposta.

> **🤖 Consultor:** Excelente — agora o cenário está bem mais completo! Vocês estão em **4 canais de venda** (Instagram, site próprio, Shopee e Mercado Livre), o que multiplica o volume de mensagens e pedidos… e as devoluções sem resposta acabam virando uma bola de neve.

> _Antes de fechar o plano, preciso entender só mais um ponto-chave:_

> _**Quais são as perguntas mais repetidas que você recebe no WhatsApp?**_
> _(Por exemplo: “qual o prazo de entrega?”, “tem estoque desse produto?”, “como faço para trocar/devolver?”, “vocês aceitam X forma de pagamento?”)_

> _Listar 3 ou 4 dessas perguntas vai me permitir configurar um agente que responda **automaticamente e com precisão** — e já encaminhe casos complexos para você._
> **🧑 Empresário:** Meu sonho é conseguir vender enquanto durmo — automação total do atendimento e rastreio de pedidos.

> **🤖 Consultor:** Esse é um sonho totalmente realizável — e **você já está no caminho certo** com vendas em múltiplos canais e um modelo que escala.

> _Para fechar o diagnóstico e montar seu time de agentes, preciso só confirmar:_

> _**Quais são as 3 ou 4 perguntas mais repetidas que você recebe no WhatsApp?**_
> _(Por exemplo: “qual o prazo de entrega?”, “tem estoque desse produto?”, “como faço para trocar/devolver?”, “vocês aceitam X forma de pagamento?”)_

> _Com isso, consigo configurar um agente que responda **automaticamente, 24/7**, e ainda atualize o cliente sobre o status do pedido sem você precisar mexer em nada._
> **🧑 Empresário:** /fim

> **🤖 Consultor:** Pronto! Seu **blueprint de transformação com IA** foi gerado com sucesso. 🎯

> _Ele propõe um time de **4 agentes inteligentes** que vão:_

> _1. **Responder 24/7 no WhatsApp** (aliviando mais de 100 mensagens/dia)_
> _2. **Unificar pedidos** de Instagram, site, Shopee e Mercado Livre_
> _3. **Atualizar clientes automaticamente** sobre o status da entrega_
> _4. **Gerenciar devoluções e fidelizar** com follow-up pós-venda_

> _O plano começa pelo **Atendente WhatsApp**, pois é a dor mais urgente e tem implantação simples — você já pode começar a “vender enquanto dorme” em poucos dias._

> _As **perguntas em aberto** listadas no final são só para refinamento futuro (ex: qual plataforma usa no site, qual transportadora, etc.), mas não impedem de iniciar agora._

> _Se quiser, posso te ajudar a configurar o primeiro agente passo a passo. É só dizer! 😊_

### Blueprint gerado

<details>
<summary>Expandir blueprint completo</summary>

# Blueprint do Time de Agentes

## Perfil da empresa
- Segmento: ecommerce
- Porte: pequeno (3 pessoas, R$ 30k/mês)
- Modelo de negócio: ecommerce multicanal de roupas femininas (Instagram, site próprio, Shopee, Mercado Livre)
- Dores: atendimento lento no WhatsApp (>100 mensagens/dia), mensagens não respondidas, devoluções sem resposta, falta de automação em rastreio de pedidos, operação manual com planilha Excel

## Mapa de processos
- **atendimento**: respostas a clientes via WhatsApp Business sobre produtos, estoque, entrega e devoluções
- **pedidos**: recebimento e controle de pedidos vindos de Instagram, site, Shopee e Mercado Livre, registrados em planilha Excel
- **logistica**: envio e rastreio de pedidos; comunicação de status aos clientes
- **pos_venda**: gestão de devoluções, trocas e follow-up pós-compra

## Integrações detectadas
- whatsapp — WhatsApp Business (dados em: celular do dono)
- planilha — Planilha Excel (dados em: computador/local)
- marketplace — Shopee (dados em: painel da loja)
- marketplace — Mercado Livre (dados em: painel da loja)
- ecommerce — Site próprio (dados em: plataforma de e-commerce (não especificada))

## Time de agentes proposto
### Atendente WhatsApp — SAC 24/7
- Objetivo: responder automaticamente as perguntas mais comuns no WhatsApp e triar casos complexos
- Tarefas: responder FAQ sobre prazo de entrega, formas de pagamento, estoque e devoluções, encaminhar mensagens críticas para a equipe humana, coletar dados do cliente (nome, pedido, dúvida) para integração com operações
- Integrações: WhatsApp Business, planilha de pedidos
- Conversa com: Coordenador de Pedidos, Gestor de Reviews
### Coordenador de Pedidos — operações multicanal
- Objetivo: centralizar e automatizar o fluxo de pedidos de todos os canais
- Tarefas: consolidar pedidos do Instagram, site, Shopee e Mercado Livre, registrar status em planilha ou sistema futuro, notificar cliente sobre confirmação, envio e entrega, acionar logística interna ou parceira
- Integrações: WhatsApp Business, planilha Excel, painéis Shopee e Mercado Livre, site próprio
- Conversa com: Atendente WhatsApp, Agente de Logística
### Agente de Logística — rastreio e comunicação de entrega
- Objetivo: automatizar atualizações de status de entrega e reduzir mensagens repetidas
- Tarefas: monitorar código de rastreio (Correios ou outra transportadora), enviar atualizações automáticas ao cliente via WhatsApp, avisar equipe sobre atrasos ou problemas
- Integrações: API dos Correios ou transportadora, WhatsApp Business, planilha de pedidos
- Conversa com: Coordenador de Pedidos
### Gestor de Reviews — pós-venda e fidelização
- Objetivo: gerenciar devoluções, solicitar avaliações e reativar clientes
- Tarefas: enviar mensagem pós-compra pedindo avaliação, acompanhar solicitações de devolução e garantir resposta em até 24h, oferecer cupom de retorno após 30 dias sem compra
- Integrações: WhatsApp Business, planilha de clientes
- Conversa com: Atendente WhatsApp

## Roadmap
1. **Atendente WhatsApp** — resolve a dor principal (mais de 100 mensagens/dia) com implantação rápida e alto impacto
2. **Coordenador de Pedidos** — unifica a operação multicanal e prepara base para automação completa
3. **Agente de Logística** — elimina perguntas repetidas sobre 'onde está meu pedido?'
4. **Gestor de Reviews** — melhora reputação e recupera vendas perdidas com devoluções mal gerenciadas

## Perguntas em aberto
- Quais são as perguntas mais repetidas recebidas no WhatsApp? (ex: prazo, estoque, devolução)
- Qual plataforma de e-commerce é usada no site próprio? (Shopify, Tray, WooCommerce, etc.)
- Qual transportadora ou método de entrega é usado com mais frequência?
- A planilha Excel está estruturada com colunas claras (cliente, produto, status, código de rastreio)?
- Há interesse em migrar para um CRM simples no médio prazo?

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
| Perguntas em aberto | 5 | 5 | `██████████` | 4 perguntas documentadas |
| Integrações detectadas | 10 | 10 | `██████████` | 3 integrações |
| Profundidade da entrevista | 10 | 10 | `██████████` | 6 turnos do usuário |

### ✅ Pontos positivos

- Segmento detectado corretamente: `alimentacao`
- Blueprint gerado e salvo com sucesso
- Time com 3 agentes propostos
- Roadmap com 3 etapas bem definidas
- 3 processos mapeados no blueprint
- 4 perguntas em aberto documentadas (boa prática)
- 3 integrações detectadas corretamente
- Entrevista aprofundada: 6 turnos do empresário

### Transcrição da entrevista

> _Olá! Seja muito bem-vindo(a). 🤝_

> _Meu nome é Orbe e sou especialista em implementação de inteligência artificial para negócios. Já ajudei dezenas de empresas brasileiras a montar times de agentes que trabalham 24 horas por dia — atendendo clientes, criando conteúdo para redes sociais, gerenciando pedidos, automatizando orçamentos e muito mais._

> _Antes de qualquer proposta, quero entender bem a sua realidade. Não existe solução pronta: o plano certo depende do que você faz, de como você opera e de onde você quer chegar._

> _Então me conta: **o que a sua empresa faz** e qual é o maior desafio que você enfrenta hoje no dia a dia?_
> **🧑 Empresário:** Tenho um restaurante de comida caseira. Atendo no salão e faço delivery pelo iFood.

> **🤖 Consultor:** Legal! Restaurante de comida caseira com salão + delivery pelo iFood — um modelo bem comum, mas cheio de oportunidades para escalar com IA.

> _Antes de tudo, quero entender melhor como funciona o **atendimento hoje**:_

> _- Quando alguém quer saber o cardápio, horário de funcionamento ou fazer uma reserva (se você aceita), por onde costuma entrar em contato?_
> _(WhatsApp? Instagram? Telefone?)_

> _Isso vai me ajudar a ver onde a automação pode aliviar sua equipe logo de cara._
> **🧑 Empresário:** O maior problema é a gestão: pedidos do iFood chegam misturados com os do salão. Muito caos na cozinha.

> **🤖 Consultor:** Entendi perfeitamente — o caos na cozinha por causa dos pedidos misturados é um problema **operacional crítico**, e resolver isso vai trazer alívio imediato pra sua equipe.

> _Vamos focar nisso agora:_

> _**Como você recebe e registra os pedidos que vêm do salão e os que vêm de fora do iFood?**_
> _(Por exemplo: anota em papel, usa planilha no celular, tem algum sistema?)_

> _Isso vai me ajudar a desenhar um fluxo único e organizado para todos os pedidos chegarem à cozinha sem confusão._
> **🧑 Empresário:** Uso o iFood, WhatsApp para delivery próprio, e o sistema da operadora de cartão. Tudo separado.

> **🤖 Consultor:** Perfeito — agora ficou claro: você tem **três fluxos de pedidos totalmente separados** (iFood, WhatsApp e salão), e isso é o que está gerando o caos na cozinha.

> _Antes de propor a solução, preciso entender uma última peça importante:_

> _**Você tem um cardápio digital atualizado (com fotos, descrições e preços) que poderia ser usado tanto no WhatsApp quanto nas redes sociais?**_
> _(Se não tem, costuma usar foto do cardápio físico ou só digita o que tem?)_

> _Isso vai definir se podemos unificar a apresentação do seu menu e facilitar tanto o atendimento quanto as vendas._
> **🧑 Empresário:** Faturamos em torno de R$ 60 mil por mês. Temos 8 funcionários incluindo cozinha e salão.

> **🤖 Consultor:** Ótimo, já tenho um bom retrato do seu negócio: **restaurante de comida caseira, R$60k/mês, 8 funcionários, com salão + delivery via iFood e WhatsApp**, e o grande gargalo é a **falta de integração entre os canais de pedido**, causando confusão na cozinha.

> _Só mais uma pergunta rápida pra fechar o diagnóstico:_

> _**Vocês têm presença no Instagram ou outras redes sociais? Postam com alguma frequência (pratos do dia, promoções, etc.)?**_

> _Isso vai me ajudar a ver se há oportunidade de atrair mais clientes com marketing automatizado — mas se não tiverem, tudo bem, focamos primeiro em organizar a operação._
> **🧑 Empresário:** Quero um agente que responda clientes no WhatsApp sobre cardápio, horários e reservas automaticamente.

> **🤖 Consultor:** Entendi perfeitamente — você quer um **agente no WhatsApp que responda automaticamente sobre cardápio, horários e reservas**. Isso é totalmente viável e vai aliviar muito sua equipe!

> _Antes de fechar o plano completo, preciso só confirmar:_

> _**Quais são as perguntas mais frequentes que você recebe hoje no WhatsApp?**_
> _(Por exemplo: “vocês entregam em X bairro?”, “qual o prato do dia?”, “abrem aos domingos?”, etc.)_

> _Isso me ajuda a treinar o agente com as respostas certas desde o primeiro dia — e também revela se há outras oportunidades escondidas (como gerar pedidos diretos pelo WhatsApp, não só informar)._
> **🧑 Empresário:** /fim

> **🤖 Consultor:** Pronto! Acabei de gerar seu **plano completo de transformação com agentes de IA**, focado em resolver o caos na cozinha e automatizar o atendimento no WhatsApp — exatamente como você pediu.

> _### 📌 Resumo do que foi entregado:_

> _1. **Atendente WhatsApp**_
> _→ Responde 24/7 sobre cardápio, horários, entrega e reservas._
> _→ Primeiro a ser implantado: alívio imediato para sua equipe._

> _2. **Coordenador de Pedidos**_
> _→ Une iFood, WhatsApp e salão num único fluxo organizado para a cozinha._
> _→ Resolve a dor principal: pedidos misturados = caos._

> _3. **Gerente de Redes Sociais**_
> _→ Cria conteúdo (prato do dia, promoções) para atrair mais clientes._
> _→ Entra depois que a operação estiver estável._

> _### ❓ O que ainda precisaria confirmar (listado no blueprint):_
> _- Quais são as perguntas mais frequentes no WhatsApp?_
> _- Você já tem um cardápio digital atualizado?_
> _- O iFood permite integração automatizada?_
> _- Vocês postam no Instagram?_

> _Com essas respostas, o plano pode ser refinado — mas mesmo com o que temos, já dá pra começar com alto impacto e baixa complexidade._

> _Se quiser ajustar algo ou partir para a implementação, é só dizer!_

### Blueprint gerado

<details>
<summary>Expandir blueprint completo</summary>

# Blueprint do Time de Agentes

## Perfil da empresa
- Segmento: alimentacao
- Porte: pequeno (8 funcionários, R$ 60k/mês)
- Modelo de negócio: restaurante de comida caseira com salão e delivery (iFood + WhatsApp)
- Dores: pedidos misturados na cozinha, caos operacional entre delivery e salão, sistemas desconectados (iFood, WhatsApp, terminal de cartão)

## Mapa de processos
- **atendimento**: dúvidas sobre cardápio, horários e reservas via WhatsApp
- **pedidos**: recebimento de pedidos por iFood, WhatsApp e salão em sistemas separados
- **operações**: encaminhamento desorganizado de pedidos para a cozinha

## Integrações detectadas
- marketplace — iFood (dados em: painel do parceiro)
- whatsapp — WhatsApp Business (dados em: celular do dono)
- payment_terminal — Sistema da operadora de cartão (dados em: terminal no salão)

## Time de agentes proposto
### Atendente WhatsApp — SAC 24/7
- Objetivo: responder automaticamente perguntas frequentes sobre cardápio, horários, entrega e reservas
- Tarefas: responder FAQ do restaurante, informar se entrega em determinado bairro, confirmar horário de funcionamento, registrar solicitações de reserva
- Integrações: whatsapp, cardápio digital
- Conversa com: Coordenador de Pedidos
### Coordenador de Pedidos — operações
- Objetivo: unificar todos os pedidos (iFood, WhatsApp e salão) num único fluxo organizado para a cozinha
- Tarefas: consolidar pedidos de todas as fontes, formatar e encaminhar para a cozinha, notificar cliente sobre atrasos ou confirmação
- Integrações: ifood, whatsapp, sistema da operadora
- Conversa com: Atendente WhatsApp
### Gerente de Redes Sociais — marketing de conteúdo
- Objetivo: criar presença digital que gere novos pedidos e reforce o cardápio
- Tarefas: publicar prato do dia no Instagram, criar stories com promoções, compartilhar cardápio digital atualizado
- Integrações: instagram, cardápio digital
- Conversa com: Atendente WhatsApp

## Roadmap
1. **Atendente WhatsApp** — resolve a demanda explícita do empresário e alivia o atendimento imediatamente
2. **Coordenador de Pedidos** — ataca a dor principal: o caos na cozinha causado por pedidos fragmentados
3. **Gerente de Redes Sociais** — amplia o alcance e gera mais pedidos após estabilizar a operação interna

## Perguntas em aberto
- Quais são as perguntas mais frequentes recebidas no WhatsApp?
- Existe um cardápio digital atualizado (com fotos e preços)?
- O painel do iFood permite integração automatizada (API ou webhook)?
- Há presença ativa no Instagram ou outras redes sociais?

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
| Mapa de processos | 10 | 10 | `██████████` | 3 processos mapeados |
| Perguntas em aberto | 5 | 5 | `██████████` | 5 perguntas documentadas |
| Integrações detectadas | 10 | 10 | `██████████` | 7 integrações |
| Profundidade da entrevista | 10 | 10 | `██████████` | 6 turnos do usuário |

### ✅ Pontos positivos

- Segmento detectado corretamente: `saude`
- Blueprint gerado e salvo com sucesso
- Time com 3 agentes propostos
- Roadmap com 3 etapas bem definidas
- 3 processos mapeados no blueprint
- 5 perguntas em aberto documentadas (boa prática)
- 7 integrações detectadas corretamente
- Entrevista aprofundada: 6 turnos do empresário

### Transcrição da entrevista

> _Olá! Seja muito bem-vindo(a). 🤝_

> _Meu nome é Orbe e sou especialista em implementação de inteligência artificial para negócios. Já ajudei dezenas de empresas brasileiras a montar times de agentes que trabalham 24 horas por dia — atendendo clientes, criando conteúdo para redes sociais, gerenciando pedidos, automatizando orçamentos e muito mais._

> _Antes de qualquer proposta, quero entender bem a sua realidade. Não existe solução pronta: o plano certo depende do que você faz, de como você opera e de onde você quer chegar._

> _Então me conta: **o que a sua empresa faz** e qual é o maior desafio que você enfrenta hoje no dia a dia?_
> **🧑 Empresário:** Tenho uma clínica médica com 3 médicos: clínico geral, dermatologista e ortopedista.

> **🤖 Consultor:** Ótimo! Uma clínica com três especialidades já tem um fluxo bem definido — e também dores bem conhecidas nesse segmento, como **faltas de pacientes** e **agendamento manual**, que consomem tempo da equipe e geram perda de receita.

> _Vamos começar pelo essencial: **como vocês fazem o agendamento hoje?**_
> _É por WhatsApp, telefone, algum sistema de agenda online? E quem cuida disso na equipe?_
> **🧑 Empresário:** A recepção gasta o dia inteiro agendando e desmarcando consultas. Pacientes ligam para confirmar, remarcar.

> **🤖 Consultor:** Entendi — a recepção está literalmente “preso ao telefone” o dia todo, entre agendar, desmarcar e confirmar consultas. Isso tira foco de outras tarefas importantes e ainda gera risco de erro humano (como dupla marcação ou esquecer um paciente).

> _Antes de avançar para soluções, preciso entender melhor **como vocês se comunicam com os pacientes hoje**:_

> _- Vocês usam **WhatsApp Business** ou só o WhatsApp pessoal?_
> _- Além do WhatsApp e ligação, usam **e-mail, Instagram ou outro canal** para contato?_
> _- Qual é o **volume médio diário** de mensagens ou ligações só sobre agendamento?_

> _Essas respostas vão me ajudar a desenhar um time de agentes que realmente alivie a rotina da sua equipe._
> **🧑 Empresário:** Usamos um software de clínica chamado Nuvem, integrado com Google Calendar. Também WhatsApp para confirmações.

> **🤖 Consultor:** Ótimo! O fato de vocês já usarem o **Nuvem + Google Calendar** é uma ótima notícia — isso significa que dá pra conectar um agente inteligente à agenda sem precisar mudar seu sistema atual.

> _Agora, para entender melhor o volume de trabalho da recepção e onde a IA pode aliviar mais, me conta:_

> _**Quantas mensagens ou ligações vocês recebem por dia só sobre agendamento, confirmação ou remarcação?**_
> _(Ex: “10 ligações e 20 mensagens no WhatsApp por dia”)_

> _E dessas, **quais são as perguntas mais repetidas?**_
> _(Ex: “Tem vaga para amanhã?”, “Como remarcar?”, “Quanto custa a consulta com o dermatologista?”)_
> **🧑 Empresário:** Atendemos convênios Unimed e Bradesco Saúde, e particular. Faturamos R$ 120 mil por mês.

> **🤖 Consultor:** Com esse faturamento e atendimento a convênios, é claro que **cada consulta confirmada conta** — e cada falta (no-show) impacta diretamente na receita.

> _Voltando ao ponto mais urgente: **o volume de contato diário**. Me ajuda com isso?_

> _- Quantas **mensagens no WhatsApp** e **ligações** vocês recebem por dia só sobre agendamento, confirmação ou remarcação?_
> _- E quais são as **3 perguntas mais repetidas** nesses contatos?_

> _Essa informação é essencial para eu desenhar um **agente de atendimento** que resolva sozinho 80% dessas interações — liberando sua recepção para tarefas mais estratégicas._
> **🧑 Empresário:** Quero automação de agendamento pelo WhatsApp com confirmação automática 24 horas antes da consulta.

> **🤖 Consultor:** Perfeito! Automatizar **agendamento + confirmação 24h antes** é uma das maiores alavancas para clínicas como a sua — reduz faltas, libera a recepção e melhora a experiência do paciente.

> _Agora, só mais um detalhe importante para fechar o ciclo:_

> _**Depois da consulta, vocês fazem algum tipo de follow-up?**_
> _Por exemplo:_
> _- Perguntam se o paciente precisa retornar?_
> _- Enviam lembrete para quem deveria voltar em 30 ou 60 dias?_
> _- Têm alguma forma de reativar pacientes que não marcam há meses?_

> _Isso vai me ajudar a incluir um agente de **pós-venda** que aumente o retorno dos pacientes — algo que impacta diretamente no faturamento mensal._
> **🧑 Empresário:** /fim

> **🤖 Consultor:** Pronto! O blueprint da sua clínica está finalizado e salvo. Ele propõe um **time de 3 agentes inteligentes** focados em:

> _1. **Automatizar agendamento e confirmação pelo WhatsApp** (aliviando imediatamente a recepção),_
> _2. **Garantir operação confiável** com sincronização entre Nuvem, Google Calendar e mensagens,_
> _3. **Aumentar retornos e reativar pacientes** com follow-up pós-consulta._

> _O plano começa pelo agente de maior impacto e menor complexidade — o **Agente de Agendamento WhatsApp** — e evolui para retenção e eficiência operacional._

> _As **perguntas em aberto** (como volume exato de mensagens e integração do Nuvem via API) são pontos que recomendo validar antes da implementação técnica, mas não impedem o início do projeto._

> _Se quiser avançar para a próxima etapa — como protótipo funcional ou cotação — é só avisar!_

### Blueprint gerado

<details>
<summary>Expandir blueprint completo</summary>

# Blueprint do Time de Agentes

## Perfil da empresa
- Segmento: saude
- Porte: pequeno (3 médicos + recepção)
- Modelo de negócio: clínica multiprofissional com atendimento presencial, atendendo convênios (Unimed, Bradesco Saúde) e particular
- Dores: recepção sobrecarregada com agendamento e remarcações, agendamento manual via WhatsApp e ligação, faltas de pacientes (no-show), sem automação de confirmação pré-consulta

## Mapa de processos
- **agendamento**: Recepção gerencia agenda via software Nuvem + Google Calendar, mas recebe ligações e mensagens no WhatsApp para marcar, desmarcar e confirmar consultas.
- **atendimento**: Pacientes entram em contato por WhatsApp e telefone para tirar dúvidas, confirmar horários e remarcar.
- **pós-consulta**: Não há follow-up estruturado; retorno depende da iniciativa do paciente.

## Integrações detectadas
- agenda — Nuvem + Google Calendar (dados em: sistema Nuvem)
- whatsapp — WhatsApp (provavelmente pessoal ou Business) (dados em: celular da recepção)
- convenio — Unimed (dados em: sistema Nuvem ou portal do prestador)
- convenio — Bradesco Saúde (dados em: sistema Nuvem ou portal do prestador)

## Time de agentes proposto
### Agente de Agendamento WhatsApp — Atendimento & Agendamento
- Objetivo: Permitir que pacientes agendem, confirmem e remarquem consultas pelo WhatsApp sem intervenção humana.
- Tarefas: Mostrar agenda disponível em tempo real por especialidade, Registrar agendamentos diretamente no Nuvem/Google Calendar, Enviar lembrete automático 24h antes da consulta, Oferecer opção de remarcar ou cancelar via botão interativo
- Integrações: whatsapp, nuvem, google calendar
- Conversa com: Coordenador de Pós-Venda
### Coordenador de Pós-Venda — Fidelização & Retenção
- Objetivo: Reduzir perda de pacientes e aumentar retornos com follow-up automatizado.
- Tarefas: Enviar mensagem pós-consulta perguntando se precisam retornar, Agendar retorno automático conforme recomendação médica (ex: 30 dias), Reativar pacientes inativos há mais de 6 meses, Solicitar avaliação no Google Meu Negócio
- Integrações: whatsapp, nuvem, google calendar
- Conversa com: Agente de Agendamento WhatsApp
### Analista de Operações Clínicas — Operações & Integração
- Objetivo: Garantir que todos os dados fluam entre sistemas e que a automação funcione sem falhas.
- Tarefas: Monitorar sincronização entre Nuvem, Google Calendar e WhatsApp, Gerar relatório semanal de faltas, agendamentos e retornos, Alertar sobre duplicidade ou conflito de horários, Atualizar disponibilidade por médico automaticamente
- Integrações: nuvem, google calendar, whatsapp
- Conversa com: Agente de Agendamento WhatsApp, Coordenador de Pós-Venda

## Roadmap
1. **Agente de Agendamento WhatsApp** — Resolve a dor principal (recepção sobrecarregada) e reduz faltas com confirmação automática. Integração viável com Nuvem + Google Calendar.
2. **Analista de Operações Clínicas** — Assegura que a automação seja confiável e sustentável, evitando erros na agenda.
3. **Coordenador de Pós-Venda** — Aumenta receita recorrente com retenção e reativação, após operação estável.

## Perguntas em aberto
- Qual é o volume diário aproximado de mensagens e ligações sobre agendamento?
- Quais são as 3 perguntas mais repetidas dos pacientes no WhatsApp?
- A clínica tem presença no Google Meu Negócio? Recebe avaliações?
- Como os novos pacientes chegam hoje? (indicação, busca no Google, redes sociais?)
- O sistema Nuvem permite integração via API ou webhook com ferramentas externas?

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
| Perguntas em aberto | 5 | 5 | `██████████` | 4 perguntas documentadas |
| Integrações detectadas | 10 | 10 | `██████████` | 3 integrações |
| Profundidade da entrevista | 10 | 10 | `██████████` | 6 turnos do usuário |

### ✅ Pontos positivos

- Segmento detectado corretamente: `educacao`
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
> **🧑 Empresário:** Tenho uma escola de idiomas. Inglês e espanhol, aulas presenciais e online pelo Zoom.

> **🤖 Consultor:** Legal! Escola de idiomas com aulas presenciais e online — um modelo híbrido que tem crescido muito. Antes de tudo, quero entender melhor como vocês recebem e conversam com os interessados hoje.

> _**Você usa WhatsApp para atendimento?** Se sim, é só um número geral ou cada professor/turma tem o seu próprio contato? E quantas mensagens em média vocês recebem por dia só de dúvidas sobre cursos, preços ou horários?_
> **🧑 Empresário:** Tenho dificuldade em converter leads que chegam pelo Instagram em alunos matriculados. Muitos somem.

> **🤖 Consultor:** Entendi — você já está gerando interesse com o Instagram, mas os leads não estão se convertendo em matrículas. Isso é super comum em escolas de idiomas, e normalmente acontece por dois motivos principais:

> _1. **Falta de follow-up rápido e estruturado** (o lead perde o interesse se não for contatado logo),_
> _2. **Ausência de um funil claro** (não há sequência de mensagens que mostre valor, responda objeções e incentive a matrícula)._

> _Antes de propor soluções, quero entender melhor como funciona hoje:_

> _**Quando alguém manda mensagem no Instagram interessado em curso, qual é o passo seguinte?**_
> _Você ou alguém da equipe responde na hora? Manda um áudio? Passa o WhatsApp? Marca uma aula experimental? Ou deixa para responder depois?_

> _Essa resposta vai me ajudar a ver onde está o gargalo na conversão._
> **🧑 Empresário:** Uso Instagram para captar alunos, WhatsApp para contato, e planilhas Google para controle de matrículas.

> **🤖 Consultor:** Ótimo — agora já tenho uma visão mais clara: você atrai pelo Instagram, converte (ou tenta) pelo WhatsApp e registra tudo em planilha. Esse é um fluxo muito comum, mas também cheio de pontos de fuga: leads esquecidos, respostas demoradas, falta de acompanhamento pós-contato.

> _Vamos olhar para a **experiência do aluno depois da matrícula**, porque isso impacta diretamente na retenção e no boca a boca:_

> _**Depois que o aluno se matricula, como funciona o suporte?**_
> _Ele recebe boas-vindas? Tem acesso a um grupo de turma? Alguém acompanha se ele está assistindo às aulas (especialmente no online)? E se ele some ou falta muito, alguém entra em contato?_

> _Isso vai me ajudar a entender se há oportunidades também no pós-venda — não só para reduzir evasão, mas para transformar alunos em promotores da escola._
> **🧑 Empresário:** Tenho 120 alunos ativos e 5 professores. Faturamento de R$ 45 mil por mês.

> **🤖 Consultor:** Com 120 alunos e R$ 45 mil/mês, você já tem uma base sólida — o próximo passo natural é **reduzir a evasão e aumentar a conversão**, porque cada aluno retido ou matriculado a mais impacta diretamente no faturamento.

> _Voltando à sua dor principal: leads que somem depois do primeiro contato no Instagram._

> _**Você costuma oferecer uma aula experimental ou um teste gratuito?**_
> _Se sim, como agenda essa aula? E se o lead não responde depois da aula, alguém faz follow-up?_

> _Essa etapa é crítica — muitas escolas perdem até 70% dos leads aqui por falta de um processo automático de engajamento pós-teste._
> **🧑 Empresário:** Quero um agente que qualifique os leads automaticamente e agende a aula experimental.

> **🤖 Consultor:** Perfeito! Um agente de pré-vendas (SDR) é exatamente o que você precisa para **não deixar leads esfriarem**. Ele pode responder no Instagram ou WhatsApp segundos depois do primeiro contato, qualificar o interesse (nível, objetivo, disponibilidade), e já marcar a aula experimental no Zoom — tudo automático.

> _Agora, para desenhar esse agente com precisão, preciso saber:_

> _**Como você agenda hoje as aulas experimentais?**_
> _Usa Google Agenda? Calendly? Ou só combina horário por mensagem e anota na planilha?_

> _Isso vai definir como o agente vai integrar o agendamento — e se ele pode mostrar em tempo real os horários disponíveis com base na agenda dos professores._
> **🧑 Empresário:** /fim

> **🤖 Consultor:** Pronto! Acabei de gerar o seu **blueprint personalizado** com um time de 3 agentes de IA pensado especialmente para sua escola de idiomas:

> _1. **SDR de Idiomas** – vai qualificar leads do Instagram/WhatsApp e agendar automaticamente a aula experimental (sua principal dor)._
> _2. **Coordenador de Matrículas** – cuida do follow-up pós-teste para converter mais alunos._
> _3. **Gerente de Redes Sociais** – cria conteúdo que atrai leads mais qualificados._

> _O plano começa pelo SDR, porque é **rápido de implantar** e tem **impacto direto na receita** — sem precisar de novos anúncios, só aproveitando melhor quem já bate na sua porta._

> _Fiquei com algumas perguntas em aberto (como qual ferramenta você usa para agendar as aulas), mas o blueprint já está funcional com o que temos. Se quiser ajustar algo depois ou tirar dúvidas sobre implementação, é só chamar!_

> _Parabéns por ter chegado até aqui — você já deu o passo mais importante: enxergar que o problema não é “falta de alunos”, mas sim **oportunidade escondida nos leads que você já tem**. 🚀_

### Blueprint gerado

<details>
<summary>Expandir blueprint completo</summary>

# Blueprint do Time de Agentes

## Perfil da empresa
- Segmento: educacao
- Porte: pequeno/médio (5 professores, 120 alunos, R$ 45k/mês)
- Modelo de negócio: escola de idiomas com aulas presenciais e online (Zoom), captação via Instagram
- Dores: baixa conversão de leads do Instagram, evasão de potenciais alunos na fase de qualificação, processo manual de matrícula e acompanhamento, falta de follow-up estruturado pós-contato

## Mapa de processos
- **captação**: leads chegam pelo Instagram, sem funil estruturado
- **qualificação e agendamento**: contato inicial via WhatsApp, agendamento manual da aula experimental
- **matrícula**: registro feito em planilha Google após aula experimental
- **atendimento ao aluno**: suporte informal, sem processo de retenção ou engajamento pós-matrícula

## Integrações detectadas
- social_media — Instagram (dados em: mensagens diretas do perfil da escola)
- whatsapp — WhatsApp Business (dados em: celular da equipe ou dono)
- spreadsheet — Planilha Google (dados em: Google Sheets (link compartilhado))
- video_conference — Zoom (dados em: conta institucional da escola)

## Time de agentes proposto
### SDR de Idiomas — Pré-vendas e qualificação
- Objetivo: converter leads do Instagram/WhatsApp em aulas experimentais agendadas
- Tarefas: responder automaticamente a mensagens no Instagram e WhatsApp, qualificar lead (idioma, nível, objetivo, disponibilidade), mostrar horários disponíveis e agendar aula experimental no Zoom, registrar lead qualificado na planilha de matrículas
- Integrações: instagram, whatsapp, google sheets, zoom
- Conversa com: Gerente de Redes Sociais, Coordenador de Matrículas
### Gerente de Redes Sociais — Marketing de conteúdo e geração de leads
- Objetivo: atrair leads qualificados com conteúdo relevante e campanhas
- Tarefas: criar posts sobre benefícios de aprender inglês/espanhol, publicar depoimentos de alunos, gerenciar stories interativos (quiz, enquetes), otimizar mensagens automáticas do Instagram para encaminhar ao SDR
- Integrações: instagram
- Conversa com: SDR de Idiomas
### Coordenador de Matrículas — Operações e CRM leve
- Objetivo: automatizar o fluxo de matrícula e reduzir evasão pós-teste
- Tarefas: enviar lembrete da aula experimental (1 dia antes), fazer follow-up pós-aula (no mesmo dia e 2 dias depois), oferecer condições especiais para matrícula imediata, atualizar status do lead na planilha (teste realizado, matriculado, perdido)
- Integrações: whatsapp, google sheets
- Conversa com: SDR de Idiomas

## Roadmap
1. **SDR de Idiomas** — resolve a dor principal (leads que somem) com impacto direto na receita; integração simples com WhatsApp e Instagram
2. **Coordenador de Matrículas** — fecha o funil com follow-up pós-teste, aumentando conversão sem mais captação
3. **Gerente de Redes Sociais** — melhora a qualidade dos leads entrantes, reduzindo esforço de qualificação

## Perguntas em aberto
- Qual ferramenta de agendamento é usada hoje (Google Agenda, Calendly, outro)?
- A planilha de matrículas tem colunas padronizadas (nome, contato, idioma, status, data do teste)?
- Há disponibilidade fixa dos professores para aulas experimentais ou é tudo combinado caso a caso?
- Os professores usam e-mail institucional ou apenas WhatsApp para comunicação?

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
| Mapa de processos | 10 | 10 | `██████████` | 5 processos mapeados |
| Perguntas em aberto | 5 | 5 | `██████████` | 4 perguntas documentadas |
| Integrações detectadas | 10 | 10 | `██████████` | 3 integrações |
| Profundidade da entrevista | 10 | 10 | `██████████` | 6 turnos do usuário |

### ✅ Pontos positivos

- Segmento detectado corretamente: `beleza`
- Blueprint gerado e salvo com sucesso
- Time com 3 agentes propostos
- Roadmap com 3 etapas bem definidas
- 5 processos mapeados no blueprint
- 4 perguntas em aberto documentadas (boa prática)
- 3 integrações detectadas corretamente
- Entrevista aprofundada: 6 turnos do empresário

### Transcrição da entrevista

> _Olá! Seja muito bem-vindo(a). 🤝_

> _Meu nome é Orbe e sou especialista em implementação de inteligência artificial para negócios. Já ajudei dezenas de empresas brasileiras a montar times de agentes que trabalham 24 horas por dia — atendendo clientes, criando conteúdo para redes sociais, gerenciando pedidos, automatizando orçamentos e muito mais._

> _Antes de qualquer proposta, quero entender bem a sua realidade. Não existe solução pronta: o plano certo depende do que você faz, de como você opera e de onde você quer chegar._

> _Então me conta: **o que a sua empresa faz** e qual é o maior desafio que você enfrenta hoje no dia a dia?_
> **🧑 Empresário:** Tenho um salão de beleza com 5 profissionais: cabelo, manicure e estética.

> **🤖 Consultor:** Opa, tudo bem? Legal saber que você tem um salão com uma equipe completa — cabelo, manicure e estética já cobrem um leque forte de serviços!

> _Antes de mais nada, quero entender melhor **como vocês recebem os agendamentos hoje**._
> _É tudo por WhatsApp? Usam alguma agenda digital (tipo Mindbody, Agendor, Google Agenda)? Ou ainda é no caderno/papel?_

> _Essa pergunta é crucial porque, em salões de beleza, o maior gargalo costuma estar justamente na gestão de horários: cliente marca, esquece, some… e sobra cadeira vazia no dia. Vamos ver como está aí pra depois propor algo que realmente resolva!_
> **🧑 Empresário:** O maior problema é no-show. Clientes que marcam e não aparecem. Perdemos várias horas por semana.

> **🤖 Consultor:** Entendi perfeitamente — no-show é um dos maiores sangradores de receita em salões, e você já identificou isso com clareza.

> _Agora, me conta: **vocês já fazem algum tipo de confirmação ou lembrete antes do horário marcado?**_
> _Por exemplo: mandam mensagem no dia anterior? Ligam? Ou o cliente agenda e só aparece (ou não) no dia?_

> _Essa resposta vai me ajudar a entender se o problema está na falta de processo… ou se o processo existe, mas não está funcionando direito._
> **🧑 Empresário:** Usamos um app de agendamento chamado Booksy e WhatsApp para confirmações manuais.

> **🤖 Consultor:** Ótimo — já temos um ponto de partida sólido! Usar o Booksy é um ótimo sinal, porque significa que os agendamentos já estão digitalizados. E fazer confirmação manual no WhatsApp mostra que vocês **já tentam** evitar o no-show… mas claramente isso está consumindo tempo da equipe sem resolver direito.

> _Agora quero entender melhor o **restante do negócio**, porque muitas vezes a solução do no-show abre portas pra outras melhorias:_

> _Vocês têm **presença ativa no Instagram**? Postam fotos dos trabalhos, antes/depois, promoções?_
> _E **como fazem para atrair clientes novos** — indicação, redes sociais, Google Meu Negócio?_

> _Essa parte é importante porque, se reduzirmos o no-show, vão sobrar mais horários… e queremos garantir que esses horários sejam preenchidos com **clientes pagantes**, não com cadeiras vazias!_
> **🧑 Empresário:** Faturamos R$ 25 mil por mês. Sou eu mais 4 profissionais autônomos.

> **🤖 Consultor:** Beleza! Com R$ 25 mil/mês e uma equipe enxuta (você + 4 autônomos), faz todo sentido que o tempo seja **super escasso** — ninguém sobra pra ficar mandando mensagem o dia inteiro, né?

> _Voltando à pergunta anterior (agora com mais contexto):_
> _Vocês têm **Instagram ativo**? Postam trabalhos, antes/depois, stories?_
> _E como os **clientes novos chegam hoje** — é tudo por indicação, ou vocês usam Google Meu Negócio, anúncios, posts orgânicos?_

> _Pergunto isso porque, se vamos automatizar os lembretes e reduzir no-show, vai sobrar capacidade ociosa… e queremos garantir que ela seja preenchida com **novos clientes**, não com silêncio._
> **🧑 Empresário:** Quero confirmação automática 48h e 2h antes pelo WhatsApp, com link para remarcar se necessário.

> **🤖 Consultor:** Perfeito! Esse fluxo de **confirmação em duas etapas (48h + 2h antes) com link para remarcar** é exatamente o que salões precisam — e vai resolver grande parte do seu problema de no-show.

> _Agora, só mais uma peça antes de montar o plano completo:_

> _Vocês **já usam alguma forma de pós-venda ou fidelização**?_
> _Por exemplo: pedem avaliação no Google depois do atendimento? Mandam mensagem tipo “como foi seu corte?”? Ou oferecem cupom para a próxima visita?_

> _Isso é importante porque, depois de reduzir o no-show e atrair mais clientes novos, o próximo passo natural é **fazer os bons clientes voltarem** — e isso pode ser totalmente automatizado também._
> **🧑 Empresário:** /fim

> **🤖 Consultor:** Pronto! Acabei de gerar o seu **blueprint personalizado** com um time de 3 agentes inteligentes pensado especialmente para o seu salão:

> _1. **Agente de Confirmação Automática** – vai resolver seu problema de no-show com mensagens automáticas 48h e 2h antes + link direto para remarcar (exatamente como você pediu)._
> _2. **Gerente de Redes Sociais** – atrai novos clientes com conteúdo visual (antes/depois, stories) para preencher os horários que ficarem livres._
> _3. **Agente de Pós-Venda** – faz follow-up após o atendimento, pede avaliações e oferece cupom para retorno, aumentando a fidelização._

> _O plano começa justamente pelo agente que resolve sua dor principal (no-show), depois escala para trazer mais gente e, por fim, garante que os bons clientes voltem._

> _Fiquei com algumas perguntas em aberto (como a origem dos seus clientes novos e se o Booksy permite integração via API), mas o blueprint já está totalmente utilizável com o que temos._

> _Se quiser ajustar algo ou avançar na implementação, é só chamar! 💇‍♀️✨_

### Blueprint gerado

<details>
<summary>Expandir blueprint completo</summary>

# Blueprint do Time de Agentes

## Perfil da empresa
- Segmento: beleza
- Porte: pequeno (5 pessoas, R$ 25k/mês)
- Modelo de negócio: salão com profissionais autônomos
- Dores: no-show frequente, horários ociosos por falta de cliente, confirmação manual ineficaz

## Mapa de processos
- **agendamento**: clientes marcam via Booksy
- **confirmação**: equipe confirma manualmente via WhatsApp, mas com baixa eficácia
- **atendimento**: serviços de cabelo, manicure e estética prestados no salão
- **marketing**: origem de novos clientes não mapeada; presença digital incerta
- **fidelização**: sem processo estruturado de pós-venda ou reativação

## Integrações detectadas
- agenda_online — Booksy (dados em: plataforma Booksy)
- whatsapp — WhatsApp Business (dados em: celular do dono ou recepcionista)

## Time de agentes proposto
### Agente de Confirmação Automática — Atendimento & Operações
- Objetivo: reduzir no-show com lembretes automáticos 48h e 2h antes + link para remarcar
- Tarefas: enviar mensagem automática 48h antes do agendamento, enviar segundo lembrete 2h antes, oferecer link direto para remarcação no Booksy, registrar resposta do cliente (confirmou, cancelou, não respondeu)
- Integrações: Booksy, WhatsApp Business API
- Conversa com: Agente de Pós-Venda
### Gerente de Redes Sociais — Marketing de Conteúdo
- Objetivo: atrair novos clientes com conteúdo visual e promoções
- Tarefas: criar posts de antes/depois dos serviços, publicar stories diários com agenda aberta, responder mensagens no Instagram, promover cupom para primeira visita
- Integrações: Instagram, Canva
- Conversa com: Agente de Confirmação Automática
### Agente de Pós-Venda — Fidelização
- Objetivo: aumentar retorno de clientes com follow-up automatizado
- Tarefas: enviar mensagem 1 dia após o atendimento perguntando sobre a experiência, pedir avaliação no Google ou Instagram, oferecer cupom para próxima visita em 30 dias, reativar clientes inativos após 60 dias
- Integrações: WhatsApp, Google Meu Negócio
- Conversa com: Agente de Confirmação Automática

## Roadmap
1. **Agente de Confirmação Automática** — resolve a dor principal (no-show) com integração direta entre Booksy e WhatsApp; alto impacto, complexidade média
2. **Gerente de Redes Sociais** — preenche os horários livres gerados pela redução de no-show com novos clientes
3. **Agente de Pós-Venda** — aumenta LTV e fideliza clientes após operação estabilizada

## Perguntas em aberto
- O Booksy permite integração via webhook ou API para disparar mensagens automáticas?
- Qual é a origem atual dos novos clientes (indicação, Google, Instagram)?
- O salão tem perfil no Google Meu Negócio? Está atualizado?
- Há interesse em coletar avaliações online consistentemente?

</details>

---

## Cenário: Software House B2B

- **Descrição:** Software house que desenvolve sistemas sob medida para empresas
- **Segmento esperado:** `tecnologia`
- **Segmento detectado:** `tecnologia`
- **Blueprint emitido:** ✅ Sim
- **Score:** 100/100 (100%) — A — Excelente

```
Score  [████████████████████] 100/100
```

### Pontuação por critério

| Critério | Score | Máx | Barra | Observação |
|----------|------:|----:|-------|------------|
| Segmento | 20 | 20 | `██████████` | Correto: `tecnologia` |
| Blueprint gerado | 20 | 20 | `██████████` | Emitido com sucesso |
| Agentes propostos | 15 | 15 | `██████████` | 3 agentes — equipe completa |
| Roadmap | 10 | 10 | `██████████` | 3 etapas — detalhado |
| Mapa de processos | 10 | 10 | `██████████` | 3 processos mapeados |
| Perguntas em aberto | 5 | 5 | `██████████` | 4 perguntas documentadas |
| Integrações detectadas | 10 | 10 | `██████████` | 8 integrações |
| Profundidade da entrevista | 10 | 10 | `██████████` | 6 turnos do usuário |

### ✅ Pontos positivos

- Segmento detectado corretamente: `tecnologia`
- Blueprint gerado e salvo com sucesso
- Time com 3 agentes propostos
- Roadmap com 3 etapas bem definidas
- 3 processos mapeados no blueprint
- 4 perguntas em aberto documentadas (boa prática)
- 8 integrações detectadas corretamente
- Entrevista aprofundada: 6 turnos do empresário

### Transcrição da entrevista

> _Olá! Seja muito bem-vindo(a). 🤝_

> _Meu nome é Orbe e sou especialista em implementação de inteligência artificial para negócios. Já ajudei dezenas de empresas brasileiras a montar times de agentes que trabalham 24 horas por dia — atendendo clientes, criando conteúdo para redes sociais, gerenciando pedidos, automatizando orçamentos e muito mais._

> _Antes de qualquer proposta, quero entender bem a sua realidade. Não existe solução pronta: o plano certo depende do que você faz, de como você opera e de onde você quer chegar._

> _Então me conta: **o que a sua empresa faz** e qual é o maior desafio que você enfrenta hoje no dia a dia?_
> **🧑 Empresário:** Tenho uma software house. Desenvolvemos sistemas sob medida e temos um SaaS de gestão para clínicas.

> **🤖 Consultor:** Entendi! Você tem uma software house com dois braços: um que desenvolve sistemas **sob medida** (projetos customizados) e outro que oferece um **SaaS de gestão específico para clínicas**.

> _Esses dois modelos têm desafios bem diferentes — o primeiro costuma depender muito de prospecção e pré-vendas, enquanto o segundo exige escalar aquisição, onboarding e retenção._

> _Para eu entender melhor por onde começar a transformação com agentes de IA, me conta:_

> _**Qual desses dois negócios é sua prioridade hoje?**_
> _Ou seja, onde você sente mais dor, mais oportunidade ou mais foco da equipe?_
> **🧑 Empresário:** Nosso funil de vendas é todo manual. Leads chegam pelo site e LinkedIn e esfriam antes de receber proposta.

> **🤖 Consultor:** Interessante — você mencionou que os leads chegam pelo **site e LinkedIn**, mas esfriam antes de receber proposta. Isso é super comum em software houses, porque normalmente falta um processo ágil de **triagem + qualificação + follow-up**.

> _Antes de desenhar o time ideal, preciso entender melhor como vocês **captam e classificam esses leads hoje**:_

> _**Vocês têm algum critério para saber se um lead é mais quente (pronto pra comprar) ou frio (só pesquisando)?**_
> _Por exemplo: ele já marcou uma reunião? Preencheu um formulário detalhado? Veio de indicação?_

> _Isso vai me ajudar a ver se dá pra automatizar a **pré-venda** com um agente especializado._
> **🧑 Empresário:** Usamos Pipedrive como CRM, Slack interno, e Jira para os projetos. Suporte é por e-mail e fica sobrecarregado.

> **🤖 Consultor:** Ótimo — agora já temos um retrato mais completo!

> _Vocês têm:_
> _- **Dois modelos de negócio**: projetos customizados + SaaS para clínicas_
> _- **Ferramentas definidas**: Pipedrive (CRM), Slack (comunicação), Jira (projetos)_
> _- **Duas dores claras**:_
> _1. **Vendas**: leads entram, mas esfriam no funil manual_
> _2. **Suporte**: sobrecarregado por e-mail, sem escalabilidade_

> _Antes de fechar o plano, preciso entender uma última peça importante:_

> _**O suporte atende os dois tipos de cliente (projetos customizados e SaaS) ou só um deles?**_
> _E, nesse suporte, quais são as **perguntas ou problemas mais repetitivos** que vocês recebem?_

> _Isso vai me dizer se dá pra resolver boa parte da sobrecarga com um **agente de atendimento automatizado** — algo que libera muito tempo da equipe técnica._
> **🧑 Empresário:** Somos 12 pessoas: 8 devs, 2 comerciais, 1 designer e eu. Faturamos R$ 180 mil por mês.

> **🤖 Consultor:** Com 12 pessoas e R$ 180k/mês de faturamento, vocês já estão num patamar sólido — mas com **apenas 2 comerciais**, faz todo sentido que o funil esteja engasgado. E com **8 devs**, qualquer tempo perdido respondendo e-mail de suporte é um custo alto demais.

> _Só preciso confirmar mais uma coisa para fechar o diagnóstico:_

> _**Vocês têm landing pages ou materiais específicos (catálogo, demo, vídeo) para cada um dos dois negócios?**_
> _Ou seja:_
> _- Um visitante do site consegue entender claramente a diferença entre contratar um **projeto customizado** e assinar o **SaaS para clínicas**?_
> _- Existe alguma forma automatizada de **mostrar o produto** (ex: demo interativa, vídeo explicativo, trial) antes mesmo da reunião?_

> _Essa resposta vai me dizer se precisamos incluir um agente focado em **pré-venda/marketing** para nutrir leads enquanto os comerciais focam em fechar._
> **🧑 Empresário:** Quero automatizar a qualificação de leads e o primeiro atendimento do suporte do SaaS.

> **🤖 Consultor:** Perfeito! Com esse foco, já dá pra montar um **time de agentes de IA com alto impacto e baixa complexidade**.

> _Só preciso de uma última confirmação rápida:_

> _**O suporte do SaaS hoje responde perguntas como “como cadastrar um paciente?”, “como emitir relatório X?”, “esqueci minha senha?” — ou seja, dúvidas operacionais dentro do sistema?**_

> _Se sim, conseguimos automatizar **80%+ desse primeiro atendimento** com um agente treinado no manual do seu SaaS. Isso tira pressão imediata da sua equipe técnica._

> _Me confirma isso, por favor?_
> **🧑 Empresário:** /fim

> **🤖 Consultor:** Pronto! O blueprint foi gerado com base em tudo o que conversamos.

> _**Resumo do plano:**_
> _1. **SDR (Pré-vendas)** – vai qualificar leads do site e LinkedIn automaticamente e alimentar seu funil no Pipedrive, evitando que esfriem._
> _2. **Atendente SaaS** – responde as dúvidas repetitivas dos clientes do seu sistema de clínicas por e-mail (ou WhatsApp, se quiser migrar depois), liberando seus devs._
> _3. **Gerente de Redes Sociais** – cria conteúdo técnico que atrai leads qualificados, mostrando cases reais e funcionalidades do seu SaaS e projetos._

> _O roadmap começa pelo **SDR**, porque é a maior dor e tem implantação mais simples com o Pipedrive já em uso._

> _As **perguntas em aberto** (como as FAQs do suporte e a estrutura do Pipedrive) são só para ajustes finos — nada que impeça você de começar._

> _Se quiser, posso te ajudar a detalhar o briefing de um desses agentes ou simular como ele responderia um lead real. É só dizer!_

### Blueprint gerado

<details>
<summary>Expandir blueprint completo</summary>

# Blueprint do Time de Agentes

## Perfil da empresa
- Segmento: tecnologia
- Porte: pequeno (12 funcionários, R$ 180k/mês)
- Modelo de negócio: software house com projetos customizados + SaaS vertical para clínicas
- Dores: funil de vendas manual, leads esfriando, suporte sobrecarregado

## Mapa de processos
- **qualificacao_leads**: Leads entram por site e LinkedIn, mas não são rapidamente qualificados nem recebem follow-up estruturado.
- **suporte_saas**: Primeiro atendimento do SaaS feito por e-mail, com perguntas repetitivas sobre uso do sistema.
- **vendas_comercial**: Apenas 2 comerciais para atender dois modelos de negócio distintos.

## Integrações detectadas
- crm — Pipedrive (dados em: contas e leads no Pipedrive)
- email — Suporte por e-mail (SaaS) (dados em: caixa de entrada de suporte)
- website — Site institucional (dados em: formulários de contato)
- linkedin — LinkedIn (prospecção e inbound) (dados em: mensagens e conexões)
- saas_product — SaaS de gestão para clínicas (dados em: próprio sistema)

## Time de agentes proposto
### SDR (Pré-vendas) — Qualificação de leads
- Objetivo: Capturar, classificar e nutrir leads do site e LinkedIn antes que esfriem, preparando-os para os comerciais.
- Tarefas: receber lead do site/LinkedIn, enviar mensagem inicial personalizada, fazer perguntas de qualificação (orçamento, prazo, necessidade), agendar reunião ou mover para nurture, atualizar status no Pipedrive
- Integrações: pipdrive, site, linkedin
- Conversa com: Closer
### Atendente SaaS — Suporte 24/7 ao cliente do SaaS
- Objetivo: Responder dúvidas operacionais do dia a dia no sistema, reduzindo tickets manuais.
- Tarefas: responder FAQ do SaaS (cadastro, relatórios, acesso), guiar passo a passo dentro do sistema, escalar para humano apenas quando necessário, registrar interação no CRM
- Integrações: email, saas_product, pipdrive
- Conversa com: Coordenador de Pós-Venda
### Gerente de Redes Sociais — Marketing de conteúdo técnico
- Objetivo: Criar presença digital que gera autoridade e leads qualificados para ambos os modelos.
- Tarefas: criar posts sobre cases de clínicas no SaaS, mostrar diferenciais de projetos customizados, produzir vídeos curtos de funcionalidades, responder comentários com link para demo
- Integrações: instagram, linkedin, site
- Conversa com: SDR (Pré-vendas)

## Roadmap
1. **SDR (Pré-vendas)** — Resolve a dor principal: leads esfriando. Integração com Pipedrive é simples e impacto imediato na conversão.
2. **Atendente SaaS** — Alivia pressão dos devs no suporte e melhora experiência do cliente do SaaS.
3. **Gerente de Redes Sociais** — Gera fluxo contínuo de leads qualificados, sustentando o funil a longo prazo.

## Perguntas em aberto
- Quais são as perguntas mais frequentes no suporte do SaaS?
- O SaaS tem documentação interna ou base de conhecimento que possa ser usada para treinar o agente?
- Existe landing page ou demo automatizada para o SaaS?
- Os leads de projetos customizados e SaaS são tratados no mesmo pipeline do Pipedrive?

</details>

---

## Cenário: Construtora de Reformas

- **Descrição:** Construtora focada em reformas residenciais e comerciais
- **Segmento esperado:** `construcao`
- **Segmento detectado:** `construcao`
- **Blueprint emitido:** ✅ Sim
- **Score:** 100/100 (100%) — A — Excelente

```
Score  [████████████████████] 100/100
```

### Pontuação por critério

| Critério | Score | Máx | Barra | Observação |
|----------|------:|----:|-------|------------|
| Segmento | 20 | 20 | `██████████` | Correto: `construcao` |
| Blueprint gerado | 20 | 20 | `██████████` | Emitido com sucesso |
| Agentes propostos | 15 | 15 | `██████████` | 3 agentes — equipe completa |
| Roadmap | 10 | 10 | `██████████` | 3 etapas — detalhado |
| Mapa de processos | 10 | 10 | `██████████` | 4 processos mapeados |
| Perguntas em aberto | 5 | 5 | `██████████` | 3 perguntas documentadas |
| Integrações detectadas | 10 | 10 | `██████████` | 3 integrações |
| Profundidade da entrevista | 10 | 10 | `██████████` | 7 turnos do usuário |

### ✅ Pontos positivos

- Segmento detectado corretamente: `construcao`
- Blueprint gerado e salvo com sucesso
- Time com 3 agentes propostos
- Roadmap com 3 etapas bem definidas
- 4 processos mapeados no blueprint
- 3 perguntas em aberto documentadas (boa prática)
- 3 integrações detectadas corretamente
- Entrevista aprofundada: 7 turnos do empresário

### Transcrição da entrevista

> _Olá! Seja muito bem-vindo(a). 🤝_

> _Meu nome é Orbe e sou especialista em implementação de inteligência artificial para negócios. Já ajudei dezenas de empresas brasileiras a montar times de agentes que trabalham 24 horas por dia — atendendo clientes, criando conteúdo para redes sociais, gerenciando pedidos, automatizando orçamentos e muito mais._

> _Antes de qualquer proposta, quero entender bem a sua realidade. Não existe solução pronta: o plano certo depende do que você faz, de como você opera e de onde você quer chegar._

> _Então me conta: **o que a sua empresa faz** e qual é o maior desafio que você enfrenta hoje no dia a dia?_
> **🧑 Empresário:** Tenho uma construtora especializada em reformas residenciais e comerciais. Também fazemos obras pequenas.

> **🤖 Consultor:** Obrigado pela descrição! Reformas residenciais e comerciais são um negócio com muitos detalhes — e justamente por isso há **muito ganho de eficiência** ao organizar os processos com agentes inteligentes.

> _Antes de tudo, quero entender melhor uma coisa essencial:_

> _**Como vocês recebem e respondem os primeiros contatos dos clientes hoje?**_
> _(ex: WhatsApp, Instagram, ligações, site?)_

> _E, nesse primeiro atendimento, quais são as **3 perguntas mais repetidas** que os clientes fazem? (ex: “quanto custa reformar um banheiro?”, “vocês atendem na minha região?”, etc.)_
> **🧑 Empresário:** Orçamento é nossa maior dor. Cliente pede orçamento e a gente leva uma semana para responder. Muitos desistem.

> **🤖 Consultor:** Entendi perfeitamente — **perder cliente porque o orçamento demora uma semana** é uma dor real e evitável. Na construção civil, velocidade na resposta é quase tão importante quanto preço.

> _Vamos focar nisso. Para resolver essa lentidão, preciso entender melhor:_

> _**Como funciona hoje o processo de um orçamento?**_
> _Por exemplo:_
> _- O cliente manda mensagem → alguém agenda visita?_
> _- Vocês vão ao local antes de dar qualquer valor?_
> _- Ou já conseguem passar um “orçamento estimado” por foto/mensagem?_

> _Me conte o passo a passo que vocês seguem hoje — mesmo que seja informal._
> **🧑 Empresário:** Usamos WhatsApp para tudo, planilha Excel para custos e Google Agenda para as visitas técnicas.

> **🤖 Consultor:** Ótimo — agora já vejo claramente o cenário: **WhatsApp + planilha + Google Agenda** é uma base sólida, mas totalmente manual. E é justamente essa dependência de visita presencial *antes* de qualquer estimativa que faz você perder leads.

> _Aqui vai uma pergunta-chave para desbloquear velocidade:_

> _**Vocês já conseguem dar um “orçamento inicial” (mesmo que aproximado) com base em fotos e medidas que o cliente envia por WhatsApp?**_
> _Ou **só avançam depois da visita presencial**?_

> _Por exemplo: se alguém manda “quero reformar meu banheiro de 3m²”, vocês têm um valor médio por m² ou por tipo de reforma que poderia ser enviado em minutos — mesmo que sujeito a ajustes na visita?_

> _Isso define se podemos criar um agente que responde **em minutos, não em dias**._
> **🧑 Empresário:** Somos 15 pessoas entre engenheiros, mestres de obra e equipe. Faturamos uns R$ 250 mil por mês.

> **🤖 Consultor:** Com 15 pessoas e R$ 250k/mês, vocês já têm escala para **automatizar sem perder o toque humano** — e justamente por isso não dá mais pra depender só de WhatsApp e planilha.

> _Voltando à pergunta essencial (porque ela define o primeiro agente que vai salvar seus leads):_

> _👉 **Vocês conseguem dar um orçamento *inicial* com base em fotos e medidas enviadas pelo cliente?**_
> _Ou **só respondem após visita presencial**?_

> _Se for possível dar um valor estimado (ex: “reforma de banheiro médio: R$ 8.000 a R$ 12.000, sujeito a ajustes na visita”), podemos criar um **Agente de Pré-Vendas** que responde isso **em minutos**, direto no WhatsApp — e já agenda a visita para quem quiser seguir._

> _Mas se a resposta for “só damos valor depois da visita”, aí o foco muda: vamos automatizar o **agendamento imediato da visita** + envio automático de portfólio, para manter o lead aquecido._

> _Então me ajuda com essa definição?_
> **🧑 Empresário:** Os clientes reclamam que não sabem como está a obra. Ligam toda semana pedindo atualização.

> **🤖 Consultor:** Essa reclamação é **ouro** — porque revela uma oportunidade clara de **encantar o cliente** enquanto reduz trabalho da sua equipe.

> _Imagina isso: toda sexta-feira, **sem o cliente precisar ligar**, ele recebe automaticamente no WhatsApp:_
> _- Foto do andamento da obra_
> _- Próximos passos da semana_
> _- Nome do engenheiro/mestre responsável_

> _Isso acaba com as ligações repetitivas e ainda faz o cliente se sentir cuidado. E dá pra automatizar 90% disso._

> _Mas antes de desenhar essa solução, volto à pergunta pendente — porque ela define **qual agente implantamos primeiro**:_

> _👉 **Vocês conseguem dar um orçamento *inicial estimado* com base em fotos e medidas que o cliente envia por WhatsApp?**_
> _(Ex: “banheiro de 4m² com troca de piso e azulejo: entre R$ 9k e R$ 13k”)_

> _Ou **só fornecem valor após visita presencial**?_

> _Essa resposta decide se começamos com:_
> _- **Agente de Pré-Vendas** (se der pra estimar por mensagem) → converte mais leads_
> _- **Agente de Agendamento + Portfólio** (se precisar de visita) → reduz abandono_

> _Me confirma isso, por favor?_
> **🧑 Empresário:** Quero agilizar os orçamentos e dar visibilidade da obra para o cliente sem minha equipe parar para responder.

> **🤖 Consultor:** Perfeito — você já definiu **exatamente os dois maiores pontos de impacto**:
> _1. **Orçamento rápido** (para não perder cliente)_
> _2. **Visibilidade da obra** (para parar as ligações e encantar)_

> _Agora, só preciso de uma última peça para desenhar o time ideal:_

> _**Vocês têm um “cardápio” de serviços com preços médios por tipo de reforma?**_
> _Por exemplo:_
> _- Reforma de banheiro simples: R$ X – R$ Y_
> _- Cozinha completa: R$ A – R$ B_
> _- Pintura residencial por m²: R$ Z_

> _Ou os orçamentos são **totalmente customizados**, sem base prévia?_

> _Se tiverem esses valores médios (mesmo que aproximados), podemos criar um agente que responde **em minutos** com uma faixa realista — e isso resolve 80% dos leads. Se for totalmente customizado, focamos em **agendar a visita no mesmo dia** + enviar portfólio automático._

> _Me confirma essa parte?_
> **🧑 Empresário:** /fim

> **🤖 Consultor:** Pronto! Acabei de gerar o **blueprint completo** para transformar sua construtora com um time de agentes inteligentes.

> _### 🚀 Resumo do que vai mudar:_
> _1. **Orçamentos em minutos, não em dias**_
> _→ Um agente responde leads com estimativas realistas e agenda visita no mesmo dia._
> _2. **Clientes nunca mais ligam pedindo “como está a obra?”**_
> _→ Atualizações automáticas semanais no WhatsApp: foto + próximos passos._
> _3. **Sua equipe foca no que importa**_
> _→ Nada de parar obra pra responder mensagem ou planilha perdida._

> _### 👥 Time proposto (3 agentes essenciais):_
> _- **Agente de Pré-Vendas**: converte mais leads com velocidade_
> _- **Coordenador de Obras**: comunica andamento sem esforço_
> _- **Analista de Operações**: mantém tudo integrado e atualizado_

> _O plano começa pelo **Agente de Pré-Vendas**, porque resolve sua maior dor hoje — e pode ser implantado em poucos dias com as ferramentas que você já usa (WhatsApp + planilha + Google Agenda)._

> _Os arquivos detalhados estão salvos na pasta da sessão (`blueprint.json` e `blueprint.md`). Se quiser ajustar algo ou tirar dúvidas sobre a implantação, é só chamar!_

### Blueprint gerado

<details>
<summary>Expandir blueprint completo</summary>

# Blueprint do Time de Agentes

## Perfil da empresa
- Segmento: construcao
- Porte: pequeno-médio (15 pessoas, R$ 250k/mês)
- Modelo de negócio: reformas residenciais e comerciais com visita técnica obrigatória
- Dores: orçamento demora dias, levando à perda de leads, clientes sem visibilidade do andamento da obra, equipe interrompida constantemente por ligações e mensagens de atualização

## Mapa de processos
- **atendimento inicial**: recebimento de leads via WhatsApp, sem resposta rápida
- **elaboração de orçamento**: depende de visita técnica presencial; cálculo feito em planilha Excel
- **gestão de obras**: sem comunicação estruturada de andamento com o cliente
- **agendamento**: visitas técnicas agendadas via Google Agenda

## Integrações detectadas
- whatsapp — WhatsApp Business (dados em: celular da equipe)
- spreadsheet — Planilha Excel de custos (dados em: computador/local ou Google Sheets)
- calendar — Google Agenda (dados em: conta Google da empresa)

## Time de agentes proposto
### Agente de Pré-Vendas (SDR) — Qualificação e estimativa inicial de orçamento
- Objetivo: Responder leads em minutos com faixa de preço estimada e agendar visita técnica no mesmo dia
- Tarefas: receber lead no WhatsApp, classificar tipo de reforma (banheiro, cozinha, etc.), consultar base de preços médios por m² ou por serviço, enviar estimativa realista com disclaimer de ajuste na visita, agendar visita técnica via link do Google Agenda, enviar portfólio de obras similares
- Integrações: whatsapp, planilha de preços médios, google agenda
- Conversa com: Coordenador de Obras
### Coordenador de Obras — Gestão de comunicação durante a execução
- Objetivo: Automatizar atualizações semanais para o cliente e reduzir ligações
- Tarefas: receber cronograma da obra (etapas e datas), gerar atualização automática toda sexta: foto + próximo passo + responsável, notificar cliente via WhatsApp sobre atrasos ou mudanças, registrar conclusão de etapas
- Integrações: whatsapp, google agenda, planilha de cronograma
- Conversa com: Agente de Pré-Vendas, mestre de obra (humano)
### Analista de Operações — Automação interna e integração de dados
- Objetivo: Conectar WhatsApp, planilhas e agenda em fluxos unificados
- Tarefas: manter base de preços médios atualizada, estruturar cronograma padrão por tipo de reforma, automatizar criação de cardápio digital de serviços, gerar relatórios de conversão (lead → visita → contrato)
- Integrações: planilha excel/google sheets, whatsapp api, google calendar api
- Conversa com: Agente de Pré-Vendas, Coordenador de Obras

## Roadmap
1. **Agente de Pré-Vendas (SDR)** — Resolve a dor principal: perda de leads por lentidão. Implantação simples com WhatsApp + planilha.
2. **Coordenador de Obras** — Elimina ligações repetitivas e aumenta satisfação com atualizações automáticas.
3. **Analista de Operações** — Centraliza e mantém os dados que alimentam os outros agentes, garantindo escalabilidade.

## Perguntas em aberto
- A empresa possui uma base consolidada de preços médios por tipo de reforma (ex: R$/m² para banheiro, cozinha etc.)?
- As fotos de andamento das obras são registradas regularmente? Em que formato (WhatsApp, e-mail, pasta)?
- O Google Agenda usado hoje é compartilhado entre engenheiros/mestres, ou cada um tem sua própria agenda?

</details>

---

## Cenário: Escritório de Advocacia

- **Descrição:** Escritório de advocacia empresarial e trabalhista com 4 advogados
- **Segmento esperado:** `servicos_b2b`
- **Segmento detectado:** `servicos_b2b`
- **Blueprint emitido:** ✅ Sim
- **Score:** 100/100 (100%) — A — Excelente

```
Score  [████████████████████] 100/100
```

### Pontuação por critério

| Critério | Score | Máx | Barra | Observação |
|----------|------:|----:|-------|------------|
| Segmento | 20 | 20 | `██████████` | Correto: `servicos_b2b` |
| Blueprint gerado | 20 | 20 | `██████████` | Emitido com sucesso |
| Agentes propostos | 15 | 15 | `██████████` | 3 agentes — equipe completa |
| Roadmap | 10 | 10 | `██████████` | 3 etapas — detalhado |
| Mapa de processos | 10 | 10 | `██████████` | 4 processos mapeados |
| Perguntas em aberto | 5 | 5 | `██████████` | 4 perguntas documentadas |
| Integrações detectadas | 10 | 10 | `██████████` | 6 integrações |
| Profundidade da entrevista | 10 | 10 | `██████████` | 7 turnos do usuário |

### ✅ Pontos positivos

- Segmento detectado corretamente: `servicos_b2b`
- Blueprint gerado e salvo com sucesso
- Time com 3 agentes propostos
- Roadmap com 3 etapas bem definidas
- 4 processos mapeados no blueprint
- 4 perguntas em aberto documentadas (boa prática)
- 6 integrações detectadas corretamente
- Entrevista aprofundada: 7 turnos do empresário

### Transcrição da entrevista

> _Olá! Seja muito bem-vindo(a). 🤝_

> _Meu nome é Orbe e sou especialista em implementação de inteligência artificial para negócios. Já ajudei dezenas de empresas brasileiras a montar times de agentes que trabalham 24 horas por dia — atendendo clientes, criando conteúdo para redes sociais, gerenciando pedidos, automatizando orçamentos e muito mais._

> _Antes de qualquer proposta, quero entender bem a sua realidade. Não existe solução pronta: o plano certo depende do que você faz, de como você opera e de onde você quer chegar._

> _Então me conta: **o que a sua empresa faz** e qual é o maior desafio que você enfrenta hoje no dia a dia?_
> **🧑 Empresário:** Tenho um escritório de advocacia. Atendemos empresas em direito trabalhista e tributário.

> **🤖 Consultor:** Obrigado pela descrição! Escritórios de advocacia B2B têm desafios bem específicos — e muitas oportunidades para ganhar eficiência com agentes inteligentes.

> _Antes de tudo, quero entender melhor **como vocês captam clientes hoje**. Vocês recebem indicações? Têm presença digital (site, LinkedIn, Instagram)? Fazem prospecção ativa? Ou é tudo por indicação?_

> _Essa resposta vai me ajudar a mapear desde o primeiro contato até a entrega do serviço — e ver onde a IA pode acelerar sem perder a qualidade jurídica que seus clientes esperam._
> **🧑 Empresário:** Perdemos muito tempo respondendo clientes que perguntam sobre o andamento dos processos. Ligam toda semana.

> **🤖 Consultor:** Entendi perfeitamente a dor: perder tempo respondendo à mesma pergunta toda semana é frustrante — e tira foco do que realmente importa, que é cuidar dos processos.

> _Vamos agora entender **como vocês acompanham os processos internamente**. Vocês usam algum sistema jurídico (como Velt, Lex, SAJ), uma planilha no Excel/Google Sheets, ou tudo fica na memória/anotações?_

> _Essa resposta é crucial para saber se podemos conectar um agente de IA diretamente ao seu sistema e fazer com que ele informe o andamento automaticamente — sem ninguém precisar parar o que está fazendo para responder._
> **🧑 Empresário:** Usamos o Astrea para gestão dos processos, e-mail e WhatsApp para falar com clientes, e Excel no financeiro.

> **🤖 Consultor:** Ótimo! O Astrea é um sistema robusto — e isso abre uma oportunidade **muito concreta** para automatizar as respostas sobre andamento dos processos.

> _Antes de avançar, preciso entender:_
> _**Quantos clientes ou processos ativos vocês têm hoje?** (Por exemplo: 30 empresas atendidas, com 50 processos em andamento?)_

> _Isso me ajuda a dimensionar o volume real de trabalho e garantir que a solução de IA seja proporcional ao tamanho do seu escritório — sem overengineering, mas também sem subdimensionar._
> **🧑 Empresário:** Somos 4 advogados e 2 estagiários. Faturamos R$ 90 mil por mês.

> **🤖 Consultor:** Com 6 pessoas e R$ 90k/mês, vocês estão num tamanho ideal para ganhar **muito** com automação inteligente — sem burocracia, mas com impacto real no dia a dia.

> _Vamos agora entender melhor o **pós-venda**:_
> _Vocês enviam algum tipo de atualização proativa sobre os processos (por exemplo, um resumo semanal por e-mail ou WhatsApp), ou só respondem quando o cliente pergunta?_

> _Essa resposta vai me dizer se podemos **substituir** o contato manual por um agente automatizado… ou se, ainda melhor, podemos **elevar o nível do serviço** oferecendo atualizações regulares que impressionam o cliente — sem custo de tempo da equipe._
> **🧑 Empresário:** Captação é fraca: dependemos só de indicação. Não temos presença digital nem produção de conteúdo jurídico.

> **🤖 Consultor:** Interessante — e muito comum em escritórios de alto nível técnico! Vocês têm um serviço sólido (afinal, as indicações existem), mas estão deixando **muito potencial de crescimento na mesa** por não ter presença digital.

> _Antes de fechar o diagnóstico, preciso confirmar:_
> _Vocês **enviam atualizações proativas** sobre os processos (ex: “seu processo X teve audiência marcada”), ou **só respondem quando o cliente pergunta**?_

> _Essa resposta vai definir se o primeiro agente que eu proponho será focado em **reduzir retrabalho** (respondendo automaticamente) ou em **elevar o padrão do serviço** (enviando updates sem o cliente precisar cobrar). As duas são valiosas — mas a escolha muda o impacto inicial._
> **🧑 Empresário:** Quero automatizar o informe de status dos processos e melhorar a captação de novos clientes empresariais.

> **🤖 Consultor:** Perfeito! Com esses dois objetivos — **automatizar o status dos processos** e **melhorar a captação** — já dá para montar um plano de transformação digital muito sólido para o seu escritório.

> _Só preciso de mais uma confirmação rápida:_
> _Quando você pensa em informar o andamento automaticamente, **qual canal é mais natural para seus clientes?**_
> _- WhatsApp (mensagem direta com resumo do processo)_
> _- E-mail (com update mais formal)_
> _- Ou os dois?_

> _Essa escolha vai definir como o agente se integra ao Astrea e entrega valor sem parecer robótico._
> **🧑 Empresário:** /fim

> **🤖 Consultor:** Pronto! Acabei de gerar o **blueprint completo** para transformar seu escritório com agentes inteligentes.

> _Ele propõe um time de **3 agentes especializados**:_

> _1. **Agente de Atendimento Jurídico** – vai responder automaticamente sobre andamento dos processos, conectado ao Astrea, reduzindo drasticamente as ligações e mensagens repetidas._
> _2. **Coordenador de Operações Jurídicas** – garante que os dados do Astrea fluam para os canais certos (WhatsApp, e-mail) sem intervenção manual._
> _3. **Agente de Marketing Jurídico** – cria presença digital no LinkedIn (e opcionalmente Instagram), produz conteúdo sobre direito trabalhista/tributário e atrai novos clientes empresariais — reduzindo a dependência de indicações._

> _O plano é implantado em **3 fases**, começando pela automação do atendimento (maior dor, menor complexidade)._

> _### O que ficou em aberto (para validar antes da implantação):_
> _- Qual canal seus clientes preferem para updates: WhatsApp, e-mail ou os dois?_
> _- O Astrea permite extração automatizada de status via API?_
> _- Vocês já têm site registrado?_
> _- Há interesse em usar Instagram além do LinkedIn?_

> _Se quiser, posso agora detalhar **como seria a primeira semana de implantação** do Agente de Atendimento Jurídico — ou explicar como o marketing jurídico pode gerar 5–10 leads qualificados por mês com pouco esforço._

> _É só dizer!_

### Blueprint gerado

<details>
<summary>Expandir blueprint completo</summary>

# Blueprint do Time de Agentes

## Perfil da empresa
- Segmento: servicos_b2b
- Porte: pequeno/médio (6 pessoas, R$ 90k/mês)
- Modelo de negócio: escritório de advocacia B2B em direito trabalhista e tributário
- Dores: perda de tempo com perguntas repetidas sobre andamento de processos, clientes ligam toda semana para saber status, captação fraca — dependência total de indicações, sem presença digital nem conteúdo jurídico

## Mapa de processos
- **atendimento**: respostas manuais sobre andamento de processos via WhatsApp e telefone
- **operacoes**: gestão de processos no Astrea, sem comunicação automática de status
- **marketing_vendas**: captação exclusivamente por indicação, sem presença digital
- **pos_venda**: sem atualizações proativas; cliente só sabe do andamento se perguntar

## Integrações detectadas
- sistema_juridico — Astrea (dados em: plataforma Astrea)
- whatsapp — WhatsApp Business (dados em: celular da equipe)
- email — E-mail corporativo (dados em: provedor de e-mail)
- planilha — Excel (financeiro) (dados em: arquivo local ou OneDrive)

## Time de agentes proposto
### Agente de Atendimento Jurídico — SAC 24/7 para clientes ativos
- Objetivo: responder automaticamente sobre andamento de processos, reduzindo ligações e mensagens repetidas
- Tarefas: consultar status atualizado no Astrea, responder perguntas frequentes sobre processos, enviar resumo semanal proativo por WhatsApp ou e-mail
- Integrações: Astrea, WhatsApp Business, e-mail
- Conversa com: Agente de Marketing Jurídico
### Agente de Marketing Jurídico — presença digital e geração de leads
- Objetivo: criar autoridade digital e atrair novos clientes empresariais com conteúdo relevante
- Tarefas: criar posts sobre direito trabalhista e tributário, gerenciar perfil do escritório no LinkedIn, desenvolver landing page com formulário de contato, responder comentários e mensagens de potenciais clientes
- Integrações: LinkedIn, Instagram (opcional), landing page (Webflow/Framer)
- Conversa com: Agente de Atendimento Jurídico
### Coordenador de Operações Jurídicas — automação interna e integração de sistemas
- Objetivo: conectar Astrea, WhatsApp e financeiro para fluxo unificado de informação
- Tarefas: extrair eventos relevantes do Astrea (audiências, prazos), disparar notificações internas e externas, registrar interações no histórico do cliente
- Integrações: Astrea, WhatsApp Business, Excel
- Conversa com: Agente de Atendimento Jurídico

## Roadmap
1. **Agente de Atendimento Jurídico** — resolve a dor principal (tempo perdido com status) com implantação rápida via integração Astrea + WhatsApp
2. **Coordenador de Operações Jurídicas** — garante que os dados do Astrea fluam automaticamente para comunicação e registro
3. **Agente de Marketing Jurídico** — após estabilizar operação, gera crescimento sustentável com presença digital

## Perguntas em aberto
- Qual o canal preferido pelos clientes para receber updates: WhatsApp, e-mail ou ambos?
- O Astrea permite extração automatizada de status via API ou webhook?
- Há interesse em criar conteúdo para Instagram além do LinkedIn?
- Existe domínio/site institucional registrado hoje?

</details>

---

## Análise Global e Melhorias Sugeridas

### Recomendações de melhoria

1. Nenhum problema recorrente nesta rodada. Manter o avaliador como gate de regressão: rode `python scripts/eval_discovery.py` após qualquer mudança em `prompts.py`, `tools.py` ou na seed CNAE (há um smoke e2e opt-in via `QWENPAW_EVAL_E2E=1` no pytest).
2. Adicionar personas de segmentos FORA da seed (ex.: pet shop, oficina mecânica) para exercitar o caminho de raciocínio livre do `segment_lookup`.
3. Evoluir o scoring com critérios qualitativos (clareza das perguntas, empatia, não-repetição) usando LLM-as-judge em vez de só contagens.

---

_Relatório gerado por `scripts/eval_discovery.py` em 20260611_194029_
