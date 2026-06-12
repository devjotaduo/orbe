# Relatório de Avaliação — Discovery Agent

**Data:** 20260611_224118  
**Cenários testados:** 1  
**Pontuação máxima por cenário:** 100 pts  

## Sumário Executivo

| Cenário | Segmento | Blueprint | Score | Qualidade | Nota |
|---------|----------|-----------|-------|-----------|------|
| Loja Virtual de Roupas | ✅ | ✅ | 120/120 (100%) | 32/40 | A — Excelente |

**Média geral:** 100.0% — A — Excelente

---

## Cenário: Loja Virtual de Roupas

- **Descrição:** E-commerce de moda feminina, vende pelo Instagram e site próprio
- **Segmento esperado:** `ecommerce`
- **Segmento detectado:** `ecommerce`
- **Blueprint emitido:** ✅ Sim
- **Score:** 120/120 (100%) — A — Excelente

```
Score  [████████████████████] 120/120
```

### Pontuação por critério

| Critério | Score | Máx | Barra | Observação |
|----------|------:|----:|-------|------------|
| Segmento | 20 | 20 | `██████████` | Correto: `ecommerce` |
| Blueprint gerado | 20 | 20 | `██████████` | Emitido com sucesso |
| Agentes propostos | 15 | 15 | `██████████` | 3 agentes — equipe completa |
| Roadmap | 10 | 10 | `██████████` | 3 etapas — detalhado |
| Mapa de processos | 10 | 10 | `██████████` | 4 processos mapeados |
| Perguntas em aberto | 5 | 5 | `██████████` | 2 perguntas documentadas |
| Integrações detectadas | 10 | 10 | `██████████` | 4 integrações |
| Profundidade da entrevista | 10 | 10 | `██████████` | 7 turnos do usuário |
| Onboarding WhatsApp | 10 | 10 | `██████████` | Contato registrado: João |
| Requisitos por agente | 10 | 10 | `██████████` | 3 agente(s) com pendências mapeadas |

### Avaliação qualitativa (LLM-as-judge)

| Critério | Nota | Barra |
|----------|-----:|-------|
| Clareza das perguntas | 9/10 | `█████████░` |
| Empatia | 10/10 | `██████████` |
| Não-repetição | 7/10 | `███████░░░` |
| Linguagem simples | 6/10 | `██████░░░░` |
| **Total** | **32/40** | |

> O consultor foi empático, usou linguagem acessível e fez perguntas claras e contextualizadas. Houve leve repetição na pergunta sobre o método de entrega. O relatório final, porém, contém jargões técnicos como "WhatsApp Cloud API (oficial Meta)", "Google Sheets" (como ferramenta técnica) e estrutura muito próxima de termos como "canais", "fluxo" e "consolidar", além de mencionar etapas sequenciais que sugerem prazos implícitos.

### ✅ Pontos positivos

- Segmento detectado corretamente: `ecommerce`
- Blueprint gerado e salvo com sucesso
- Time com 3 agentes propostos
- Roadmap com 3 etapas bem definidas
- 4 processos mapeados no blueprint
- 2 perguntas em aberto documentadas (boa prática)
- 4 integrações detectadas corretamente
- Entrevista aprofundada: 7 turnos do empresário
- WhatsApp do responsável capturado (João)
- Fase de requisitos cobriu todos os agentes do time

### Transcrição da entrevista

> _Olá! Seja muito bem-vindo(a). 🤝_

> _Meu nome é Orbe e sou especialista em implementação de inteligência artificial para negócios. Já ajudei dezenas de empresas brasileiras a montar times de agentes que trabalham 24 horas por dia — atendendo clientes, criando conteúdo para redes sociais, gerenciando pedidos, automatizando orçamentos e muito mais._

> _Antes de qualquer proposta, quero entender bem a sua realidade. Não existe solução pronta: o plano certo depende do que você faz, de como você opera e de onde você quer chegar._

> _Então me conta: **o que a sua empresa faz** e qual é o maior desafio que você enfrenta hoje no dia a dia?_
> **🧑 Empresário:** Tenho uma loja virtual de roupas femininas. Vendemos pelo Instagram e site próprio.

> **🤖 Consultor:** Opa, tudo bem? Legal saber que você tem uma loja virtual de roupas femininas — e já vende tanto pelo Instagram quanto pelo site próprio. Isso mostra que você já está com um bom pé no digital!

