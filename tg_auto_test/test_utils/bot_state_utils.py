"""Utilities for getting bot state."""

from telegram import BotCommandScopeDefault


async def get_bot_state_dict(bot: object, chat_id: int) -> dict[str, list[dict[str, str]] | str]:
    """Get bot state including commands and menu button type."""
    commands = await bot.get_my_commands(scope=BotCommandScopeDefault())
    menu_btn = await bot.get_chat_menu_button(chat_id=chat_id)
    command_list = [{"command": cmd.command, "description": cmd.description} for cmd in commands]
    return {"commands": command_list, "menu_button_type": str(getattr(menu_btn, "type", "default"))}


async def get_client_bot_state(application: object, chat_id: int) -> dict[str, list[dict[str, str]] | str]:
    """Get bot state for a client."""
    return await get_bot_state_dict(application.bot, chat_id)
