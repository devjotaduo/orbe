# Relatório de Avaliação — Discovery Agent

**Data:** 20260611_192116  
**Cenários testados:** 7  
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
| Perguntas em aberto | 5 | 5 | `██████████` | 4 perguntas documentadas |
| Integrações detectadas | 10 | 10 | `██████████` | 4 integrações |
| Profundidade da entrevista | 10 | 10 | `██████████` | 7 turnos do usuário |

### ✅ Pontos positivos

- Segmento detectado corretamente: `ecommerce`
- Blueprint gerado e salvo com sucesso
- Time com 4 agentes propostos
- Roadmap com 4 etapas bem definidas
- 5 processos mapeados no blueprint
- 4 perguntas em aberto documentadas (boa prática)
- 4 integrações detectadas corretamente
- Entrevista aprofundada: 7 turnos do empresário

### Transcrição da entrevista

> _Olá! Seja muito bem-vindo(a). 🤝_

> _Meu nome é Orbe e sou especialista em implementação de inteligência artificial para negócios. Já ajudei dezenas de empresas brasileiras a montar times de agentes que trabalham 24 horas por dia — atendendo clientes, criando conteúdo para redes sociais, gerenciando pedidos, automatizando orçamentos e muito mais._

> _Antes de qualquer proposta, quero entender bem a sua realidade. Não existe solução pronta: o plano certo depende do que você faz, de como você opera e de onde você quer chegar._

> _Então me conta: **o que a sua empresa faz** e qual é o maior desafio que você enfrenta hoje no dia a dia?_
> **🧑 Empresário:** Tenho uma loja virtual de roupas femininas. Vendemos pelo Instagram e site próprio.

> **🤖 Consultor:** Opa, ótimo! Loja virtual de roupas femininas com vendas no Instagram e site próprio — segmento clássico de e-commerce, mas com muitas nuances interessantes.

> _Antes de tudo, quero entender melhor como funciona seu **atendimento hoje**:_

> _- Quando um cliente manda mensagem (no Instagram ou por outro canal), **quem responde**? É você, alguém da equipe?_
> _- Vocês usam **WhatsApp Business** também, ou só Instagram + site?_
> _- Qual o **volume médio de mensagens por dia** que vocês precisam responder?_

> _Isso me ajuda a ver se dá pra aliviar logo essa parte — que costuma consumir MUITO tempo em lojas como a sua._
> **🧑 Empresário:** O maior problema é o atendimento. Recebo mais de 100 mensagens por dia no WhatsApp e não consigo responder todas.

> **🤖 Consultor:** Entendi perfeitamente — mais de 100 mensagens por dia no WhatsApp e sem conseguir responder tudo é um fardo **imenso**, principalmente quando você está tentando vender, fechar pedidos e ainda cuidar do resto do negócio.

> _Antes de propor uma solução, preciso entender melhor **o tipo de perguntas** que chegam:_

> _- Quais são as **3 perguntas mais repetidas** que você recebe? (ex: “tem estoque?”, “quanto custa o frete?”, “qual o prazo de entrega?”)_
> _- Além do WhatsApp, os clientes também mandam mensagem no **Instagram**? Com que frequência?_
> _- Vocês têm um **catálogo digital organizado** (com fotos, descrições e preços) que poderia ser mostrado automaticamente?_

> _Essas respostas vão me ajudar a montar um atendente automático que realmente alivia sua rotina — e não só responde, mas **converte**._
> **🧑 Empresário:** Uso WhatsApp Business e uma planilha Excel para controlar os pedidos. Não tenho CRM.

> **🤖 Consultor:** Show! Agora já tenho um retrato mais completo:

> _- **Atendimento sobrecarregado** no WhatsApp (100+ mensagens/dia)_
> _- **Operação manual** com planilha Excel_
> _- **Sem CRM**, o que dificulta acompanhar pedidos e clientes_

> _Vamos agora entender melhor sua **logística e pós-venda**, áreas que costumam gerar muitas dessas mensagens repetidas:_

> _- Como vocês **entregam os pedidos**? (Correios, motoboy, retirada?)_
> _- Os clientes **perguntam muito sobre o status do pedido** depois de comprar?_
> _- Vocês fazem **follow-up após a entrega**? (ex: “chegou tudo certo?”, “pode deixar seu feedback?”)_

> _Essas respostas vão me ajudar a ver se dá pra automatizar também o **acompanhamento pós-compra** — o que reduz mensagens no WhatsApp e ainda aumenta a chance de o cliente voltar._
> **🧑 Empresário:** Faturamos em torno de R$ 30 mil por mês. Somos 3 pessoas: eu, uma assistente e uma responsável pelo estoque.

> **🤖 Consultor:** Perfeito — com R$ 30 mil/mês e uma equipe de 3 pessoas, cada minuto poupado com automação vira **tempo para crescer**.

> _Voltando à logística e pós-venda (áreas que geram muitas mensagens no WhatsApp):_

> _- Como vocês **entregam os pedidos**? (Correios, motoboy, retirada?)_
> _- Os clientes **perguntam muito sobre o status do pedido** depois de comprar?_
> _- Vocês fazem **follow-up após a entrega**? (ex: “chegou tudo certo?”, “pode deixar seu feedback?”)_

> _Essas respostas vão me ajudar a ver se dá pra automatizar também o **acompanhamento pós-compra** — o que reduz mensagens no WhatsApp e ainda aumenta a chance de o cliente voltar._
> **🧑 Empresário:** Vendo também na Shopee e no Mercado Livre. Tenho problemas com devoluções que ficam sem resposta.

> **🤖 Consultor:** Agora fechou o quebra-cabeça! Você está em **quatro canais de venda** (Instagram, site próprio, Shopee e Mercado Livre), com uma equipe pequena, e as **devoluções estão caindo no vazio** — o que pode afetar sua reputação nos marketplaces e gerar insatisfação.

> _Só mais uma pergunta-chave para eu montar um plano realista:_

> _- Vocês têm um **processo definido para devoluções/trocas**? (ex: prazo, forma de reembolso, quem analisa o produto devolvido?)_
> _- E sobre **marketing**: vocês postam conteúdo regular no Instagram? Usam anúncios pagos (Meta Ads)?_

> _Com isso, consigo propor um time de agentes que não só responde WhatsApp 24/7, mas também **organiza suas operações**, **cuida do pós-venda** e até **ajuda a atrair mais clientes** — tudo alinhado com sua realidade de R$ 30k/mês e 3 pessoas._
> **🧑 Empresário:** Meu sonho é conseguir vender enquanto durmo — automação total do atendimento e rastreio de pedidos.

> **🤖 Consultor:** Seu sonho é **100% possível** — e, na verdade, bem comum entre lojistas que estão exatamente onde você está: vendendo em múltiplos canais, com equipe enxuta, mas já gerando R$ 30k/mês. A automação certa transforma isso em um negócio que **vende mesmo enquanto você dorme**.

> _Com tudo que já conversamos, tenho elementos suficientes para montar seu **blueprint de transformação** com agentes inteligentes. Só preciso confirmar mais um detalhe rápido:_

> _👉 **Qual plataforma você usa para o site próprio?** (ex: Shopify, Tray, WooCommerce, Nuvem Shop?)_

> _Isso define como vamos integrar o catálogo, o carrinho e o rastreio — e garante que a automação funcione sem falhas._
> **🧑 Empresário:** /fim

> **🤖 Consultor:** Pronto! Seu **blueprint de transformação digital** foi gerado com base em tudo o que conversamos.

> _Ele propõe um time de **4 agentes inteligentes** que vão:_

> _1. **Respirar alívio no WhatsApp** (Atendente 24/7)_
> _2. **Unificar pedidos de todos os canais** (Instagram, site, Shopee, ML)_
> _3. **Garantir que nenhuma devolução fique sem resposta**_
> _4. **Manter seu Instagram ativo e vendendo**, mesmo nos dias corridos_

> _O plano começa pelo agente de **maior impacto e menor complexidade** — o Atendente WhatsApp — para você já sentir resultado rápido._

> _As **perguntas em aberto** (como a plataforma do seu site) são só para ajustes finos na implementação — nada que impeça você de começar._

> _Se quiser seguir com a implantação ou tirar dúvidas sobre algum agente, é só chamar! 🚀_

### Blueprint gerado

<details>
<summary>Expandir blueprint completo</summary>

# Blueprint do Time de Agentes

## Perfil da empresa
- Segmento: ecommerce
- Porte: pequeno (3 pessoas, R$ 30k/mês)
- Modelo de negócio: e-commerce de roupas femininas multicanal: Instagram, site próprio, Shopee e Mercado Livre
- Dores: atendimento lento no WhatsApp (100+ mensagens/dia), mensagens não respondidas, devoluções sem resposta, falta de automação em pedidos e rastreio, operação manual com planilha Excel

## Mapa de processos
- **atendimento**: respostas a clientes via WhatsApp, Instagram, Shopee e Mercado Livre
- **pedidos**: controle manual de pedidos em planilha Excel, sem integração entre canais
- **logistica_entrega**: entregas via Correios ou terceiros, com clientes perguntando status
- **pos_venda**: gestão de devoluções sem processo definido, sem follow-up
- **marketing**: presença no Instagram, mas sem rotina clara de conteúdo ou anúncios

