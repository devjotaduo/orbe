# Relatório de Avaliação — Discovery Agent

**Data:** 20260611_202746  
**Cenários testados:** 10  
**Pontuação máxima por cenário:** 100 pts  

## Sumário Executivo

| Cenário | Segmento | Blueprint | Score | Qualidade | Nota |
|---------|----------|-----------|-------|-----------|------|
| Loja Virtual de Roupas | ✅ | ✅ | 100/100 (100%) | 19/30 | A — Excelente |
| Restaurante Familiar | ✅ | ✅ | 100/100 (100%) | 22/30 | A — Excelente |
| Clínica Médica | ✅ | ✅ | 100/100 (100%) | 25/30 | A — Excelente |
| Escola de Idiomas | ✅ | ✅ | 100/100 (100%) | 24/30 | A — Excelente |
| Salão de Beleza | ✅ | ✅ | 100/100 (100%) | 23/30 | A — Excelente |
| Software House B2B | ✅ | ✅ | 100/100 (100%) | 25/30 | A — Excelente |
| Construtora de Reformas | ✅ | ✅ | 100/100 (100%) | 26/30 | A — Excelente |
| Escritório de Advocacia | ✅ | ✅ | 100/100 (100%) | 25/30 | A — Excelente |
| Pet Shop (fora da seed) | ✅ | ✅ | 100/100 (100%) | 29/30 | A — Excelente |
| Oficina Mecânica (fora da seed) | ✅ | ✅ | 95/100 (95%) | 26/30 | A — Excelente |

**Média geral:** 99.5% — A — Excelente

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
| Agentes propostos | 15 | 15 | `██████████` | 3 agentes — equipe completa |
| Roadmap | 10 | 10 | `██████████` | 3 etapas — detalhado |
| Mapa de processos | 10 | 10 | `██████████` | 5 processos mapeados |
| Perguntas em aberto | 5 | 5 | `██████████` | 5 perguntas documentadas |
| Integrações detectadas | 10 | 10 | `██████████` | 4 integrações |
| Profundidade da entrevista | 10 | 10 | `██████████` | 7 turnos do usuário |

### Avaliação qualitativa (LLM-as-judge)

| Critério | Nota | Barra |
|----------|-----:|-------|
| Clareza das perguntas | 7/10 | `███████░░░` |
| Empatia | 9/10 | `█████████░` |
| Não-repetição | 3/10 | `███░░░░░░░` |
| **Total** | **19/30** | |

> O consultor demonstra alta empatia, reconhecendo dores reais e usando linguagem acolhedora e motivadora. As perguntas são claras, mas há uma repetição excessiva da mesma solicitação — pedir as "3 ou 4 dúvidas mais repetidas no WhatsApp" ao menos cinco vezes, com mínima variação. Isso prejudica a fluidez e sugere falta de adaptação à relutância do empresário em responder.

### ✅ Pontos positivos

- Segmento detectado corretamente: `ecommerce`
- Blueprint gerado e salvo com sucesso
- Time com 3 agentes propostos
- Roadmap com 3 etapas bem definidas
- 5 processos mapeados no blueprint
- 5 perguntas em aberto documentadas (boa prática)
- 4 integrações detectadas corretamente
- Entrevista aprofundada: 7 turnos do empresário

### ❌ Problemas encontrados

- Qualidade conversacional abaixo do esperado (não-repetição: 3/10) — O consultor demonstra alta empatia, reconhecendo dores reais e usando linguagem acolhedora e motivadora. As perguntas são claras, mas há uma repetição excessiva da mesma solicitação — pedir as "3 ou 4 dúvidas mais repetidas no WhatsApp" ao menos cinco vezes, com mínima variação. Isso prejudica a fluidez e sugere falta de adaptação à relutância do empresário em responder.

### Transcrição da entrevista

> _Olá! Seja muito bem-vindo(a). 🤝_

> _Meu nome é Orbe e sou especialista em implementação de inteligência artificial para negócios. Já ajudei dezenas de empresas brasileiras a montar times de agentes que trabalham 24 horas por dia — atendendo clientes, criando conteúdo para redes sociais, gerenciando pedidos, automatizando orçamentos e muito mais._

> _Antes de qualquer proposta, quero entender bem a sua realidade. Não existe solução pronta: o plano certo depende do que você faz, de como você opera e de onde você quer chegar._

> _Então me conta: **o que a sua empresa faz** e qual é o maior desafio que você enfrenta hoje no dia a dia?_
> **🧑 Empresário:** Tenho uma loja virtual de roupas femininas. Vendemos pelo Instagram e site próprio.

> **🤖 Consultor:** Opa, tudo bem? Legal saber que você tem uma loja virtual de roupas femininas — um segmento com muito potencial, especialmente quando bem alinhado entre Instagram e site!

> _Antes de mergulhar nas perguntas certas pra te entregar um plano realista e eficaz, quero entender melhor como está funcionando hoje._

> _Vamos começar pelo **atendimento**:_
> _Você responde dúvidas dos clientes por qual canal? Só Instagram e site, ou também usa WhatsApp? E quantas mensagens/dúvidas em média recebe por dia?_

> _(Essa resposta já vai me ajudar a ver se o gargalo está no volume, na repetição das perguntas ou na demora para responder.)_
> **🧑 Empresário:** O maior problema é o atendimento. Recebo mais de 100 mensagens por dia no WhatsApp e não consigo responder todas.

> **🤖 Consultor:** Entendi perfeitamente — mais de 100 mensagens por dia no WhatsApp é inviável de responder sozinha(o), e isso certamente está fazendo você perder vendas e frustrar clientes.

> _Antes de propor uma solução, preciso entender **quais são as perguntas mais repetidas** que você recebe. Por exemplo:_

> _- As pessoas perguntam sobre **tamanhos**, **cores disponíveis**, **prazo de entrega**, **trocas**, **formas de pagamento**...?_

> _Me conta as 3 ou 4 dúvidas que mais aparecem — isso vai me ajudar a montar um atendente automático que resolva o grosso do volume pra você._
> **🧑 Empresário:** Uso WhatsApp Business e uma planilha Excel para controlar os pedidos. Não tenho CRM.

> **🤖 Consultor:** Ótimo — agora já tenho um retrato mais claro: você está com o atendimento sobrecarregado no WhatsApp e gerenciando tudo com uma planilha, sem CRM. Isso é super comum em lojas que crescem rápido!

> _Voltando à pergunta anterior (importante pra acertar na solução):_
> _**Quais são as 3 ou 4 dúvidas mais repetidas** que você recebe no WhatsApp? Por exemplo:_

> _- “Qual o tamanho ideal para mim?”_
> _- “Quando chega meu pedido?”_
> _- “Aceita boleto/pix/parcelamento?”_
> _- “Como faço troca?”_

> _Me ajuda com essa lista — assim posso montar um atendente automático que responda essas perguntas **sem você precisar digitar nada**, liberando seu tempo pra fechar vendas e cuidar da operação._
> **🧑 Empresário:** Faturamos em torno de R$ 30 mil por mês. Somos 3 pessoas: eu, uma assistente e uma responsável pelo estoque.

> **🤖 Consultor:** Perfeito — com R$ 30 mil/mês e uma equipe de 3 pessoas, você está num estágio em que **automatizar o essencial** pode liberar horas valiosas da sua semana e ainda aumentar as vendas.

> _Mas ainda preciso de uma peça-chave pra montar a solução certa:_
> _**Quais são as perguntas mais repetidas no WhatsApp?**_

> _Por exemplo:_
> _- “Tem estoque desse produto?”_
> _- “Qual o prazo de entrega?”_
> _- “Como funciona a troca?”_
> _- “Aceita parcelamento?”_

> _Se você me der as 3 ou 4 dúvidas que mais aparecem, consigo projetar um atendente automático que resolva **80% das mensagens sozinho**, sem deixar cliente esperando. Pode ser até copiando e colando mensagens reais que recebe!_
> **🧑 Empresário:** Vendo também na Shopee e no Mercado Livre. Tenho problemas com devoluções que ficam sem resposta.

> **🤖 Consultor:** Agora fez *click*! Você não só tem volume alto no WhatsApp, mas também precisa gerenciar **devoluções em múltiplos canais** (site, Instagram, Mercado Livre, Shopee) — e isso está caindo no esquecimento. Isso afeta diretamente sua reputação e pode gerar avaliações negativas.

> _Antes de seguir, preciso confirmar algo essencial para resolver **tanto o atendimento quanto as devoluções**:_

> _👉 **Quais são as 3 ou 4 perguntas mais repetidas que você recebe no WhatsApp?**_

> _Por exemplo:_
> _- “Meu pedido já foi enviado?”_
> _- “Como faço pra trocar?”_
> _- “Esse produto ainda tem estoque?”_
> _- “Aceita parcelar em 6x?”_

> _Se eu souber exatamente quais dúvidas se repetem, posso montar um **Atendente WhatsApp** que responda sozinho desde o primeiro contato até o pós-venda — incluindo instruções claras para devoluções, com links diretos para formulários ou passos simples._

> _Não precisa ser perfeito — me dá só as frases que você mais copia e cola!_
> **🧑 Empresário:** Meu sonho é conseguir vender enquanto durmo — automação total do atendimento e rastreio de pedidos.

> **🤖 Consultor:** Esse é um dos meus sonhos favoritos de ouvir — **vender enquanto você dorme** é 100% possível pra uma loja como a sua, e já tenho o caminho claro pra te levar lá.

> _Mas pra garantir que a automação cubra **tudo** — desde a primeira mensagem até o pós-venda nas quatro plataformas (Instagram, site, Mercado Livre e Shopee) — preciso só de mais um detalhe:_

> _👉 **Quais são as 3 ou 4 perguntas mais repetidas no WhatsApp?**_

> _Por exemplo:_
> _- “Qual o prazo de entrega?”_
> _- “Como faço troca/devolução?”_
> _- “Tem estoque do [produto X]?”_
> _- “Aceita PIX/boleto/parcelamento?”_

> _Com essa lista, eu monto um **Atendente WhatsApp 24/7** que:_
> _- Responde automaticamente essas dúvidas com informações reais (atualizadas da sua planilha ou estoque),_
> _- Registra pedidos,_
> _- Envia link de rastreio quando o pedido sai,_
> _- E ainda orienta o cliente passo a passo em caso de devolução — evitando que fiquem sem resposta._

> _Me ajuda com essas frases? Pode ser exatamente como seus clientes escrevem!_
> **🧑 Empresário:** /fim

> **🤖 Consultor:** Pronto! 🎯

> _Com base em tudo o que você compartilhou, montei um **plano realista de transformação digital** para sua loja de roupas femininas — com foco em **vender enquanto você dorme**, exatamente como sonha._

> _### O que está no blueprint:_
> _- **3 agentes inteligentes** que trabalham 24/7:_
> _1. **Atendente WhatsApp** – responde dúvidas repetidas e tria mensagens._
> _2. **Coordenador de Pedidos** – unifica pedidos do Instagram, site, Mercado Livre e Shopee._
> _3. **Coordenador de Pós-Venda** – garante que nenhuma devolução fique sem resposta._

> _- **Roadmap por prioridade**: começamos pelo atendimento (sua maior dor), depois operações e por fim fidelização._

> _- **Integrações detectadas**: WhatsApp Business, planilha Excel/Google Sheets, Mercado Livre e Shopee._

> _### O que ficou em aberto (para refinamento futuro):_
> _- Quais são as perguntas mais repetidas no WhatsApp?_
> _- Qual plataforma usa para o site (Shopify, WooCommerce etc.)?_
> _- Sua planilha está no Excel local ou Google Sheets?_
> _- Os marketplaces permitem integração automática (webhook/API)?_
> _- Você tem fotos e descrições completas dos produtos?_

> _Mesmo sem essas respostas, já dá pra implantar a **primeira versão funcional em 3-5 dias** — e começar a liberar horas do seu dia imediatamente._

> _Se quiser avançar com a implementação ou ajustar algo no plano, é só chamar! 💡_

### Blueprint gerado

<details>
<summary>Expandir blueprint completo</summary>

# Blueprint do Time de Agentes

## Perfil da empresa
- Segmento: ecommerce
- Porte: pequeno (3 pessoas, R$ 30k/mês)
- Modelo de negócio: ecommerce multicanal de roupas femininas (Instagram, site próprio, Mercado Livre, Shopee)
- Dores: atendimento lento no WhatsApp com mais de 100 mensagens/dia, devoluções sem resposta em múltiplos canais, operação manual com planilha Excel, sem CRM, dificuldade de escalar vendas sem aumentar esforço

## Mapa de processos
- **atendimento**: respostas a dúvidas via WhatsApp, Instagram e marketplaces
- **pedidos**: registro e controle manual via planilha Excel
- **logística**: envio e rastreio de pedidos sem automação
- **pós-venda**: gestão de trocas e devoluções sem follow-up estruturado
- **marketing**: presença no Instagram e vendas via site próprio + marketplaces

## Integrações detectadas
- whatsapp — WhatsApp Business (dados em: celular do dono)
- planilha — Excel (dados em: computador local ou Google Sheets)
- marketplace — Mercado Livre (dados em: painel do vendedor)
- marketplace — Shopee (dados em: painel do vendedor)
- ecommerce — Site próprio (dados em: plataforma não especificada)

## Time de agentes proposto
### Atendente WhatsApp — SAC 24/7
- Objetivo: Responder automaticamente as dúvidas mais comuns e triar mensagens para reduzir sobrecarga humana
- Tarefas: responder FAQ sobre tamanhos, estoque, prazos e pagamento, coletar dados do cliente para registro de pedido, encaminhar casos complexos à equipe humana, oferecer link de rastreio após envio
- Integrações: whatsapp, planilha de pedidos
- Conversa com: Coordenador de Pedidos, Coordenador de Pós-Venda
### Coordenador de Pedidos — Operações
- Objetivo: Unificar e automatizar o fluxo de pedidos de todos os canais (Instagram, site, ML, Shopee)
- Tarefas: consolidar pedidos numa única base, atualizar status de envio, notificar cliente via WhatsApp com link de rastreio, sincronizar estoque básico
- Integrações: planilha, whatsapp, painel Mercado Livre, painel Shopee
- Conversa com: Atendente WhatsApp, Responsável pelo Estoque
### Coordenador de Pós-Venda — Fidelização
- Objetivo: Garantir que nenhuma devolução fique sem resposta e recuperar experiência do cliente
- Tarefas: enviar follow-up pós-compra em 3 dias, oferecer formulário simples de solicitação de troca/devolução, registrar e acompanhar casos abertos, solicitar avaliação positiva após resolução
- Integrações: whatsapp, planilha de pós-venda
- Conversa com: Atendente WhatsApp, Coordenador de Pedidos

