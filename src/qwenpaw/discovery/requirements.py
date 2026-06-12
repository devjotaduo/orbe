# -*- coding: utf-8 -*-
"""Agente de requisitos: reflete sobre o que falta para cada agente operar."""
from __future__ import annotations

import json

from agentscope.agent import Agent, ReActConfig
from agentscope.permission import PermissionMode

from ..agents.model_factory import create_model_and_formatter
from .state import RequirementsReport
from .tools import DiscoverySession

_REQUIREMENTS_SYSTEM = """\
Você é o **engenheiro de implantação** do time de agentes que acabou de ser
desenhado para uma PME brasileira. Sua única missão: para CADA agente do
plano, levantar as informações CONCRETAS que ainda faltam para ele
desempenhar o papel no setor desta empresa — e redigir as mensagens que
serão enviadas no grupo de WhatsApp do empresário pedindo cada uma.

COMO PENSAR (exemplos por papel — adapte ao setor da empresa):
• Vendas/SDR → lista de produtos/serviços com PREÇOS, catálogo com fotos,
  política de desconto, se tem delivery/frete e quanto custa, formas de
  pagamento aceitas.
• Atendente → informações da empresa (endereço, horário de funcionamento),
  perguntas frequentes REAIS dos clientes com as respostas, e os casos
  NÃO-ÓBVIOS em que ele deve transferir para um humano (cliente irritado,
  pedido de reembolso acima de X, negociação especial...).
• Agendamento → lista de serviços com duração e preço, profissionais e
  seus horários, regras de remarcação/no-show.
• Marketing/Redes → fotos e vídeos dos produtos, tom de voz da marca,
  promoções vigentes, acesso ao Instagram.
• Logística/Pedidos → como consultar o status real (planilha? sistema?),
  transportadoras usadas, prazo por região.
• Pós-venda → política de troca/devolução, script de follow-up.

REGRAS:
1. Use o plano e a entrevista abaixo. NÃO peça o que o empresário JÁ
   informou — peça só o que falta de verdade.
2. 2 a 5 pedidos por agente. Cada pedido com: item (o que é), why (por que
   o agente precisa, em linguagem simples) e group_message (mensagem
   pronta para o grupo de WhatsApp — curta, simpática, direta, como se
   fosse uma pessoa do time pedindo; NUNCA tecnês, NUNCA prazo).
3. summary_for_owner: parágrafo de abertura do grupo — acolhedor, leigo,
   explica que por ali vamos pedir o que falta e que ele vai testar o
   atendente antes dos clientes.
4. Chame a tool `emit_requirements` UMA vez com o JSON completo. Não
   escreva o relatório no texto — só pela tool.

SCHEMA RequirementsReport (JSON):
{schema}
"""


def build_requirements_prompt() -> str:
    """System prompt da fase de requisitos com o schema embutido."""
    return _REQUIREMENTS_SYSTEM.format(
        schema=json.dumps(
            RequirementsReport.model_json_schema(),
            ensure_ascii=False,
            indent=2,
        )
    )


def build_requirements_agent(
    session: DiscoverySession,
    max_iters: int = 4,
) -> Agent:
    """Monta o agente de requisitos com o toolkit restrito da fase."""
    model, formatter = create_model_and_formatter()
    # Attach do formatter — padrão de react_agent.py ~171-180.
    innermost = model
    while hasattr(innermost, "_inner"):
        innermost = innermost._inner
    while hasattr(innermost, "_model"):
        innermost = innermost._model
    if hasattr(innermost, "formatter"):
        innermost.formatter = formatter
    agent = Agent(
        name="RequirementsAgent",
        system_prompt=build_requirements_prompt(),
        model=model,
        toolkit=session.build_requirements_toolkit(),
        react_config=ReActConfig(max_iters=max_iters),
    )
    # Mesmo padrão do discovery agent: tool única, in-process, só escreve
    # no out_dir da sessão — ver react_agent.py:196-198.
    agent.state.permission_context.mode = PermissionMode.BYPASS
    return agent


def build_requirements_input(session: DiscoverySession) -> str:
    """Monta o contexto (blueprint + entrevista) para o agente de requisitos."""
    bp_path = session.out_dir / "blueprint.json"
    blueprint_json = (
        bp_path.read_text(encoding="utf-8") if bp_path.exists() else "{}"
    )
    transcript = "\n".join(
        f"[{t.role}] {t.text}" for t in session.state.transcript
    )
    return (
        "PLANO DO TIME (blueprint.json):\n"
        f"{blueprint_json}\n\n"
        "RESUMO DA ENTREVISTA (o que o empresário já informou):\n"
        f"{transcript}\n\n"
        "Levante as informações pendentes por agente e chame "
        "emit_requirements."
    )