> _Antes de mergulhar nas soluções, quero entender melhor como funciona hoje o **atendimento aos clientes**. Por exemplo:_

> _- Quando alguém manda mensagem no Instagram ou no WhatsApp da loja (se tiver), quem responde?_
> _- Vocês recebem muitas perguntas repetidas, como “qual o prazo de entrega?” ou “como faço para trocar?”?_

> _Me conta um pouco desse dia a dia!_
> **🧑 Empresário:** O maior problema é o atendimento. Recebo mais de 100 mensagens por dia no WhatsApp e não consigo responder todas.

> **🤖 Consultor:** Entendi perfeitamente — mais de 100 mensagens por dia no WhatsApp é um volume que **ninguém** consegue acompanhar sozinho, ainda mais com qualidade. E no seu ramo, cada cliente perdida pode ser uma venda a menos, né?

> _Agora me ajuda a entender melhor o **lado das vendas e marketing**:_
> _Você vende pelo Instagram e pelo site próprio — mas como funciona essa conversão?_

> _Por exemplo:_
> _- Você posta fotos das peças no feed ou stories? Com que frequência?_
> _- Quando alguém se interessa (comenta, manda mensagem ou entra no site), como você faz para transformar isso em venda?_
> _- Tem catálogo digital ou as pessoas precisam perguntar tudo na mão?_

> _Essas respostas vão me ajudar a ver se dá pra automatizar não só o atendimento, mas também **atrair e converter mais clientes** com menos esforço._
> **🧑 Empresário:** Uso WhatsApp Business e uma planilha Excel para controlar os pedidos. Não tenho CRM.

> **🤖 Consultor:** Show! Usar WhatsApp Business e uma planilha já é um começo — mas dá pra imaginar o quanto de tempo você gasta copiando dados, atualizando status e respondendo a mesma pergunta várias vezes ("já foi enviado?", "qual o código de rastreio?", etc.).

> _Agora me conta sobre a **entrega**:_
> _- Você envia as roupas pelos Correios, transportadora ou motoboy?_
> _- Os clientes costumam perguntar sobre o status do pedido depois de comprar?_
> _- Você avisa quando o pedido sai ou só responde se perguntarem?_

> _Essa parte é crucial porque, se a gente automatizar o envio de atualizações (tipo “seu pedido foi postado!” + código de rastreio), **você reduz drasticamente o volume de mensagens repetidas** — e ainda deixa o cliente mais feliz._
> **🧑 Empresário:** Faturamos em torno de R$ 30 mil por mês. Somos 3 pessoas: eu, uma assistente e uma responsável pelo estoque.

> **🤖 Consultor:** Perfeito — com 3 pessoas e R$ 30 mil de faturamento, vocês já têm uma operação sólida, mas claramente **estão no limite da capacidade manual**, especialmente no atendimento.

> _Voltando à entrega (pra fechar essa parte):_
> _- Vocês usam **Correios, transportadora ou motoboy** para enviar os pedidos?_
> _- E depois que enviam, **avisam o cliente automaticamente** ou só respondem se ele perguntar?_

> _Isso vai me ajudar a propor um agente que **envie atualizações automáticas de rastreio**, reduzindo mensagens repetidas e liberando sua equipe pra focar no que realmente importa._
> **🧑 Empresário:** Vendo também na Shopee e no Mercado Livre. Tenho problemas com devoluções que ficam sem resposta.

> **🤖 Consultor:** Ah, agora faz ainda mais sentido! Vendendo em **4 canais** (Instagram, site próprio, Shopee e Mercado Livre), o volume de mensagens e processos só aumenta — e as devoluções sem resposta podem virar **avaliações negativas** ou até prejuízo.

> _Sobre o **pós-venda**, me ajuda com isso:_
> _- Quando um cliente pede devolução ou troca, **vocês têm um passo a passo definido** (ex.: “manda foto do defeito”, “aguarda aprovação”, “envia código de postagem”)?_
> _- Ou cada caso vira uma conversa longa no WhatsApp que acaba se perdendo?_