## Roadmap
1. **Atendente WhatsApp** — Resolve a dor principal (100+ mensagens/dia) com implantação rápida e alto impacto na percepção do cliente.
2. **Coordenador de Pedidos** — Centraliza operação multicanal e permite automação de rastreio — essencial para vender enquanto dorme.
3. **Coordenador de Pós-Venda** — Fecha o ciclo, evita avaliações negativas e aumenta retenção com mínimo esforço humano.

## Perguntas em aberto
- Quais são as perguntas mais repetidas recebidas no WhatsApp?
- Qual plataforma hospeda o site próprio (Shopify, WooCommerce, etc.)?
- A planilha de pedidos está no Excel local ou Google Sheets?
- Os marketplaces (ML/Shopee) permitem notificações automáticas de novo pedido via webhook ou API?
- Há fotos atualizadas e descrições completas dos produtos para alimentar respostas automáticas?

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

### Avaliação qualitativa (LLM-as-judge)

| Critério | Nota | Barra |
|----------|-----:|-------|
| Clareza das perguntas | 8/10 | `████████░░` |
| Empatia | 9/10 | `█████████░` |
| Não-repetição | 5/10 | `█████░░░░░` |
| **Total** | **22/30** | |

> O consultor faz perguntas claras e contextualizadas, demonstrando boa empatia ao reconhecer dores reais do empresário e adaptar o discurso ao setor de restaurantes. No entanto, repete quase que literalmente a mesma pergunta sobre o WhatsApp duas vezes, prejudicando a fluidez e sugerindo falta de atenção à resposta anterior.

### ✅ Pontos positivos

- Segmento detectado corretamente: `alimentacao`
- Blueprint gerado e salvo com sucesso
- Time com 3 agentes propostos
- Roadmap com 3 etapas bem definidas
- 3 processos mapeados no blueprint
- 4 perguntas em aberto documentadas (boa prática)
- 3 integrações detectadas corretamente
- Entrevista aprofundada: 6 turnos do empresário

### ❌ Problemas encontrados

- Qualidade conversacional abaixo do esperado (não-repetição: 5/10) — O consultor faz perguntas claras e contextualizadas, demonstrando boa empatia ao reconhecer dores reais do empresário e adaptar o discurso ao setor de restaurantes. No entanto, repete quase que literalmente a mesma pergunta sobre o WhatsApp duas vezes, prejudicando a fluidez e sugerindo falta de atenção à resposta anterior.

### Transcrição da entrevista

> _Olá! Seja muito bem-vindo(a). 🤝_

> _Meu nome é Orbe e sou especialista em implementação de inteligência artificial para negócios. Já ajudei dezenas de empresas brasileiras a montar times de agentes que trabalham 24 horas por dia — atendendo clientes, criando conteúdo para redes sociais, gerenciando pedidos, automatizando orçamentos e muito mais._

> _Antes de qualquer proposta, quero entender bem a sua realidade. Não existe solução pronta: o plano certo depende do que você faz, de como você opera e de onde você quer chegar._

> _Então me conta: **o que a sua empresa faz** e qual é o maior desafio que você enfrenta hoje no dia a dia?_
> **🧑 Empresário:** Tenho um restaurante de comida caseira. Atendo no salão e faço delivery pelo iFood.

> **🤖 Consultor:** Legal! Restaurante de comida caseira com salão e delivery pelo iFood — um modelo bem comum, mas cheio de oportunidades para melhorar a operação e crescer com menos estresse.

> _Pelo que vi nos trilhos do segmento, os maiores pontos de dor costumam estar em **pedidos manuais**, **erros na comunicação com a cozinha** e **falta de acompanhamento pós-venda**. Mas quero entender melhor como funciona **hoje** pra te entregar um plano realista._

> _Vamos começar pelo atendimento:_
> _**Você recebe pedidos ou dúvidas dos clientes por WhatsApp também? Ou só pelo iFood e no balcão?**_
> **🧑 Empresário:** O maior problema é a gestão: pedidos do iFood chegam misturados com os do salão. Muito caos na cozinha.

> **🤖 Consultor:** Entendi perfeitamente — esse caos entre iFood e salão é uma dor **muito** comum, e dá pra resolver de forma simples e eficaz.

> _Antes de propor a solução, preciso entender melhor como você lida com isso hoje:_

> _**Como os pedidos do iFood e do salão chegam na cozinha atualmente?**_
> _Por exemplo: o iFood imprime em um papel? Você anota em um caderno? Usa alguma planilha ou sistema? E os pedidos do salão — são passados verbalmente, escritos à mão, ou tem algum outro método?_

> _Essa resposta vai me ajudar a desenhar um fluxo que realmente funcione pra sua realidade._
> **🧑 Empresário:** Uso o iFood, WhatsApp para delivery próprio, e o sistema da operadora de cartão. Tudo separado.

> **🤖 Consultor:** Agora ficou bem claro: você tem **três canais operando de forma isolada** — iFood, WhatsApp e o sistema da operadora — e isso está gerando o caos que você descreveu. Resolver essa fragmentação é o primeiro passo pra trazer calma pra sua cozinha.

> _Antes de avançar, preciso entender um pouco sobre o **atendimento no WhatsApp**, já que é um canal direto com o cliente:_

> _**Quem responde as mensagens no WhatsApp hoje? É você, um funcionário, ou mais de uma pessoa? E quantas mensagens em média vocês recebem por dia (só de pedidos e dúvidas)?**_

> _Isso vai me ajudar a dimensionar o agente certo pra cuidar disso — e talvez até aliviar alguém da equipe que está sobrecarregado._
> **🧑 Empresário:** Faturamos em torno de R$ 60 mil por mês. Temos 8 funcionários incluindo cozinha e salão.

> **🤖 Consultor:** Com esse porte — R$ 60k/mês e 8 funcionários — faz todo sentido que o caos nos pedidos esteja pesando tanto. Em times pequenos, qualquer processo manual vira gargalo rápido.

> _Voltando ao WhatsApp, que é um canal-chave pro seu delivery próprio:_

> _**Quem responde as mensagens no WhatsApp hoje? É você, um funcionário, ou mais de uma pessoa? E quantas mensagens em média vocês recebem por dia (só de pedidos e dúvidas)?**_

> _Essa informação é crucial pra eu propor um agente que realmente alivie a carga da sua equipe — sem criar mais trabalho._
> **🧑 Empresário:** Quero um agente que responda clientes no WhatsApp sobre cardápio, horários e reservas automaticamente.

> **🤖 Consultor:** Perfeito! Um agente de WhatsApp que responda **cardápio, horários e reservas** automaticamente é uma ótima ideia — e totalmente viável. Isso já vai liberar tempo da sua equipe pra focar no que realmente importa: preparar os pratos com qualidade.

> _Agora, pra esse agente funcionar bem, ele precisa de um **catálogo digital atualizado** (com fotos, descrições e preços) e de um jeito claro de registrar reservas._

> _Então, duas perguntas rápidas:_

> _1. **Você já tem um cardápio digital (em PDF, site, Instagram, etc.)? Ele está sempre atualizado com os preços e itens do dia?**_
> _2. **Como você registra as reservas hoje? Em caderno, planilha, ou só na memória?**_

> _Com essas respostas, consigo desenhar não só o agente de atendimento, mas também quem vai cuidar do catálogo e das reservas nos bastidores._
> **🧑 Empresário:** /fim

> **🤖 Consultor:** Pronto! Acabei de gerar o seu **blueprint personalizado** com um time de 3 agentes inteligentes pensado especialmente para o seu restaurante:

> _1. **Atendente WhatsApp** – para responder cardápio, horários e reservas 24/7_
> _2. **Coordenador de Pedidos** – para unificar iFood, WhatsApp e salão e acabar com o caos na cozinha_
> _3. **Criador de Catálogo** – para manter seu cardápio digital sempre bonito e atualizado_

> _O plano começa pelo agente que dá alívio imediato (o do WhatsApp), depois resolve a raiz do problema operacional (pedidos misturados) e, por fim, garante que tudo funcione com informação de qualidade (catálogo)._

> _Fiquei com algumas perguntas em aberto (como o formato atual do seu cardápio e como você registra reservas), mas mesmo sem essas respostas o plano já é totalmente aplicável._

> _Se quiser ajustar algo ou entender como implantar passo a passo, é só chamar! 🍽️_

### Blueprint gerado

<details>
<summary>Expandir blueprint completo</summary>

# Blueprint do Time de Agentes

## Perfil da empresa
- Segmento: alimentacao
- Porte: pequeno (8 funcionários, R$ 60k/mês)
- Modelo de negócio: restaurante com salão e delivery (iFood + WhatsApp)
- Dores: pedidos misturados na cozinha, caos operacional entre canais de venda, falta de unificação de pedidos, atendimento manual no WhatsApp

## Mapa de processos
- **atendimento**: dúvidas sobre cardápio, horários e reservas via WhatsApp
- **pedidos**: pedidos fragmentados entre iFood, WhatsApp e salão, sem consolidação
- **operações**: comunicação caótica com a cozinha devido à falta de fluxo unificado

## Integrações detectadas
- marketplace — iFood (dados em: painel do parceiro iFood)
- whatsapp — WhatsApp Business (dados em: celular do dono/equipe)
- payment — Sistema da operadora de cartão (dados em: terminal ou app da operadora)

## Time de agentes proposto
### Atendente WhatsApp — SAC 24/7
- Objetivo: responder automaticamente dúvidas sobre cardápio, horários e reservas no WhatsApp, sem intervenção humana
- Tarefas: responder FAQ de cardápio e horários, registrar intenção de reserva, encaminhar pedidos de delivery próprio para o Coordenador de Pedidos
- Integrações: whatsapp, catálogo digital
- Conversa com: Coordenador de Pedidos
### Coordenador de Pedidos — operações
- Objetivo: unificar todos os pedidos (iFood, WhatsApp e salão) num único fluxo visível para a cozinha
- Tarefas: consolidar pedidos de todos os canais, gerar ordens de produção padronizadas, notificar atrasos ou problemas
- Integrações: ifood, whatsapp, planilha ou sistema simples
- Conversa com: Atendente WhatsApp, cozinha
### Criador de Catálogo — marketing & conteúdo
- Objetivo: manter um catálogo digital sempre atualizado para alimentar o atendimento e vendas
- Tarefas: montar catálogo com fotos, descrições e preços, atualizar itens do dia ou promoções, disponibilizar link integrado ao WhatsApp e redes sociais
- Integrações: whatsapp, instagram (opcional)
- Conversa com: Atendente WhatsApp

## Roadmap
1. **Atendente WhatsApp** — resolve a dor imediata de atendimento manual e é de implantação rápida
2. **Coordenador de Pedidos** — elimina o caos na cozinha unificando todos os canais de pedido
3. **Criador de Catálogo** — garante que o atendimento automático tenha informação precisa e atrativa

## Perguntas em aberto
- Como as reservas são registradas hoje (caderno, planilha, etc.)?
- Existe um cardápio digital atualizado? Em qual formato?
- O painel do iFood permite exportação ou notificação de novos pedidos (ex: por e-mail ou webhook)?
- Há uso de Instagram ou outras redes sociais para divulgação?

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
| Perguntas em aberto | 5 | 5 | `██████████` | 4 perguntas documentadas |
| Integrações detectadas | 10 | 10 | `██████████` | 7 integrações |
| Profundidade da entrevista | 10 | 10 | `██████████` | 6 turnos do usuário |

### Avaliação qualitativa (LLM-as-judge)

| Critério | Nota | Barra |
|----------|-----:|-------|
| Clareza das perguntas | 9/10 | `█████████░` |
| Empatia | 9/10 | `█████████░` |
| Não-repetição | 7/10 | `███████░░░` |
| **Total** | **25/30** | |

> O consultor faz perguntas claras e contextualizadas, demonstrando empatia ao reconhecer a sobrecarga da recepção e adaptar o discurso ao setor médico. No entanto, repete duas vezes a mesma pergunta sobre o uso do WhatsApp Business e o envio manual de confirmações, o que reduz levemente a nota de não repetição.

### ✅ Pontos positivos

- Segmento detectado corretamente: `saude`
- Blueprint gerado e salvo com sucesso
- Time com 3 agentes propostos
- Roadmap com 3 etapas bem definidas
- 3 processos mapeados no blueprint
- 4 perguntas em aberto documentadas (boa prática)
- 7 integrações detectadas corretamente
- Entrevista aprofundada: 6 turnos do empresário

### Transcrição da entrevista

> _Olá! Seja muito bem-vindo(a). 🤝_

> _Meu nome é Orbe e sou especialista em implementação de inteligência artificial para negócios. Já ajudei dezenas de empresas brasileiras a montar times de agentes que trabalham 24 horas por dia — atendendo clientes, criando conteúdo para redes sociais, gerenciando pedidos, automatizando orçamentos e muito mais._

> _Antes de qualquer proposta, quero entender bem a sua realidade. Não existe solução pronta: o plano certo depende do que você faz, de como você opera e de onde você quer chegar._

> _Então me conta: **o que a sua empresa faz** e qual é o maior desafio que você enfrenta hoje no dia a dia?_
> **🧑 Empresário:** Tenho uma clínica médica com 3 médicos: clínico geral, dermatologista e ortopedista.

> **🤖 Consultor:** Obrigado pela descrição! Com 3 especialidades diferentes, sua clínica já tem uma boa diversificação — isso é ótimo para atrair mais pacientes.

> _Pelo que vejo nos trilhos típicos de clínicas médicas, a maior dor costuma estar no **agendamento e na confirmação de consultas**, com muitas faltas (no-show) e agendas feitas manualmente. Mas quero entender melhor como funciona **hoje** pra você._

