# -*- coding: utf-8 -*-
"""
Avaliador end-to-end do Discovery Agent.

Roda 5 personas PME brasileiras com respostas pré-roteirizadas,
pontua os blueprints gerados e produz um relatório Markdown completo.

Uso:
    python scripts/eval_discovery.py
    python scripts/eval_discovery.py --out reports/meu_relatorio.md
    python scripts/eval_discovery.py --persona ecommerce_roupas
"""
from __future__ import annotations

import asyncio
import io
import sys
import tempfile
import traceback
from collections import deque
from contextlib import redirect_stdout
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional
from unittest.mock import patch

import click

# Garante importação do src/ quando executado como script solto
_SRC = Path(__file__).parent.parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))


# ─── Personas ────────────────────────────────────────────────────────────────

@dataclass
class Persona:
    id: str
    name: str
    description: str
    expected_segment: str
    script: list[str]   # respostas em ordem; última deve ser /fim


PERSONAS: list[Persona] = [
    Persona(
        id="ecommerce_roupas",
        name="Loja Virtual de Roupas",
        description="E-commerce de moda feminina, vende pelo Instagram e site próprio",
        expected_segment="ecommerce",
        script=[
            "Tenho uma loja virtual de roupas femininas. Vendemos pelo Instagram e site próprio.",
            "O maior problema é o atendimento. Recebo mais de 100 mensagens por dia no WhatsApp e não consigo responder todas.",
            "Uso WhatsApp Business e uma planilha Excel para controlar os pedidos. Não tenho CRM.",
            "Faturamos em torno de R$ 30 mil por mês. Somos 3 pessoas: eu, uma assistente e uma responsável pelo estoque.",
            "Vendo também na Shopee e no Mercado Livre. Tenho problemas com devoluções que ficam sem resposta.",
            "Meu sonho é conseguir vender enquanto durmo — automação total do atendimento e rastreio de pedidos.",
            "/fim",
        ],
    ),
    Persona(
        id="restaurante",
        name="Restaurante Familiar",
        description="Restaurante de comida caseira com salão e delivery pelo iFood",
        expected_segment="alimentacao",
        script=[
            "Tenho um restaurante de comida caseira. Atendo no salão e faço delivery pelo iFood.",
            "O maior problema é a gestão: pedidos do iFood chegam misturados com os do salão. Muito caos na cozinha.",
            "Uso o iFood, WhatsApp para delivery próprio, e o sistema da operadora de cartão. Tudo separado.",
            "Faturamos em torno de R$ 60 mil por mês. Temos 8 funcionários incluindo cozinha e salão.",
            "Quero um agente que responda clientes no WhatsApp sobre cardápio, horários e reservas automaticamente.",
            "/fim",
        ],
    ),
    Persona(
        id="clinica_medica",
        name="Clínica Médica",
        description="Clínica com 3 especialistas, atende convênios e particular",
        expected_segment="saude",
        script=[
            "Tenho uma clínica médica com 3 médicos: clínico geral, dermatologista e ortopedista.",
            "A recepção gasta o dia inteiro agendando e desmarcando consultas. Pacientes ligam para confirmar, remarcar.",
            "Usamos um software de clínica chamado Nuvem, integrado com Google Calendar. Também WhatsApp para confirmações.",
            "Atendemos convênios Unimed e Bradesco Saúde, e particular. Faturamos R$ 120 mil por mês.",
            "Quero automação de agendamento pelo WhatsApp com confirmação automática 24 horas antes da consulta.",
            "/fim",
        ],
    ),
    Persona(
        id="escola_idiomas",
        name="Escola de Idiomas",
        description="Escola de inglês e espanhol presencial e online, 120 alunos",
        expected_segment="educacao",
        script=[
            "Tenho uma escola de idiomas. Inglês e espanhol, aulas presenciais e online pelo Zoom.",
            "Tenho dificuldade em converter leads que chegam pelo Instagram em alunos matriculados. Muitos somem.",
            "Uso Instagram para captar alunos, WhatsApp para contato, e planilhas Google para controle de matrículas.",
            "Tenho 120 alunos ativos e 5 professores. Faturamento de R$ 45 mil por mês.",
            "Quero um agente que qualifique os leads automaticamente e agende a aula experimental.",
            "/fim",
        ],
    ),
    Persona(
        id="salao_beleza",
        name="Salão de Beleza",
        description="Salão com 5 profissionais, problema grave de no-shows",
        expected_segment="beleza",
        script=[
            "Tenho um salão de beleza com 5 profissionais: cabelo, manicure e estética.",
            "O maior problema é no-show. Clientes que marcam e não aparecem. Perdemos várias horas por semana.",
            "Usamos um app de agendamento chamado Booksy e WhatsApp para confirmações manuais.",
            "Faturamos R$ 25 mil por mês. Sou eu mais 4 profissionais autônomos.",
            "Quero confirmação automática 48h e 2h antes pelo WhatsApp, com link para remarcar se necessário.",
            "/fim",
        ],
    ),
    Persona(
        id="software_house",
        name="Software House B2B",
        description="Software house que desenvolve sistemas sob medida para empresas",
        expected_segment="tecnologia",
        script=[
            "Tenho uma software house. Desenvolvemos sistemas sob medida e temos um SaaS de gestão para clínicas.",
            "Nosso funil de vendas é todo manual. Leads chegam pelo site e LinkedIn e esfriam antes de receber proposta.",
            "Usamos Pipedrive como CRM, Slack interno, e Jira para os projetos. Suporte é por e-mail e fica sobrecarregado.",
            "Somos 12 pessoas: 8 devs, 2 comerciais, 1 designer e eu. Faturamos R$ 180 mil por mês.",
            "Quero automatizar a qualificação de leads e o primeiro atendimento do suporte do SaaS.",
            "/fim",
        ],
    ),
    Persona(
        id="construtora",
        name="Construtora de Reformas",
        description="Construtora focada em reformas residenciais e comerciais",
        expected_segment="construcao",
        script=[
            "Tenho uma construtora especializada em reformas residenciais e comerciais. Também fazemos obras pequenas.",
            "Orçamento é nossa maior dor. Cliente pede orçamento e a gente leva uma semana para responder. Muitos desistem.",
            "Usamos WhatsApp para tudo, planilha Excel para custos e Google Agenda para as visitas técnicas.",
            "Somos 15 pessoas entre engenheiros, mestres de obra e equipe. Faturamos uns R$ 250 mil por mês.",
            "Os clientes reclamam que não sabem como está a obra. Ligam toda semana pedindo atualização.",
            "Quero agilizar os orçamentos e dar visibilidade da obra para o cliente sem minha equipe parar para responder.",
            "/fim",
        ],
    ),
    Persona(
        id="advocacia",
        name="Escritório de Advocacia",
        description="Escritório de advocacia empresarial e trabalhista com 4 advogados",
        expected_segment="servicos_b2b",
        script=[
            "Tenho um escritório de advocacia. Atendemos empresas em direito trabalhista e tributário.",
            "Perdemos muito tempo respondendo clientes que perguntam sobre o andamento dos processos. Ligam toda semana.",
            "Usamos o Astrea para gestão dos processos, e-mail e WhatsApp para falar com clientes, e Excel no financeiro.",
            "Somos 4 advogados e 2 estagiários. Faturamos R$ 90 mil por mês.",
            "Captação é fraca: dependemos só de indicação. Não temos presença digital nem produção de conteúdo jurídico.",
            "Quero automatizar o informe de status dos processos e melhorar a captação de novos clientes empresariais.",
            "/fim",
        ],
    ),
]