> _Se a gente organizar esse fluxo e colocar um agente pra **acompanhar automaticamente** esses casos, você evita que pedidos fiquem esquecidos e ainda melhora a experiência do cliente. Como é hoje?_
> **🧑 Empresário:** Meu sonho é conseguir vender enquanto durmo — automação total do atendimento e rastreio de pedidos.

> **🤖 Consultor:** Que sonho **absolutamente possível** — e mais comum do que você imagina! Muitas lojas como a sua já estão vendendo 24/7 com um time de agentes digitais cuidando do atendimento, rastreio e pós-venda. Vamos montar isso pra você.

> _Antes de fechar o plano, preciso só de uma última peça:_
> _**Qual é o WhatsApp da sua loja?** (o número que os clientes usam pra falar com você)_

> _Vou usá-lo pra:_
> _1. Conectar como **canal oficial** do seu time de agentes (é por ele que eles vão responder)._
> _2. Criar um **grupo no WhatsApp com você** pra pedir as informações que faltarem (ex.: respostas padrão, políticas de troca) e você **testar o atendente antes** de ele falar com clientes reais._

> _Pode me passar o número com DDD? (ex.: 11 98765-4321)_
> **🧑 Empresário:** Pode ser no meu número mesmo: 11 98765-4321. Sou eu que cuido disso, pode me chamar de João.

> **🤖 Consultor:** João, seu plano está pronto! Vamos transformar seu sonho de **vender enquanto dorme** em realidade com um time de agentes digitais que cuidam do atendimento, pedidos e pós-venda 24/7.

> _### Por onde vamos começar?_
> _1. **Conectar o WhatsApp da sua loja** (11 98765-4321) como canal oficial — é por ele que os agentes vão responder._
> _2. **Criar um grupo no WhatsApp com você** pra:_
> _- Pedir as informações que faltam (ex.: políticas de troca, respostas padrão)._
> _- Você **testar o atendente antes** de ele falar com clientes reais._
> _3. Colocar o **Atendente WhatsApp** funcionando primeiro — ele já vai reduzir drasticamente seu volume de mensagens repetidas._

> _Em seguida, montamos o Coordenador de Pedidos (pra unificar tudo numa planilha e enviar rastreio automático) e o Coordenador de Pós-Venda (pra garantir que nenhuma devolução fique esquecida)._

> _Você vai acompanhar tudo pelo grupo, sem precisar instalar nada ou mexer em código. Vamos nessa? 🚀_

> _(Levantando as informações que faltam para o seu time começar...)_

> **🤖 Consultor:** Oi, João! Tudo bem? Estamos montando seu time de agentes para resolver o caos do WhatsApp, organizar os pedidos e cuidar direitinho das devoluções. Por aqui, vamos pedir só as informações que ainda faltam para cada agente funcionar direito — nada de repetir o que você já contou. Assim que tivermos tudo, você vai testar o atendente antes de qualquer cliente ver!

> _O que vamos pedir no grupo do WhatsApp:_

> _Atendente WhatsApp:_
> _- Lista completa de produtos com preços e fotos_
> _- Política de troca e devolução (prazos, condições, como funciona)_
> _- Perguntas frequentes reais dos clientes com respostas_
> _- Horário de atendimento da loja (se aplica)_

> _Coordenador de Pedidos:_
> _- Link ou acesso à planilha de pedidos (Google Sheets ou Excel)_
> _- Lista de status dos pedidos usados na planilha (ex: pago, separado, enviado)_
> _- Transportadoras usadas e prazo médio de entrega por região_

> _Coordenador de Pós-Venda:_
> _- Passo a passo interno para processar uma devolução/troca_
> _- Prazo máximo para processar reembolso após recebimento do produto_
> _- Valor ou regra do cupom de retorno pós-devolução_

> _(Detalhes em C:\Users\ruthe\AppData\Local\Temp\qwenpaw_eval_mbdapp6f\ecommerce_roupas\informacoes_pendentes.md e mensagens prontas em C:\Users\ruthe\AppData\Local\Temp\qwenpaw_eval_mbdapp6f\ecommerce_roupas\mensagens_grupo.md)_

### Blueprint gerado

<details>
<summary>Expandir blueprint completo</summary>

# Seu Time de Agentes

Preparamos este plano com base na nossa conversa. Aqui está o que entendemos do seu negócio e o time que vamos montar para você.