> _Vamos começar pelo atendimento inicial:_
> _**Como os pacientes entram em contato hoje pra marcar consulta?**_
> _É só por WhatsApp? Também recebem ligações, e-mails ou têm um site com formulário?_

> _Me conta também: qual canal consome mais tempo da sua equipe?_
> **🧑 Empresário:** A recepção gasta o dia inteiro agendando e desmarcando consultas. Pacientes ligam para confirmar, remarcar.

> **🤖 Consultor:** Entendi perfeitamente — sua recepção está atolada com ligações repetitivas o dia todo, e isso tira o foco de outras tarefas importantes.

> _Antes de propor soluções, preciso entender melhor **como você gerencia os horários hoje**:_

> _Vocês usam **algum sistema de agenda**?_
> _É uma planilha do Excel/Google Sheets? Um software específico (como Agendador, Doctoralia, Zenklub, Agenda Fácil)? Ou é tudo feito no papel ou na memória?_

> _Essa resposta vai me ajudar a desenhar um agente que se integre exatamente ao seu fluxo atual — sem exigir mudanças drásticas._
> **🧑 Empresário:** Usamos um software de clínica chamado Nuvem, integrado com Google Calendar. Também WhatsApp para confirmações.

> **🤖 Consultor:** Ótimo! Saber que você já usa o **Nuvem + Google Calendar** é uma excelente notícia — isso facilita muito a automação, pois essas ferramentas têm boa estrutura para integração.

> _Agora, sobre o **WhatsApp**:_
> _Vocês usam o **WhatsApp Business** (o app específico para empresas) ou é o WhatsApp pessoal da recepcionista?_

> _E mais importante: **quem envia as mensagens de confirmação hoje?**_
> _É feito manualmente (um por um), ou já existe algum lembrete automático pelo Nuvem que alguém só revisa?_

> _Isso vai me ajudar a entender se podemos simplesmente “conectar” um agente ao seu fluxo atual ou se precisamos montar um novo passo automatizado do zero._
> **🧑 Empresário:** Atendemos convênios Unimed e Bradesco Saúde, e particular. Faturamos R$ 120 mil por mês.

> **🤖 Consultor:** Perfeito — com esse faturamento e atendimento a convênios, sua clínica já tem uma base sólida. Isso reforça que **automatizar o operacional** vai liberar tempo pra focar em crescimento (como atrair mais pacientes particulares ou expandir especialidades).

> _Voltando à pergunta anterior (importante para o desenho do agente):_
> _Vocês usam **WhatsApp Business** ou o WhatsApp pessoal da recepcionista?_
> _E as **confirmações de consulta são enviadas manualmente**, ou o sistema Nuvem já dispara algo automático que alguém só revisa?_

> _Essa resposta define se conseguimos conectar um agente diretamente ao seu fluxo atual — sem mudar nada no dia a dia da equipe._
> **🧑 Empresário:** Quero automação de agendamento pelo WhatsApp com confirmação automática 24 horas antes da consulta.

> **🤖 Consultor:** Excelente! Automatizar **agendamento + confirmação 24h antes** pelo WhatsApp é totalmente viável — e vai aliviar imediatamente a carga da sua recepção.

> _Antes de fechar o plano, quero explorar uma oportunidade que muitas clínicas perdem:_
> _**Vocês fazem follow-up após a consulta?**_

> _Por exemplo:_
> _- Enviam mensagem no dia seguinte perguntando se o paciente está bem?_
> _- Pedem avaliação (Google, Doctoralia)?_
> _- Relembram sobre retorno ou exames futuros?_

> _Esse pós-consulta é **ouro** para fidelização e reduzir cancelamentos futuros. Se hoje é feito manualmente (ou nem é feito), podemos automatizar com um segundo agente simples._

> _Me conta como funciona hoje?_
> **🧑 Empresário:** /fim

> **🤖 Consultor:** Pronto! Acabei de gerar seu **blueprint personalizado** com um time de 3 agentes inteligentes pensado especialmente para sua clínica:

> _1. **Agente de Agendamento WhatsApp** – permite que pacientes marquem, cancelem ou reagendem consultas diretamente pelo WhatsApp, consultando a agenda em tempo real no Nuvem._
> _2. **Coordenador de Confirmação** – envia lembrete automático 24h antes e registra respostas, reduzindo faltas sem esforço humano._
> _3. **Agente de Pós-Consulta** – cuida do follow-up após a consulta, pede avaliações e incentiva retornos, aumentando fidelização._

> _O plano começa pelo agente de **maior impacto imediato** (agendamento) e escala para fidelização — tudo integrado ao seu Nuvem e Google Calendar._

> _### O que ficou em aberto (para validação técnica futura):_
> _- Se o **Nuvem permite integração via API/webhook** (essencial para automação em tempo real)._
> _- Se você já usa ou precisará migrar para o **WhatsApp Business oficial**._
> _- Se há interesse em conectar com **Doctoralia/Google Meu Negócio** para coletar avaliações automaticamente._

> _Se quiser avançar na implementação ou tirar dúvidas sobre essas integrações, é só chamar! 🩺🤖_

### Blueprint gerado

<details>
<summary>Expandir blueprint completo</summary>

# Blueprint do Time de Agentes

## Perfil da empresa
- Segmento: saude
- Porte: pequeno (3 médicos + recepção, R$ 120k/mês)
- Modelo de negócio: clínica multiprofissional com atendimento a convênios (Unimed, Bradesco Saúde) e particular
- Dores: recepção sobrecarregada com tarefas repetitivas, pacientes ligam para confirmar/remarcar, sem automação de agendamento e confirmação

## Mapa de processos
- **agendamento**: marcação e remarcação de consultas via ligação e WhatsApp
- **confirmação**: confirmação manual de consultas pelo WhatsApp
- **atendimento**: triagem inicial e suporte pré-consulta

## Integrações detectadas
- agenda — Nuvem + Google Calendar (dados em: software Nuvem)
- whatsapp — WhatsApp Business (dados em: será configurado)
- convenio — Unimed (dados em: desconhecido)
- convenio — Bradesco Saúde (dados em: desconhecido)

## Time de agentes proposto
### Agente de Agendamento WhatsApp — Atendimento e agendamento 24/7
- Objetivo: Permitir que pacientes marquem, cancelem ou reagendem consultas diretamente pelo WhatsApp sem intervenção humana.
- Tarefas: receber solicitações de agendamento, consultar disponibilidade em tempo real no Nuvem/Google Calendar, confirmar horário com paciente, registrar dados no sistema
- Integrações: whatsapp, nuvem, google calendar
- Conversa com: Coordenador de Confirmação
### Coordenador de Confirmação — Automação de lembretes
- Objetivo: Enviar confirmação automática 24h antes da consulta e registrar resposta do paciente.
- Tarefas: ler agenda do dia seguinte, enviar mensagem de confirmação personalizada, registrar confirmação ou cancelamento, notificar recepção sobre desistências
- Integrações: whatsapp, nuvem, google calendar
- Conversa com: Agente de Agendamento WhatsApp
### Agente de Pós-Consulta — Fidelização e follow-up
- Objetivo: Aumentar satisfação e retenção com acompanhamento pós-consulta automatizado.
- Tarefas: enviar mensagem no dia seguinte à consulta, solicitar avaliação no Google ou Doctoralia, lembrar retorno ou exames pendentes, oferecer reagendamento rápido
- Integrações: whatsapp, nuvem
- Conversa com: Coordenador de Confirmação

## Roadmap
1. **Agente de Agendamento WhatsApp** — Resolve a dor principal da recepção; alto impacto com integração direta ao Nuvem e WhatsApp.
2. **Coordenador de Confirmação** — Reduz no-shows automaticamente; complementa o primeiro agente.
3. **Agente de Pós-Consulta** — Gera fidelização e novos agendamentos com esforço zero da equipe.

## Perguntas em aberto
- O software Nuvem permite integração via API ou webhook para leitura/escrita de agendas?
- Vocês usam WhatsApp Business oficial (com número fixo e API) ou será necessário migrar do WhatsApp pessoal?
- Existe interesse em integrar lembretes de retorno com prontuário eletrônico?
- Há presença em plataformas como Doctoralia ou Google Meu Negócio onde avaliações poderiam ser solicitadas?

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
| Perguntas em aberto | 5 | 5 | `██████████` | 3 perguntas documentadas |
| Integrações detectadas | 10 | 10 | `██████████` | 3 integrações |
| Profundidade da entrevista | 10 | 10 | `██████████` | 5 turnos do usuário |

### Avaliação qualitativa (LLM-as-judge)

| Critério | Nota | Barra |
|----------|-----:|-------|
| Clareza das perguntas | 9/10 | `█████████░` |
| Empatia | 8/10 | `████████░░` |
| Não-repetição | 7/10 | `███████░░░` |
| **Total** | **24/30** | |

> O consultor faz perguntas claras e bem estruturadas, alinhadas ao objetivo de entender o negócio. Demonstra empatia ao reconhecer desafios comuns e validar a dor do empresário. No entanto, há certa repetição na abordagem: pergunta múltiplas vezes sobre o fluxo de atendimento e qualificação de leads, ainda que com pequenas variações.

### ✅ Pontos positivos

- Segmento detectado corretamente: `educacao`
- Blueprint gerado e salvo com sucesso
- Time com 3 agentes propostos
- Roadmap com 3 etapas bem definidas
- 4 processos mapeados no blueprint
- 3 perguntas em aberto documentadas (boa prática)
- 3 integrações detectadas corretamente
- Entrevista aprofundada: 5 turnos do empresário

### Transcrição da entrevista

> _Olá! Seja muito bem-vindo(a). 🤝_

> _Meu nome é Orbe e sou especialista em implementação de inteligência artificial para negócios. Já ajudei dezenas de empresas brasileiras a montar times de agentes que trabalham 24 horas por dia — atendendo clientes, criando conteúdo para redes sociais, gerenciando pedidos, automatizando orçamentos e muito mais._

> _Antes de qualquer proposta, quero entender bem a sua realidade. Não existe solução pronta: o plano certo depende do que você faz, de como você opera e de onde você quer chegar._

> _Então me conta: **o que a sua empresa faz** e qual é o maior desafio que você enfrenta hoje no dia a dia?_
> **🧑 Empresário:** Tenho uma escola de idiomas. Inglês e espanhol, aulas presenciais e online pelo Zoom.

> **🤖 Consultor:** Ótimo! Você tem uma escola de idiomas com aulas presenciais e online — um modelo híbrido que está cada vez mais comum. Antes de tudo, quero entender melhor como funciona o **atendimento aos interessados** hoje:

> _- Quando alguém entra em contato com a escola (por WhatsApp, Instagram, telefone etc.), **quem responde**?_
> _- Esse atendimento é feito por você, por um funcionário específico ou por mais de uma pessoa?_
> _- E quais são as **perguntas mais repetidas** que vocês recebem? (ex: preços, horários, método de ensino, teste de nivelamento etc.)_

> _Essa primeira visão me ajuda a ver onde a IA pode aliviar a carga da sua equipe logo de cara._
> **🧑 Empresário:** Tenho dificuldade em converter leads que chegam pelo Instagram em alunos matriculados. Muitos somem.

> **🤖 Consultor:** Entendi — muitos leads chegam pelo Instagram, mas acabam sumindo antes de se matricularem. Isso é super comum em escolas de idiomas, e normalmente acontece por dois motivos principais:

> _1. **Demora ou falha no primeiro contato** (ex: resposta lenta, não agendar logo o teste/ligação)_
> _2. **Falta de acompanhamento contínuo** (ex: não reativar quem não respondeu na primeira vez)_

> _Antes de propor uma solução, preciso entender melhor seu **fluxo atual de captação e vendas**:_

> _👉 Quando alguém demonstra interesse pelo Instagram (manda mensagem, comenta, salva post etc.), **como você faz hoje para transformar esse lead em aluno?**_

> _- Você agenda um **teste de nivelamento ou uma aula experimental**?_
> _- Usa algum **formulário, link fixo na bio ou só conversa direto no direct**?_
> _- Depois do primeiro contato, **você faz follow-up** com quem não respondeu?_

> _Essa visão me ajuda a desenhar um agente que não só responda rápido, mas também **não deixe nenhum lead cair no esquecimento**._
> **🧑 Empresário:** Uso Instagram para captar alunos, WhatsApp para contato, e planilhas Google para controle de matrículas.

> **🤖 Consultor:** Valeu pela clareza! Então seu fluxo hoje é:

> _**Instagram → WhatsApp → Planilha Google**_

> _Esse modelo funciona no começo, mas como você já percebeu, **muitos leads somem no caminho** — especialmente entre o primeiro “oi” no direct e a efetiva matrícula._

> _Agora quero entender melhor o **processo de atendimento pós-contato inicial**:_

> _👉 Quando alguém manda mensagem no WhatsApp (depois de ver seu Instagram), **quem responde?**_
> _- É você mesmo(a)? Um professor? Uma recepcionista?_
> _- E quanto tempo demora, em média, para responder?_

> _Além disso:_
> _👉 Vocês têm um **roteiro ou lista de perguntas padrão** que usam para qualificar o lead? (ex: objetivo do aluno, disponibilidade, nível atual etc.)_

> _Essas respostas vão me ajudar a desenhar um agente que não só responda rápido 24/7, mas também **qualifique bem o lead antes de passar para um humano** — aumentando muito sua taxa de conversão._
> **🧑 Empresário:** Tenho 120 alunos ativos e 5 professores. Faturamento de R$ 45 mil por mês.

> **🤖 Consultor:** Com esse tamanho (120 alunos, R$ 45k/mês e 5 professores), faz todo sentido que você esteja sentindo o peso de **gerenciar tudo manualmente** — especialmente a conversão de leads, que exige atenção constante.

> _Antes de fechar o plano, preciso só confirmar mais uma coisa sobre **pós-venda e retenção**:_

> _👉 Depois que o aluno se matricula, **vocês fazem algum acompanhamento contínuo?**_
> _- Avaliam satisfação ao longo do curso?_
> _- Têm alguma estratégia para **reduzir evasão** (ex: check-in mensal, relatório de progresso)?_
> _- E quando um aluno **para de frequentar**, tentam entender o motivo ou reativá-lo?_

