# -*- coding: utf-8 -*-
"""DiscoverySession: estado mutável + as três tools do discovery agent."""
from __future__ import annotations

import json
from pathlib import Path

from agentscope.message import TextBlock, ToolResultState
from agentscope.tool import FunctionTool, ToolChunk, Toolkit

import re

from .segments.taxonomy import lookup_connectors, lookup_segment
from .state import (
    DiscoveryState,
    Integration,
    OnboardingInfo,
    OpenArea,
    ReflectUpdate,
    RequirementsReport,
    TeamBlueprint,
    Turn,
)


def _ok(text: str) -> ToolChunk:
    return ToolChunk(
        is_last=True,
        state=ToolResultState.SUCCESS,
        content=[TextBlock(type="text", text=text)],
    )


def _err(text: str) -> ToolChunk:
    return ToolChunk(
        is_last=True,
        state=ToolResultState.ERROR,
        content=[TextBlock(type="text", text=text)],
    )


def _friendly_tool_name(ref: str, bp: TeamBlueprint) -> str:
    """Converte 'origin:slug' no nome amigável do conector, se houver."""
    slug = ref.split(":", 1)[1] if ":" in ref else ref
    for c in bp.recommended_connectors:
        if c.slug_or_url and c.slug_or_url == slug:
            return c.name
        if c.name.lower() == slug.lower():
            return c.name
    return slug.replace("-", " ").replace("_", " ").strip().title()


def _blueprint_to_markdown(bp: TeamBlueprint) -> str:
    """Relatório do empresário: linguagem simples, sem jargão, sem prazos."""
    cp = bp.company_profile
    lines: list[str] = ["# Seu Time de Agentes\n"]
    lines.append(
        "Preparamos este plano com base na nossa conversa. Aqui está o que "
        "entendemos do seu negócio e o time que vamos montar para você.\n"
    )

    lines.append("## O que entendemos do seu negócio")
    if cp.business_model:
        lines.append(f"- O que a empresa faz: {cp.business_model}")
    if cp.size:
        lines.append(f"- Tamanho da operação: {cp.size}")
    if cp.pains:
        lines.append("- Desafios que você nos contou:")
        for pain in cp.pains:
            lines.append(f"  - {pain}")

    if bp.process_map:
        lines.append("\n## Como o trabalho acontece hoje")
        for p in bp.process_map:
            lines.append(f"- **{p.name}**: {p.description}")

    if bp.detected_integrations:
        lines.append("\n## Ferramentas que você já usa")
        for i in bp.detected_integrations:
            loc = f" (fica em: {i.data_location})" if i.data_location else ""
            lines.append(f"- {i.name}{loc}")

    lines.append("\n## Quem vai trabalhar para você")
    for a in bp.proposed_team:
        lines.append(f"### {a.name} — {a.role}")
        lines.append(f"- Missão: {a.objective}")
        if a.tasks:
            lines.append("- O que ele faz no dia a dia:")
            for task in a.tasks:
                lines.append(f"  - {task}")
        if a.tools_integrations:
            friendly = sorted(
                {_friendly_tool_name(t, bp) for t in a.tools_integrations}
            )
            lines.append(f"- Vai trabalhar com: {', '.join(friendly)}")
        if a.talks_to:
            lines.append(f"- Trabalha junto com: {', '.join(a.talks_to)}")

    if bp.roadmap:
        lines.append("\n## Por onde vamos começar")
        lines.append(
            "Cada etapa entra no ar quando a anterior estiver redonda — "
            "você acompanha e aprova tudo."
        )
        for r in sorted(bp.roadmap, key=lambda x: x.order):
            lines.append(f"{r.order}. **{r.title}** — {r.rationale}")

    if bp.open_questions:
        lines.append("\n## O que ainda vamos confirmar com você")
        for q in bp.open_questions:
            lines.append(f"- {q}")

    lines.append("\n## Próximos passos")
    if bp.onboarding:
        contato = (
            f"{bp.onboarding.responsible_name} "
            f"({bp.onboarding.whatsapp_number})"
        )
    else:
        contato = "você"
    lines.append(
        "1. Vamos conectar o WhatsApp da sua empresa — ele será o canal "
        "oficial de atendimento do seu time de agentes."
    )
    lines.append(
        f"2. Vamos criar um grupo no WhatsApp com {contato} para "
        "acompanhar tudo de perto."
    )
    lines.append(
        "3. Pelo grupo, você nos passa as informações que faltarem e "
        "testa o atendente antes de ele começar a falar com seus clientes."
    )
    lines.append(
        "\nVamos montar o seu time de agentes — e você acompanha cada "
        "passo pelo grupo. 🤝"
    )
    return "\n".join(lines) + "\n"