# ─── Scoring ─────────────────────────────────────────────────────────────────

@dataclass
class CriterionScore:
    name: str
    score: float
    max_score: float
    note: str


@dataclass
class ScoreResult:
    persona_id: str
    criteria: list[CriterionScore] = field(default_factory=list)
    issues: list[str] = field(default_factory=list)
    positives: list[str] = field(default_factory=list)
    error: Optional[str] = None

    @property
    def total(self) -> float:
        return sum(c.score for c in self.criteria)

    @property
    def max_total(self) -> float:
        return sum(c.max_score for c in self.criteria)

    @property
    def pct(self) -> float:
        return (self.total / self.max_total * 100) if self.max_total else 0.0


def _add(result: ScoreResult, name: str, score: float, max_score: float, note: str):
    result.criteria.append(CriterionScore(name, score, max_score, note))


def score_session(
    persona: Persona,
    session,  # DiscoverySession
    blueprint_path: Optional[Path],
) -> ScoreResult:
    from qwenpaw.discovery.state import TeamBlueprint

    state = session.state
    result = ScoreResult(persona_id=persona.id)

    # 1. Segmento detectado (20 pts)
    detected = state.company.segment
    if detected == persona.expected_segment:
        _add(result, "Segmento", 20, 20, f"Correto: `{detected}`")
        result.positives.append(f"Segmento detectado corretamente: `{detected}`")
    elif detected:
        _add(result, "Segmento", 8, 20, f"Errado: `{detected}` (esperado: `{persona.expected_segment}`)")
        result.issues.append(f"Segmento detectado incorretamente: `{detected}` (esperado `{persona.expected_segment}`)")
    else:
        _add(result, "Segmento", 0, 20, "Não detectado")
        result.issues.append("Segmento NÃO detectado — `segment_lookup` não foi chamado ou falhou")

    # 2. Blueprint emitido (20 pts)
    if session.emitted:
        _add(result, "Blueprint gerado", 20, 20, "Emitido com sucesso")
        result.positives.append("Blueprint gerado e salvo com sucesso")
    else:
        _add(result, "Blueprint gerado", 0, 20, "Não emitido")
        result.issues.append("Blueprint NÃO emitido — a entrevista terminou sem conclusão")

    # 3. Qualidade do blueprint (40 pts, só pontuável se emitido)
    agents_count = 0
    roadmap_steps = 0
    open_questions = 0
    process_map_len = 0

    if blueprint_path and blueprint_path.exists():
        try:
            bp = TeamBlueprint.model_validate_json(
                blueprint_path.read_text(encoding="utf-8")
            )
            agents_count = len(bp.proposed_team)
            roadmap_steps = len(bp.roadmap)
            open_questions = len(bp.open_questions)
            process_map_len = len(bp.process_map)
        except Exception as exc:
            result.issues.append(f"Erro ao ler blueprint JSON: {exc}")

    # 3a. Agentes propostos (15 pts)
    if agents_count >= 3:
        _add(result, "Agentes propostos", 15, 15, f"{agents_count} agentes — equipe completa")
        result.positives.append(f"Time com {agents_count} agentes propostos")
    elif agents_count == 2:
        _add(result, "Agentes propostos", 10, 15, f"{agents_count} agentes — adequado mas pode expandir")
        result.positives.append(f"{agents_count} agentes propostos")
    elif agents_count == 1:
        _add(result, "Agentes propostos", 4, 15, "Apenas 1 agente — muito simples")
        result.issues.append("Apenas 1 agente proposto — time insuficiente para a maioria das PMEs")
    else:
        _add(result, "Agentes propostos", 0, 15, "Nenhum agente")
        result.issues.append("Nenhum agente proposto no blueprint")

    # 3b. Roadmap (10 pts)
    if roadmap_steps >= 3:
        _add(result, "Roadmap", 10, 10, f"{roadmap_steps} etapas — detalhado")
        result.positives.append(f"Roadmap com {roadmap_steps} etapas bem definidas")
    elif roadmap_steps == 2:
        _add(result, "Roadmap", 7, 10, "2 etapas — funcional")
    elif roadmap_steps == 1:
        _add(result, "Roadmap", 3, 10, "Apenas 1 etapa — superficial")
        result.issues.append("Roadmap com apenas 1 etapa — sem progressão de implantação")
    else:
        _add(result, "Roadmap", 0, 10, "Sem roadmap")
        result.issues.append("Roadmap vazio no blueprint")

    # 3c. Mapa de processos (10 pts)
    if process_map_len >= 2:
        _add(result, "Mapa de processos", 10, 10, f"{process_map_len} processos mapeados")
        result.positives.append(f"{process_map_len} processos mapeados no blueprint")
    elif process_map_len == 1:
        _add(result, "Mapa de processos", 5, 10, "1 processo — incompleto")
        result.issues.append("Apenas 1 processo no mapa — pode estar superficial")
    else:
        _add(result, "Mapa de processos", 0, 10, "Sem mapa de processos")
        result.issues.append("Mapa de processos ausente")

    # 3d. Perguntas em aberto (5 pts)
    if open_questions >= 2:
        _add(result, "Perguntas em aberto", 5, 5, f"{open_questions} perguntas documentadas")
        result.positives.append(f"{open_questions} perguntas em aberto documentadas (boa prática)")
    elif open_questions == 1:
        _add(result, "Perguntas em aberto", 3, 5, "1 pergunta — aceitável")
    else:
        _add(result, "Perguntas em aberto", 0, 5, "Nenhuma pergunta documentada")
        result.issues.append("Nenhuma pergunta em aberto — entrevista pode ter sido superficial")

    # 4. Integrações detectadas (10 pts)
    integ_count = len(state.integrations)
    if integ_count >= 2:
        _add(result, "Integrações detectadas", 10, 10, f"{integ_count} integrações")
        result.positives.append(f"{integ_count} integrações detectadas corretamente")
    elif integ_count == 1:
        _add(result, "Integrações detectadas", 5, 10, "1 integração — insuficiente")
        result.issues.append("Apenas 1 integração detectada — o empresário mencionou mais ferramentas")
    else:
        _add(result, "Integrações detectadas", 0, 10, "Nenhuma integração detectada")
        result.issues.append("Nenhuma integração detectada — o agente não usou `reflect` para capturar ferramentas")

    # 5. Profundidade da entrevista (10 pts)
    user_turns = len([t for t in state.transcript if t.role == "user"])
    if user_turns >= 5:
        _add(result, "Profundidade da entrevista", 10, 10, f"{user_turns} turnos do usuário")
        result.positives.append(f"Entrevista aprofundada: {user_turns} turnos do empresário")
    elif user_turns >= 3:
        _add(result, "Profundidade da entrevista", 6, 10, f"{user_turns} turnos — razoável")
    elif user_turns >= 1:
        _add(result, "Profundidade da entrevista", 2, 10, f"{user_turns} turno(s) — muito curto")
        result.issues.append(f"Entrevista muito curta: apenas {user_turns} turno(s) do usuário")
    else:
        _add(result, "Profundidade da entrevista", 0, 10, "Nenhum turno capturado")
        result.issues.append("Nenhum turno de usuário na transcrição — erro de captura")

    return result