> _Esse ponto é crucial porque, em escolas de idiomas, **reter um aluno existente é muito mais barato (e lucrativo) do que captar um novo**. Um agente de pós-venda pode fazer essa diferença — mas quero saber se já existe algo nesse sentido hoje._
> **🧑 Empresário:** Quero um agente que qualifique os leads automaticamente e agende a aula experimental.

> **🤖 Consultor:** Pronto! Acabei de gerar e salvar seu **plano personalizado de transformação digital** com um time de agentes de IA feito sob medida para sua escola de idiomas.

> _📁 Você encontrará dois arquivos na pasta da sessão:_
> _- `blueprint.json` – versão técnica, pronta para implementação_
> _- `blueprint.md` – versão amigável, com explicação passo a passo_

> _### O que o plano entrega:_
> _✅ **Agente de Pré-Vendas (SDR)** – responde leads do Instagram/WhatsApp 24/7, qualifica por objetivo, disponibilidade e nível, e agenda automaticamente a aula experimental no seu Google Calendar_
> _✅ **Agente de Marketing de Conteúdo** – sugere e agenda posts semanais no Instagram (frases em inglês/espanhol, depoimentos, dicas) para atrair mais leads qualificados_
> _✅ **Agente de Pós-Venda** – envia check-ins mensais, coleta NPS e identifica alunos em risco de evasão antes que desistam_

> _🚀 **Roadmap sugerido**: começamos pelo Agente de Pré-Vendas (maior impacto imediato na conversão), depois Pós-Venda (reduz evasão), e por fim Marketing (alimenta o funil com mais qualidade)._

> _Se quiser ajustar algo ou entender como implantar passo a passo, é só dizer!_

### Blueprint gerado

<details>
<summary>Expandir blueprint completo</summary>

# Blueprint do Time de Agentes

## Perfil da empresa
- Segmento: educacao
- Porte: pequeno (5 professores + dono, ~R$ 45k/mês)
- Modelo de negócio: escola de idiomas com aulas presenciais e online (Zoom)
- Dores: baixa conversão de leads do Instagram, evasão de prospects, processo manual de matrícula, sem qualificação estruturada de leads

## Mapa de processos
- **captação**: leads chegam pelo Instagram e são encaminhados para WhatsApp
- **pré-vendas**: contato inicial, qualificação e agendamento de aula experimental
- **matrícula**: registro manual em planilha após aula experimental
- **pós-venda**: sem acompanhamento estruturado; risco de evasão

## Integrações detectadas
- social_media — Instagram (dados em: perfil da escola)
- whatsapp — WhatsApp Business (dados em: celular do dono ou equipe)
- spreadsheet — Planilha Google (dados em: Google Sheets (link compartilhado))

## Time de agentes proposto
### SDR - Pré-Vendas — Qualificação e agendamento de leads
- Objetivo: Converter leads do Instagram/WhatsApp em aulas experimentais agendadas, sem intervenção humana
- Tarefas: responder primeiro contato no WhatsApp, perguntar objetivo, disponibilidade e nível do aluno, mostrar horários disponíveis de aula experimental, agendar diretamente na agenda da escola, registrar lead qualificado na planilha
- Integrações: whatsapp, google sheets, google calendar
- Conversa com: Gerente de Redes Sociais, Coordenador de Pós-Venda
### Gerente de Redes Sociais — Marketing de conteúdo
- Objetivo: Manter Instagram ativo com posts que geram leads qualificados
- Tarefas: criar posts semanais (dicas, depoimentos, promoções), gerar stories interativos (quiz, enquetes), monitorar mensagens diretas e encaminhar para o SDR, testar novos formatos de anúncio orgânico
- Integrações: instagram
- Conversa com: SDR - Pré-Vendas
### Coordenador de Pós-Venda — Retenção e fidelização
- Objetivo: Reduzir evasão e aumentar satisfação dos alunos ativos
- Tarefas: enviar check-in mensal por WhatsApp, coletar feedback após 4 aulas, identificar alunos inativos e sugerir reativação, pedir depoimentos e avaliações
- Integrações: whatsapp, google sheets
- Conversa com: SDR - Pré-Vendas

## Roadmap
1. **SDR - Pré-Vendas** — Resolve a dor principal: converte leads que hoje somem; implantação simples via WhatsApp + Google Calendar
2. **Gerente de Redes Sociais** — Alimenta o funil com conteúdo contínuo, reduzindo dependência de anúncios pagos
3. **Coordenador de Pós-Venda** — Aumenta LTV dos alunos existentes e gera social proof para novos leads

## Perguntas em aberto
- A agenda de aulas experimentais está em Google Calendar ou outro sistema?
- Há formulário de inscrição prévio ou tudo é feito por conversa no WhatsApp?
- Os professores têm horários fixos para aulas experimentais ou é flexível?

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
| Mapa de processos | 10 | 10 | `██████████` | 3 processos mapeados |
| Perguntas em aberto | 5 | 5 | `██████████` | 4 perguntas documentadas |
| Integrações detectadas | 10 | 10 | `██████████` | 3 integrações |
| Profundidade da entrevista | 10 | 10 | `██████████` | 6 turnos do usuário |

### Avaliação qualitativa (LLM-as-judge)

| Critério | Nota | Barra |
|----------|-----:|-------|
| Clareza das perguntas | 8/10 | `████████░░` |
| Empatia | 9/10 | `█████████░` |
| Não-repetição | 6/10 | `██████░░░░` |
| **Total** | **23/30** | |

> O consultor demonstra alta empatia, reconhecendo claramente a dor do empresário (no-show) e adaptando o discurso ao contexto de um salão pequeno. As perguntas são claras e orientadas à solução. No entanto, há repetição significativa ao insistir três vezes na mesma pergunta sobre como é feita a confirmação de agendamento, mesmo após o cliente já ter dado informações relevantes.

### ✅ Pontos positivos

- Segmento detectado corretamente: `beleza`
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
> **🧑 Empresário:** Tenho um salão de beleza com 5 profissionais: cabelo, manicure e estética.

> **🤖 Consultor:** Opa, tudo bem? Legal saber que você tem um salão com 5 profissionais — cabelo, manicure e estética. Isso já dá pra imaginar uma operação bem movimentada!

> _Antes de mais nada, quero entender **como vocês fazem o agendamento hoje**._
> _Vocês usam algum sistema online (tipo Google Agenda, Agendor, Booksy, etc.), ou ainda é tudo por WhatsApp, ligação ou até caderno?_

> _Essa parte é crucial porque, no segmento de beleza, o agendamento mal organizado costuma gerar faltas, horários vazios e muito retrabalho — e a boa notícia é que dá pra resolver isso de forma bem leve com automação._
> **🧑 Empresário:** O maior problema é no-show. Clientes que marcam e não aparecem. Perdemos várias horas por semana.

> **🤖 Consultor:** Entendi perfeitamente — no-show é um dos maiores sangramentos em salões de beleza, e perder horas por semana com cadeira vazia dói demais, principalmente com uma equipe de 5 profissionais.

> _Vamos direto ao ponto: **como vocês fazem o agendamento hoje?**_
> _É tudo por WhatsApp? Usam algum app ou sistema online (tipo Booksy, BeOn, Google Agenda, etc.)? Ou ainda anotam em papel/caderno?_

> _Essa resposta vai me ajudar a desenhar uma solução que **confirme automaticamente os horários**, **lembre os clientes com antecedência** e até **abra espaço para remarcação fácil** — reduzindo drasticamente as faltas._
> **🧑 Empresário:** Usamos um app de agendamento chamado Booksy e WhatsApp para confirmações manuais.

> **🤖 Consultor:** Ótimo! Usar o **Booksy** já é um ótimo começo — significa que seus agendamentos estão centralizados e digitais. O gargalo hoje está na **confirmação manual pelo WhatsApp**, que consome tempo e ainda falha (já que depende de alguém lembrar de enviar mensagem a cada cliente).

> _Vamos aprofundar um pouco nisso:_
> _**Hoje, quem faz as confirmações? Quantos dias antes do horário vocês costumam confirmar? E qual é a mensagem que vocês enviam?**_

> _Essa resposta vai me ajudar a projetar um agente automático que **substitua esse passo manual** com mensagens personalizadas, no momento ideal — e até ofereça um botão para remarcar ou cancelar com um clique, reduzindo drasticamente o no-show._
> **🧑 Empresário:** Faturamos R$ 25 mil por mês. Sou eu mais 4 profissionais autônomos.

> **🤖 Consultor:** Entendi — com faturamento de R$ 25 mil/mês e você gerenciando tudo sozinho (além de atender), faz todo o sentido que a confirmação manual esteja virando um peso. E com profissionais autônomos, cada horário vago é uma perda direta de renda pra todo mundo.

> _Voltando à confirmação: **você consegue me contar como é feito esse processo hoje?**_
> _Por exemplo:_
> _- Você manda mensagem para todos os clientes do dia seguinte na noite anterior?_
> _- Costuma confirmar com 1 dia de antecedência? 2 dias?_
> _- A mensagem é algo como “Oi, tudo bem? Amanhã às 15h você tem corte com João. Confirmado?”_
> _- E se o cliente não responde… o que você faz?_

> _Esses detalhes são ouro: com eles, consigo montar um agente que **reproduza exatamente seu jeito de confirmar**, mas de forma automática, 24/7, sem você precisar lembrar._
> **🧑 Empresário:** Quero confirmação automática 48h e 2h antes pelo WhatsApp, com link para remarcar se necessário.

> **🤖 Consultor:** Perfeito! Com essa demanda clara — **confirmação automática 48h e 2h antes, com link para remarcar** — já dá pra desenhar um agente que vai resolver seu maior problema de forma elegante e sem complicação.

> _Agora, quero olhar além do atendimento:_
> _**Vocês têm Instagram ou outro canal onde mostram os trabalhos (antes/depois, dicas, promoções)?**_
> _E, depois do atendimento, **vocês pedem avaliação no Google ou incentivam o cliente a voltar (com cupom, por exemplo)?**_

> _Essas duas áreas — **atrair novos clientes** e **fidelizar os atuais** — são essenciais pra crescer sem depender só do boca a boca. E com automação, dá pra fazer isso quase de graça, mesmo com time enxuto._
> **🧑 Empresário:** /fim

> **🤖 Consultor:** Pronto! Acabei de gerar o **blueprint completo** para transformar seu salão com automação inteligente, focado em resolver o problema do **no-show** e ainda abrir caminho para **atrair mais clientes** e **fidelizar os atuais** — tudo pensado para uma operação enxuta como a sua (sem equipe administrativa).

> _### 🚀 Resumo do plano:_
> _1. **Agente de Confirmação** → Envia lembretes automáticos 48h e 2h antes pelo WhatsApp, com link direto para remarcar no Booksy. Isso sozinho pode reduzir faltas em 60-80%._
> _2. **Coordenador de Pós-Venda** → Manda mensagem após o atendimento pedindo avaliação e oferece cupom para retorno, aumentando a recorrência._
> _3. **Gerente de Redes Sociais** → Cria conteúdo simples (antes/depois, dicas) no Instagram para atrair novos clientes sem gastar com anúncios._

> _O roadmap começa justamente pelo **Agente de Confirmação**, já que resolve sua maior dor com baixa complexidade._

> _### ❓ O que ficou em aberto (para decidirmos depois, se quiser avançar):_
> _- O Booksy permite integração via API para gerar links dinâmicos de remarcação?_
> _- Vocês usam Instagram pessoal ou têm conta comercial?_
> _- Há interesse em automatizar relatórios de desempenho por profissional?_

> _Se quiser implementar isso passo a passo, posso te guiar na configuração — ou até sugerir ferramentas low-code que não exigem programador. É só dizer! 💇‍♀️✨_

### Blueprint gerado

<details>
<summary>Expandir blueprint completo</summary>

# Blueprint do Time de Agentes

## Perfil da empresa
- Segmento: beleza
- Porte: pequeno (5 pessoas, R$ 25k/mês)
- Modelo de negócio: salão com dono + 4 profissionais autônomos (cabelo, manicure, estética)
- Dores: no-show frequente, confirmação manual ineficiente, horários ociosos por faltas

## Mapa de processos
- **agendamento**: Agendamento feito via Booksy, mas confirmação e remarcação são manuais via WhatsApp
- **atendimento**: Contato inicial e suporte feitos pelo WhatsApp do dono
- **fidelizacao**: Sem processo estruturado de pós-venda ou reativação

## Integrações detectadas
- agenda_online — Booksy (dados em: conta do Booksy vinculada ao salão)
- whatsapp — WhatsApp Business (dados em: celular da recepção/dono)

## Time de agentes proposto
### Agente de Confirmação — Atendimento automatizado
- Objetivo: Reduzir no-show com lembretes automáticos e opção fácil de remarcar
- Tarefas: Enviar mensagem de confirmação 48h antes do agendamento, Enviar lembrete final 2h antes do horário, Incluir link direto para remarcar/cancelar no Booksy, Registrar respostas e atualizar status do agendamento
- Integrações: whatsapp, booksy
- Conversa com: Coordenador de Pós-Venda
### Gerente de Redes Sociais — Marketing de conteúdo
- Objetivo: Criar presença digital que atraia novos clientes com baixo custo
- Tarefas: Postar antes/depois dos serviços semanalmente, Criar stories com dicas rápidas de beleza, Destacar promoções ou horários disponíveis, Responder mensagens no Instagram
- Integrações: instagram
- Conversa com: Agente de Confirmação
### Coordenador de Pós-Venda — Fidelização
- Objetivo: Transformar clientes esporádicos em recorrentes
- Tarefas: Enviar mensagem pós-atendimento pedindo avaliação no Google, Oferecer cupom de retorno após 30-45 dias, Reativar clientes inativos com oferta especial, Coletar feedback para melhorar serviços
- Integrações: whatsapp, google reviews
- Conversa com: Agente de Confirmação

