# -*- coding: utf-8 -*-
# pylint: disable=wrong-import-order,wrong-import-position,ungrouped-imports
"""Pareamento de WhatsApp por codigo PIN — helper puro (sem FastAPI).

Espelha o fluxo neonize provado em
``qwenpaw.app.routers.config.start_whatsapp_pair`` (conectar -> PairPhone
-> polling do ConnectedEv), mas sem nenhum acoplamento com HTTP/Request.
Tanto o endpoint REST quanto a CLI ``qwenpaw discovery pair`` podem usar
este helper (a CLI usa; o router segue como esta por enquanto).

neonize NAO faz parte do AgentScope; nao ha nenhuma API ``agentscope.*``
neste modulo.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Callable

# Tempo (s) de espera apos ``connect()`` antes de pedir o PIN. O websocket
# precisa subir antes de ``PairPhone`` (mesmo valor do router REST).
_CONNECT_SETTLE_SECONDS = 3.0


class PairingDependencyError(Exception):
    """neonize-qwenpaw nao esta instalado (extra ``whatsapp``)."""


class PairingError(Exception):
    """Falha no fluxo de pareamento (PairPhone, conexao, etc.)."""


async def pair_by_code(
    auth_dir: str,
    phone: str,
    on_pin: Callable[[str], None],
    timeout: float = 120.0,
) -> bool:
    """Pareia o WhatsApp via codigo PIN, gravando a sessao em ``auth_dir``.

    Cria/usa ``<auth_dir>/neonize.db`` — o MESMO arquivo que o canal do
    agente le quando roda — conecta, solicita o PIN via ``PairPhone`` e
    chama ``on_pin(code)`` para a borda (CLI/REST) exibir o codigo. Em
    seguida faz polling ate o ``ConnectedEv`` disparar ou estourar o
    ``timeout``. Sempre desconecta o cliente e cancela a task no finally.

    Args:
        auth_dir: Diretorio da sessao WhatsApp do agente. Criado se faltar.
        phone: Numero em E.164 (ex.: ``+5511987654321``).
        on_pin: Callback chamado com o PIN (string ~8 chars) assim que o
            neonize o devolve.
        timeout: Tempo maximo (s) aguardando a confirmacao no celular.

    Returns:
        True se o ``ConnectedEv`` disparou dentro do timeout; False se
        estourou o tempo.

    Raises:
        PairingDependencyError: se ``neonize`` nao estiver instalado.
        PairingError: se ``PairPhone`` ou a conexao falharem.
    """
    try:
        from neonize.aioze.client import NewAClient
        from neonize.events import ConnectedEv
    except ImportError as exc:  # pragma: no cover - depende do ambiente
        raise PairingDependencyError(
            "neonize-qwenpaw nao instalado. "
            "Instale com: pip install qwenpaw[whatsapp]",
        ) from exc

    auth_path = Path(auth_dir).expanduser()
    auth_path.mkdir(parents=True, exist_ok=True)
    db_path = str(auth_path / "neonize.db")

    connected = asyncio.Event()
    client = NewAClient(name=db_path)

    @client.event(ConnectedEv)
    async def _on_connected(_c, _evt):  # pragma: no cover - callback neonize
        connected.set()

    task = None
    try:
        task = await client.connect()
        await asyncio.sleep(_CONNECT_SETTLE_SECONDS)

        try:
            code = await client.PairPhone(phone, True)
        except Exception as exc:  # noqa: BLE001 - superficie amigavel
            raise PairingError(
                f"Falha ao solicitar o codigo de pareamento: {exc}",
            ) from exc

        on_pin(code)

        try:
            await asyncio.wait_for(connected.wait(), timeout=timeout)
        except asyncio.TimeoutError:
            return False
        return True
    finally:
        try:
            await client.disconnect()
        except Exception:  # noqa: BLE001 - cleanup best-effort
            pass
        if task is not None and not task.done():
            task.cancel()
            try:
                await asyncio.wait_for(task, timeout=2.0)
            except (asyncio.TimeoutError, asyncio.CancelledError):
                pass
            except Exception:  # noqa: BLE001 - cleanup best-effort
                pass