## Integrações detectadas
- whatsapp — WhatsApp Business (dados em: celular do dono)
- planilha — Planilha Excel (dados em: computador local ou Google Sheets)
- marketplace — Shopee (dados em: painel do vendedor)
- marketplace — Mercado Livre (dados em: painel do vendedor)

## Time de agentes proposto
### Atendente WhatsApp — SAC 24/7
- Objetivo: responder automaticamente dúvidas frequentes e triar mensagens sem intervenção humana
- Tarefas: responder FAQ (frete, prazo, estoque, trocas), mostrar catálogo digital atualizado, encaminhar pedidos e devoluções para o Coordenador de Pedidos
- Integrações: whatsapp, catálogo digital
- Conversa com: Coordenador de Pedidos
### Coordenador de Pedidos — operações
- Objetivo: unificar e automatizar o fluxo de pedidos de todos os canais
- Tarefas: consolidar pedidos do site, Instagram, Shopee e Mercado Livre, registrar status em planilha ou sistema simples, notificar cliente sobre postagem e código de rastreio, acionar Gestor de Pós-Venda em caso de devolução
- Integrações: whatsapp, planilha, painel Shopee, painel Mercado Livre
- Conversa com: Atendente WhatsApp, Gestor de Pós-Venda
### Gestor de Pós-Venda — fidelização
- Objetivo: garantir que toda devolução seja respondida e transformar experiências em oportunidades
- Tarefas: enviar follow-up pós-entrega, receber e processar solicitações de devolução, solicitar avaliações positivas após resolução, reativar clientes inativos com cupons
- Integrações: whatsapp, planilha
- Conversa com: Coordenador de Pedidos
### Gerente de Redes Sociais — marketing de conteúdo
- Objetivo: criar presença consistente no Instagram que gera vendas contínuas
- Tarefas: publicar looks diários com link direto para produto, criar stories interativos (enquetes, lançamentos), responder comentários e mensagens públicas, replicar conteúdo para alimentar o Atendente WhatsApp
- Integrações: instagram
- Conversa com: Atendente WhatsApp

## Roadmap
1. **Atendente WhatsApp** — resolve a dor mais urgente (100+ mensagens/dia) e tem implantação rápida
2. **Coordenador de Pedidos** — centraliza operações manuais e evita pedidos perdidos entre canais
3. **Gestor de Pós-Venda** — fecha o ciclo de experiência do cliente e reduz risco em marketplaces
4. **Gerente de Redes Sociais** — alimenta o funil com conteúdo contínuo, aumentando vendas passivas

## Perguntas em aberto
- Qual plataforma é usada para o site próprio? (Shopify, Tray, WooCommerce etc.)
- Existe um catálogo digital atualizado com fotos, descrições e preços?
- Há processo formal de devolução/troca definido (prazos, reembolso, análise)?
- Os marketplaces (Shopee e Mercado Livre) permitem notificações automáticas via API ou webhook?

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
| Mapa de processos | 10 | 10 | `██████████` | 4 processos mapeados |
| Perguntas em aberto | 5 | 5 | `██████████` | 5 perguntas documentadas |
| Integrações detectadas | 10 | 10 | `██████████` | 3 integrações |
| Profundidade da entrevista | 10 | 10 | `██████████` | 6 turnos do usuário |

### ✅ Pontos positivos

- Segmento detectado corretamente: `alimentacao`
- Blueprint gerado e salvo com sucesso
- Time com 3 agentes propostos
- Roadmap com 3 etapas bem definidas
- 4 processos mapeados no blueprint
- 5 perguntas em aberto documentadas (boa prática)
- 3 integrações detectadas corretamente
- Entrevista aprofundada: 6 turnos do empresário

### Transcrição da entrevista

> _Olá! Seja muito bem-vindo(a). 🤝_

> _Meu nome é Orbe e sou especialista em implementação de inteligência artificial para negócios. Já ajudei dezenas de empresas brasileiras a montar times de agentes que trabalham 24 horas por dia — atendendo clientes, criando conteúdo para redes sociais, gerenciando pedidos, automatizando orçamentos e muito mais._

> _Antes de qualquer proposta, quero entender bem a sua realidade. Não existe solução pronta: o plano certo depende do que você faz, de como você opera e de onde você quer chegar._

> _Então me conta: **o que a sua empresa faz** e qual é o maior desafio que você enfrenta hoje no dia a dia?_
> **🧑 Empresário:** Tenho um restaurante de comida caseira. Atendo no salão e faço delivery pelo iFood.

> **🤖 Consultor:** Entendi! Você tem um restaurante de comida caseira com atendimento no salão e delivery via iFood — um modelo bem comum, mas cheio de oportunidades para se destacar.

> _Antes de tudo: **vocês também recebem pedidos ou dúvidas diretamente pelo WhatsApp?**_
> _Ou o WhatsApp é usado só para comunicação interna/outras coisas?_

> _Isso muda bastante a forma como podemos estruturar os agentes de IA pra você._
> **🧑 Empresário:** O maior problema é a gestão: pedidos do iFood chegam misturados com os do salão. Muito caos na cozinha.

> **🤖 Consultor:** Esse caos na cozinha é algo que vejo **muito** em restaurantes com salão + delivery — os pedidos chegam de fontes diferentes, sem padronização, e a equipe acaba se perdendo. Imagina se você tivesse um único fluxo claro, onde todo pedido (iFood, salão ou até WhatsApp) entrasse organizado, com prioridade e status visível?

> _Antes de propor a solução ideal, preciso entender melhor:_
> _**Hoje, como vocês registram os pedidos do salão?**_
> _É por planilha, bloco de papel, algum app específico, ou tudo “na memória” mesmo?_

> _Essa resposta vai me dizer se podemos integrar tudo num sistema simples ou se precisamos começar do zero._
> **🧑 Empresário:** Uso o iFood, WhatsApp para delivery próprio, e o sistema da operadora de cartão. Tudo separado.

> **🤖 Consultor:** Agora ficou bem claro: vocês estão operando em **três frentes simultâneas** — salão (com sistema da operadora), delivery próprio via WhatsApp e delivery pelo iFood — mas tudo está **desconectado**. Não é à toa que a cozinha vive no caos!

> _Antes de mergulhar na solução completa, quero entender uma coisa que pode abrir uma grande oportunidade:_
> _**Vocês têm Instagram ou outra rede social? Postam fotos dos pratos, promoções do dia ou stories com o movimento do restaurante?**_

> _Muitos restaurantes de comida caseira crescem muito só com um bom conteúdo visual — e isso pode ser totalmente automatizado depois._
> **🧑 Empresário:** Faturamos em torno de R$ 60 mil por mês. Temos 8 funcionários incluindo cozinha e salão.

> **🤖 Consultor:** Com R$ 60 mil/mês e 8 funcionários, vocês já têm uma operação sólida — mas claramente **esticada demais** com três canais de pedidos não integrados. Automatizar aqui não é luxo, é sobrevivência para escalar sem virar um inferno na cozinha.

> _Voltando à pergunta anterior (importante pra ver se dá pra gerar mais receita):_
> _**Vocês têm Instagram? Postam fotos dos pratos, promoções ou stories com o dia a dia do restaurante?**_

> _Se sim, com que frequência? Se não, já pensaram em fazer isso? Muitos clientes novos vêm justamente dessas redes hoje._
> **🧑 Empresário:** Quero um agente que responda clientes no WhatsApp sobre cardápio, horários e reservas automaticamente.

> **🤖 Consultor:** Perfeito! Um **agente no WhatsApp para responder cardápio, horários e reservas** é uma ótima primeira prioridade — e totalmente viável.

> _Para montar isso direito, preciso de duas informações rápidas:_

> _1. **Vocês já têm um catálogo digital do cardápio?** (tipo um PDF bonito, site simples ou até um álbum no Instagram com fotos e preços atualizados?)_
> _2. **Como fazem as reservas hoje?** Só por WhatsApp, também por telefone ou só presencial?_

> _Esses detalhes vão definir se o agente pode responder 100% sozinho ou se precisa de um passo intermediário (como criar um catálogo digital antes)._
> **🧑 Empresário:** /fim

> **🤖 Consultor:** Pronto! Com base nas informações que você compartilhou, elaborei um **plano de transformação digital com 3 agentes de IA** pensado especialmente para o seu restaurante de comida caseira.

> _### 📌 Resumo do que foi proposto:_

> _1. **Atendente WhatsApp**_
> _→ Responde automaticamente sobre cardápio, horários e reservas — exatamente o que você pediu._
> _→ Alivia sua equipe de perguntas repetitivas 24/7._

> _2. **Coordenador de Pedidos**_
> _→ Resolve o caos na cozinha unificando pedidos do iFood, WhatsApp e salão num único fluxo._
> _→ Evita erros e atrasos com notificações claras para a cozinha._