## Roadmap
1. **Agente de Confirmação** — Resolve a dor principal (no-show) com integração simples entre Booksy e WhatsApp
2. **Coordenador de Pós-Venda** — Aumenta o retorno dos clientes já atendidos, maximizando o valor de cada lead
3. **Gerente de Redes Sociais** — Gera novos leads de forma orgânica, reduzindo dependência de indicações

## Perguntas em aberto
- O Booksy permite webhook ou API para disparar links de remarcação dinâmicos?
- Há conta comercial no Instagram ou apenas perfil pessoal?
- Como é feita a divisão financeira com os profissionais autônomos? (afeta automação de relatórios futuros)
- Há interesse em coletar e analisar NPS ou métricas de satisfação?

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
| Integrações detectadas | 10 | 10 | `██████████` | 7 integrações |
| Profundidade da entrevista | 10 | 10 | `██████████` | 6 turnos do usuário |

### Avaliação qualitativa (LLM-as-judge)

| Critério | Nota | Barra |
|----------|-----:|-------|
| Clareza das perguntas | 9/10 | `█████████░` |
| Empatia | 9/10 | `█████████░` |
| Não-repetição | 7/10 | `███████░░░` |
| **Total** | **25/30** | |

> O consultor faz perguntas claras, contextualizadas e direcionadas aos pontos críticos do negócio. Demonstra empatia ao reconhecer dores reais (leads esfriando, suporte sobrecarregado) e adaptar a linguagem ao perfil do empresário. Houve leve repetição na pergunta sobre onboarding, feita duas vezes com pequenas variações, o que justifica a nota 7 em não repetição.

### ✅ Pontos positivos

- Segmento detectado corretamente: `tecnologia`
- Blueprint gerado e salvo com sucesso
- Time com 3 agentes propostos
- Roadmap com 3 etapas bem definidas
- 3 processos mapeados no blueprint
- 4 perguntas em aberto documentadas (boa prática)
- 7 integrações detectadas corretamente
- Entrevista aprofundada: 6 turnos do empresário

### Transcrição da entrevista

> _Olá! Seja muito bem-vindo(a). 🤝_

> _Meu nome é Orbe e sou especialista em implementação de inteligência artificial para negócios. Já ajudei dezenas de empresas brasileiras a montar times de agentes que trabalham 24 horas por dia — atendendo clientes, criando conteúdo para redes sociais, gerenciando pedidos, automatizando orçamentos e muito mais._

> _Antes de qualquer proposta, quero entender bem a sua realidade. Não existe solução pronta: o plano certo depende do que você faz, de como você opera e de onde você quer chegar._

> _Então me conta: **o que a sua empresa faz** e qual é o maior desafio que você enfrenta hoje no dia a dia?_
> **🧑 Empresário:** Tenho uma software house. Desenvolvemos sistemas sob medida e temos um SaaS de gestão para clínicas.

> **🤖 Consultor:** Entendi! Você tem uma software house com dois braços: um de **projetos customizados** e outro com um **SaaS de gestão voltado para clínicas**. Isso já me dá um bom norte.

> _Vamos começar pelo que costuma gerar mais dor no dia a dia:_
> _**Como vocês fazem hoje o atendimento e suporte aos clientes do SaaS?**_

> _Por exemplo:_
> _- Usam WhatsApp, e-mail, algum sistema de ticket?_
> _- Quantos clientes ativos o SaaS tem hoje?_
> _- Quais são as dúvidas ou problemas mais repetidos que eles trazem?_
> **🧑 Empresário:** Nosso funil de vendas é todo manual. Leads chegam pelo site e LinkedIn e esfriam antes de receber proposta.

> **🤖 Consultor:** Ótimo — essa informação é crítica. **Leads esfriando por falta de follow-up rápido** é uma das maiores perdas de receita em SaaS, especialmente em nichos B2B como clínicas.

> _Antes de desenhar a solução, preciso entender melhor o fluxo atual:_
> _**Vocês usam algum CRM, planilha ou ferramenta para registrar e acompanhar esses leads do site e do LinkedIn?**_

> _Por exemplo:_
> _- Tudo vai parar no WhatsApp pessoal?_
> _- Usam planilha no Google Sheets?_
> _- Já tentaram ferramentas como RD Station, HubSpot, Pipedrive?_

> _Isso vai me ajudar a propor uma automação que se encaixe na sua realidade — sem complicar o que já funciona._
> **🧑 Empresário:** Usamos Pipedrive como CRM, Slack interno, e Jira para os projetos. Suporte é por e-mail e fica sobrecarregado.

> **🤖 Consultor:** Perfeito — agora tenho um retrato mais completo:
> _- **Vendas**: leads entram, mas o funil é manual e esfria (mesmo com Pipedrive)._
> _- **Suporte**: por e-mail e sobrecarregado._
> _- **Ferramentas sólidas já em uso**: Pipedrive, Slack, Jira._

> _Vamos fechar mais uma peça importante:_
> _**Quando um cliente novo assina o SaaS, como é feito o onboarding?**_

> _Por exemplo:_
> _- Tem checklist ou tutorial?_
> _- Alguém da equipe faz chamada de boas-vindas?_
> _- Muitos clientes desistem nos primeiros dias por não entenderem o sistema?_

> _Esse momento é crucial — um onboarding fraco é uma das maiores causas de *churn* em SaaS, mesmo que o produto seja bom._
> **🧑 Empresário:** Somos 12 pessoas: 8 devs, 2 comerciais, 1 designer e eu. Faturamos R$ 180 mil por mês.

> **🤖 Consultor:** Excelente — com 12 pessoas e R$ 180k/mês, vocês têm uma base sólida, mas claramente **o gargalo está na ponta comercial e de atendimento**, não na entrega.

> _Voltando à pergunta anterior (importante para o blueprint):_
> _**Como é feito o onboarding dos clientes do SaaS hoje?**_

> _- Existe um processo estruturado?_
> _- Alguém acompanha os primeiros passos?_
> _- Vocês percebem clientes travando ou desistindo logo após a contratação?_

> _Essa resposta vai me dizer se precisamos de um **agente de sucesso do cliente** ou se podemos resolver com automações mais simples no início._
> **🧑 Empresário:** Quero automatizar a qualificação de leads e o primeiro atendimento do suporte do SaaS.

> **🤖 Consultor:** Perfeito — com esse foco, já dá para desenhar um time enxuto e de alto impacto.

> _Para acertar na automação, preciso de dois detalhes rápidos:_

> _1. **No suporte por e-mail**, quais são as **3 perguntas mais repetidas** que os clientes fazem?_
> _(Ex: "como emitir nota?", "como cadastrar novo profissional?", "esqueci minha senha?")_

> _2. **Na pré-venda**, o que vocês consideram um **lead qualificado**?_
> _(Ex: clínica com mais de 5 profissionais, já usa outro sistema, tem orçamento definido?)_

> _Com essas respostas, consigo propor agentes que realmente resolvam — sem ficar genérico._
> **🧑 Empresário:** /fim

> **🤖 Consultor:** Feito! 🎯

> _Com base no que conversamos, elaborei um **blueprint focado em alto impacto com baixa complexidade**, ideal para uma software house enxuta como a sua. O plano prioriza exatamente o que você pediu — **qualificação rápida de leads** e **primeiro atendimento do suporte** — mas também inclui um terceiro agente estratégico para evitar churn no onboarding, já que é um risco comum em SaaS B2B._

> _Os três agentes propostos são:_
> _1. **SDR Autônomo** – entra em contato com leads em minutos, qualifica e agenda demo._
> _2. **Atendente de Suporte SaaS** – resolve FAQs por e-mail sem sobrecarregar seu time._
> _3. **Coordenador de Onboarding** – garante que novos clientes não desistam nos primeiros dias._

> _O roadmap começa pelo SDR, pois é onde você perde receita hoje (leads esfriando). Depois vem o suporte (alívio operacional) e, por fim, o onboarding (crescimento sustentável)._

> _As **perguntas em aberto** estão listadas no final — respondê-las depois permitirá refinar ainda mais as automações._

> _Se quiser ajustar algo ou avançar na implementação de algum agente, é só dizer!_

### Blueprint gerado

<details>
<summary>Expandir blueprint completo</summary>

# Blueprint do Time de Agentes

## Perfil da empresa
- Segmento: tecnologia
- Porte: médio (12 funcionários, R$ 180k/mês)
- Modelo de negócio: software house com projetos customizados + SaaS B2B para clínicas
- Dores: funil de vendas manual, leads esfriando, suporte sobrecarregado

## Mapa de processos
- **pré-venda SaaS**: leads entram por site e LinkedIn, mas não são qualificados nem contatados rapidamente
- **suporte ao cliente SaaS**: atendimento por e-mail, volume alto, sem triagem automatizada
- **onboarding**: processo não detalhado, risco de churn precoce

## Integrações detectadas
- crm — Pipedrive (dados em: contas e leads no Pipedrive)
- communication — Slack (dados em: canais internos)
- project_management — Jira (dados em: projetos customizados)
- support — E-mail (suporte) (dados em: caixa de entrada de suporte)
- website — Site institucional (dados em: formulário de contato)
- social — LinkedIn (dados em: mensagens diretas)
- saas_product — SaaS de gestão para clínicas (dados em: não informado)

## Time de agentes proposto
### SDR Autônomo — Pré-vendas / Qualificação de Leads
- Objetivo: Contatar leads em minutos após o cadastro, qualificar e agendar demo com critérios claros
- Tarefas: responder formulário do site em até 5 minutos, enviar mensagem inicial no LinkedIn para leads ativos, perguntar critérios-chave (tamanho da clínica, sistema atual, orçamento), criar lead qualificado no Pipedrive com score, agendar reunião com comercial se for quente
- Integrações: Pipedrive, site, LinkedIn, Slack
- Conversa com: Closer Comercial
### Atendente de Suporte SaaS — Suporte Técnico Nível 1
- Objetivo: Resolver 70%+ dos tickets repetitivos sem passar para humano
- Tarefas: responder FAQs por e-mail (senha, cadastro, emissão de nota), encaminhar dúvidas complexas para equipe técnica via Slack, registrar solução em base de conhecimento, notificar cliente sobre resolução
- Integrações: e-mail, Slack, SaaS de gestão para clínicas
- Conversa com: Equipe de Suporte Humano
### Coordenador de Onboarding — Sucesso do Cliente / Ativação
- Objetivo: Garantir que novos clientes usem o SaaS nos primeiros 7 dias e não desistam
- Tarefas: enviar sequência automatizada de boas-vindas, detectar inatividade nos primeiros dias, agendar chamada de suporte proativo se necessário, coletar feedback inicial
- Integrações: Pipedrive, e-mail, SaaS de gestão para clínicas
- Conversa com: Atendente de Suporte SaaS, SDR Autônomo

## Roadmap
1. **SDR Autônomo** — Resolve a dor principal: leads esfriando. Alta ROI imediata com baixa complexidade.
2. **Atendente de Suporte SaaS** — Alivia a sobrecarga do time e melhora tempo de resposta.
3. **Coordenador de Onboarding** — Reduz churn precoce e aumenta LTV, após estabilizar entrada e suporte.

## Perguntas em aberto
- Quais são as 3 perguntas mais frequentes no suporte por e-mail?
- Quais critérios definem um lead qualificado para o SaaS (ex: número de profissionais, orçamento, tipo de clínica)?
- O SaaS permite integração via API para leitura de dados de uso (ex: login, configuração concluída)?
- Como é feito hoje o onboarding? Existe checklist ou tutorial?

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

### Avaliação qualitativa (LLM-as-judge)

| Critério | Nota | Barra |
|----------|-----:|-------|
| Clareza das perguntas | 9/10 | `█████████░` |
| Empatia | 10/10 | `██████████` |
| Não-repetição | 7/10 | `███████░░░` |
| **Total** | **26/30** | |

> O consultor faz perguntas claras e contextualizadas, sempre vinculadas às dores do empresário, demonstrando alta empatia e adaptação ao perfil leigo. No entanto, há leve repetição na abordagem sobre como os orçamentos são gerados (duas perguntas muito semelhantes sobre visitas técnicas e estimativas), o que reduz um pouco a nota de não repetição.

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

> **🤖 Consultor:** Opa, construtora de reformas — que legal! Esse é um segmento cheio de oportunidades pra deixar tudo mais ágil e transparente, tanto pra sua equipe quanto pros clientes.

> _Antes de mergulhar nas perguntas, quero entender melhor como você opera hoje. Vamos começar pelo **atendimento**:_

> _**Você usa WhatsApp como principal canal pra falar com clientes?**_
> _(Se sim: ele é usado só pra tirar dúvidas, ou também pra agendar visita, enviar orçamento, atualizar sobre a obra?)_

> _Me conta um pouco do dia a dia — isso me ajuda a ver onde a automação pode aliviar mais o seu time._
> **🧑 Empresário:** Orçamento é nossa maior dor. Cliente pede orçamento e a gente leva uma semana para responder. Muitos desistem.

> **🤖 Consultor:** Entendi perfeitamente — orçamento lento é um **grande** gargalo em reformas, porque o cliente geralmente está comparando várias opções e quem responde rápido leva a obra.

> _Vamos desmontar esse processo juntos. Me conta:_

> _**Hoje, quando um cliente pede um orçamento, quais passos vocês precisam seguir até conseguir entregar o valor?**_
> _(Por exemplo: agendar visita → ir no local → medir → consultar fornecedores → montar planilha → revisar com engenheiro → enviar...)_

> _Quanto mais detalhes você der, melhor consigo ver onde dá pra acelerar — ou até automatizar partes inteiras com um agente de IA._
> **🧑 Empresário:** Usamos WhatsApp para tudo, planilha Excel para custos e Google Agenda para as visitas técnicas.

> **🤖 Consultor:** Show! Agora já tenho uma boa visão do cenário: tudo roda no WhatsApp, os custos estão numa planilha e as visitas são marcadas no Google Agenda — ou seja, **muito trabalho manual** entre um pedido de orçamento e a resposta final.

> _Vamos focar na **visita técnica**, que parece ser o primeiro passo crítico:_

> _**Hoje, quando chega um pedido de orçamento no WhatsApp, como você decide se vai marcar uma visita ou tenta dar um valor logo por mensagem?**_
> _(Ex.: pergunta o tipo de reforma? Fotos? Metragem? Ou sempre agenda?)_

