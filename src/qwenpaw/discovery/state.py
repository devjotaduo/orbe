# -*- coding: utf-8 -*-
"""Schemas Pydantic do discovery agent.

Estado da entrevista e blueprint do time.
"""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


# --- Estado da entrevista -------------------------------------------------

class CompanyProfile(BaseModel):
    segment: Optional[str] = None
    cnae: Optional[str] = None
    size: Optional[str] = None
    business_model: Optional[str] = None
    pains: list[str] = Field(default_factory=list)


class OpenArea(BaseModel):
    """Uma ramificação ainda por aprofundar na entrevista."""
    id: str
    topic: str
    confidence: float = Field(ge=0.0, le=1.0, default=0.0)
    priority: int = Field(ge=1, le=5, default=3)
    notes: str = ""


class Integration(BaseModel):
    kind: str            # crm | erp | planilha | whatsapp | outro
    name: str
    data_location: str = ""
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)


class Turn(BaseModel):
    role: str            # "user" | "assistant"
    text: str


class OnboardingInfo(BaseModel):
    """Contato de WhatsApp para o onboarding (canal oficial + grupo)."""
    whatsapp_number: str
    responsible_name: str
    is_owner: bool = True


class DiscoveryState(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    session_id: str
    company: CompanyProfile = Field(default_factory=CompanyProfile)
    open_areas: list[OpenArea] = Field(default_factory=list)
    integrations: list[Integration] = Field(default_factory=list)
    transcript: list[Turn] = Field(default_factory=list)
    onboarding: Optional[OnboardingInfo] = None

    @field_validator("open_areas")
    @classmethod
    def _unique_area_ids(cls, v: list[OpenArea]) -> list[OpenArea]:
        ids = [a.id for a in v]
        if len(ids) != len(set(ids)):
            raise ValueError("open_areas contém ids duplicados")
        return v

    def next_focus(self) -> Optional[OpenArea]:
        """Área de maior prioridade e menor confiança (não-formulário)."""
        if not self.open_areas:
            return None
        return sorted(
            self.open_areas, key=lambda a: (a.confidence, -a.priority)
        )[0]

    def ready_to_emit(self, threshold: float = 0.7) -> bool:
        """Pronto quando toda área prioritária (priority>=3) supera limiar.

        Retorna False quando open_areas está vazio (nenhuma descoberta ainda).
        """
        if not self.open_areas:
            return False
        critical = [a for a in self.open_areas if a.priority >= 3]
        return all(a.confidence >= threshold for a in critical)


class ReflectUpdate(BaseModel):
    """Saída estruturada do passo de raciocínio `reflect`."""
    learned: str
    close_area_ids: list[str] = Field(default_factory=list)
    new_areas: list[OpenArea] = Field(default_factory=list)
    integrations: list[Integration] = Field(default_factory=list)
    company_updates: dict = Field(default_factory=dict)
    confidence_updates: dict[str, float] = Field(default_factory=dict)


# --- Blueprint do time ----------------------------------------------------

class ProcessArea(BaseModel):
    name: str
    description: str = ""


class AgentSpec(BaseModel):
    name: str
    role: str
    objective: str
    tasks: list[str] = Field(default_factory=list)
    tools_integrations: list[str] = Field(default_factory=list)
    talks_to: list[str] = Field(default_factory=list)


class RoadmapItem(BaseModel):
    order: int
    title: str
    rationale: str = ""


class ConnectorRef(BaseModel):
    """Conector recomendado no blueprint (whitelist curada).

    Campos string lenientes de propósito: o JSON vem do LLM; a validação
    estrita de vocabulário vive em ConnectorInfo (taxonomy.py).
    """
    integration_kind: str
    name: str
    origin: str
    slug_or_url: str = ""
    status: str
    notes: str = ""


class TeamBlueprint(BaseModel):
    company_profile: CompanyProfile
    process_map: list[ProcessArea] = Field(default_factory=list)
    detected_integrations: list[Integration] = Field(default_factory=list)
    proposed_team: list[AgentSpec] = Field(default_factory=list)
    roadmap: list[RoadmapItem] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)
    recommended_connectors: list[ConnectorRef] = Field(default_factory=list)
    onboarding: Optional[OnboardingInfo] = None


# --- Requisitos por agente (fase pós-blueprint) -----------------------------

class InfoRequest(BaseModel):
    """Uma informação concreta que falta para um agente operar."""
    item: str            # ex.: "catálogo de produtos com preços"
    why: str             # por que o agente precisa (linguagem simples)
    group_message: str   # mensagem pronta, leiga, para pedir no grupo


class AgentRequirements(BaseModel):
    """Informações pendentes de um agente do time proposto."""
    agent_name: str
    requests: list[InfoRequest] = Field(default_factory=list)


class RequirementsReport(BaseModel):
    """Relatório consolidado de informações pendentes por agente."""
    items: list[AgentRequirements] = Field(default_factory=list)
    summary_for_owner: str = ""   # parágrafo leigo de abertura do grupo