> _3. **Gerente de Redes Sociais**_
> _→ Cria conteúdo automático (fotos de pratos, promoções, stories) para atrair mais clientes._
> _→ Transforma seu Instagram numa vitrine ativa — mesmo sem tempo para postar._

> _### 🚀 Roadmap sugerido:_
> _- **1º passo**: Atendente WhatsApp (rápido, resolve sua dor imediata)_
> _- **2º passo**: Coordenador de Pedidos (acaba com o caos operacional)_
> _- **3º passo**: Gerente de Redes Sociais (cresce sua receita)_

> _### ❓ O que ficou em aberto (para refinamento futuro):_
> _- Se já existe um catálogo digital do cardápio_
> _- Como são feitas as reservas hoje_
> _- Detalhes técnicos de integração com o iFood e sistema de salão_

> _Você pode revisar o plano completo nos arquivos `blueprint.json` e `blueprint.md` gerados na pasta da sessão._

> _Se quiser avançar com a implementação ou ajustar algo, é só dizer!_

### Blueprint gerado

<details>
<summary>Expandir blueprint completo</summary>

# Blueprint do Time de Agentes

## Perfil da empresa
- Segmento: alimentacao
- Porte: pequeno (8 funcionários, R$ 60k/mês)
- Modelo de negócio: restaurante de comida caseira com salão, delivery próprio via WhatsApp e delivery via iFood
- Dores: pedidos misturados na cozinha, caos operacional por canais não integrados (iFood, WhatsApp, salão), sem automação no atendimento do WhatsApp

## Mapa de processos
- **atendimento**: dúvidas sobre cardápio, horários e reservas via WhatsApp
- **pedidos**: recebimento e consolidação de pedidos de iFood, WhatsApp e salão em canais separados
- **marketing**: presença digital não confirmada; potencial para conteúdo e catálogo digital
- **operações**: gestão manual de múltiplos canais sem integração central

## Integrações detectadas
- marketplace — iFood (dados em: painel do parceiro)
- whatsapp — WhatsApp Business (dados em: celular do dono/equipe)
- payment — Sistema da operadora de cartão (dados em: terminal ou app da operadora)

## Time de agentes proposto
### Atendente WhatsApp — SAC 24/7
- Objetivo: responder automaticamente dúvidas sobre cardápio, horários e reservas no WhatsApp
- Tarefas: responder FAQ sobre pratos e preços, informar horário de funcionamento, registrar solicitações de reserva e encaminhar para equipe
- Integrações: whatsapp, catálogo digital (a ser criado)
- Conversa com: Coordenador de Pedidos
### Coordenador de Pedidos — operações
- Objetivo: unificar e organizar todos os pedidos (iFood, WhatsApp, salão) em um único fluxo para a cozinha
- Tarefas: consolidar pedidos de todas as fontes, notificar cozinha com prioridade e detalhes, acompanhar status e avisar sobre atrasos
- Integrações: ifood, whatsapp, planilha ou sistema simples
- Conversa com: Atendente WhatsApp
### Gerente de Redes Sociais — marketing de conteúdo
- Objetivo: criar presença digital que gere pedidos e reservas espontâneas
- Tarefas: criar posts diários/semanais com pratos do dia, publicar stories com movimento e promoções, manter álbum atualizado de pratos com fotos e preços
- Integrações: instagram
- Conversa com: Atendente WhatsApp

## Roadmap
1. **Atendente WhatsApp** — resolve a demanda explícita do empresário; implantação rápida com alto impacto no atendimento
2. **Coordenador de Pedidos** — ataca a dor principal de caos na cozinha unificando os canais de pedido
3. **Gerente de Redes Sociais** — amplia alcance e gera receita adicional após estabilizar operação

## Perguntas em aberto
- Existe catálogo digital atualizado do cardápio com fotos e preços?
- Como são registradas as reservas atualmente (apenas WhatsApp, telefone ou presencial)?
- O painel do iFood permite integração via API ou webhook para leitura automática de pedidos?
- Qual sistema ou método é usado para registrar pedidos do salão (planilha, papel, app)?
- Há presença ativa no Instagram ou outra rede social?

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
| Integrações detectadas | 10 | 10 | `██████████` | 6 integrações |
| Profundidade da entrevista | 10 | 10 | `██████████` | 6 turnos do usuário |

### ✅ Pontos positivos

- Segmento detectado corretamente: `saude`
- Blueprint gerado e salvo com sucesso
- Time com 3 agentes propostos
- Roadmap com 3 etapas bem definidas
- 3 processos mapeados no blueprint
- 4 perguntas em aberto documentadas (boa prática)
- 6 integrações detectadas corretamente
- Entrevista aprofundada: 6 turnos do empresário

### Transcrição da entrevista

> _Olá! Seja muito bem-vindo(a). 🤝_

> _Meu nome é Orbe e sou especialista em implementação de inteligência artificial para negócios. Já ajudei dezenas de empresas brasileiras a montar times de agentes que trabalham 24 horas por dia — atendendo clientes, criando conteúdo para redes sociais, gerenciando pedidos, automatizando orçamentos e muito mais._

> _Antes de qualquer proposta, quero entender bem a sua realidade. Não existe solução pronta: o plano certo depende do que você faz, de como você opera e de onde você quer chegar._

> _Então me conta: **o que a sua empresa faz** e qual é o maior desafio que você enfrenta hoje no dia a dia?_
> **🧑 Empresário:** Tenho uma clínica médica com 3 médicos: clínico geral, dermatologista e ortopedista.

> **🤖 Consultor:** Obrigado pela descrição! Já tenho um bom ponto de partida com o segmento **saúde**, mas quero entender melhor como funciona a operação da sua clínica hoje para propor um plano que realmente resolva suas dores.

> _Vamos começar pelo **atendimento e agendamento**, que costumam ser críticos em clínicas:_

> _**Como os pacientes entram em contato com vocês hoje?**_
> _(Eles usam WhatsApp, ligam, marcam direto pelo Instagram, site ou outro canal?)_

> _Além disso: **vocês têm muitos pacientes que marcam e não aparecem (faltas)?**_
> **🧑 Empresário:** A recepção gasta o dia inteiro agendando e desmarcando consultas. Pacientes ligam para confirmar, remarcar.

> **🤖 Consultor:** Perfeito — já entendi que a recepção está atolada com ligações para agendar, desmarcar e confirmar consultas, tudo de forma manual.

> _Agora quero entender **qual sistema vocês usam hoje para marcar as consultas**:_
> _É uma planilha do Excel/Google Sheets? Um software de agenda médica (como o iClinic, Tasy, Agenda Simples)? Ou só caderno mesmo?_

> _Isso vai me ajudar a ver como podemos automatizar isso sem quebrar seu fluxo atual._
> **🧑 Empresário:** Usamos um software de clínica chamado Nuvem, integrado com Google Calendar. Também WhatsApp para confirmações.

> **🤖 Consultor:** Ótimo! Saber que vocês já usam o **Nuvem + Google Calendar** e o **WhatsApp** é uma ótima notícia — isso facilita muito a automação.

> _Agora, para entender melhor o volume de trabalho da recepção:_

> _**Quantas mensagens ou ligações vocês recebem por dia só sobre agendamento?**_
> _(Por exemplo: “tem horário com o ortopedista?”, “quero remarcar”, “vou faltar hoje” etc.)_

> _E aproveitando: **vocês já tentam confirmar consultas antes do dia?** Se sim, como fazem isso hoje (mensagem manual no WhatsApp, ligação)?_
> **🧑 Empresário:** Atendemos convênios Unimed e Bradesco Saúde, e particular. Faturamos R$ 120 mil por mês.

> **🤖 Consultor:** Entendi — com R$ 120 mil de faturamento e atendimento a convênios importantes, dá pra imaginar que o volume de pacientes é considerável, o que explica a sobrecarga da recepção.

> _Voltemos à pergunta anterior, que é essencial para dimensionar a automação:_

> _**Quantas mensagens ou ligações vocês recebem por dia só sobre agendamento?**_
> _(Por exemplo: “tem horário com o ortopedista?”, “quero remarcar”, “vou faltar hoje” etc.)_

> _E: **vocês já tentam confirmar consultas antes do dia?** Se sim, como fazem isso hoje (mensagem manual no WhatsApp, ligação)?_

> _Essa resposta vai me dizer exatamente onde um agente de IA pode aliviar mais o trabalho da equipe._
> **🧑 Empresário:** Quero automação de agendamento pelo WhatsApp com confirmação automática 24 horas antes da consulta.

> **🤖 Consultor:** Perfeito! Automatizar **agendamento pelo WhatsApp + confirmação 24h antes** é totalmente viável com a infraestrutura que você já tem (Nuvem + Google Calendar + WhatsApp).

> _Agora, para garantir que o plano cubra não só o que você pediu, mas também oportunidades que muitas clínicas perdem:_

> _**Vocês fazem algum tipo de follow-up depois da consulta?**_
> _Por exemplo:_
> _- Perguntar se o paciente melhorou?_
> _- Lembrar de retornar em 6 meses (especialmente dermatologia/ortopedia)?_
> _- Pedir uma avaliação no Google ou indicar a clínica?_

