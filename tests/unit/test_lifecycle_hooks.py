"""Lifecycle conformance: post_init and post_shutdown hooks.

ServerlessTelegramClient must mirror the PTB Application lifecycle:
  connect  -> initialize() -> post_init(app)
  disconnect -> shutdown()  -> post_shutdown(app)

These tests verify the hooks are actually invoked and in the correct order.
"""

import pytest
from telegram.ext import Application, ApplicationBuilder

from tg_auto_test.test_utils.serverless_telegram_client import ServerlessTelegramClient


def _logging_post_init(log: list[str]) -> ...:
    async def _hook(application: Application) -> None:
        await application.bot.get_me()
        log.append("post_init")

    return _hook


def _logging_post_shutdown(log: list[str]) -> ...:
    async def _hook(application: Application) -> None:  # noqa: RUF029
        del application
        log.append("post_shutdown")

    return _hook


@pytest.mark.asyncio
async def test_post_init_called_on_connect() -> None:
    """post_init must be invoked exactly once during connect()."""
    log: list[str] = []

    def build(builder: ApplicationBuilder) -> Application:
        return builder.post_init(_logging_post_init(log)).build()

    client = ServerlessTelegramClient(build_application=build)
    await client.connect()
    try:
        assert log == ["post_init"]
    finally:
        await client.disconnect()


@pytest.mark.asyncio
async def test_post_shutdown_called_on_disconnect() -> None:
    """post_shutdown must be invoked exactly once during disconnect()."""
    log: list[str] = []

    def build(builder: ApplicationBuilder) -> Application:
        return builder.post_shutdown(_logging_post_shutdown(log)).build()

    client = ServerlessTelegramClient(build_application=build)
    await client.connect()
    assert log == []
    await client.disconnect()
    assert log == ["post_shutdown"]


@pytest.mark.asyncio
async def test_full_lifecycle_order() -> None:
    """Both hooks fire in the correct order across connect/disconnect."""
    log: list[str] = []

    def build(builder: ApplicationBuilder) -> Application:
        return builder.post_init(_logging_post_init(log)).post_shutdown(_logging_post_shutdown(log)).build()

    client = ServerlessTelegramClient(build_application=build)
    await client.connect()
    assert log == ["post_init"]
    await client.disconnect()
    assert log == ["post_init", "post_shutdown"]


@pytest.mark.asyncio
async def test_no_hooks_is_fine() -> None:
    """A plain application without hooks must connect/disconnect cleanly."""

    def build(builder: ApplicationBuilder) -> Application:
        return builder.build()

    client = ServerlessTelegramClient(build_application=build)
    await client.connect()
    await client.disconnect()


@pytest.mark.asyncio
async def test_idempotent_connect() -> None:
    """Calling connect() twice must not invoke post_init a second time."""
    log: list[str] = []

    def build(builder: ApplicationBuilder) -> Application:
        return builder.post_init(_logging_post_init(log)).build()

    client = ServerlessTelegramClient(build_application=build)
    await client.connect()
    await client.connect()  # second call — should be no-op
    try:
        assert log == ["post_init"]
    finally:
        await client.disconnect()


@pytest.mark.asyncio
async def test_idempotent_disconnect() -> None:
    """Calling disconnect() twice must not invoke post_shutdown a second time."""
    log: list[str] = []

    def build(builder: ApplicationBuilder) -> Application:
        return builder.post_shutdown(_logging_post_shutdown(log)).build()

    client = ServerlessTelegramClient(build_application=build)
    await client.connect()
    await client.disconnect()
    await client.disconnect()  # second call — should be no-op
    assert log == ["post_shutdown"]
