from typing import cast

from telethon.tl import functions, types

from tg_auto_test.test_utils.serverless_telegram_client_core import ServerlessTelegramClientCore

TypeBotCommandScope = (
    types.BotCommandScopeDefault
    | types.BotCommandScopeUsers
    | types.BotCommandScopePeer
    | types.BotCommandScopePeerAdmins
    | types.BotCommandScopePeerUser
    | types.BotCommandScopeChats
    | types.BotCommandScopeChatAdmins
)


def _scope_key_from_telethon(scope: TypeBotCommandScope) -> str:
    """Convert a Telethon scope object to the same key format used by the stub."""
    if isinstance(scope, (types.BotCommandScopePeer, types.BotCommandScopePeerUser)):
        peer = scope.peer
        if isinstance(peer, types.InputPeerUser):
            return f"chat:{peer.user_id}"
        return "default"
    if isinstance(scope, types.BotCommandScopeDefault):
        return "default"
    return "default"


TelethonRequest = (
    functions.payments.GetStarsStatusRequest
    | functions.payments.GetPaymentFormRequest
    | functions.payments.SendStarsFormRequest
    | functions.bots.GetBotCommandsRequest
    | functions.bots.GetBotMenuButtonRequest
    | functions.messages.SendVoteRequest
)
TelethonResponse = (
    types.payments.StarsStatus
    | types.payments.PaymentForm
    | types.payments.PaymentResult
    | list[types.BotCommand]
    | types.BotMenuButtonCommands
    | types.BotMenuButtonDefault
    | types.Updates
)


async def handle_telethon_request(client: ServerlessTelegramClientCore, request: TelethonRequest) -> TelethonResponse:
    if isinstance(request, functions.payments.GetStarsStatusRequest):
        balance = client._stars_balance
        return types.payments.StarsStatus(balance=types.StarsAmount(amount=balance, nanos=0), chats=[], users=[])

    if isinstance(request, functions.payments.GetPaymentFormRequest):
        invoice = request.invoice
        if not isinstance(invoice, types.InputInvoiceMessage):
            raise NotImplementedError(f"Unsupported invoice type: {type(invoice)!r}")
        invoices = client._invoices
        if invoice.msg_id not in invoices:
            raise RuntimeError(f"Unknown invoice message id: {invoice.msg_id}")
        invoice_data = invoices[invoice.msg_id]
        currency = invoice_data["currency"]
        prices = invoice_data["prices"]
        if not isinstance(currency, str):
            raise ValueError(f"Expected currency to be str, got {type(currency)}")
        if not isinstance(prices, list):
            raise ValueError(f"Expected prices to be list, got {type(prices)}")
        tg_invoice = types.Invoice(currency=cast(str, currency), prices=cast(list, prices))
        return types.payments.PaymentForm(
            form_id=invoice.msg_id,
            bot_id=999_999,
            title="Donate",
            description="",
            invoice=tg_invoice,
            provider_id=0,
            url="",
            users=[],
        )

    if isinstance(request, functions.payments.SendStarsFormRequest):
        invoice = request.invoice
        if not isinstance(invoice, types.InputInvoiceMessage):
            raise NotImplementedError(f"Unsupported invoice type: {type(invoice)!r}")
        await client._simulate_stars_payment(invoice.msg_id)  # noqa: SLF001
        return types.payments.PaymentResult(
            updates=types.Updates(updates=[], users=[], chats=[], date=None, seq=0),
        )

    if isinstance(request, functions.bots.GetBotCommandsRequest):
        key = _scope_key_from_telethon(request.scope)
        stored = client.request.get_scoped_commands(key)
        return [types.BotCommand(command=cmd["command"], description=cmd["description"]) for cmd in stored]

    if isinstance(request, functions.bots.GetBotMenuButtonRequest):
        menu = client.request.get_menu_button()
        if menu is not None and menu.get("type") == "commands":
            return types.BotMenuButtonCommands()
        return types.BotMenuButtonDefault()

    if isinstance(request, functions.messages.SendVoteRequest):
        # Handle poll vote - delegate to new method that will be added to the core
        await client._handle_send_vote_request(request.peer, request.msg_id, request.options)
        # Return minimal Updates object - in serverless mode we don't need full update tracking
        return types.Updates(updates=[], users=[], chats=[], date=None, seq=0)

    raise NotImplementedError(f"Unsupported Telethon request: {type(request)!r}")