> _Isso é crucial para fidelizar e reduzir a dependência de novos pacientes — e pode ser automatizado junto com o agendamento._
> **🧑 Empresário:** /fim

> **🤖 Consultor:** Pronto! Acabei de gerar o **blueprint completo** para transformar sua clínica com agentes de IA.

> _### 🎯 O que você vai ganhar:_
> _1. **Agente de Agendamento WhatsApp** – seus pacientes marcam, confirmam e remarcam consultas sozinhos, 24/7, sem sobrecarregar a recepção._
> _2. **Coordenador de Pós-Venda** – recupera pacientes que poderiam se perder e aumenta retornos (especialmente importante em dermatologia e ortopedia)._
> _3. **Analista de Operações** – garante que tudo funcione em harmonia entre Nuvem, Google Calendar e WhatsApp._

> _### ⏩ Próximos passos:_
> _- Validamos se o **Nuvem permite integração para agendamento automático** (alguns sistemas só permitem leitura)._
> _- Definimos se usaremos **WhatsApp Business oficial** (recomendado para evitar bloqueios)._

> _O plano foi feito pensando no seu porte (R$ 120k/mês, 3 médicos) e na infraestrutura que você já tem — então é **realista, rápido de implantar e com ROI claro** (menos faltas + mais tempo da recepção para tarefas importantes)._

> _Se quiser revisar os detalhes, o blueprint completo está nos arquivos `blueprint.json` e `blueprint.md` na pasta da sessão._

> _Boa sorte com a clínica — e qualquer dúvida, estou por aqui!_

### Blueprint gerado

<details>
<summary>Expandir blueprint completo</summary>

# Blueprint do Time de Agentes

## Perfil da empresa
- Segmento: saude
- Porte: pequeno/médio (3 médicos + recepção, R$ 120k/mês)
- Modelo de negócio: clínica multiprofissional com convênios (Unimed, Bradesco Saúde) e particular
- Dores: sobrecarga da recepção com agendamento e remarcações, faltas de pacientes (no-show), processos manuais de confirmação

## Mapa de processos
- **agendamento**: recebimento de solicitações por ligação/WhatsApp, marcação manual no Nuvem
- **confirmação**: confirmação manual pré-consulta, sem sistema automático
- **atendimento ao paciente**: interações repetitivas sobre horários, especialidades e remarcações

## Integrações detectadas
- software_clinica — Nuvem (dados em: sistema Nuvem + Google Calendar)
- whatsapp — WhatsApp Business (dados em: celular da recepção)
- convenio — Unimed (dados em: sistema Nuvem)
- convenio — Bradesco Saúde (dados em: sistema Nuvem)

## Time de agentes proposto
### Agente de Agendamento WhatsApp — Atendimento & Agendamento Automático
- Objetivo: Permitir que pacientes marquem, confirmem e remarquem consultas pelo WhatsApp sem intervenção humana.
- Tarefas: responder perguntas sobre especialidades e horários disponíveis, buscar agenda em tempo real no Google Calendar/Nuvem, registrar agendamento diretamente no Nuvem, enviar lembrete automático 24h antes da consulta, permitir remarcação/cancelamento via WhatsApp
- Integrações: whatsapp, nuvem, google calendar
- Conversa com: Coordenador de Pós-Venda
### Coordenador de Pós-Venda — Fidelização & Retorno
- Objetivo: Reduzir perda de pacientes e aumentar retorno com follow-up automatizado pós-consulta.
- Tarefas: enviar mensagem 3 dias após consulta perguntando se melhorou, sugerir retorno preventivo (ex: dermatologia a cada 6 meses), pedir avaliação no Google ou indicação, registrar feedback no Nuvem
- Integrações: whatsapp, nuvem
- Conversa com: Agente de Agendamento WhatsApp
### Analista de Operações Clínicas — Automação & Integração
- Objetivo: Garantir sincronização entre sistemas e monitorar eficácia da automação.
- Tarefas: monitorar falhas de integração Nuvem ↔ WhatsApp, gerar relatório semanal de faltas e remarcações, ajustar regras de agendamento conforme disponibilidade dos médicos, alertar sobre picos de demanda
- Integrações: nuvem, google calendar, whatsapp
- Conversa com: Agente de Agendamento WhatsApp, Coordenador de Pós-Venda

## Roadmap
1. **Agente de Agendamento WhatsApp** — Resolve a dor principal (sobrecarga da recepção) e tem alta viabilidade técnica com as ferramentas já em uso.
2. **Coordenador de Pós-Venda** — Aumenta retenção e valor do paciente ao longo do tempo, com baixo esforço adicional.
3. **Analista de Operações Clínicas** — Garante sustentabilidade e melhoria contínua do sistema automatizado.

## Perguntas em aberto
- O software Nuvem permite integração via API para escrita de agendamentos (não só leitura)?
- A clínica tem número de WhatsApp Business oficial ou usa celular comum?
- Há interesse em captar novos pacientes por Instagram ou Google Meu Negócio?
- Como é feito hoje o controle de retorno de pacientes (ex: check-ups periódicos)?

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
| Mapa de processos | 10 | 10 | `██████████` | 5 processos mapeados |
| Perguntas em aberto | 5 | 5 | `██████████` | 3 perguntas documentadas |
| Integrações detectadas | 10 | 10 | `██████████` | 3 integrações |
| Profundidade da entrevista | 10 | 10 | `██████████` | 5 turnos do usuário |

### ✅ Pontos positivos

- Segmento detectado corretamente: `educacao`
- Blueprint gerado e salvo com sucesso
- Time com 3 agentes propostos
- Roadmap com 3 etapas bem definidas
- 5 processos mapeados no blueprint
- 3 perguntas em aberto documentadas (boa prática)
- 3 integrações detectadas corretamente
- Entrevista aprofundada: 5 turnos do empresário

### Transcrição da entrevista

> _Olá! Seja muito bem-vindo(a). 🤝_

> _Meu nome é Orbe e sou especialista em implementação de inteligência artificial para negócios. Já ajudei dezenas de empresas brasileiras a montar times de agentes que trabalham 24 horas por dia — atendendo clientes, criando conteúdo para redes sociais, gerenciando pedidos, automatizando orçamentos e muito mais._

> _Antes de qualquer proposta, quero entender bem a sua realidade. Não existe solução pronta: o plano certo depende do que você faz, de como você opera e de onde você quer chegar._

> _Então me conta: **o que a sua empresa faz** e qual é o maior desafio que você enfrenta hoje no dia a dia?_
> **🧑 Empresário:** Tenho uma escola de idiomas. Inglês e espanhol, aulas presenciais e online pelo Zoom.

> **🤖 Consultor:** Obrigado pela descrição! Escolas de idiomas têm um potencial enorme — mas também desafios bem específicos, como manter os alunos engajados e responder rápido a dúvidas de quem está considerando se matricular.

> _Antes de tudo, quero entender melhor **como você lida com o atendimento hoje**:_

> _- Quais canais você usa para falar com alunos e interessados? (WhatsApp, Instagram, e-mail, telefone?)_
> _- Quantas mensagens ou ligações você recebe por dia, em média?_
> _- Quais são as perguntas que mais se repetem?_

> _Essa parte é crítica porque, muitas vezes, o tempo da equipe acaba sendo consumido respondendo as mesmas coisas várias vezes — e isso pode ser totalmente automatizado._
> **🧑 Empresário:** Tenho dificuldade em converter leads que chegam pelo Instagram em alunos matriculados. Muitos somem.

> **🤖 Consultor:** Entendi perfeitamente — e essa é uma dor **muito comum** em escolas de idiomas. O Instagram traz leads quentes, mas se não há um acompanhamento rápido e estruturado, eles simplesmente somem.

> _Antes de propor soluções, preciso entender melhor **como você capta e acompanha esses leads hoje**:_

> _1. Quando alguém demonstra interesse no Instagram (por mensagem direta ou comentário), como você normalmente prossegue?_
> _2. Você tem algum tipo de **funil de vendas** (ex.: resposta rápida → agendamento de aula experimental → follow-up)?_
> _3. Usa alguma ferramenta para registrar esses contatos (planilha, CRM, bloco de notas)?_

> _Essas respostas vão me ajudar a desenhar um time de agentes que não só responda rápido, mas também **guie o lead até a matrícula** — sem depender só da sua memória ou disponibilidade._
> **🧑 Empresário:** Uso Instagram para captar alunos, WhatsApp para contato, e planilhas Google para controle de matrículas.

> **🤖 Consultor:** Ótimo — agora já tenho uma visão clara do seu fluxo: **Instagram atrai**, **WhatsApp conversa**, e **planilha registra**. O problema é que, entre um passo e outro, muitos leads caem no esquecimento, especialmente se não há um follow-up rápido e consistente.

> _Vamos agora olhar para **o pós-venda e a retenção**, outra área crítica em escolas de idiomas:_