> _Isso é importante porque, com um bom agente de pré-atendimento, dá pra **qualificar o lead antes da visita** — e até gerar um orçamento preliminar em minutos, não em dias._
> **🧑 Empresário:** Somos 15 pessoas entre engenheiros, mestres de obra e equipe. Faturamos uns R$ 250 mil por mês.

> **🤖 Consultor:** Ótimo — com 15 pessoas e esse faturamento, vocês já têm escala suficiente pra **transformar o orçamento de gargalo em vantagem competitiva**. Imagine responder um orçamento em **2 horas** em vez de 7 dias... muitos clientes ficariam impressionados!

> _Voltando à pergunta anterior (importante pra desenhar a solução):_

> _**Quando alguém pede orçamento no WhatsApp, vocês sempre marcam visita técnica, ou às vezes conseguem dar um valor estimado só com fotos e descrição?**_
> _(Por exemplo: “vou reformar cozinha de 10m², quero trocar piso e azulejo” → daria pra calcular sem ir no local?)_

> _Essa resposta vai me ajudar a ver se dá pra criar um **agente inteligente que faz pré-orçamento automático** com base em padrões das suas planilhas — e só agenda visita quando for realmente necessário._
> **🧑 Empresário:** Os clientes reclamam que não sabem como está a obra. Ligam toda semana pedindo atualização.

> **🤖 Consultor:** Essa reclamação dos clientes é **super comum** em reformas — e também uma **grande oportunidade**. Imagine se, em vez de eles terem que ligar toda semana, recebessem um **update automático toda sexta**:
> _> “Sua obra está 60% concluída! Esta semana instalamos o piso da cozinha e começamos a marcenaria. Próxima etapa: pintura.”_

> _Isso aumenta a confiança, reduz o estresse da sua equipe e ainda evita retrabalho por mal-entendidos._

> _Agora quero entender melhor como vocês **acompanham o andamento hoje**:_

> _**Vocês usam algum método para registrar o progresso da obra?**_
> _(Por exemplo: fotos no WhatsApp com o mestre de obra, planilha com etapas, checklist impresso, ou é tudo na memória?)_

> _Essa resposta vai me ajudar a propor um agente que **coleta essas atualizações automaticamente** e transforma em mensagem clara pro cliente — sem trabalho extra pra sua equipe._
> **🧑 Empresário:** Quero agilizar os orçamentos e dar visibilidade da obra para o cliente sem minha equipe parar para responder.

> **🤖 Consultor:** Perfeito! Com essas duas metas — **orçamento rápido** e **obra transparente sem trabalho manual** — já dá pra desenhar um time de agentes que vai transformar sua operação.

> _Antes de fechar o plano, só preciso confirmar uma última peça:_

> _**Vocês têm um modelo padrão de orçamento na planilha?**_
> _(Por exemplo: itens como “m² de piso”, “ponto de elétrica”, “banheiro completo” já têm custos unitários definidos?)_

> _Se sim, consigo propor um agente que **gera orçamento automático em minutos** com base nesses dados — e até envia pro cliente pelo WhatsApp com um link bonito. Se não, a gente começa criando esse modelo primeiro (ainda assim, bem rápido)._

> _Me confirma isso?_
> **🧑 Empresário:** /fim

> **🤖 Consultor:** Pronto! Acabei de gerar seu **blueprint personalizado** com um time de 3 agentes inteligentes feitos sob medida para sua construtora:

> _1. **Agente de Pré-Orçamento** – responde em minutos, não em dias_
> _2. **Coordenador de Obras** – atualiza o cliente automaticamente sem sua equipe precisar parar_
> _3. **Gestor de Pós-Venda** – transforma clientes satisfeitos em promotores_

> _O plano começa pelo orçamento (sua maior dor hoje) e escala para transparência total da obra — tudo integrado ao WhatsApp, planilha e Google Agenda que você já usa._

> _Ficaram só 3 perguntas em aberto (listadas no relatório), mas nada que impeça de começar. Se quiser ajustar algo ou ver como implantar passo a passo, é só chamar!_

> _Boa sorte com as reformas — e prepare-se pra impressionar seus próximos clientes com velocidade e profissionalismo! 🛠️✨_

### Blueprint gerado

<details>
<summary>Expandir blueprint completo</summary>

# Blueprint do Time de Agentes

## Perfil da empresa
- Segmento: construcao
- Porte: médio (15 pessoas, R$ 250k/mês)
- Modelo de negócio: construtora especializada em reformas residenciais e comerciais, com orçamento sob demanda e execução própria
- Dores: orçamento demora cerca de uma semana, muitos clientes desistem, clientes não têm visibilidade do andamento da obra, equipe sobrecarregada respondendo atualizações repetitivas, processos manuais: WhatsApp, planilha Excel, Google Agenda

## Mapa de processos
- **atendimento_inicial**: Primeiro contato via WhatsApp, pedido de orçamento
- **orcamento**: Visita técnica, coleta de dados, cálculo em planilha, envio manual
- **gestao_obra**: Execução da reforma sem atualização estruturada ao cliente
- **comunicacao_pos_contratacao**: Clientes ligam semanalmente para saber status; equipe responde manualmente

## Integrações detectadas
- whatsapp — WhatsApp Business (dados em: celular da equipe comercial/engenheiros)
- spreadsheet — Planilha Excel de custos (dados em: computador local ou Google Sheets)
- calendar — Google Agenda (dados em: conta Google da empresa)

## Time de agentes proposto
### Agente de Pré-Orçamento — Pré-vendas e qualificação
- Objetivo: Reduzir de 7 dias para menos de 2 horas o tempo de resposta inicial ao cliente
- Tarefas: receber pedido de orçamento no WhatsApp, fazer perguntas guiadas (tipo de reforma, m², fotos), consultar base de custos unitários, gerar orçamento preliminar com link visual, agendar visita técnica só se necessário
- Integrações: whatsapp, planilha de custos, google agenda
- Conversa com: Coordenador de Obras
### Coordenador de Obras — Gestão de execução e comunicação
- Objetivo: Automatizar atualizações de obra para o cliente sem sobrecarregar a equipe
- Tarefas: receber registros diários do mestre de obra (texto/foto), classificar etapa concluída (ex: alvenaria, piso, pintura), gerar resumo semanal automático, enviar update pro cliente via WhatsApp, alertar sobre atrasos
- Integrações: whatsapp, planilha de cronograma
- Conversa com: Agente de Pré-Orçamento, Gestor de Pós-Venda
### Gestor de Pós-Venda — Fidelização e feedback
- Objetivo: Transformar clientes em promotores após entrega da obra
- Tarefas: enviar NPS 7 dias após conclusão, solicitar avaliação no Google, oferecer manutenção preventiva, reativar clientes inativos com promoção
- Integrações: whatsapp, google forms
- Conversa com: Coordenador de Obras

## Roadmap
1. **Agente de Pré-Orçamento** — Resolve a maior dor (perda de leads) com impacto imediato e baixa complexidade, usando dados já existentes na planilha
2. **Coordenador de Obras** — Elimina chamados repetitivos e aumenta percepção de profissionalismo com updates automáticos
3. **Gestor de Pós-Venda** — Gera receita recorrente e melhora reputação online após estabilizar as fases anteriores

## Perguntas em aberto
- A planilha de custos tem itens padronizados com preços unitários (ex: R$/m² de piso, R$/ponto elétrico)?
- Os mestres de obra já enviam fotos ou relatos do andamento da obra? Por qual canal?
- Há um cronograma de etapas definido por tipo de reforma (ex: cozinha = 4 semanas, etapas X, Y, Z)?

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
| Integrações detectadas | 10 | 10 | `██████████` | 5 integrações |
| Profundidade da entrevista | 10 | 10 | `██████████` | 7 turnos do usuário |

### Avaliação qualitativa (LLM-as-judge)

| Critério | Nota | Barra |
|----------|-----:|-------|
| Clareza das perguntas | 9/10 | `█████████░` |
| Empatia | 9/10 | `█████████░` |
| Não-repetição | 7/10 | `███████░░░` |
| **Total** | **25/30** | |

> O consultor faz perguntas claras e contextualizadas ao negócio do cliente, demonstrando empatia ao reconhecer desafios comuns de escritórios jurídicos. No entanto, repete a pergunta sobre captação de novos clientes duas vezes, mesmo após resposta parcial, o que reduz levemente a nota de não repetição.

### ✅ Pontos positivos

- Segmento detectado corretamente: `servicos_b2b`
- Blueprint gerado e salvo com sucesso
- Time com 3 agentes propostos
- Roadmap com 3 etapas bem definidas
- 4 processos mapeados no blueprint
- 4 perguntas em aberto documentadas (boa prática)
- 5 integrações detectadas corretamente
- Entrevista aprofundada: 7 turnos do empresário

### Transcrição da entrevista

> _Olá! Seja muito bem-vindo(a). 🤝_

> _Meu nome é Orbe e sou especialista em implementação de inteligência artificial para negócios. Já ajudei dezenas de empresas brasileiras a montar times de agentes que trabalham 24 horas por dia — atendendo clientes, criando conteúdo para redes sociais, gerenciando pedidos, automatizando orçamentos e muito mais._

> _Antes de qualquer proposta, quero entender bem a sua realidade. Não existe solução pronta: o plano certo depende do que você faz, de como você opera e de onde você quer chegar._

> _Então me conta: **o que a sua empresa faz** e qual é o maior desafio que você enfrenta hoje no dia a dia?_
> **🧑 Empresário:** Tenho um escritório de advocacia. Atendemos empresas em direito trabalhista e tributário.

> **🤖 Consultor:** Obrigado pela descrição! Escritórios de advocacia B2B têm desafios bem específicos — e boas oportunidades para automatizar o que hoje consome muito tempo da equipe jurídica com tarefas repetitivas.

> _Antes de tudo, me conta: **como vocês fazem hoje o atendimento inicial a um novo cliente ou lead?**_
> _Por exemplo: alguém entra em contato por WhatsApp, site, indicação... Como é feita essa primeira conversa, triagem e qualificação?_

> _Isso me ajuda a entender se há espaço para um agente cuidar disso 24/7 — liberando os advogados para focar no que só eles podem fazer._
> **🧑 Empresário:** Perdemos muito tempo respondendo clientes que perguntam sobre o andamento dos processos. Ligam toda semana.

> **🤖 Consultor:** Entendi perfeitamente — e é super comum em escritórios: clientes querendo atualizações frequentes, e a equipe jurídica tendo que parar o que está fazendo para dar um retorno rápido.

> _Isso já mostra duas oportunidades claras:_
> _1. **Automatizar as atualizações de andamento** (para o cliente não precisar ligar)_
> _2. **Criar um canal de atendimento dedicado** só para essas perguntas repetitivas_

> _Mas antes de desenhar isso, preciso entender melhor:_
> _**Vocês usam algum sistema hoje para acompanhar os processos?**_
> _Pode ser um software jurídico, uma planilha no Google Sheets ou Excel, ou até algo informal?_

> _Se sim, como ele funciona? Onde fica registrado o status atual de cada processo?_
> **🧑 Empresário:** Usamos o Astrea para gestão dos processos, e-mail e WhatsApp para falar com clientes, e Excel no financeiro.

> **🤖 Consultor:** Ótimo! O Astrea é uma ótima base — ele já centraliza os status dos processos, o que facilita muito a automação.

> _Agora, sobre **novos clientes**: como vocês captam e qualificam leads hoje?_
> _Por exemplo: alguém chega por indicação, site, Instagram... Como é feito o primeiro contato, a triagem e a decisão de aceitar ou não o caso?_

> _Isso me ajuda a ver se há oportunidade para um agente pré-vendas (SDR) que qualifique automaticamente novos contatos — antes mesmo de envolver um advogado._
> **🧑 Empresário:** Somos 4 advogados e 2 estagiários. Faturamos R$ 90 mil por mês.

> **🤖 Consultor:** Entendi — time enxuto, então cada minuto perdido com tarefa repetitiva impacta diretamente na capacidade de atender mais clientes ou focar em casos complexos.

> _Voltando à pergunta anterior (agora com esse contexto):_
> _**Como vocês captam e qualificam novos clientes hoje?**_

> _Por exemplo:_
> _- Têm site com formulário de contato?_
> _- Recebem indicações?_
> _- Fazem marketing em redes sociais (LinkedIn, Instagram)?_
> _- Alguém da equipe faz prospecção ativa?_

> _E quando um novo lead entra em contato (por WhatsApp, e-mail, etc.), **quem faz a primeira triagem**? Vocês têm um roteiro ou critérios para decidir se o caso é viável?_
> **🧑 Empresário:** Captação é fraca: dependemos só de indicação. Não temos presença digital nem produção de conteúdo jurídico.

> **🤖 Consultor:** Agradeço pela clareza — e é um cenário muito comum: escritórios excelentes tecnicamente, mas que dependem 100% de indicação porque nunca tiveram tempo (ou estrutura) para construir presença digital.

> _Isso abre uma **grande oportunidade**: com pouco esforço contínuo, vocês podem começar a atrair clientes qualificados sem depender só de quem indica._

> _Mas antes de propor isso, quero fechar o ciclo do **pós-venda**. Vocês fazem algum tipo de **acompanhamento após encerrar um processo ou projeto**?_
> _Por exemplo: pedem feedback, enviam relatório final, oferecem suporte contínuo?_

> _E os clientes **voltam para novos serviços**, ou a maioria dos casos é pontual?_
> **🧑 Empresário:** Quero automatizar o informe de status dos processos e melhorar a captação de novos clientes empresariais.

> **🤖 Consultor:** Perfeito — com esses dois objetivos, já dá para desenhar um plano realista e de alto impacto para o escritório.

> _Só preciso de mais um detalhe para fechar:_
> _**Como vocês gostariam de atualizar os clientes sobre o andamento dos processos?**_

> _Por exemplo:_
> _- Um resumo semanal automático por WhatsApp?_
> _- Notificação só quando houver mudança de status (ex: “petição protocolada”, “audiência marcada”)?_
> _- Um link onde o cliente possa ver o status a qualquer momento?_