# ─── Execução de uma sessão ──────────────────────────────────────────────────

@dataclass
class SessionRun:
    persona: Persona
    score: ScoreResult
    stdout_log: str
    session: object   # DiscoverySession
    out_dir: Path


async def _run_persona(persona: Persona, tmp_dir: Path) -> SessionRun:
    """Executa uma sessão completa com respostas pré-roteirizadas."""
    from qwenpaw.discovery import run_discovery_session
    import qwenpaw.discovery.runner as runner_mod

    script_queue: deque[str] = deque(persona.script)

    def scripted_input(_prompt: str) -> str:
        if script_queue:
            answer = script_queue.popleft()
            # Escreve para o stdout capturado para aparecer no log
            print(f"Você: {answer}")
            return answer
        return "/fim"

    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            with patch.object(runner_mod, "_read_user_input", scripted_input):
                session = await run_discovery_session(
                    session_id=persona.id,
                    out_dir=tmp_dir,
                )
        score = score_session(
            persona, session, tmp_dir / "blueprint.json"
        )
    except Exception as exc:
        score = ScoreResult(persona_id=persona.id, error=traceback.format_exc())
        session = None  # type: ignore[assignment]
        print(f"[ERRO] {persona.name}: {exc}", file=sys.stderr)

    return SessionRun(
        persona=persona,
        score=score,
        stdout_log=buf.getvalue(),
        session=session,
        out_dir=tmp_dir,
    )


