# Relatório de Avaliação — Discovery Agent

**Data:** 20260611_205049  
**Cenários testados:** 1  
**Pontuação máxima por cenário:** 100 pts  

## Sumário Executivo

| Cenário | Segmento | Blueprint | Score | Qualidade | Nota |
|---------|----------|-----------|-------|-----------|------|
| Loja Virtual de Roupas | ✅ | ✅ | 100/100 (100%) | 26/30 | A — Excelente |

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
| Perguntas em aberto | 5 | 5 | `██████████` | 6 perguntas documentadas |
| Integrações detectadas | 10 | 10 | `██████████` | 4 integrações |
| Profundidade da entrevista | 10 | 10 | `██████████` | 7 turnos do usuário |

### Avaliação qualitativa (LLM-as-judge)

| Critério | Nota | Barra |
|----------|-----:|-------|
| Clareza das perguntas | 9/10 | `█████████░` |
| Empatia | 10/10 | `██████████` |
| Não-repetição | 7/10 | `███████░░░` |
| **Total** | **26/30** | |

> O consultor faz perguntas claras e contextualizadas, demonstrando forte empatia ao reconhecer as dores do empresário e adaptar o discurso ao seu modelo de negócio. No entanto, repete duas vezes a pergunta sobre as "3 perguntas mais frequentes", ainda que com ligeiras variações, o que reduz parcialmente a nota de não repetição.

### ✅ Pontos positivos

- Segmento detectado corretamente: `ecommerce`
- Blueprint gerado e salvo com sucesso
- Time com 4 agentes propostos
- Roadmap com 4 etapas bem definidas
- 5 processos mapeados no blueprint
- 6 perguntas em aberto documentadas (boa prática)
- 4 integrações detectadas corretamente
- Entrevista aprofundada: 7 turnos do empresário

### Transcrição da entrevista

> _Olá! Seja muito bem-vindo(a). 🤝_

> _Meu nome é Orbe e sou especialista em implementação de inteligência artificial para negócios. Já ajudei dezenas de empresas brasileiras a montar times de agentes que trabalham 24 horas por dia — atendendo clientes, criando conteúdo para redes sociais, gerenciando pedidos, automatizando orçamentos e muito mais._

> _Antes de qualquer proposta, quero entender bem a sua realidade. Não existe solução pronta: o plano certo depende do que você faz, de como você opera e de onde você quer chegar._

> _Então me conta: **o que a sua empresa faz** e qual é o maior desafio que você enfrenta hoje no dia a dia?_
> **🧑 Empresário:** Tenho uma loja virtual de roupas femininas. Vendemos pelo Instagram e site próprio.

> **🤖 Consultor:** Legal! Loja virtual de roupas femininas com vendas pelo Instagram e site próprio — um modelo bem comum hoje, mas com muitas oportunidades de escalar com IA.

> _Antes de tudo, quero entender melhor como funciona o **atendimento** dos seus clientes._

> _- Vocês usam WhatsApp para responder dúvidas?_
> _- Qual o volume médio de mensagens por dia (só uma estimativa)?_
> _- Quais são as perguntas que mais se repetem?_

> _Isso me ajuda a ver se um agente de atendimento 24/7 já resolveria boa parte do esforço da sua equipe._
> **🧑 Empresário:** O maior problema é o atendimento. Recebo mais de 100 mensagens por dia no WhatsApp e não consigo responder todas.

> **🤖 Consultor:** Entendi perfeitamente — mais de 100 mensagens por dia no WhatsApp é inviável de responder sozinho(a), e isso certamente faz você perder vendas.

> _Vamos aprofundar um pouco nesse atendimento:_

> _**Quais são as 3 perguntas que mais aparecem nas mensagens?**_
> _(ex: “tem em estoque?”, “qual o prazo de entrega?”, “aceita parcelamento?”)_

> _Isso me ajuda a montar um agente que já resolva essas dúvidas automaticamente, sem precisar da sua intervenção._
> **🧑 Empresário:** Uso WhatsApp Business e uma planilha Excel para controlar os pedidos. Não tenho CRM.

> **🤖 Consultor:** Ótimo — agora já tenho uma visão mais clara: você está com o atendimento sobrecarregado no WhatsApp Business e gerenciando tudo com uma planilha, sem CRM.

> _Antes de seguir para outras áreas, volto à pergunta anterior (mas de forma mais direta):_