> _- Depois que o aluno se matricula, você faz algum tipo de **acompanhamento periódico** (ex.: “como está achando as aulas?”)?_
> _- Tem alguma estratégia para **reduzir a evasão** (alunos que param de frequentar)?_
> _- Pede **avaliações ou indicações**? Por exemplo, no Google ou diretamente por mensagem?_

> _Muitas escolas focam só na captação, mas **manter um aluno custa muito menos do que conquistar um novo** — e aí entra uma grande oportunidade com agentes inteligentes._
> **🧑 Empresário:** Tenho 120 alunos ativos e 5 professores. Faturamento de R$ 45 mil por mês.

> **🤖 Consultor:** Com base nas informações que você já compartilhou, já consigo montar um **blueprint realista e de alto impacto** para sua escola — focado em resolver a conversão de leads, melhorar o atendimento e reduzir a evasão, tudo com um time de agentes que se integra ao seu fluxo atual (Instagram, WhatsApp e planilha).

> _Mas antes de fechar, só mais uma pergunta rápida para garantir que o plano cubra tudo:_

> _**Você oferece aula experimental ou teste grátis?**_
> _Se sim: como agenda e acompanha essas aulas hoje?_

> _Essa etapa é frequentemente o “gatilho” da matrícula — e automatizá-la pode dobrar sua conversão._
> **🧑 Empresário:** Quero um agente que qualifique os leads automaticamente e agende a aula experimental.

> **🤖 Consultor:** Pronto! Acabei de gerar um **plano completo e realista** para sua escola de idiomas, com foco no que você mais precisa: **converter leads do Instagram em alunos matriculados** — sem sobrecarregar você ou sua equipe.

> _### 🎯 O que o plano entrega:_
> _1. **Atendente WhatsApp 24/7** – responde dúvidas repetitivas (preços, horários, idiomas) e já filtra quem está realmente interessado._
> _2. **Agente de Pré-Vendas (SDR)** – qualifica o lead automaticamente e agenda a **aula experimental** no melhor horário disponível._
> _3. **Coordenador de Matrículas** – cuida do pós-aula, registra a matrícula e faz follow-up para **evitar evasão**._

> _Tudo integrado ao seu fluxo atual: **Instagram → WhatsApp → Planilha Google**. Nada de sistema caro ou complicado._

> _### ▶️ Próximos passos:_
> _- Começamos pelo **Atendente WhatsApp**, pois ele já alivia sua carga imediatamente e prepara o terreno para os outros agentes._
> _- Depois, implantamos o **SDR**, que vai resolver diretamente o problema dos leads que somem._
> _- Por fim, o **Coordenador de Matrículas** fecha o ciclo, transformando experimentos em alunos fiéis._

> _Os arquivos detalhados (`blueprint.json` e `blueprint.md`) já foram salvos com todo o escopo técnico, tarefas e integrações._

> _Se quiser, posso agora te mostrar **exatamente como seria a primeira conversa entre um lead e o Atendente WhatsApp** — pra você ver na prática como isso funciona. Quer?_

### Blueprint gerado

<details>
<summary>Expandir blueprint completo</summary>

# Blueprint do Time de Agentes

## Perfil da empresa
- Segmento: educacao
- Porte: pequeno (120 alunos, 5 professores, R$45k/mês)
- Modelo de negócio: escola de idiomas com aulas presenciais e online (Zoom)
- Dores: dificuldade em converter leads do Instagram, evasão de prospects, processo manual de acompanhamento, sem qualificação automatizada de leads

## Mapa de processos
- **captação**: leads chegam pelo Instagram e precisam ser qualificados rapidamente
- **pré-venda**: agendamento e follow-up de aula experimental para conversão
- **atendimento ao aluno**: dúvidas sobre horários, professores, cancelamentos, etc.
- **operações**: controle manual de matrículas em planilha, sem CRM
- **retenção**: sem acompanhamento estruturado pós-matrícula, risco de evasão

## Integrações detectadas
- social_media — Instagram (dados em: perfil da escola)
- whatsapp — WhatsApp Business (dados em: celular do dono ou equipe)
- spreadsheet — Google Sheets (dados em: link compartilhado)
- video_conference — Zoom (dados em: conta da escola)

## Time de agentes proposto
### SDR - Pré-Vendas — Qualificação e Agendamento
- Objetivo: Converter leads do Instagram em aulas experimentais agendadas, sem intervenção humana
- Tarefas: receber leads do Instagram via WhatsApp, qualificar interesse (idioma, nível, disponibilidade), mostrar horários disponíveis para aula experimental, agendar automaticamente no Google Calendar, enviar lembrete 1h antes da aula
- Integrações: whatsapp, instagram, google calendar, google sheets
- Conversa com: Atendente WhatsApp, Coordenador de Matrículas
### Atendente WhatsApp — SAC 24/7
- Objetivo: Responder dúvidas frequentes de alunos e prospects sem sobrecarregar a equipe
- Tarefas: responder FAQ (valores, horários, idiomas, professores), encaminhar leads qualificados para o SDR, avisar sobre feriados ou mudanças de aula, coletar feedback pós-aula experimental
- Integrações: whatsapp, google sheets
- Conversa com: SDR - Pré-Vendas
### Coordenador de Matrículas — Operações & Retenção
- Objetivo: Automatizar registro de matrículas e reduzir evasão com follow-up estruturado
- Tarefas: registrar matrícula após aula experimental, atualizar status do lead na planilha, enviar pesquisa de satisfação após 2 semanas, acionar aluno inativo há 14 dias, oferecer cupom de indicação
- Integrações: whatsapp, google sheets
- Conversa com: SDR - Pré-Vendas

## Roadmap
1. **Atendente WhatsApp** — Resolve dúvidas repetitivas e filtra leads 24/7 — base para os demais agentes
2. **SDR - Pré-Vendas** — Ataca diretamente a dor principal: conversão de leads em aulas agendadas
3. **Coordenador de Matrículas** — Fechamento do ciclo: transforma experimento em matrícula e reduz evasão

## Perguntas em aberto
- A planilha de matrículas tem colunas padronizadas (nome, idioma, status, data de início)?
- Há disponibilidade fixa dos professores para aulas experimentais (ex.: seg/qua 18h)?
- O perfil do Instagram permite salvar mensagens em pastas (ex.: 'Interessados')?

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
| Perguntas em aberto | 5 | 5 | `██████████` | 3 perguntas documentadas |
| Integrações detectadas | 10 | 10 | `██████████` | 2 integrações |
| Profundidade da entrevista | 10 | 10 | `██████████` | 6 turnos do usuário |

### ✅ Pontos positivos

- Segmento detectado corretamente: `beleza`
- Blueprint gerado e salvo com sucesso
- Time com 3 agentes propostos
- Roadmap com 3 etapas bem definidas
- 4 processos mapeados no blueprint
- 3 perguntas em aberto documentadas (boa prática)
- 2 integrações detectadas corretamente
- Entrevista aprofundada: 6 turnos do empresário

### Transcrição da entrevista

> _Olá! Seja muito bem-vindo(a). 🤝_

> _Meu nome é Orbe e sou especialista em implementação de inteligência artificial para negócios. Já ajudei dezenas de empresas brasileiras a montar times de agentes que trabalham 24 horas por dia — atendendo clientes, criando conteúdo para redes sociais, gerenciando pedidos, automatizando orçamentos e muito mais._

> _Antes de qualquer proposta, quero entender bem a sua realidade. Não existe solução pronta: o plano certo depende do que você faz, de como você opera e de onde você quer chegar._

> _Então me conta: **o que a sua empresa faz** e qual é o maior desafio que você enfrenta hoje no dia a dia?_
> **🧑 Empresário:** Tenho um salão de beleza com 5 profissionais: cabelo, manicure e estética.

> **🤖 Consultor:** Opa, tudo bem? Legal saber que você tem um salão com uma equipe completa — cabelo, manicure e estética já cobre um bom leque de serviços!

> _Antes de mergulhar em soluções, quero entender melhor como funciona hoje o **atendimento e agendamento** no seu dia a dia. Me conta:_

> _**Como os clientes marcam horário com vocês hoje?**_
> _É por WhatsApp? Telefone? Presencialmente? Vocês usam algum sistema de agenda online (como MindBody, Agendor, Google Agenda) ou ainda é tudo em papel/caderno?_

> _Essa parte é crítica porque, na maioria dos salões, o maior gargalo está justamente aí: horários vazios por falta de confirmação, clientes esquecendo do compromisso ou dificuldade de visualizar a disponibilidade em tempo real._

> _Fico no aguardo! 😊_
> **🧑 Empresário:** O maior problema é no-show. Clientes que marcam e não aparecem. Perdemos várias horas por semana.

> **🤖 Consultor:** Entendi perfeitamente — no-show é um dos maiores vilões de salões como o seu. Horas paradas que poderiam estar gerando receita.

> _Antes de propor qualquer solução, preciso entender **como vocês fazem hoje a confirmação dos agendamentos**:_

> _Vocês mandam alguma mensagem ou ligam para confirmar o horário antes do dia?_
> _Se sim: quando (1 dia antes? 2 horas antes?) e por qual canal (WhatsApp, ligação)?_
> _Se não: os clientes recebem algum lembrete automático ou tudo depende da memória deles?_

