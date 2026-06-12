# -*- coding: utf-8 -*-
"""Helpers genéricos para montar surfaces A2UI (adjacency-list).

Um ``Node`` é uma árvore aninhada; ``surface()`` a achata na lista de
componentes (filhos por id) e devolve as mensagens createSurface +
updateComponents [+ updateDataModel]. Não conhece nenhum domínio.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .schema import (
    A2UIMessage,
    Component,
    CreateSurface,
    UpdateComponents,
    UpdateDataModel,
)


@dataclass
class Node:
    """Nó aninhado de uma surface (achatado por ``surface()``)."""

    id: str
    type: str
    properties: dict[str, Any] = field(default_factory=dict)
    children: list["Node"] = field(default_factory=list)


def column(cid: str, children: list[Node]) -> Node:
    return Node(cid, "Column", children=children)


def row(cid: str, children: list[Node]) -> Node:
    return Node(cid, "Row", children=children)


def card(cid: str, children: list[Node]) -> Node:
    return Node(cid, "Card", children=children)


def lst(cid: str, children: list[Node]) -> Node:
    return Node(cid, "List", children=children)


def text(cid: str, value: str) -> Node:
    return Node(cid, "Text", {"text": value})


def heading(cid: str, value: str) -> Node:
    return Node(cid, "Heading", {"text": value})


def tag(cid: str, value: str) -> Node:
    return Node(cid, "Tag", {"text": value})


def button(cid: str, label: str, action: dict[str, Any]) -> Node:
    return Node(cid, "Button", {"text": label, "action": action})


def _flatten(node: Node, out: list[Component]) -> None:
    out.append(
        Component(
            id=node.id,
            type=node.type,
            properties=dict(node.properties),
            children=[c.id for c in node.children],
        ),
    )
    for c in node.children:
        _flatten(c, out)


def surface(
    surface_id: str,
    root: Node,
    data: dict[str, Any] | None = None,
) -> list[A2UIMessage]:
    """Achata ``root`` e devolve as mensagens A2UI da surface.

    Retorna ``[CreateSurface, UpdateComponents]`` e, se ``data`` for
    informado, também ``UpdateDataModel``.
    """
    comps: list[Component] = []
    _flatten(root, comps)
    msgs: list[A2UIMessage] = [
        CreateSurface(surface_id=surface_id, root=root.id),
        UpdateComponents(surface_id=surface_id, components=comps),
    ]
    if data is not None:
        msgs.append(UpdateDataModel(surface_id=surface_id, data=data))
    return msgs