> _Isso define como o agente de atendimento vai se integrar ao Astrea e entregar valor sem sobrecarregar ninguém._
> **🧑 Empresário:** /fim

> **🤖 Consultor:** Pronto! Acabei de gerar o **blueprint completo** para transformar seu escritório com agentes de IA.

> _### O que você vai receber:_
> _- **Redução imediata** nas ligações repetitivas sobre andamento de processos_
> _- **Presença digital profissional** que atrai empresas (sem depender só de indicação)_
> _- **Triagem automática** de novos contatos, protegendo o tempo dos advogados_

> _### Próximos passos sugeridos:_
> _1. **Começar pelo Agente de Atendimento Jurídico** — ele se integra ao Astrea e WhatsApp e resolve sua maior dor hoje._
> _2. Enquanto isso, validar com a equipe: *como os clientes preferem receber atualizações?* (isso ajusta o comportamento do agente)._
> _3. Depois, lançar o **Coordenador de Marketing Jurídico** com 2–3 posts por semana — já gera visibilidade._

> _O plano todo foi feito pensando em um time enxuto como o seu: **máximo de impacto com mínimo de esforço operacional**._

> _Se quiser revisar os detalhes, o arquivo `blueprint.md` está salvo na pasta da sessão — ou posso resumir qualquer parte aqui!_

> _Boa sorte, e parabéns por dar esse passo estratégico! 🚀_

### Blueprint gerado

<details>
<summary>Expandir blueprint completo</summary>

# Blueprint do Time de Agentes

## Perfil da empresa
- Segmento: servicos_b2b
- Porte: pequeno/médio (6 pessoas, R$ 90k/mês)
- Modelo de negócio: escritório de advocacia B2B especializado em direito trabalhista e tributário, com captação atual por indicação
- Dores: clientes ligam toda semana para saber andamento de processos, perda de tempo com tarefas repetitivas, captação fraca, sem presença digital

## Mapa de processos
- **atendimento_pós_venda**: respostas repetitivas sobre status de processos via WhatsApp e e-mail
- **gestão_de_processos**: acompanhamento e atualização de status no Astrea
- **captação_de_leads**: dependência exclusiva de indicação, sem marketing ativo
- **financeiro**: controle de receitas e despesas via Excel

## Integrações detectadas
- legaltech — Astrea (dados em: plataforma Astrea)
- whatsapp — WhatsApp (dados em: celular da equipe)
- email — E-mail (dados em: caixa de entrada da equipe)
- financeiro — Excel (financeiro) (dados em: arquivo local ou Google Sheets)

## Time de agentes proposto
### Agente de Atendimento Jurídico — SAC 24/7 para clientes existentes
- Objetivo: reduzir ligações e mensagens repetitivas sobre andamento de processos
- Tarefas: consultar status atual no Astrea, enviar atualizações automáticas por WhatsApp quando houver mudança, responder perguntas frequentes (prazos, documentos, audiências), encaminhar dúvidas complexas aos advogados
- Integrações: whatsapp, astrea
- Conversa com: Coordenador de Marketing Jurídico
### Coordenador de Marketing Jurídico — marketing de conteúdo e geração de leads B2B
- Objetivo: criar presença digital que atraia empresas interessadas em direito trabalhista e tributário
- Tarefas: criar posts educativos para LinkedIn e Instagram, produzir conteúdos como 'erros comuns em rescisões' ou 'como se preparar para fiscalização', gerenciar perfil profissional do escritório, capturar leads de formulários ou mensagens diretas
- Integrações: instagram, linkedin, whatsapp
- Conversa com: Agente de Atendimento Jurídico, SDR Jurídico
### SDR Jurídico (Pré-vendas) — qualificação de novos leads
- Objetivo: triagem automática de contatos interessados antes de envolver advogado
- Tarefas: receber leads do site, redes sociais ou indicações, aplicar roteiro de qualificação (tipo de empresa, problema, urgência), agendar conversa com advogado qualificado, registrar lead no Excel ou CRM simples
- Integrações: whatsapp, email, excel
- Conversa com: Coordenador de Marketing Jurídico

## Roadmap
1. **Agente de Atendimento Jurídico** — resolve a dor mais urgente (ligações repetitivas) com integração viável ao Astrea e WhatsApp
2. **Coordenador de Marketing Jurídico** — começa a gerar demanda própria com baixo esforço contínuo
3. **SDR Jurídico** — garante que leads gerados sejam convertidos sem sobrecarregar os advogados

## Perguntas em aberto
- Qual é o formato ideal de atualização de status para os clientes? (ex: notificação por mudança vs. resumo semanal)
- O Astrea permite acesso automatizado à API ou extração de dados de status dos processos?
- Há interesse em criar um site institucional ou landing page para captar leads?
- Quais critérios definem se um novo caso é viável para o escritório?

</details>

---

## Cenário: Pet Shop (fora da seed)

- **Descrição:** Pet shop com banho e tosa — segmento fora da taxonomia curada
- **Segmento esperado:** fora da seed (raciocínio livre) — deve mencionar: pet, animal
- **Segmento detectado:** `pet_shop`
- **Blueprint emitido:** ✅ Sim
- **Score:** 100/100 (100%) — A — Excelente

```
Score  [████████████████████] 100/100
```

### Pontuação por critério

| Critério | Score | Máx | Barra | Observação |
|----------|------:|----:|-------|------------|
| Segmento | 20 | 20 | `██████████` | Fora da seed — descrição livre coerente: `pet_shop` |
| Blueprint gerado | 20 | 20 | `██████████` | Emitido com sucesso |
| Agentes propostos | 15 | 15 | `██████████` | 3 agentes — equipe completa |
| Roadmap | 10 | 10 | `██████████` | 3 etapas — detalhado |
| Mapa de processos | 10 | 10 | `██████████` | 4 processos mapeados |
| Perguntas em aberto | 5 | 5 | `██████████` | 4 perguntas documentadas |
| Integrações detectadas | 10 | 10 | `██████████` | 3 integrações |
| Profundidade da entrevista | 10 | 10 | `██████████` | 6 turnos do usuário |

### Avaliação qualitativa (LLM-as-judge)

| Critério | Nota | Barra |
|----------|-----:|-------|
| Clareza das perguntas | 9/10 | `█████████░` |
| Empatia | 10/10 | `██████████` |
| Não-repetição | 10/10 | `██████████` |
| **Total** | **29/30** | |

> O consultor faz perguntas claras, específicas e contextualizadas ao negócio do entrevistado, sempre explicando por que cada informação é relevante. Demonstra alta empatia ao reconhecer as dores (sobrecarga no WhatsApp, processos manuais) e adaptar a linguagem para um empresário leigo. Não repete perguntas nem estruturas — cada bloco explora uma dimensão distinta (atendimento, estoque, marketing, pós-venda) de forma fluida e progressiva.

### ✅ Pontos positivos

- Raciocínio livre funcionou: segmento descrito como `pet_shop`
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
> **🧑 Empresário:** Tenho um pet shop com banho e tosa. Também vendemos ração e acessórios na nossa lojinha.

> **🤖 Consultor:** Entendi! Você tem um pet shop com duas frentes: **serviços** (banho e tosa) e **venda de produtos** (ração e acessórios) direto na loja física.

> _Antes de mergulhar em detalhes, quero entender melhor como funciona o **atendimento aos clientes hoje**. Por exemplo:_

> _- Como os clientes entram em contato? Só presencialmente ou também por WhatsApp, Instagram, telefone?_
> _- Quando alguém quer agendar banho ou tosa, como faz isso?_

> _Essa parte é essencial porque, em pet shops, o agendamento costuma ser uma das maiores dores — e também uma das mais fáceis de resolver com automação inteligente._
> **🧑 Empresário:** O agendamento do banho e tosa é todo pelo WhatsApp e a gente se perde. Cliente reclama da demora pra responder.

> **🤖 Consultor:** Agora ficou claro: o WhatsApp virou o coração do seu negócio — mas também virou um gargalo. Imagina se, toda vez que alguém mandasse “Quero agendar banho pro Thor”, um assistente respondesse na hora com os horários disponíveis e marcasse automaticamente na agenda da equipe? Sem sobrecarregar ninguém.

> _Mas antes de propor isso, quero entender melhor a outra parte do seu negócio: **a venda de ração e acessórios**._

> _- Vocês têm estoque controlado (em planilha, sistema, etc.) ou é tudo no “olhômetro”?_
> _- Clientes costumam perguntar por WhatsApp se tem ração X ou coleira Y em estoque?_

> _Essa informação vai me ajudar a ver se dá pra integrar produto e serviço num só fluxo — por exemplo, sugerir uma ração nova quando o cliente marca o banho._
> **🧑 Empresário:** Usamos WhatsApp, uma agenda de papel para os horários e a máquina de cartão. Nada é integrado.

> **🤖 Consultor:** Entendi perfeitamente: vocês estão rodando o negócio com **WhatsApp + papel + máquina de cartão** — ou seja, tudo na mão, sem nada conversando entre si. Isso explica a sobrecarga e os erros.

> _Agora quero olhar para o **marketing e captação de novos clientes**, porque muitos pet shops perdem oportunidades ali sem perceber:_

> _- Vocês têm Instagram ou Facebook? Postam fotos dos pets depois do banho?_
> _- Recebem clientes novos por indicação, por passar na frente da loja… ou por algum anúncio online?_

> _Essa resposta vai me ajudar a ver se dá pra transformar cada pet feliz num “anúncio vivo” — e atrair mais gente sem gastar muito._
> **🧑 Empresário:** Somos 4 pessoas: eu, minha esposa e dois banhistas. Faturamos uns R$ 20 mil por mês.

> **🤖 Consultor:** Ótimo — agora tenho um retrato claro: vocês são uma **microempresa familiar**, com 4 pessoas e faturamento de R$ 20 mil/mês, operando com processos manuais e sobrecarga no WhatsApp.

> _Vamos fechar mais uma peça importante: **pós-venda**._

> _- Depois que o pet faz banho/tosa ou compra algo, vocês costumam fazer algum tipo de acompanhamento?_
> _- Já pensaram em pedir avaliações no Google ou reativar clientes que não aparecem há um tempo?_

> _Muitos pet shops deixam isso passar, mas é justamente aí que se constrói fidelidade — e clientes que voltam todo mês sem precisar de desconto._
> **🧑 Empresário:** Queria lembrar os clientes da vacina e do banho mensal automaticamente, e parar de perder horário vazio.

> **🤖 Consultor:** Perfeito — agora tudo faz sentido. Você não só quer **responder mais rápido no WhatsApp**, mas também **preencher a agenda automaticamente** e **não depender da memória** para lembrar clientes de vacinas ou banhos mensais. Isso é ouro em um pet shop!

> _Só mais uma pergunta rápida pra fechar o diagnóstico:_

> _- Vocês já tentaram postar fotos dos pets antes/depois do banho no Instagram ou Facebook? Mesmo que esporadicamente?_

> _Se sim, como foi a resposta? Se não, há interesse em usar isso pra atrair novos clientes — sem precisar criar conteúdo todo dia?_

> _Com essa peça, consigo montar um plano completo com agentes que resolvam **atendimento, operações e marketing** de forma integrada._
> **🧑 Empresário:** /fim

> **🤖 Consultor:** Pronto! Acabei de gerar o seu **plano personalizado de transformação digital** com um time de 3 agentes inteligentes, pensado especialmente para o seu pet shop familiar de 4 pessoas e R$ 20 mil/mês de faturamento.

> _### 🧠 O que o plano resolve:_
> _1. **Acaba com a demora no WhatsApp** → respostas automáticas + agendamento em tempo real._
> _2. **Preenche horários vazios** → lembretes proativos para clientes inativos ou próximos da data do próximo banho._
> _3. **Cria presença digital sem esforço** → posts simples com “antes/depois” que atraem novos tutores da vizinhança._

> _### ⏩ Próximos passos (roadmap):_
> _1. **Comece pelo Atendente WhatsApp** — impacto imediato, implantação em dias._
> _2. **Depois, ative o Coordenador de Clientes** — para nunca mais perder um retorno._
> _3. **Por fim, o Gerente de Redes Sociais** — para crescer com marketing orgânico._

> _### ❓ O que ainda precisaria confirmar (listado no blueprint):_
> _- Vocês têm interesse em postar fotos dos pets (com autorização)?_
> _- Qual tipo de agenda digital aceitariam (ex: planilha no celular)?_
> _- Já registram vacinas ou histórico de banhos (mesmo em papel)?_
> _- Clientes perguntam por produtos via WhatsApp?_

> _Se quiser, posso te ajudar a implementar o primeiro agente (Atendente WhatsApp) passo a passo — é mais simples do que parece, e já vai aliviar a pressão da equipe._

> _Parabéns por pensar na automação! Muitos pet shops perdem anos atolados em mensagens… você está prestes a virar o jogo. 🐾_

### Blueprint gerado

<details>
<summary>Expandir blueprint completo</summary>

# Blueprint do Time de Agentes

## Perfil da empresa
- Segmento: pet_shop
- Porte: micro (4 funcionários, R$ 20k/mês)
- Modelo de negócio: serviços (banho/tosa) + varejo físico (ração/acessórios)
- Dores: demora para responder no WhatsApp, agendamento caótico com agenda de papel, horários vazios não preenchidos, sem lembrete automático para vacina ou banho mensal, processos manuais desconectados (WhatsApp, papel, máquina de cartão)

## Mapa de processos
- **atendimento_e_agendamento**: Todas as solicitações de banho/tosa e dúvidas chegam por WhatsApp; resposta lenta e sem automação.
- **operacoes_manuais**: Agenda em papel, pagamentos na máquina de cartão, sem integração entre canais.
- **fidelizacao_inexistente**: Sem follow-up pós-serviço, sem lembretes de vacina ou retorno programado.
- **marketing_nao_estruturado**: Presença digital inexistente ou esporádica; sem uso de conteúdo (antes/depois) para atrair clientes.

## Integrações detectadas
- whatsapp — WhatsApp Business (dados em: celular da equipe)
- paper_agenda — Agenda física (dados em: balcão da loja)
- payment_terminal — Máquina de cartão (dados em: física na loja)