# ─── Geração do relatório ────────────────────────────────────────────────────

# (padrão presente nos issues, recomendação concreta)
_RECOMMENDATION_MAP: list[tuple[str, str]] = [
    (
        "Segmento NÃO detectado",
        "**Reforçar o `segment_lookup`** — o agente não classificou o segmento. "
        "Verifique se o prompt exige a chamada na primeira resposta e se as "
        "keywords da seed cobrem o vocabulário usado pelo empresário.",
    ),
    (
        "Segmento detectado incorretamente",
        "**Corrigir a classificação de segmento** — a chave gravada difere da "
        "esperada. Confira a proteção de `company.segment` no `reflect` e se há "
        "colisão de keywords entre segmentos na seed.",
    ),
    (
        "agente proposto",
        "**Reforçar o time mínimo no prompt** — blueprints saíram com menos de 3 "
        "agentes. Revise a seção 'TIME MÍNIMO' do system prompt e o exemplo "
        "few-shot.",
    ),
    (
        "Nenhum agente proposto",
        "**Blueprint sem time** — o JSON emitido veio com `proposed_team` vazio. "
        "Endureça a instrução de qualidade do blueprint no prompt.",
    ),
    (
        "Blueprint NÃO emitido",
        "**Garantir a emissão do blueprint** — a entrevista terminou sem "
        "`emit_blueprint`. Avalie aumentar `max_iters` em "
        "`build_discovery_agent` ou reforçar a instrução de encerramento.",
    ),
    (
        "Roadmap",
        "**Exigir roadmap com 3+ etapas** — roadmaps superficiais ou vazios. "
        "Reforce no prompt que o roadmap deve progredir do mais simples ao mais "
        "complexo.",
    ),
    (
        "processo",
        "**Aprofundar o mapa de processos** — menos de 2 processos mapeados. O "
        "agente deve explorar as 5 áreas obrigatórias antes de emitir.",
    ),
    (
        "integração",
        "**Melhorar captura de integrações** — o `reflect` não registrou as "
        "ferramentas mencionadas. Confira o alerta de integrações vazias no "
        "resultado do `reflect`.",
    ),
    (
        "pergunta em aberto",
        "**Documentar lacunas** — blueprints sem `open_questions`. Toda "
        "informação não confirmada deve virar pergunta em aberto.",
    ),
    (
        "Entrevista muito curta",
        "**Aprofundar a entrevista** — poucas trocas antes de emitir. O agente "
        "deve cobrir as 5 áreas antes de aceitar encerrar.",
    ),
]

