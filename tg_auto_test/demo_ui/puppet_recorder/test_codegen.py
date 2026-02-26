"""Generate pytest test code from a recorded puppet session."""

from tg_auto_test.demo_ui.puppet_recorder.recorder_models import RecordedStep


def _escape_string(value: str) -> str:
    """Escape a string for use in generated Python source code."""
    return value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def _generate_send_message(step: RecordedStep, indent: str) -> list[str]:
    """Generate code lines for a send_message step."""
    escaped = _escape_string(step.text)
    lines = [
        f'{indent}await conv.send_message("{escaped}")',
        f"{indent}response = await conv.get_response()",
    ]
    if step.response_text:
        escaped_resp = _escape_string(step.response_text)
        lines.append(f'{indent}assert response.text == "{escaped_resp}"')
    if step.response_type and step.response_type != "text":
        lines.append(f"{indent}assert response.{step.response_type} is not None")
    return lines


def _generate_send_file(step: RecordedStep, indent: str) -> list[str]:
    """Generate code lines for a send_file step."""
    kwargs = []
    if step.file_type == "document":
        kwargs.append("force_document=True")
    elif step.file_type == "voice":
        kwargs.append("voice_note=True")
    elif step.file_type == "video_note":
        kwargs.append("video_note=True")
    if step.caption:
        escaped_caption = _escape_string(step.caption)
        kwargs.append(f'caption="{escaped_caption}"')
    kwargs_str = ", ".join(kwargs)
    if kwargs_str:
        kwargs_str = ", " + kwargs_str
    lines = [
        f"{indent}# Send a {step.file_type or 'photo'} file",
        f'{indent}await conv.send_file(b"test_file_data"{kwargs_str})',
        f"{indent}response = await conv.get_response()",
    ]
    if step.response_text:
        escaped_resp = _escape_string(step.response_text)
        lines.append(f'{indent}assert response.text == "{escaped_resp}"')
    return lines


def _generate_click_button(step: RecordedStep, indent: str) -> list[str]:
    """Generate code lines for a click_button step."""
    escaped_data = _escape_string(step.callback_data)
    lines = [
        f'{indent}# Click button with callback_data="{escaped_data}"',
        f"{indent}msg = await client.get_messages(peer, ids={step.message_id})",
        f'{indent}response = await msg.click(data=b"{escaped_data}")',
    ]
    if step.response_text:
        escaped_resp = _escape_string(step.response_text)
        lines.append(f'{indent}assert response.text == "{escaped_resp}"')
    return lines


def _generate_pay_invoice(step: RecordedStep, indent: str) -> list[str]:
    """Generate code lines for a pay_invoice step."""
    lines = [
        f"{indent}# Pay invoice on message {step.message_id}",
        f"{indent}# (Stars payment simulation via Telethon TL request)",
    ]
    if step.response_text:
        escaped_resp = _escape_string(step.response_text)
        lines.append(f'{indent}# Expected response: "{escaped_resp}"')
    return lines


def _generate_poll_vote(step: RecordedStep, indent: str) -> list[str]:
    """Generate code lines for a poll_vote step."""
    options_str = ", ".join(str(i) for i in step.option_ids)
    lines = [
        f"{indent}# Vote on poll (message {step.message_id}) with options [{options_str}]",
    ]
    if step.response_text:
        escaped_resp = _escape_string(step.response_text)
        lines.append(f'{indent}# Expected response: "{escaped_resp}"')
    return lines


_STEP_GENERATORS = {
    "send_message": _generate_send_message,
    "send_file": _generate_send_file,
    "click_button": _generate_click_button,
    "pay_invoice": _generate_pay_invoice,
    "poll_vote": _generate_poll_vote,
}


def generate_test_code(steps: list[RecordedStep], test_name: str = "test_recorded_session") -> str:
    """Generate a complete pytest test function from recorded steps.

    Args:
        steps: List of recorded interaction steps
        test_name: Name for the generated test function

    Returns:
        Complete Python test source code as a string
    """
    if not steps:
        return _generate_empty_test(test_name)

    indent = "        "
    lines = [
        "import pytest",
        "",
        "from tg_auto_test.test_utils.serverless_telegram_client import ServerlessTelegramClient",
        "",
        "",
        f"@pytest.mark.asyncio",
        f"async def {test_name}(build_application) -> None:",
        '    """Auto-generated test from puppet recorder session."""',
        "    client = ServerlessTelegramClient(build_application=build_application)",
        "    await client.connect()",
        "    try:",
        '        async with client.conversation("test_bot") as conv:',
        '            peer = "test_bot"',
    ]

    for i, step in enumerate(steps):
        if i > 0:
            lines.append("")
        generator = _STEP_GENERATORS[step.action]
        lines.extend(generator(step, indent))

    lines.extend([
        "    finally:",
        "        await client.disconnect()",
        "",
    ])

    return "\n".join(lines)


def _generate_empty_test(test_name: str) -> str:
    """Generate a test stub when no steps have been recorded."""
    return "\n".join([
        "import pytest",
        "",
        "from tg_auto_test.test_utils.serverless_telegram_client import ServerlessTelegramClient",
        "",
        "",
        f"@pytest.mark.asyncio",
        f"async def {test_name}(build_application) -> None:",
        '    """Auto-generated test from puppet recorder session (no steps recorded)."""',
        "    client = ServerlessTelegramClient(build_application=build_application)",
        "    await client.connect()",
        "    await client.disconnect()",
        "",
    ])
