"""Recording control and interactive routes for the puppet recorder."""

from typing import TYPE_CHECKING  # noqa: TID251

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

from tg_auto_test.demo_ui.puppet_recorder.recorder_models import RecordedStep
from tg_auto_test.demo_ui.puppet_recorder.test_codegen import generate_test_code
from tg_auto_test.demo_ui.server.api_models import InvoicePayRequest, MessageResponse, PollVoteRequest
from tg_auto_test.demo_ui.server.serialize import serialize_message

if TYPE_CHECKING:
    from tg_auto_test.demo_ui.puppet_recorder.recorder_server import PuppetRecorderServer


def register_recording_control_routes(app: FastAPI, server: "PuppetRecorderServer") -> None:
    """Register recording control and Telethon interactive routes."""

    @app.post("/api/invoice/pay")
    async def pay_invoice(req: InvoicePayRequest) -> MessageResponse:
        from telethon.tl.functions.payments import SendStarsFormRequest  # noqa: PLC0415
        from telethon.tl.types import InputInvoiceMessage  # noqa: PLC0415

        peer = await server.client.get_input_entity(server.peer)
        request = SendStarsFormRequest(
            form_id=req.message_id,
            invoice=InputInvoiceMessage(peer=peer, msg_id=req.message_id),
        )
        async with server.client.conversation(server.peer, timeout=server.timeout) as conv:
            await server.client(request)
            response = await conv.get_response()
        result = await serialize_message(response, server.file_store)
        server.session.add_step(
            RecordedStep(
                action="pay_invoice",
                message_id=req.message_id,
                response_type=result.type,
                response_text=result.text,
                response_message_id=result.message_id,
            )
        )
        return result

    @app.post("/api/poll/vote")
    async def vote_poll(request: PollVoteRequest) -> MessageResponse:
        from telethon.tl.functions.messages import SendVoteRequest  # noqa: PLC0415

        peer = await server.client.get_input_entity(server.peer)
        option_bytes = [bytes([i]) for i in request.option_ids]
        vote_request = SendVoteRequest(peer=peer, msg_id=request.message_id, options=option_bytes)
        async with server.client.conversation(server.peer, timeout=server.timeout) as conv:
            await server.client(vote_request)
            response = await conv.get_response()
        result = await serialize_message(response, server.file_store)
        server.session.add_step(
            RecordedStep(
                action="poll_vote",
                message_id=request.message_id,
                option_ids=tuple(request.option_ids),
                response_type=result.type,
                response_text=result.text,
                response_message_id=result.message_id,
            )
        )
        return result

    @app.post("/api/recording/start")
    async def start_recording() -> dict[str, bool]:
        server.session.start()
        return {"recording": True}

    @app.post("/api/recording/stop")
    async def stop_recording() -> dict[str, bool]:
        server.session.stop()
        return {"recording": False}

    @app.post("/api/recording/clear")
    async def clear_recording() -> dict[str, str]:
        server.session.clear()
        return {"status": "cleared"}

    @app.get("/api/recording/status")
    async def recording_status() -> dict[str, bool | int]:
        return {"recording": server.session.is_recording, "step_count": server.session.step_count}

    @app.get("/api/recording/steps")
    async def recording_steps() -> list[dict[str, str | int | list[int]]]:
        result = []
        for step in server.session.steps:
            entry: dict[str, str | int | list[int]] = {
                "action": step.action,
                "response_type": step.response_type,
                "response_text": step.response_text,
                "response_message_id": step.response_message_id,
            }
            if step.text:
                entry["text"] = step.text
            if step.file_type:
                entry["file_type"] = step.file_type
            if step.caption:
                entry["caption"] = step.caption
            if step.callback_data:
                entry["callback_data"] = step.callback_data
            if step.message_id:
                entry["message_id"] = step.message_id
            if step.option_ids:
                entry["option_ids"] = list(step.option_ids)
            result.append(entry)
        return result

    @app.get("/api/recording/export")
    async def export_test_code() -> PlainTextResponse:
        code = generate_test_code(server.session.steps)
        return PlainTextResponse(code, media_type="text/x-python")