_MAINTENANCE_RECS = [
    "Nenhum problema recorrente nesta rodada. Manter o avaliador como gate de "
    "regressão: rode `python scripts/eval_discovery.py` após qualquer mudança "
    "em `prompts.py`, `tools.py` ou na seed CNAE (há um smoke e2e opt-in via "
    "`QWENPAW_EVAL_E2E=1` no pytest).",
    "Adicionar personas de segmentos FORA da seed (ex.: pet shop, oficina "
    "mecânica) para exercitar o caminho de raciocínio livre do "
    "`segment_lookup`.",
    "Evoluir o scoring com critérios qualitativos (clareza das perguntas, "
    "empatia, não-repetição) usando LLM-as-judge em vez de só contagens.",
]


def _build_recommendations(runs: list[SessionRun]) -> list[str]:
    """Deriva recomendações dos problemas realmente encontrados na rodada."""
    all_issues = " | ".join(
        issue
        for run in runs
        if not run.score.error
        for issue in run.score.issues
    )
    recs = [rec for marker, rec in _RECOMMENDATION_MAP if marker in all_issues]
    if any(run.score.error for run in runs):
        failed = ", ".join(
            run.persona.name for run in runs if run.score.error
        )
        recs.append(
            f"**Investigar cenários com ERRO** ({failed}) — o traceback "
            f"completo está na seção do cenário."
        )
    return recs or list(_MAINTENANCE_RECS)