def _requirements_to_markdown(
    report: RequirementsReport, state: DiscoveryState
) -> str:
    """Relatório leigo de informações pendentes, por agente."""
    lines: list[str] = ["# O que falta para o seu time começar\n"]
    if report.summary_for_owner:
        lines.append(report.summary_for_owner + "\n")
    for item in report.items:
        lines.append(f"## {item.agent_name}")
        if not item.requests:
            lines.append("- Nada pendente — pronto para começar! ✅")
            continue
        for req in item.requests:
            lines.append(f"- **{req.item}**")
            lines.append(f"  - Por quê: {req.why}")
        lines.append("")
    contato = state.onboarding
    if contato:
        lines.append(
            f"\n_Vamos pedir essas informações no grupo do WhatsApp com "
            f"{contato.responsible_name} ({contato.whatsapp_number})._"
        )
    else:
        lines.append(
            "\n_Vamos pedir essas informações no grupo do WhatsApp assim "
            "que o contato for confirmado._"
        )
    return "\n".join(lines) + "\n"


def _group_messages_markdown(
    report: RequirementsReport, state: DiscoveryState
) -> str:
    """Mensagens prontas para enviar no grupo de onboarding."""
    lines: list[str] = ["# Mensagens prontas para o grupo do WhatsApp\n"]
    contato = state.onboarding
    if contato:
        lines.append(
            f"_Grupo de onboarding com {contato.responsible_name} "
            f"({contato.whatsapp_number})._\n"
        )
    lines.append("## Mensagem de abertura\n")
    lines.append("```")
    lines.append(
        report.summary_for_owner
        or "Olá! Este é o grupo de acompanhamento do seu time de agentes. "
        "Por aqui vamos pedir as informações que faltam e você testa o "
        "atendente antes de ele falar com seus clientes."
    )
    lines.append("```\n")
    for item in report.items:
        if not item.requests:
            continue
        lines.append(f"## Para o {item.agent_name}\n")
        for req in item.requests:
            lines.append("```")
            lines.append(req.group_message)
            lines.append("```\n")
    return "\n".join(lines) + "\n"