## O que entendemos do seu negócio
- O que a empresa faz: ecommerce multicanal (Instagram, site próprio, Shopee, Mercado Livre)
- Tamanho da operação: pequeno (3 pessoas, R$ 30k/mês)
- Desafios que você nos contou:
  - atendimento lento no WhatsApp (100+ mensagens/dia)
  - devoluções sem resposta
  - sem automação de rastreio

## Como o trabalho acontece hoje
- **atendimento**: respostas a dúvidas, pedidos e devoluções via WhatsApp
- **pedidos**: registro manual em planilha Excel de pedidos de 4 canais
- **logística**: envio e rastreio sem atualização automática ao cliente
- **pós-venda**: trocas e devoluções sem acompanhamento estruturado

## Ferramentas que você já usa
- WhatsApp Business (fica em: celular do dono)
- Planilha Excel de pedidos (fica em: computador local ou Google Sheets)
- Shopee (fica em: painel da loja)
- Mercado Livre (fica em: painel da loja)

## Quem vai trabalhar para você
### Atendente WhatsApp — SAC 24/7
- Missão: responder automaticamente dúvidas frequentes, pedidos e devoluções no WhatsApp
- O que ele faz no dia a dia:
  - responder FAQ (tamanhos, prazos, políticas)
  - registrar novos pedidos na planilha
  - iniciar fluxo de devolução com passo a passo claro
- Vai trabalhar com: Google Sheets, WhatsApp Cloud API (oficial Meta)
- Trabalha junto com: Coordenador de Pedidos, Coordenador de Pós-Venda
### Coordenador de Pedidos — operações
- Missão: centralizar e atualizar pedidos de todos os canais numa única planilha
- O que ele faz no dia a dia:
  - consolidar pedidos do Instagram, site, Shopee e Mercado Livre
  - atualizar status (pago, separado, enviado)
  - gerar código de rastreio e enviar ao cliente
- Vai trabalhar com: Google Sheets, Whatsapp
- Trabalha junto com: Atendente WhatsApp
### Coordenador de Pós-Venda — fidelização
- Missão: garantir que nenhuma devolução fique esquecida e recuperar clientes insatisfeitos
- O que ele faz no dia a dia:
  - acompanhar prazo de devolução/troca
  - avisar quando reembolso for processado
  - enviar cupom de retorno após resolução
- Vai trabalhar com: Google Sheets, Whatsapp
- Trabalha junto com: Atendente WhatsApp

## Por onde vamos começar
Cada etapa entra no ar quando a anterior estiver redonda — você acompanha e aprova tudo.
1. **Atendente WhatsApp** — resolve a dor principal (100+ mensagens/dia) e é o ponto de entrada de tudo
2. **Coordenador de Pedidos** — elimina o caos de pedidos espalhados e automatiza o rastreio
3. **Coordenador de Pós-Venda** — protege sua reputação e transforma problemas em oportunidades de fidelização

## O que ainda vamos confirmar com você
- qual plataforma usa para o site próprio (Shopify, Nuvemshop, outro)?
- a planilha de pedidos está no Excel local ou Google Sheets?

## Próximos passos
1. Vamos conectar o WhatsApp da sua empresa — ele será o canal oficial de atendimento do seu time de agentes.
2. Vamos criar um grupo no WhatsApp com João (+55 (11) 98765-4321) para acompanhar tudo de perto.
3. Pelo grupo, você nos passa as informações que faltarem e testa o atendente antes de ele começar a falar com seus clientes.

Vamos montar o seu time de agentes — e você acompanha cada passo pelo grupo. 🤝

</details>

---

## Análise Global e Melhorias Sugeridas

### Recomendações de melhoria

1. Nenhum problema recorrente nesta rodada. Manter o avaliador como gate de regressão: rode `python scripts/eval_discovery.py` após qualquer mudança em `prompts.py`, `tools.py` ou na seed CNAE (há um smoke e2e opt-in via `QWENPAW_EVAL_E2E=1` no pytest).
2. Adicionar personas de segmentos FORA da seed (ex.: pet shop, oficina mecânica) para exercitar o caminho de raciocínio livre do `segment_lookup`.
3. Evoluir o scoring com critérios qualitativos (clareza das perguntas, empatia, não-repetição) usando LLM-as-judge em vez de só contagens.

---

_Relatório gerado por `scripts/eval_discovery.py` em 20260611_224118_