> _Essa resposta vai me ajudar a desenhar um sistema que reduza drasticamente as faltas — sem sobrecarregar sua equipe._
> **🧑 Empresário:** Usamos um app de agendamento chamado Booksy e WhatsApp para confirmações manuais.

> **🤖 Consultor:** Ótimo — já usam o **Booksy**, que é uma ótima base! E fazem confirmações manuais pelo WhatsApp, mas mesmo assim os no-shows persistem. Isso é super comum: confirmar manualmente é trabalhoso e, muitas vezes, acontece tarde demais ou acaba esquecido em dias corridos.

> _Me conta só mais um detalhe sobre essa **confirmação manual**:_

> _- **Quem na equipe faz isso?** (você, uma recepcionista, as profissionais?)_
> _- **Com quantas horas ou dias de antecedência costumam confirmar?**_
> _- E quando o cliente **não responde** à mensagem de confirmação — o que vocês fazem?_

> _Essa resposta vai me ajudar a projetar um agente que automatize justamente esse ponto crítico: garantir que o cliente confirme com antecedência suficiente para liberar o horário caso não compareça._
> **🧑 Empresário:** Faturamos R$ 25 mil por mês. Sou eu mais 4 profissionais autônomos.

> **🤖 Consultor:** Agora fez total sentido! Com uma estrutura enxuta — você cuidando de tudo e mais 4 profissionais autônomas —, não dá pra ficar lembrando de confirmar cada horário manualmente. E se esquecer um ou dois, já vira prejuízo.

> _Vamos focar na **confirmação automática**, que é a chave contra o no-show. Só preciso de mais uma peça:_

> _**Você já testou usar os lembretes automáticos do próprio Booksy?**_
> _Se sim: funcionou? Se não: por quê (não sabia que tinha, não confia, não gosta do formato)?_

> _Isso vai me ajudar a decidir se integramos com o Booksy diretamente ou criamos um fluxo paralelo via WhatsApp — o canal que seus clientes já usam e respondem._
> **🧑 Empresário:** Quero confirmação automática 48h e 2h antes pelo WhatsApp, com link para remarcar se necessário.

> **🤖 Consultor:** Perfeito! Confirmação automática com **48h e 2h de antecedência** + **link para remarcar** é exatamente o que reduz no-show em até 80% nos salões que implementamos isso.

> _Só preciso confirmar uma última coisa sobre o **Booksy**:_

> _**Você sabe se o Booksy gera um link público de reagendamento por cliente?**_
> _(Exemplo: um link único que, ao ser clicado, mostra só os horários disponíveis daquela profissional e permite mudar o agendamento sem precisar falar com ninguém.)_

> _Se sim, conseguimos usar esse link direto nas mensagens automáticas._
> _Se não, podemos criar um fluxo alternativo (ainda simples) usando um formulário ou landing page leve._

> _Me conta isso e já fechamos o plano! 💡_
> **🧑 Empresário:** /fim

> **🤖 Consultor:** Pronto! Acabei de gerar o seu **blueprint personalizado** com um time de 3 agentes inteligentes pensado especialmente para o seu salão:

> _1. **Agente de Confirmação e No-Show** – vai acabar com as horas perdidas, confirmando automaticamente 48h e 2h antes pelo WhatsApp e liberando horários não confirmados._
> _2. **Agente de Atendimento Inicial** – responde dúvidas frequentes (preços, serviços, localização) e direciona para o agendamento, sem você precisar ficar colado no celular._
> _3. **Agente de Fidelização** – reativa quem faltou com um cupom simpático e lembra clientes de voltarem na hora certa (ex: unhas a cada 3 semanas)._

> _O plano começa justamente pelo **Agente de Confirmação**, porque é ele que resolve sua maior dor hoje — e usa as ferramentas que você já tem (Booksy + WhatsApp)._

> _### O que ainda precisaria confirmar (listado como perguntas em aberto):_
> _- Se o Booksy gera link público de reagendamento por cliente._
> _- Se permite integração automática (API/webhook) para liberar horários._
> _- Qual é sua taxa atual de no-show (% dos agendamentos que viram falta)._

> _Se quiser avançar na implementação ou tirar dúvidas sobre algum agente, é só chamar! 💇‍♀️✨_

### Blueprint gerado

<details>
<summary>Expandir blueprint completo</summary>

# Blueprint do Time de Agentes

## Perfil da empresa
- Segmento: beleza
- Porte: micro (5 pessoas, R$ 25k/mês)
- Modelo de negócio: salão de beleza com profissionais autônomos
- Dores: no-show de clientes, horários ociosos por faltas, confirmação manual ineficaz, operação enxuta sem apoio administrativo

## Mapa de processos
- **agendamento**: Clientes marcam via Booksy; horários gerenciados na plataforma.
- **confirmacao**: Confirmação manual via WhatsApp feita pelo dono, mas inconsistente.
- **atendimento**: Atendimento presencial pelos profissionais autônomos.
- **remarcacao**: Processo de remarcar não automatizado; depende de contato direto.

## Integrações detectadas
- agenda_online — Booksy (dados em: plataforma Booksy)
- whatsapp — WhatsApp Business (dados em: celular do dono)

## Time de agentes proposto
### Agente de Confirmação e No-Show — Operações / Atendimento
- Objetivo: Reduzir no-shows com confirmações automáticas em dois momentos (48h e 2h antes) e permitir remarcação fácil.
- Tarefas: Enviar mensagem automática 48h antes do agendamento pedindo confirmação, Enviar lembrete final 2h antes com link para remarcar, Liberar automaticamente o horário se cliente não confirmar até 1h antes, Notificar a profissional sobre cancelamento ou confirmação
- Integrações: whatsapp, booksy
- Conversa com: Agente de Fidelização
### Agente de Atendimento Inicial — Atendimento
- Objetivo: Responder dúvidas frequentes e direcionar para agendamento quando relevante.
- Tarefas: Responder FAQ: preços, serviços, localização, horários, Enviar link do Booksy para agendamento, Coletar nome e serviço desejado para pré-agendamento
- Integrações: whatsapp
- Conversa com: Agente de Confirmação e No-Show
### Agente de Fidelização — Pós-venda
- Objetivo: Reativar clientes que faltaram e incentivar retorno após atendimento.
- Tarefas: Enviar mensagem 1 dia após falta convidando para remarcar com cupom, Solicitar avaliação após atendimento, Enviar lembrete de retorno com base na periodicidade do serviço (ex: 21 dias para unhas)
- Integrações: whatsapp
- Conversa com: Agente de Confirmação e No-Show

## Roadmap
1. **Agente de Confirmação e No-Show** — Resolve a dor principal (perda de horas) com impacto imediato e uso de ferramentas já existentes.
2. **Agente de Atendimento Inicial** — Reduz trabalho manual de responder mensagens repetidas e gera mais agendamentos qualificados.
3. **Agente de Fidelização** — Transforma faltas em novas oportunidades e aumenta a recorrência, essencial em salões com profissionais autônomos.

## Perguntas em aberto
- O Booksy permite geração de link público de reagendamento por cliente?
- Há permissão para integrar o Booksy via API ou webhook para liberação automática de horários?
- Qual é a taxa atual de no-show (% de agendamentos perdidos)?

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
| Integrações detectadas | 10 | 10 | `██████████` | 6 integrações |
| Profundidade da entrevista | 10 | 10 | `██████████` | 6 turnos do usuário |

### ✅ Pontos positivos

- Segmento detectado corretamente: `tecnologia`
- Blueprint gerado e salvo com sucesso
- Time com 3 agentes propostos
- Roadmap com 3 etapas bem definidas
- 3 processos mapeados no blueprint
- 4 perguntas em aberto documentadas (boa prática)
- 6 integrações detectadas corretamente
- Entrevista aprofundada: 6 turnos do empresário

### Transcrição da entrevista

> _Olá! Seja muito bem-vindo(a). 🤝_

> _Meu nome é Orbe e sou especialista em implementação de inteligência artificial para negócios. Já ajudei dezenas de empresas brasileiras a montar times de agentes que trabalham 24 horas por dia — atendendo clientes, criando conteúdo para redes sociais, gerenciando pedidos, automatizando orçamentos e muito mais._

> _Antes de qualquer proposta, quero entender bem a sua realidade. Não existe solução pronta: o plano certo depende do que você faz, de como você opera e de onde você quer chegar._

> _Então me conta: **o que a sua empresa faz** e qual é o maior desafio que você enfrenta hoje no dia a dia?_
> **🧑 Empresário:** Tenho uma software house. Desenvolvemos sistemas sob medida e temos um SaaS de gestão para clínicas.

> **🤖 Consultor:** Opa, software house com SaaS próprio — que legal! Isso muda bastante o jogo, porque vocês têm **dois modelos de negócio rodando ao mesmo tempo**:

> _1. **Projetos customizados** (venda única, escopo variável)_
> _2. **SaaS para clínicas** (receita recorrente, precisa de retenção)_

