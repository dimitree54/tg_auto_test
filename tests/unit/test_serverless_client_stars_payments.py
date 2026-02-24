"""Test Telegram Stars payment handling with ServerlessTelegramClient."""

import pytest
from telethon.tl.functions.payments import SendStarsFormRequest
from telethon.tl.types import InputInvoiceMessage, InputPeerEmpty

from tests.unit.helpers_ptb_app import build_test_application
from tg_auto_test.test_utils.serverless_telegram_client import ServerlessTelegramClient


@pytest.mark.asyncio
async def test_stars_invoice_creation() -> None:
    """Test that /donate command creates a proper Stars invoice."""
    client = ServerlessTelegramClient(build_application=build_test_application)
    await client.connect()
    try:
        async with client.conversation("test_bot") as conv:
            await conv.send_message("/donate")
            msg = await conv.get_response()

            # Check that the message has invoice data
            assert msg.invoice is not None
            invoice = msg.invoice

            # Check invoice properties
            assert invoice.title == "Donate"
            assert invoice.description == "Donate 1 Star"
            assert invoice.currency == "XTR"
            assert invoice.total_amount == 1
            assert invoice.start_param == "donate"
    finally:
        await client.disconnect()


@pytest.mark.asyncio
async def test_successful_stars_payment() -> None:
    """Test successful Stars payment flow."""
    client = ServerlessTelegramClient(build_application=build_test_application)
    await client.connect()
    try:
        async with client.conversation("test_bot") as conv:
            # Create invoice
            await conv.send_message("/donate")
            invoice_msg = await conv.get_response()

            assert invoice_msg.invoice is not None

            # Simulate payment using Telethon SendStarsFormRequest
            request = SendStarsFormRequest(
                form_id=invoice_msg.id,
                invoice=InputInvoiceMessage(peer=InputPeerEmpty(), msg_id=invoice_msg.id),
            )
            await client(request)
            payment_confirmation = client._pop_response()  # noqa: SLF001

            assert payment_confirmation.text == "Payment received!"
    finally:
        await client.disconnect()


@pytest.mark.asyncio
async def test_multiple_invoices() -> None:
    """Test handling multiple invoices with different message IDs."""
    client = ServerlessTelegramClient(build_application=build_test_application)
    await client.connect()
    try:
        async with client.conversation("test_bot") as conv:
            # Create first invoice
            await conv.send_message("/donate")
            invoice1 = await conv.get_response()

            # Create second invoice
            await conv.send_message("/donate")
            invoice2 = await conv.get_response()

            assert invoice1.id != invoice2.id
            assert invoice1.invoice is not None
            assert invoice2.invoice is not None

            # Pay first invoice
            request1 = SendStarsFormRequest(
                form_id=invoice1.id,
                invoice=InputInvoiceMessage(peer=InputPeerEmpty(), msg_id=invoice1.id),
            )
            await client(request1)
            payment1 = client._pop_response()  # noqa: SLF001
            assert payment1.text == "Payment received!"

            # Pay second invoice
            request2 = SendStarsFormRequest(
                form_id=invoice2.id,
                invoice=InputInvoiceMessage(peer=InputPeerEmpty(), msg_id=invoice2.id),
            )
            await client(request2)
            payment2 = client._pop_response()  # noqa: SLF001
            assert payment2.text == "Payment received!"
    finally:
        await client.disconnect()


@pytest.mark.asyncio
async def test_unknown_invoice_payment_fails() -> None:
    """Test that paying unknown invoice ID raises error."""
    client = ServerlessTelegramClient(build_application=build_test_application)
    await client.connect()
    try:
        async with client.conversation("test_bot"):
            # Try to pay for non-existent invoice
            request = SendStarsFormRequest(
                form_id=999,
                invoice=InputInvoiceMessage(peer=InputPeerEmpty(), msg_id=999),
            )
            with pytest.raises(RuntimeError, match="Unknown invoice message id: 999"):
                await client(request)
    finally:
        await client.disconnect()


@pytest.mark.asyncio
async def test_non_invoice_message_has_no_invoice() -> None:
    """Test that regular messages don't have invoice data."""
    client = ServerlessTelegramClient(build_application=build_test_application)
    await client.connect()
    try:
        async with client.conversation("test_bot") as conv:
            await conv.send_message("hello")
            msg = await conv.get_response()

            assert msg.invoice is None
    finally:
        await client.disconnect()


@pytest.mark.asyncio
async def test_payment_reduces_stars_balance() -> None:
    """Test that payments reduce the client's Stars balance."""
    client = ServerlessTelegramClient(build_application=build_test_application)
    await client.connect()
    try:
        # Check initial balance (should be 100 by default)
        initial_balance = client._stars_balance  # noqa: SLF001
        assert initial_balance == 100

        async with client.conversation("test_bot") as conv:
            await conv.send_message("/donate")
            invoice_msg = await conv.get_response()

            # Make payment
            request = SendStarsFormRequest(
                form_id=invoice_msg.id,
                invoice=InputInvoiceMessage(peer=InputPeerEmpty(), msg_id=invoice_msg.id),
            )
            await client(request)
            client._pop_response()  # noqa: SLF001 # Payment confirmation

            # Balance should be reduced
            new_balance = client._stars_balance  # noqa: SLF001
            assert new_balance == initial_balance - 1
    finally:
        await client.disconnect()