def _bar(score: float, max_score: float, width: int = 20) -> str:
    filled = int(round(score / max_score * width)) if max_score else 0
    return "█" * filled + "░" * (width - filled)


def _grade(pct: float) -> str:
    if pct >= 90:
        return "A — Excelente"
    if pct >= 75:
        return "B — Bom"
    if pct >= 60:
        return "C — Adequado"
    if pct >= 40:
        return "D — Insuficiente"
    return "F — Crítico"


def generate_report(runs: list[SessionRun], run_ts: str) -> str:
    lines: list[str] = []

    lines += [
        "# Relatório de Avaliação — Discovery Agent",
        "",
        f"**Data:** {run_ts}  ",
        f"**Cenários testados:** {len(runs)}  ",
        f"**Pontuação máxima por cenário:** 100 pts  ",
        "",
    ]

    # Sumário
    lines += ["## Sumário Executivo", ""]
    valid = [r for r in runs if r.score.error is None]
    if valid:
        avg = sum(r.score.pct for r in valid) / len(valid)
        lines += [
            f"| Cenário | Segmento | Blueprint | Score | Nota |",
            f"|---------|----------|-----------|-------|------|",
        ]
        for run in runs:
            s = run.score
            if s.error:
                lines.append(f"| {run.persona.name} | — | — | ERRO | — |")
                continue
            seg_ok = "✅" if run.session and run.session.state.company.segment == run.persona.expected_segment else "❌"
            bp_ok = "✅" if run.session and run.session.emitted else "❌"
            lines.append(
                f"| {run.persona.name} | {seg_ok} | {bp_ok} "
                f"| {s.total:.0f}/{s.max_total:.0f} ({s.pct:.0f}%) "
                f"| {_grade(s.pct)} |"
            )
        lines += ["", f"**Média geral:** {avg:.1f}% — {_grade(avg)}", ""]
    else:
        lines += ["Todos os cenários falharam com erro.", ""]

    # Detalhes por cenário
    for run in runs:
        lines += ["---", "", f"## Cenário: {run.persona.name}", ""]
        lines += [
            f"- **Descrição:** {run.persona.description}",
            f"- **Segmento esperado:** `{run.persona.expected_segment}`",
        ]

        if run.score.error:
            lines += [
                "",
                "### ❌ Erro durante a execução",
                "",
                "```",
                run.score.error.strip(),
                "```",
                "",
            ]
            continue

        detected = run.session.state.company.segment if run.session else "—"
        lines += [
            f"- **Segmento detectado:** `{detected or '—'}`",
            f"- **Blueprint emitido:** {'✅ Sim' if run.session and run.session.emitted else '❌ Não'}",
            f"- **Score:** {run.score.total:.0f}/{run.score.max_total:.0f} ({run.score.pct:.0f}%) — {_grade(run.score.pct)}",
            "",
        ]

        # Barra de score visual
        lines += [
            "```",
            f"Score  [{_bar(run.score.total, run.score.max_total)}] {run.score.total:.0f}/{run.score.max_total:.0f}",
            "```",
            "",
        ]

        # Critérios
        lines += ["### Pontuação por critério", ""]
        lines += ["| Critério | Score | Máx | Barra | Observação |"]
        lines += ["|----------|------:|----:|-------|------------|"]
        for c in run.score.criteria:
            bar = _bar(c.score, c.max_score, 10)
            lines.append(f"| {c.name} | {c.score:.0f} | {c.max_score:.0f} | `{bar}` | {c.note} |")
        lines.append("")

        if run.score.positives:
            lines += ["### ✅ Pontos positivos", ""]
            lines += [f"- {p}" for p in run.score.positives]
            lines.append("")

        if run.score.issues:
            lines += ["### ❌ Problemas encontrados", ""]
            lines += [f"- {i}" for i in run.score.issues]
            lines.append("")

        # Transcrição
        lines += ["### Transcrição da entrevista", ""]
        if run.stdout_log.strip():
            for raw_line in run.stdout_log.splitlines():
                line = raw_line.strip()
                if not line:
                    lines.append("")
                elif line.startswith("Você:"):
                    lines.append(f"> **🧑 Empresário:** {line[5:].strip()}")
                elif line.startswith("Consultor:"):
                    lines.append(f"> **🤖 Consultor:** {line[10:].strip()}")
                else:
                    lines.append(f"> _{line}_")
        else:
            lines.append("_Transcrição vazia._")
        lines.append("")

        # Blueprint resumido
        bp_path = run.out_dir / "blueprint.md"
        if bp_path.exists():
            lines += [
                "### Blueprint gerado",
                "",
                "<details>",
                "<summary>Expandir blueprint completo</summary>",
                "",
                bp_path.read_text(encoding="utf-8"),
                "</details>",
                "",
            ]

    # Melhorias globais
    lines += ["---", "", "## Análise Global e Melhorias Sugeridas", ""]

    all_issues: list[str] = []
    for run in runs:
        if not run.score.error:
            all_issues.extend(run.score.issues)

    if all_issues:
        issue_counts: dict[str, int] = {}
        for issue in all_issues:
            key = issue.split(":")[0].split("—")[0].strip()
            issue_counts[key] = issue_counts.get(key, 0) + 1

        lines += ["### Problemas mais frequentes", ""]
        for issue, count in sorted(issue_counts.items(), key=lambda x: -x[1]):
            badge = f"[{count}/{len(runs)} cenários]"
            lines.append(f"- **{badge}** {issue}")
        lines.append("")

    lines += ["### Recomendações de melhoria", ""]
    for n, rec in enumerate(_build_recommendations(runs), 1):
        lines.append(f"{n}. {rec}")
    lines += [
        "",
        "---",
        "",
        f"_Relatório gerado por `scripts/eval_discovery.py` em {run_ts}_",
    ]

    return "\n".join(lines) + "\n"