> _Antes de mergulhar nas dores específicas, quero entender melhor como funciona hoje o **atendimento e vendas** dos dois lados. Me conta:_

> _**Quando um lead novo entra (seja para um sistema sob medida ou para testar o SaaS), por quais canais ele chega e como vocês respondem hoje?**_
> _(ex: WhatsApp, site, indicação, Instagram?)_
> **🧑 Empresário:** Nosso funil de vendas é todo manual. Leads chegam pelo site e LinkedIn e esfriam antes de receber proposta.

> **🤖 Consultor:** Entendi — leads entram, mas o time não consegue dar seguimento rápido o suficiente, e eles esfriam. Isso é super comum em software houses com dois modelos (projetos + SaaS), porque a atenção se divide.

> _Agora quero entender melhor **o lado do SaaS**, já que ele tem dinâmicas próprias de retenção e suporte:_

> _**Como vocês fazem hoje o atendimento e suporte para os clientes do SaaS de gestão para clínicas?**_
> _(ex: respondem por WhatsApp? Têm sistema de tickets? Usam e-mail? Quantas clínicas estão ativas?)_
> **🧑 Empresário:** Usamos Pipedrive como CRM, Slack interno, e Jira para os projetos. Suporte é por e-mail e fica sobrecarregado.

> **🤖 Consultor:** Ótimo — agora já vejo claramente **três frentes críticas**:
> _1. **Pré-vendas** (leads esfriando)_
> _2. **Suporte** (sobrecarregado por e-mail)_
> _3. **Operações** (CRM, Jira e Slack sem automação entre si)_

> _Antes de propor agentes, preciso entender uma peça-chave do seu SaaS:_

> _**Vocês têm um processo de onboarding para novas clínicas que assinam o SaaS?**_
> _Ou seja: quando uma clínica contrata, como vocês ajudam ela a configurar, treinar e começar a usar o sistema? Isso é feito manualmente? Quantos dias leva?_
> **🧑 Empresário:** Somos 12 pessoas: 8 devs, 2 comerciais, 1 designer e eu. Faturamos R$ 180 mil por mês.

> **🤖 Consultor:** Perfeito — com esse tamanho e faturamento, dá pra implantar automações de alto impacto sem complicar demais.

> _Volto à pergunta anterior, porque ela é crucial para o SaaS:_

> _**Vocês têm um processo de onboarding para novas clínicas que assinam o SaaS?**_
> _Ou seja: quando uma clínica contrata, como vocês ajudam ela a configurar, treinar e começar a usar o sistema? Isso é feito manualmente? Quantos dias leva?_

> _(Isso ajuda a entender se há risco de churn por onboarding ruim — uma dor típica de SaaS B2B.)_
> **🧑 Empresário:** Quero automatizar a qualificação de leads e o primeiro atendimento do suporte do SaaS.

> **🤖 Consultor:** Excelente — com esse foco, já dá pra montar um time de agentes de alto impacto.

> _Só preciso fechar uma última peça sobre o **suporte do SaaS**:_

> _**Quais são as perguntas ou problemas mais repetitivos que os clientes do SaaS mandam por e-mail?**_
> _(ex: "como cadastrar um paciente?", "não consigo gerar relatório X", "como emitir nota fiscal?", etc.)_

> _Isso vai me ajudar a desenhar um agente de atendimento que resolva 80% dos casos sem precisar de um humano._
> **🧑 Empresário:** /fim

> **🤖 Consultor:** Pronto! Acabei de gerar o seu **blueprint de transformação com agentes de IA**, focado exatamente nas suas prioridades: **qualificação rápida de leads** e **primeiro atendimento automatizado no suporte do SaaS**.

> _### 🎯 O que você vai ganhar:_
> _1. **SDR (Pré-vendas)** – entra em contato com leads do site/LinkedIn em minutos, evitando que esfriem._
> _2. **Atendente de Suporte SaaS** – resolve dúvidas repetitivas por e-mail 24/7, liberando seu time._
> _3. **Coordenador de Operações** – conecta Pipedrive, Jira e Slack pra ninguém perder informação._

> _### 🚀 Roadmap sugerido:_
> _- **Etapa 1**: Implante o SDR → impacto direto na receita._
> _- **Etapa 2**: Atendente de Suporte → melhora retenção e reduz estresse._
> _- **Etapa 3**: Coordenação entre sistemas → eficiência operacional._

> _### ❓ O que ficou em aberto (pra ajustar depois):_
> _- Quais são as perguntas mais comuns no suporte?_
> _- Vocês já têm uma FAQ ou base de conhecimento?_
> _- Como funciona hoje o onboarding das clínicas?_

> _Se quiser, posso te ajudar a detalhar qualquer um desses agentes ou até montar os fluxos de conversa (scripts) que eles vão usar. É só dizer!_

### Blueprint gerado

<details>
<summary>Expandir blueprint completo</summary>

# Blueprint do Time de Agentes

## Perfil da empresa
- Segmento: tecnologia
- Porte: médio (12 funcionários, R$ 180k/mês)
- Modelo de negócio: software house com projetos customizados + SaaS B2B para clínicas
- Dores: funil de vendas manual, leads esfriando antes da proposta, suporte sobrecarregado por e-mail

## Mapa de processos
- **pré-vendas**: qualificação e primeiro contato com leads do site e LinkedIn
- **suporte técnico ao SaaS**: atendimento por e-mail a clientes de clínicas, com perguntas repetitivas
- **operações internas**: uso de Pipedrive, Slack e Jira sem automação entre si

## Integrações detectadas
- crm — Pipedrive (dados em: contas, leads, negócios)
- communication — Slack (dados em: conversas internas da equipe)
- project_management — Jira (dados em: tickets de projeto e bugs)
- website — Site institucional (dados em: formulário de contato)
- social — LinkedIn (dados em: mensagens diretas ou conexões)
- email — E-mail de suporte (dados em: caixa de entrada do time)

## Time de agentes proposto
### SDR (Pré-vendas) — Qualificação de leads
- Objetivo: Contatar leads do site e LinkedIn em minutos, qualificar e agendar demo antes que esfriem
- Tarefas: responder formulário do site automaticamente, enviar mensagem personalizada no LinkedIn, classificar lead como quente/morno/frio, agendar reunião no calendário do comercial
- Integrações: pipedrive, site, linkedin, calendly/google calendar
- Conversa com: Closer
### Atendente de Suporte SaaS — Primeiro atendimento 24/7
- Objetivo: Resolver as dúvidas mais comuns das clínicas sem intervenção humana
- Tarefas: responder FAQ por e-mail, encaminhar casos complexos para humano, registrar ticket no Jira se for bug, notificar sucesso do cliente sobre onboarding pendente
- Integrações: e-mail, jira, pipedrive, base de conhecimento
- Conversa com: Coordenador de Operações, Sucesso do Cliente
### Coordenador de Operações — Automação interna
- Objetivo: Conectar Pipedrive, Jira e Slack para eliminar retrabalho manual
- Tarefas: criar ticket no Jira quando suporte identifica bug, notificar comercial no Slack sobre lead qualificado, atualizar status do negócio no Pipedrive automaticamente
- Integrações: pipedrive, jira, slack
- Conversa com: SDR (Pré-vendas), Atendente de Suporte SaaS

## Roadmap
1. **SDR (Pré-vendas)** — Resolve a dor principal dos leads esfriando; alto impacto na receita com implantação simples via Pipedrive + site
2. **Atendente de Suporte SaaS** — Alivia a sobrecarga do time e melhora a experiência do cliente do SaaS
3. **Coordenador de Operações** — Integra os sistemas e elimina perda de informação entre vendas, suporte e devs

## Perguntas em aberto
- Quais são as perguntas mais repetitivas no suporte por e-mail?
- O Pipedrive já tem webhooks ou integração via API habilitada?
- Existe base de conhecimento (FAQ) documentada para o SaaS?
- Como é feito hoje o onboarding de novas clínicas no SaaS?

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
| Mapa de processos | 10 | 10 | `██████████` | 3 processos mapeados |
| Perguntas em aberto | 5 | 5 | `██████████` | 4 perguntas documentadas |
| Integrações detectadas | 10 | 10 | `██████████` | 4 integrações |
| Profundidade da entrevista | 10 | 10 | `██████████` | 7 turnos do usuário |

### ✅ Pontos positivos

- Segmento detectado corretamente: `construcao`
- Blueprint gerado e salvo com sucesso
- Time com 3 agentes propostos
- Roadmap com 3 etapas bem definidas
- 3 processos mapeados no blueprint
- 4 perguntas em aberto documentadas (boa prática)
- 4 integrações detectadas corretamente
- Entrevista aprofundada: 7 turnos do empresário

### Transcrição da entrevista

> _Olá! Seja muito bem-vindo(a). 🤝_

> _Meu nome é Orbe e sou especialista em implementação de inteligência artificial para negócios. Já ajudei dezenas de empresas brasileiras a montar times de agentes que trabalham 24 horas por dia — atendendo clientes, criando conteúdo para redes sociais, gerenciando pedidos, automatizando orçamentos e muito mais._