class DiscoverySession:
    """Mantém o DiscoveryState e expõe as tools que o operam."""

    def __init__(self, state: DiscoveryState, out_dir: Path) -> None:
        self.state = state
        self.out_dir = Path(out_dir)
        self.emitted = False
        self.requirements_emitted = False
        self.requirements: RequirementsReport | None = None

    # --- tools -----------------------------------------------------------

    async def segment_lookup(self, description: str) -> ToolChunk:
        """Classifica o segmento da empresa a partir da descrição fornecida.

        Use assim que o empresário descrever o que a empresa faz. Retorna os
        'trilhos' do segmento (áreas, processos, dores e integrações típicas)
        quando a empresa cai num segmento conhecido; caso contrário sinaliza
        que você deve raciocinar livremente sobre o segmento.

        Args:
            description: O que a empresa faz, nas palavras do empresário.

        Returns:
            `ToolChunk`: trilhos do segmento, ou aviso de fallback livre.
        """
        info = lookup_segment(description)
        if info is None:
            ids = [a.id for a in self.state.open_areas]
            if "validar-segmento" not in ids:
                self.state.open_areas.append(
                    OpenArea(
                        id="validar-segmento",
                        topic=(
                            "validar a taxonomia deste segmento"
                            " (fora da seed)"
                        ),
                        confidence=0.1,
                        priority=4,
                    )
                )
            return _ok(
                "Segmento não está na taxonomia curada. Raciocine de"
                " forma LIVRE sobre as áreas, processos, dores e"
                " integrações típicas deste tipo de negócio antes de"
                " continuar a entrevista."
            )
        self.state.company.segment = info.key
        if info.cnae:
            self.state.company.cnae = info.cnae
        payload = {
            "segment_key": info.key,
            "label": info.label,
            "typical_areas": info.typical_areas,
            "typical_processes": info.typical_processes,
            "common_pains": info.common_pains,
            "common_integrations": info.common_integrations,
        }
        return _ok(
            f"Segmento identificado: {info.key} ({info.label}). Use estes "
            f"trilhos como ponto de partida e APROFUNDE com perguntas:\n"
            + json.dumps(payload, ensure_ascii=False, indent=2)
        )

    async def connector_lookup(self, integration_kind: str) -> ToolChunk:
        """Consulta a whitelist curada de conectores de um tipo de integração.

        Chame na hora de MONTAR O BLUEPRINT, uma vez para cada integração
        detectada ou proposta (ex.: 'whatsapp', 'crm', 'planilha'). Retorna
        conectores concretos com origem, slug, status e notas de risco.
        Prefira status 'recomendado'; inclua 'validar' citando a nota de
        risco; trate 'build' como item de roadmap (conector próprio).

        Args:
            integration_kind: Tipo canônico da integração (whatsapp, crm,
                planilha, agenda, erp, pagamento, fiscal, ecommerce,
                helpdesk, email, delivery, voz, juridico, lms, pdv,
                prontuario, chat-interno, analytics).

        Returns:
            `ToolChunk`: conectores curados do tipo, ou orientação de build.
        """
        try:
            conns = lookup_connectors(
                integration_kind,
                segment=self.state.company.segment,
            )
        except ValueError as exc:
            return _err(f"{exc} Reenvie com um kind válido.")
        if not conns:
            return _ok(
                f"Nenhum conector curado para '{integration_kind}'. "
                "Registre no blueprint um ConnectorRef com origin='build' e "
                "status='build', e adicione uma open_question sobre essa "
                "integração."
            )
        payload = [
            {
                "integration_kind": c.integration_kind,
                "name": c.name,
                "origin": c.origin,
                "slug_or_url": c.slug_or_url,
                "status": c.status,
                "notes": c.notes,
            }
            for c in conns
        ]
        return _ok(
            "Conectores curados (use em recommended_connectors; referência "
            "curta em tools_integrations = '<origin>:<slug>'):\n"
            + json.dumps(payload, ensure_ascii=False, indent=2)
        )

    async def reflect(self, learned: str, updates_json: str) -> ToolChunk:
        """Raciocínio profundo sobre a última resposta do empresário.

        Chame ESTE tool ANTES de fazer a próxima pergunta, sempre. Atualiza o
        estado interno da entrevista: o que aprendeu, quais áreas pode fechar,
        quais novas ramificações abrir, integrações detectadas e ajustes de
        confiança. É o que torna a entrevista um raciocínio, não um formulário.

        Args:
            learned: Resumo em 1-2 frases do que ficou entendido agora.
            updates_json: JSON conforme o schema ReflectUpdate, com os campos:
                learned, close_area_ids (list[str]), new_areas (list de
                {id, topic, confidence, priority}), integrations (list de
                {kind, name, data_location, confidence}), company_updates
                (dict parcial de CompanyProfile), confidence_updates
                (dict area_id->float).

        Returns:
            `ToolChunk`: resumo do estado atualizado e próxima área foco.
        """
        try:
            upd = ReflectUpdate.model_validate_json(updates_json)
        except Exception as exc:
            return _err(
                f"updates_json inválido ({exc}). Reenvie um JSON válido "
                f"conforme o schema ReflectUpdate."
            )

        # fecha áreas
        if upd.close_area_ids:
            self.state.open_areas = [
                a for a in self.state.open_areas
                if a.id not in upd.close_area_ids
            ]

        # ajusta confiança
        for a in self.state.open_areas:
            if a.id in upd.confidence_updates:
                a.confidence = max(0.0, min(1.0, upd.confidence_updates[a.id]))

        # adiciona novas áreas (sem duplicar id)
        existing = {a.id for a in self.state.open_areas}
        for na in upd.new_areas:
            if na.id not in existing:
                self.state.open_areas.append(na)
                existing.add(na.id)

        # integrações (dedup por (kind, name))
        seen = {(i.kind, i.name) for i in self.state.integrations}
        for ig in upd.integrations:
            if (ig.kind, ig.name) not in seen:
                self.state.integrations.append(ig)
                seen.add((ig.kind, ig.name))

        # company — protege `segment` após ser fixado por segment_lookup
        if upd.company_updates:
            merged = self.state.company.model_dump()
            for k, v in upd.company_updates.items():
                if k == "segment" and merged.get("segment"):
                    continue  # segment_lookup já definiu a chave canônica
                if k in merged and v is not None:
                    merged[k] = v
            cls = type(self.state.company)
            self.state.company = cls.model_validate(merged)

        self.state.transcript.append(Turn(role="assistant", text=learned))

        focus = self.state.next_focus()
        if focus:
            focus_txt = f"{focus.id} — {focus.topic}"
        else:
            focus_txt = "nenhuma (pode emitir)"
        msg = (
            f"Estado atualizado. Próxima área foco: {focus_txt}. "
            f"Pronto p/ emitir? {self.state.ready_to_emit()}"
        )
        user_turns = sum(1 for t in self.state.transcript if t.role == "user")
        if not self.state.integrations and user_turns >= 2:
            msg += (
                " ATENÇÃO: nenhuma integração registrada ainda — pergunte "
                "quais sistemas/ferramentas a empresa usa (CRM, planilha, "
                "WhatsApp, ERP...) e registre via reflect."
            )
        return _ok(msg)

    async def register_onboarding(
        self,
        whatsapp_number: str,
        responsible_name: str,
        is_owner: bool = True,
    ) -> ToolChunk:
        """Registra o WhatsApp do empresário (ou responsável) para onboarding.

        Chame assim que o empresário informar o número. Esse contato será
        usado para conectar o WhatsApp da empresa como canal oficial e criar
        o grupo de acompanhamento (informações faltantes + testes do
        atendente). Peça SEMPRE antes de encerrar a entrevista.

        Args:
            whatsapp_number: Número com DDD, ex.: "11 98765-4321" ou
                "+55 11 98765-4321".
            responsible_name: Nome de quem vai responder no grupo.
            is_owner: True se for o próprio dono; False se for outra pessoa
                responsável pela parte técnica.

        Returns:
            `ToolChunk`: confirmação, ou erro se o número for inválido.
        """
        digits = re.sub(r"\D", "", whatsapp_number or "")
        if digits.startswith("55") and len(digits) > 11:
            digits = digits[2:]
        if len(digits) not in (10, 11):
            return _err(
                f"Número '{whatsapp_number}' inválido — esperado DDD + "
                f"número (10-11 dígitos). Confirme com o empresário e "
                f"chame register_onboarding de novo."
            )
        normalized = f"+55 ({digits[:2]}) {digits[2:-4]}-{digits[-4:]}"
        self.state.onboarding = OnboardingInfo(
            whatsapp_number=normalized,
            responsible_name=(responsible_name or "").strip() or "Responsável",
            is_owner=is_owner,
        )
        return _ok(
            f"Contato registrado: {self.state.onboarding.responsible_name} "
            f"— {normalized}. Será usado para conectar o canal oficial e "
            f"criar o grupo de onboarding."
        )

    async def emit_blueprint(self, blueprint_json: str) -> ToolChunk:
        """Valida e grava o blueprint final do time de agentes.

        Só chame quando as áreas prioritárias estiverem suficientemente
        compreendidas (ou o empresário sinalizar fim). Grava blueprint.json
        e blueprint.md no diretório da sessão. Antes de chamar, peça o
        WhatsApp do responsável via register_onboarding.

        Args:
            blueprint_json: JSON conforme o schema TeamBlueprint.

        Returns:
            `ToolChunk`: confirmação com os caminhos, ou o erro de validação.
        """
        try:
            bp = TeamBlueprint.model_validate_json(blueprint_json)
        except Exception as exc:
            return _err(
                f"Blueprint inválido ({exc}). Corrija o JSON conforme o "
                f"schema TeamBlueprint e chame emit_blueprint de novo."
            )
        # o contato de onboarding vive no estado — fonte da verdade
        if self.state.onboarding is not None:
            bp.onboarding = self.state.onboarding
        self.out_dir.mkdir(parents=True, exist_ok=True)
        (self.out_dir / "blueprint.json").write_text(
            bp.model_dump_json(indent=2), encoding="utf-8"
        )
        (self.out_dir / "blueprint.md").write_text(
            _blueprint_to_markdown(bp), encoding="utf-8"
        )
        self.emitted = True
        j = self.out_dir / "blueprint.json"
        m = self.out_dir / "blueprint.md"
        msg = f"Blueprint gravado em {j} e {m}. Entrevista concluída."
        if self.state.onboarding is None:
            msg += (
                " ATENÇÃO: nenhum contato de WhatsApp registrado — se a "
                "conversa permitir, peça o número e chame "
                "register_onboarding antes de se despedir."
            )
        return _ok(msg)

    async def emit_requirements(self, requirements_json: str) -> ToolChunk:
        """Valida e grava o relatório de informações pendentes por agente.

        Use na fase pós-blueprint: para CADA agente do time proposto, liste
        as informações concretas que faltam para ele operar. Grava
        requirements.json, informacoes_pendentes.md e mensagens_grupo.md
        no diretório da sessão.

        Args:
            requirements_json: JSON conforme o schema RequirementsReport:
                items (list de {agent_name, requests: [{item, why,
                group_message}]}) e summary_for_owner (parágrafo leigo que
                abre o grupo de WhatsApp).

        Returns:
            `ToolChunk`: confirmação com os caminhos, ou o erro de validação.
        """
        try:
            report = RequirementsReport.model_validate_json(requirements_json)
        except Exception as exc:
            return _err(
                f"Relatório inválido ({exc}). Corrija o JSON conforme o "
                f"schema RequirementsReport e chame emit_requirements de novo."
            )
        if not report.items:
            return _err(
                "Relatório vazio — liste as informações pendentes de cada "
                "agente do blueprint (mínimo 1 agente)."
            )
        self.out_dir.mkdir(parents=True, exist_ok=True)
        (self.out_dir / "requirements.json").write_text(
            report.model_dump_json(indent=2), encoding="utf-8"
        )
        (self.out_dir / "informacoes_pendentes.md").write_text(
            _requirements_to_markdown(report, self.state), encoding="utf-8"
        )
        (self.out_dir / "mensagens_grupo.md").write_text(
            _group_messages_markdown(report, self.state), encoding="utf-8"
        )
        self.requirements_emitted = True
        self.requirements = report
        return _ok(
            f"Relatório de pendências gravado em "
            f"{self.out_dir / 'informacoes_pendentes.md'} e mensagens do "
            f"grupo em {self.out_dir / 'mensagens_grupo.md'}."
        )

    # --- toolkit ---------------------------------------------------------

    def build_toolkit(self) -> Toolkit:
        return Toolkit(
            tools=[
                FunctionTool(self.segment_lookup, is_read_only=False),
                FunctionTool(self.reflect, is_read_only=False),
                FunctionTool(self.register_onboarding, is_read_only=False),
                FunctionTool(self.emit_blueprint, is_read_only=False),
                FunctionTool(self.connector_lookup, is_read_only=True),
            ]
        )

    def build_requirements_toolkit(self) -> Toolkit:
        """Toolkit da fase de requisitos (pós-blueprint)."""
        return Toolkit(
            tools=[
                FunctionTool(self.emit_requirements, is_read_only=False),
            ]
        )