# ─── CLI ─────────────────────────────────────────────────────────────────────

@click.command()
@click.option(
    "--out", "out_path",
    default=None,
    help="Caminho do relatório .md. Default: reports/discovery_eval_<ts>.md",
)
@click.option(
    "--persona", "persona_id",
    default=None,
    help="Rodar apenas um persona pelo ID (ex: ecommerce_roupas).",
)
def main(out_path: Optional[str], persona_id: Optional[str]) -> None:
    """Avalia o Discovery Agent com personas PME pré-roteirizadas."""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_file = Path(out_path) if out_path else Path("reports") / f"discovery_eval_{ts}.md"
    out_file.parent.mkdir(parents=True, exist_ok=True)

    personas = PERSONAS
    if persona_id:
        personas = [p for p in PERSONAS if p.id == persona_id]
        if not personas:
            ids = ", ".join(p.id for p in PERSONAS)
            raise click.BadParameter(f"Persona não encontrada. Disponíveis: {ids}", param_hint="--persona")

    click.echo(f"Discovery Agent Evaluator — {len(personas)} cenário(s)\n")

    runs: list[SessionRun] = []
    with tempfile.TemporaryDirectory(prefix="qwenpaw_eval_") as tmp_root:
        for i, persona in enumerate(personas, 1):
            click.echo(f"[{i}/{len(personas)}] {persona.name}...", nl=False)
            persona_dir = Path(tmp_root) / persona.id
            persona_dir.mkdir()
            run = asyncio.run(_run_persona(persona, persona_dir))
            runs.append(run)
            if run.score.error:
                click.echo(" ❌ ERRO")
            else:
                click.echo(f" {run.score.total:.0f}/{run.score.max_total:.0f} ({run.score.pct:.0f}%)")

        # Lê arquivos antes de deletar o diretório temporário
        report = generate_report(runs, ts)

    out_file.write_text(report, encoding="utf-8")
    click.echo(f"\nRelatório salvo em: {out_file}")

    if runs:
        valid = [r for r in runs if r.score.error is None]
        if valid:
            avg = sum(r.score.pct for r in valid) / len(valid)
            click.echo(f"Média geral: {avg:.1f}% — {_grade(avg)}")


if __name__ == "__main__":
    main()