> _**Quais são as 3 perguntas que mais aparecem nas mensagens dos clientes?**_
> _(ex: “tem em estoque?”, “qual o prazo de entrega?”, “como faço para trocar?”)_

> _Isso é essencial para eu configurar um agente de atendimento que resolva sozinho pelo menos 70% das mensagens._
> **🧑 Empresário:** Faturamos em torno de R$ 30 mil por mês. Somos 3 pessoas: eu, uma assistente e uma responsável pelo estoque.

> **🤖 Consultor:** Perfeito — com R$ 30 mil/mês e uma equipe de 3 pessoas, cada minuto conta. Automatizar o que dá pra automatizar vai liberar tempo valioso pra você focar em crescer.

> _Vamos agora olhar para **marketing e vendas**, já que você vende pelo Instagram e site:_

> _- Você posta conteúdo no Instagram todos os dias?_
> _- Usa anúncios pagos (Meta Ads)?_
> _- Tem um catálogo digital organizado (com fotos, descrições e preços atualizados)?_

> _Essas respostas me ajudam a ver se dá pra escalar suas vendas com um agente de marketing, além do atendimento._
> **🧑 Empresário:** Vendo também na Shopee e no Mercado Livre. Tenho problemas com devoluções que ficam sem resposta.

> **🤖 Consultor:** Agora fechou o quebra-cabeça! Você está vendendo em **quatro canais** (Instagram, site próprio, Shopee e Mercado Livre), e isso multiplica o volume de atendimento — incluindo devoluções que acabam sem resposta, o que pode afetar sua reputação.

> _Antes de propor a solução completa, preciso só entender melhor esse ponto:_

> _**As devoluções acontecem mais em algum canal específico?**_
> _(ex: “a maioria vem do Mercado Livre” ou “é misto, mas todas param na minha caixa de entrada”)_

> _E também:_
> _**Vocês têm um prazo ou processo definido para responder esses pedidos de devolução?**_

> _Isso vai me ajudar a desenhar um agente de pós-venda que não deixe nenhum cliente no limbo._
> **🧑 Empresário:** Meu sonho é conseguir vender enquanto durmo — automação total do atendimento e rastreio de pedidos.

> **🤖 Consultor:** Esse é um sonho totalmente realizável — e, com o seu modelo (vendas em 4 canais e operação enxuta), a automação vai ser um divisor de águas.

> _Para fechar o diagnóstico e montar seu plano exato, preciso só de mais uma peça:_

> _**Como você envia os pedidos hoje?**_
> _- Usa Correios, transportadora ou entrega própria?_
> _- Os clientes perguntam muito “onde está meu pedido?”_
> _- Você atualiza o status de entrega manualmente (ex: copiando código de rastreio na planilha ou no WhatsApp)?_

> _Com isso, consigo desenhar um agente que não só responde automaticamente sobre o status, mas também atualiza tudo sem você precisar fazer nada._
> **🧑 Empresário:** /fim

> **🤖 Consultor:** Pronto! Acabei de gerar seu **blueprint de transformação digital** com base em tudo o que conversamos.

> _### O que você vai receber:_
> _- Um time de **4 agentes inteligentes** que trabalham 24/7 pra você:_
> _1. **Atendente WhatsApp** – responde automaticamente as dúvidas mais comuns em todos os canais._
> _2. **Coordenador de Pedidos** – unifica pedidos do Instagram, site, Shopee e Mercado Livre._
> _3. **Coordenador de Pós-Venda** – garante que nenhuma devolução fique sem resposta._
> _4. **Agente de Logística** – avisa o cliente automaticamente sobre envio e status._

> _- Um **roadmap por etapas**, começando pelo que resolve sua dor mais urgente (o volume no WhatsApp) e terminando com a automação completa da jornada do cliente._

> _- Uma lista clara do que ainda precisaria confirmar para refinar ainda mais (como suas perguntas frequentes e detalhes da logística)._

> _Com isso, seu sonho de **vender enquanto dorme** fica totalmente viável — e sem sobrecarregar sua equipe de 3 pessoas._

> _Se quiser, posso te guiar na implementação passo a passo. É só dizer! 🚀_

### Blueprint gerado

<details>
<summary>Expandir blueprint completo</summary>

# Blueprint do Time de Agentes