> _Antes de qualquer proposta, quero entender bem a sua realidade. Não existe solução pronta: o plano certo depende do que você faz, de como você opera e de onde você quer chegar._

> _Então me conta: **o que a sua empresa faz** e qual é o maior desafio que você enfrenta hoje no dia a dia?_
> **🧑 Empresário:** Tenho uma construtora especializada em reformas residenciais e comerciais. Também fazemos obras pequenas.

> **🤖 Consultor:** Opa, construtora de reformas — que legal! Esse é um segmento cheio de oportunidades pra deixar tudo mais fluido, tanto pra sua equipe quanto pros clientes.

> _Antes de mergulhar nas perguntas, quero entender melhor como vocês operam hoje. Vamos começar pelo **atendimento**:_

> _**Você usa WhatsApp como principal canal de contato com clientes?**_
> _(E aí: é só o celular do dono, ou já tem algo mais organizado tipo WhatsApp Business?)_
> **🧑 Empresário:** Orçamento é nossa maior dor. Cliente pede orçamento e a gente leva uma semana para responder. Muitos desistem.

> **🤖 Consultor:** Entendi perfeitamente — orçamento lento é um **grande** gargalo em reformas, porque o cliente geralmente está comparando várias opções e quem responde rápido leva a obra.

> _Vamos entender melhor esse processo pra ver como acelerar:_

> _**Hoje, quando um cliente pede orçamento (provavelmente pelo WhatsApp), quais informações vocês precisam coletar antes de conseguir montar o valor?**_
> _Por exemplo: fotos do local? Medidas? Tipo de acabamento? Ou é tudo feito só depois de uma visita presencial?_
> **🧑 Empresário:** Usamos WhatsApp para tudo, planilha Excel para custos e Google Agenda para as visitas técnicas.

> **🤖 Consultor:** Ótimo — agora já vejo o cenário completo: tudo roda no WhatsApp, planilha e agenda, sem integração. Isso explica a demora no orçamento.

> _Vamos um passo adiante:_

> _**Depois que vocês fazem a visita técnica, quanto tempo leva pra transformar aquilo em um orçamento fechado?**_
> _E quem participa desse processo? (ex: engenheiro calcula, outro pessoa ajusta preços, alguém digita na planilha?)_
> **🧑 Empresário:** Somos 15 pessoas entre engenheiros, mestres de obra e equipe. Faturamos uns R$ 250 mil por mês.

> **🤖 Consultor:** Com 15 pessoas e R$ 250k/mês, dá pra estruturar um fluxo bem mais ágil — sem sobrecarregar ninguém.

> _Voltando à visita técnica:_

> _**Depois que a visita é feita, como os dados viram orçamento?**_
> _Por exemplo: o engenheiro anota em papel? Tira foto? Manda no grupo do WhatsApp? E quem depois pega essas informações pra preencher a planilha de custos?_
> **🧑 Empresário:** Os clientes reclamam que não sabem como está a obra. Ligam toda semana pedindo atualização.

> **🤖 Consultor:** Essa reclamação dos clientes é **muito** comum em reformas — e é uma oportunidade dourada pra se destacar. Quem mantém o cliente informado ganha confiança, indicações e menos estresse na equipe.

> _Mas antes de resolver isso, preciso fechar uma peça importante:_

> _**Depois da visita técnica, como os dados viram orçamento?**_
> _Exemplo: o engenheiro anota em papel? Tira foto do local? Manda no grupo do WhatsApp? E quem depois pega essas informações pra preencher a planilha de custos?_

> _Isso vai me ajudar a desenhar um agente que acelere esse processo sem exigir mudanças radicais na rotina de vocês._
> **🧑 Empresário:** Quero agilizar os orçamentos e dar visibilidade da obra para o cliente sem minha equipe parar para responder.

> **🤖 Consultor:** Perfeito — você já definiu os dois maiores pontos de melhoria: **orçamento rápido** e **obra transparente**, sem tirar sua equipe do foco.

> _Vamos fechar só mais um detalhe sobre o orçamento:_

> _**Hoje, depois da visita, alguém precisa digitar tudo na planilha manualmente?**_
> _Ou já existe algum tipo de checklist, template ou formulário que ajuda a padronizar os insumos (mão de obra, materiais, prazo etc.)?_

> _Isso vai me dizer se dá pra criar um “pré-orçamento” automático com base em fotos + respostas simples do cliente — algo que pode reduzir de dias para **horas**._
> **🧑 Empresário:** /fim

> **🤖 Consultor:** Pronto! Acabei de gerar o seu **blueprint de transformação digital** com um time de 3 agentes inteligentes feitos sob medida para sua construtora:

> _1. **Agente de Pré-Orçamento** → responde leads em horas (não dias) e agenda visita automaticamente_
> _2. **Coordenador de Obras** → atualiza o cliente sem sua equipe precisar parar o trabalho_
> _3. **Gestor de Pós-Obra** → pede avaliação, cuida da garantia e gera indicações_

> _O plano começa pelo agente de orçamento porque é **alta dor + baixa complexidade**: ele usa só WhatsApp, planilha e Google Agenda — nada novo pra comprar._

> _Ficaram algumas perguntas em aberto (como exatamente vocês registram a visita técnica), mas o suficiente pra entregar valor imediato._

> _Se quiser, posso agora:_
> _- Explicar passo a passo como implantar o primeiro agente_
> _- Mostrar um exemplo de pré-orçamento automático via WhatsApp_
> _- Ou ajustar o plano com base nas respostas das perguntas em aberto_

> _É só me dizer!_

### Blueprint gerado

<details>
<summary>Expandir blueprint completo</summary>

# Blueprint do Time de Agentes

## Perfil da empresa
- Segmento: construcao
- Porte: pequeno-médio (15 funcionários, R$ 250k/mês)
- Modelo de negócio: reformas residenciais e comerciais sob demanda
- Dores: orçamento demora dias, clientes desistem, cliente sem visibilidade da obra, equipe sobrecarregada com atendimento manual, comunicação fragmentada (WhatsApp, planilha, agenda)

## Mapa de processos
- **atendimento_inicial**: Recebimento de leads via WhatsApp e agendamento de visita técnica
- **elaboracao_orcamento**: Visita técnica → coleta de dados → cálculo manual em planilha → envio do orçamento
- **acompanhamento_obra**: Obra em andamento sem atualizações pro cliente; ele liga para pedir status

## Integrações detectadas
- whatsapp — WhatsApp (dados em: conversas com leads e clientes)
- spreadsheet — Planilha Excel/Google Sheets de custos (dados em: arquivo local ou na nuvem)
- calendar — Google Agenda (dados em: agendamento de visitas técnicas)

## Time de agentes proposto
### Agente de Pré-Orçamento — Pré-vendas / Qualificação de lead
- Objetivo: Reduzir de dias para horas o tempo até o primeiro orçamento, mesmo antes da visita
- Tarefas: coletar informações iniciais via WhatsApp (fotos, medidas, tipo de reforma), gerar pré-orçamento com base em templates e planilha de custos, agendar visita técnica automaticamente no Google Agenda, enviar proposta inicial com validade e escopo claro
- Integrações: whatsapp, planilha de custos, google agenda
- Conversa com: Coordenador de Obras
### Coordenador de Obras — Gestão de execução e comunicação
- Objetivo: Manter o cliente informado sobre o andamento da obra sem intervenção humana constante
- Tarefas: receber atualizações diárias da equipe no canteiro (via app simples ou WhatsApp), enviar resumo semanal automático ao cliente (etapa concluída, próxima etapa, fotos), alertar sobre atrasos ou mudanças de cronograma, registrar medições e pagamentos por etapa
- Integrações: whatsapp, google agenda, planilha de cronograma
- Conversa com: Agente de Pré-Orçamento, Gestor de Pós-Obra
### Gestor de Pós-Obra — Fidelização e garantia
- Objetivo: Transformar clientes em promotores após a entrega
- Tarefas: enviar checklist de entrega e garantia, solicitar avaliação no Google ou em redes sociais, agendar revisão pós-entrega (30/60/90 dias), oferecer manutenção preventiva ou nova reforma
- Integrações: whatsapp, google forms, planilha de clientes
- Conversa com: Coordenador de Obras

## Roadmap
1. **Agente de Pré-Orçamento** — Resolve a dor principal (perda de leads por lentidão) com baixa complexidade, usando ferramentas que já existem
2. **Coordenador de Obras** — Elimina ligações repetitivas e aumenta confiança do cliente com atualizações automáticas
3. **Gestor de Pós-Obra** — Gera indicações e fideliza, fechando o ciclo com qualidade

## Perguntas em aberto
- Como os dados da visita técnica são registrados hoje? (papel, foto, áudio?)
- A planilha de custos está em Excel local ou Google Sheets?
- Existe algum template de orçamento padronizado (por tipo de reforma)?
- A equipe no canteiro usa algum app ou só WhatsApp para comunicar progresso?

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

_Relatório gerado por `scripts/eval_discovery.py` em 20260611_192116_