## Time de agentes proposto
### Atendente WhatsApp — SAC + Agendamento Automático
- Objetivo: Responder instantaneamente no WhatsApp, mostrar horários disponíveis e agendar banho/tosa sem intervenção humana.
- Tarefas: responder FAQ (preço, duração, raças atendidas), exibir agenda em tempo real com base em planilha ou sistema simples, confirmar agendamento e enviar lembrete 1 dia antes, registrar nome do pet, tutor, serviço e observações
- Integrações: whatsapp, planilha Google ou agenda digital simples
- Conversa com: Coordenador de Clientes
### Coordenador de Clientes — Fidelização e Retenção
- Objetivo: Garantir que nenhum cliente suma: lembrar vacinas, banhos mensais e reativar quem está inativo.
- Tarefas: enviar lembrete automático de banho a cada 30 dias, notificar sobre vacinas com base em histórico, avisar quando há horário vago próximo ao cliente, registrar histórico de serviços por pet
- Integrações: planilha de clientes, whatsapp
- Conversa com: Atendente WhatsApp
### Gerente de Redes Sociais — Marketing de Conteúdo Local
- Objetivo: Transformar pets felizes em anúncios naturais e atrair novos clientes pela vizinhança.
- Tarefas: criar posts com fotos antes/depois do banho (com autorização), publicar stories semanais com promoções ou vagas na agenda, usar hashtags locais (#PetShop[SeuBairro]), responder comentários e mensagens do Instagram
- Integrações: instagram, smartphone
- Conversa com: Atendente WhatsApp

## Roadmap
1. **Atendente WhatsApp** — Resolve a dor principal (demora nas respostas) e já começa a estruturar os dados dos clientes e agenda.
2. **Coordenador de Clientes** — Aproveita os dados coletados pelo Atendente para preencher horários vazios e fidelizar — aumentando receita recorrente.
3. **Gerente de Redes Sociais** — Gera novos leads com baixo custo após estabilizar a operação interna.

## Perguntas em aberto
- Há interesse em usar fotos de pets (com autorização) para conteúdo no Instagram?
- Qual ferramenta de agenda digital seria aceitável (ex: Google Planilhas, Calendário, ou app simples)?
- Existe registro atual de vacinas ou histórico de banhos por pet (mesmo em papel)?
- Clientes costumam perguntar por produtos (ração, coleira) via WhatsApp?

</details>

---

## Cenário: Oficina Mecânica (fora da seed)

- **Descrição:** Oficina de manutenção automotiva — segmento fora da taxonomia curada
- **Segmento esperado:** fora da seed (raciocínio livre) — deve mencionar: mec, auto, oficina, veic, veíc, carro
- **Segmento detectado:** `automotivo - oficina mecânica`
- **Blueprint emitido:** ✅ Sim
- **Score:** 95/100 (95%) — A — Excelente

```
Score  [███████████████████░] 95/100
```

### Pontuação por critério

| Critério | Score | Máx | Barra | Observação |
|----------|------:|----:|-------|------------|
| Segmento | 20 | 20 | `██████████` | Fora da seed — descrição livre coerente: `automotivo - oficina mecânica` |
| Blueprint gerado | 20 | 20 | `██████████` | Emitido com sucesso |
| Agentes propostos | 15 | 15 | `██████████` | 3 agentes — equipe completa |
| Roadmap | 10 | 10 | `██████████` | 3 etapas — detalhado |
| Mapa de processos | 10 | 10 | `██████████` | 3 processos mapeados |
| Perguntas em aberto | 5 | 5 | `██████████` | 4 perguntas documentadas |
| Integrações detectadas | 5 | 10 | `█████░░░░░` | 1 integração — insuficiente |
| Profundidade da entrevista | 10 | 10 | `██████████` | 6 turnos do usuário |

### Avaliação qualitativa (LLM-as-judge)

| Critério | Nota | Barra |
|----------|-----:|-------|
| Clareza das perguntas | 9/10 | `█████████░` |
| Empatia | 10/10 | `██████████` |
| Não-repetição | 7/10 | `███████░░░` |
| **Total** | **26/30** | |

> O consultor faz perguntas claras e contextualizadas à realidade do empresário, demonstrando forte empatia ao reconhecer suas dores operacionais. No entanto, repete duas vezes a pergunta sobre presença digital (Instagram/Google Meu Negócio), o que reduz levemente a nota de não repetição.

### ✅ Pontos positivos

- Raciocínio livre funcionou: segmento descrito como `automotivo - oficina mecânica`
- Blueprint gerado e salvo com sucesso
- Time com 3 agentes propostos
- Roadmap com 3 etapas bem definidas
- 3 processos mapeados no blueprint
- 4 perguntas em aberto documentadas (boa prática)
- Entrevista aprofundada: 6 turnos do empresário

### ❌ Problemas encontrados

- Apenas 1 integração detectada — o empresário mencionou mais ferramentas

### Transcrição da entrevista

> _Olá! Seja muito bem-vindo(a). 🤝_

> _Meu nome é Orbe e sou especialista em implementação de inteligência artificial para negócios. Já ajudei dezenas de empresas brasileiras a montar times de agentes que trabalham 24 horas por dia — atendendo clientes, criando conteúdo para redes sociais, gerenciando pedidos, automatizando orçamentos e muito mais._

> _Antes de qualquer proposta, quero entender bem a sua realidade. Não existe solução pronta: o plano certo depende do que você faz, de como você opera e de onde você quer chegar._

> _Então me conta: **o que a sua empresa faz** e qual é o maior desafio que você enfrenta hoje no dia a dia?_
> **🧑 Empresário:** Tenho uma oficina mecânica. Fazemos revisão, troca de óleo, freios e suspensão de carros de passeio.

> **🤖 Consultor:** Entendi! Você tem uma oficina mecânica que cuida da manutenção de carros de passeio — desde revisões até serviços mais específicos como freios e suspensão.

> _Antes de mergulhar nos detalhes, me ajuda a entender melhor o tamanho e o dia a dia da operação:_

> _**Quantas pessoas trabalham na oficina hoje (incluindo você)? E qual é a média de carros atendidos por dia ou por mês?**_
> **🧑 Empresário:** O cliente liga toda hora perguntando se o carro ficou pronto. Isso interrompe os mecânicos o dia inteiro.

> **🤖 Consultor:** Essa interrupção constante é um problema clássico — e totalmente resolvível! Mecânico parando o serviço a cada 20 minutos pra atender ligação quebra o ritmo, cansa e ainda pode gerar retrabalho.

> _Antes de propor uma solução, preciso entender como vocês se comunicam com os clientes hoje:_

> _**Vocês usam WhatsApp para falar com os clientes? Ou é tudo por ligação mesmo?**_
> _E além disso: **guardam os dados dos carros e serviços em alguma planilha, sistema de oficina, ou é tudo no papel?**_
> **🧑 Empresário:** Orçamento é por WhatsApp com foto da peça. O controle dos serviços é num quadro branco e caderno.

> **🤖 Consultor:** Perfeito — agora já tenho uma boa visão do cenário:

> _- **Comunicação** via WhatsApp (com fotos de peças no orçamento)_
> _- **Controle interno** 100% manual: quadro branco e caderno_
> _- **Dor principal**: clientes ligando o tempo todo pra saber se o carro está pronto, atrapalhando os mecânicos_

> _Isso me leva a uma pergunta-chave sobre **marketing e captação de novos clientes**:_

> _**Vocês têm alguma presença digital? Tipo Instagram, Google Meu Negócio, ou até indicações regulares? Ou quase todo cliente vem por boca a boca / passa na frente da oficina?**_
> **🧑 Empresário:** Somos 6: eu, 4 mecânicos e uma moça no balcão. Faturamos R$ 70 mil por mês.

> **🤖 Consultor:** Ótimo! Com 6 pessoas e R$ 70 mil/mês, vocês já têm uma operação sólida — o que significa que pequenas melhorias de processo podem gerar ganhos reais de produtividade e satisfação (tanto da equipe quanto dos clientes).

> _Voltando à pergunta anterior, que é crucial para enxergar oportunidades:_

> _**Vocês têm presença digital? Tipo Instagram, Google Meu Negócio, ou até avaliações no Google? Ou quase todo cliente vem por indicação, passa na frente ou já é fixo?**_
> **🧑 Empresário:** Quero avisar o cliente do status do carro automaticamente e agilizar a aprovação dos orçamentos.

> **🤖 Consultor:** Entendi perfeitamente — e esses dois objetivos são **excelentes pontos de partida**:

> _1. **Avisar o cliente automaticamente** sobre o status do carro (ex: “seu carro entrou na oficina”, “já está na etapa de alinhamento”, “pronto para retirada”)_
> _2. **Agilizar a aprovação dos orçamentos** enviados por WhatsApp com foto da peça_

> _Isso já resolve a maior dor (as ligações constantes) e acelera o fechamento dos serviços._

> _Só preciso confirmar mais uma coisa antes de montar seu plano:_

> _**Vocês já usam o Google Meu Negócio? E costumam pedir avaliações dos clientes depois do serviço?**_
> _(Isso ajuda a entender se há oportunidade de reforçar reputação online — algo que atrai novos clientes sem esforço extra.)_
> **🧑 Empresário:** /fim

> **🤖 Consultor:** Pronto! Acabei de gerar seu **plano personalizado de transformação digital** com um time de agentes inteligentes feito sob medida para sua oficina mecânica.

> _### 🛠️ O que você vai resolver primeiro:_
> _1. **Parar as interrupções nos mecânicos** com atualizações automáticas de status via WhatsApp_
> _2. **Acelerar a aprovação dos orçamentos** (sem depender de ligação ou espera)_
> _3. **Substituir o quadro branco e caderno** por um controle digital simples e confiável_

> _### 👥 Seu time mínimo de agentes:_
> _- **Atendente WhatsApp**: cuida de status e orçamentos 24/7_
> _- **Coordenador de Ordens de Serviço**: digitaliza todo o fluxo interno_
> _- **Gerente de Redes Sociais**: constrói reputação online pra atrair mais clientes_

> _O plano está detalhado no arquivo `blueprint.json` (e também em `blueprint.md`, mais amigável). Incluí perguntas em aberto que seriam úteis confirmar depois — como uso do Google Meu Negócio e gestão de peças._

> _Se quiser implementar o primeiro agente (o **Atendente WhatsApp**) em menos de uma semana, é totalmente viável com o que já temos. É só me avisar!_

### Blueprint gerado

<details>
<summary>Expandir blueprint completo</summary>

# Blueprint do Time de Agentes

## Perfil da empresa
- Segmento: automotivo - oficina mecânica
- Porte: pequeno (6 funcionários, R$ 70k/mês)
- Modelo de negócio: prestação de serviços técnicos para veículos de passeio (revisão, óleo, freios, suspensão)
- Dores: interrupções constantes dos mecânicos por ligações de clientes, falta de atualização proativa sobre o status do serviço, controle manual de serviços (quadro/caderno), demora na aprovação de orçamentos

## Mapa de processos
- **atendimento**: comunicação com cliente via WhatsApp e ligações; envio de orçamento com foto da peça
- **operações**: controle manual de ordens de serviço em quadro branco e caderno
- **pós-venda**: sem follow-up estruturado; clientes ligam para saber status

## Integrações detectadas
- whatsapp — WhatsApp Business (dados em: celular do dono ou atendente)

## Time de agentes proposto
### Atendente WhatsApp — SAC 24/7 + aprovação de orçamento
- Objetivo: responder automaticamente sobre status do carro e acelerar aprovação de orçamentos com fotos de peças
- Tarefas: enviar atualizações automáticas de status (entrada, em execução, pronto), solicitar aprovação de orçamento com imagem da peça, registrar resposta do cliente (aprovado/recusado), notificar equipe interna quando orçamento for aprovado
- Integrações: whatsapp
- Conversa com: Coordenador de Ordens de Serviço
### Coordenador de Ordens de Serviço — operações
- Objetivo: digitalizar e automatizar o fluxo de ordens de serviço, substituindo quadro branco e caderno
- Tarefas: registrar entrada do veículo, atualizar etapas do serviço conforme evolução, disparar notificações de status ao Atendente WhatsApp, gerar histórico de serviços por cliente
- Integrações: planilha digital (Google Sheets ou similar), whatsapp
- Conversa com: Atendente WhatsApp
### Gerente de Redes Sociais — marketing de conteúdo
- Objetivo: criar presença digital que gere confiança e atrai novos clientes
- Tarefas: postar dicas de manutenção, mostrar antes/depois de serviços, destacar avaliações positivas, manter Google Meu Negócio atualizado
- Integrações: instagram, google meu negócio
- Conversa com: Atendente WhatsApp

## Roadmap
1. **Atendente WhatsApp** — resolve a dor principal (ligações constantes) e acelera aprovação de orçamentos com implantação simples via WhatsApp
2. **Coordenador de Ordens de Serviço** — digitaliza o controle manual, permitindo rastreamento preciso e alimentando as atualizações automáticas
3. **Gerente de Redes Sociais** — consolida reputação online e atrai novos clientes após operação estar estável

## Perguntas em aberto
- A oficina já utiliza Google Meu Negócio? Recebe avaliações no Google?
- Há interesse em pedir avaliações automaticamente após o serviço?
- Qual é a frequência de clientes novos vs. clientes fixos?
- Existe algum sistema de estoque de peças ou tudo é comprado sob demanda?

</details>

---

## Análise Global e Melhorias Sugeridas

### Problemas mais frequentes

- **[2/10 cenários]** Qualidade conversacional abaixo do esperado (não-repetição
- **[1/10 cenários]** Apenas 1 integração detectada

### Recomendações de melhoria

1. **Melhorar captura de integrações** — o `reflect` não registrou as ferramentas mencionadas. Confira o alerta de integrações vazias no resultado do `reflect`.
2. **Melhorar a condução conversacional** — o LLM-juiz apontou notas baixas em clareza, empatia ou não-repetição. Quando o empresário não responde uma pergunta, o agente deve variar a abordagem (reformular, dar exemplos diferentes ou seguir para outra área) em vez de repetir a mesma pergunta; considere instruir isso no system prompt.

---

_Relatório gerado por `scripts/eval_discovery.py` em 20260611_202746_