## Perfil da empresa
- Segmento: ecommerce
- Porte: pequeno (3 pessoas, R$ 30k/mês)
- Modelo de negócio: ecommerce multicanal de roupas femininas (Instagram, site próprio, Shopee, Mercado Livre)
- Dores: atendimento lento com mais de 100 mensagens/dia no WhatsApp, devoluções sem resposta, falta de automação em multicanal, gestão manual com planilha Excel

## Mapa de processos
- **atendimento**: respostas a dúvidas de clientes em WhatsApp, Instagram, Shopee e Mercado Livre
- **pedidos**: registro e acompanhamento de pedidos via planilha Excel
- **logística**: envio e rastreio de pedidos (detalhes não confirmados)
- **pós-venda**: gestão de devoluções, muitas vezes sem resposta
- **marketing**: presença no Instagram e possivelmente campanhas (não detalhado)

## Integrações detectadas
- whatsapp — WhatsApp Business (dados em: celular do dono)
- planilha — Excel (dados em: computador local ou Google Sheets)
- marketplace — Shopee (dados em: painel da loja)
- marketplace — Mercado Livre (dados em: painel da loja)
- ecommerce — site próprio (dados em: plataforma não especificada)

## Time de agentes proposto
### Atendente WhatsApp — SAC 24/7 multicanal
- Objetivo: responder automaticamente as perguntas mais frequentes em todos os canais e triar mensagens críticas
- Tarefas: responder FAQ (estoque, prazo, pagamento, trocas), encaminhar pedidos para o Coordenador de Pedidos, notificar cliente sobre status de devolução
- Integrações: whatsapp, instagram, shopee, mercado livre
- Conversa com: Coordenador de Pedidos, Coordenador de Pós-Venda
### Coordenador de Pedidos — operações
- Objetivo: centralizar e automatizar o fluxo de pedidos de todos os canais
- Tarefas: consolidar pedidos do site, Instagram, Shopee e ML numa única visão, atualizar status de envio e rastreio, notificar cliente automaticamente
- Integrações: excel, whatsapp, shopee, mercado livre, site próprio
- Conversa com: Atendente WhatsApp, Agente de Logística
### Coordenador de Pós-Venda — fidelização
- Objetivo: garantir que nenhuma solicitação de devolução fique sem resposta
- Tarefas: registrar pedidos de devolução, acompanhar prazo de resolução, solicitar feedback pós-troca/devolução
- Integrações: whatsapp, shopee, mercado livre, excel
- Conversa com: Atendente WhatsApp
### Agente de Logística — logística
- Objetivo: automatizar comunicação de status de entrega
- Tarefas: monitorar código de rastreio, avisar cliente sobre postagem e previsão de entrega, alertar equipe sobre atrasos
- Integrações: correios/transportadora (a confirmar), whatsapp, excel
- Conversa com: Coordenador de Pedidos

## Roadmap
1. **Atendente WhatsApp** — resolve a dor principal (100+ mensagens/dia) e é de implantação rápida
2. **Coordenador de Pedidos** — centraliza a operação multicanal e elimina retrabalho com planilhas
3. **Coordenador de Pós-Venda** — protege a reputação da loja e recupera vendas perdidas
4. **Agente de Logística** — fecha o ciclo de experiência do cliente com comunicação proativa

## Perguntas em aberto
- Quais são as 3 perguntas mais frequentes dos clientes?
- Como os pedidos são enviados? (Correios, transportadora, entrega própria?)
- Os clientes perguntam frequentemente 'onde está meu pedido?'?
- Há um processo definido para responder devoluções?
- As devoluções ocorrem mais em algum marketplace específico?
- A loja usa anúncios pagos ou tem catálogo digital organizado?

</details>

---

## Análise Global e Melhorias Sugeridas

### Recomendações de melhoria

1. Nenhum problema recorrente nesta rodada. Manter o avaliador como gate de regressão: rode `python scripts/eval_discovery.py` após qualquer mudança em `prompts.py`, `tools.py` ou na seed CNAE (há um smoke e2e opt-in via `QWENPAW_EVAL_E2E=1` no pytest).
2. Adicionar personas de segmentos FORA da seed (ex.: pet shop, oficina mecânica) para exercitar o caminho de raciocínio livre do `segment_lookup`.
3. Evoluir o scoring com critérios qualitativos (clareza das perguntas, empatia, não-repetição) usando LLM-as-judge em vez de só contagens.

---

_Relatório gerado por `scripts/eval_discovery.py` em 20260611_205049_
