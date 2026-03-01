"""Shared bot application builder for HTML parse_mode tests."""

from telegram import Update
from telegram.ext import Application, ApplicationBuilder, CommandHandler, ContextTypes


async def _bold_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    del context
    if update.message:
        await update.message.reply_text("<b>bold</b>", parse_mode="HTML")


async def _italic_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    del context
    if update.message:
        await update.message.reply_text("<i>italic</i>", parse_mode="HTML")


async def _underline_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    del context
    if update.message:
        await update.message.reply_text("<u>underline</u>", parse_mode="HTML")


async def _strikethrough_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    del context
    if update.message:
        await update.message.reply_text("<s>strikethrough</s>", parse_mode="HTML")


async def _code_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    del context
    if update.message:
        await update.message.reply_text("<code>inline code</code>", parse_mode="HTML")


async def _pre_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    del context
    if update.message:
        await update.message.reply_text("<pre>code block</pre>", parse_mode="HTML")


async def _link_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    del context
    if update.message:
        await update.message.reply_text('<a href="https://example.com">link</a>', parse_mode="HTML")


async def _spoiler_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    del context
    if update.message:
        await update.message.reply_text('<span class="tg-spoiler">spoiler</span>', parse_mode="HTML")


async def _tg_spoiler_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    del context
    if update.message:
        await update.message.reply_text("<tg-spoiler>spoiler</tg-spoiler>", parse_mode="HTML")


async def _nested_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    del context
    if update.message:
        await update.message.reply_text("<b><i>bold italic</i></b>", parse_mode="HTML")


async def _mixed_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    del context
    if update.message:
        await update.message.reply_text(
            "Send <b>text</b> or <b>photo</b> to translate.",
            parse_mode="HTML",
        )


def build_html_app(builder: ApplicationBuilder) -> Application:
    """Build a test application with handlers for all HTML formatting types."""
    app = builder.build()
    app.add_handler(CommandHandler("bold", _bold_handler))
    app.add_handler(CommandHandler("italic", _italic_handler))
    app.add_handler(CommandHandler("underline", _underline_handler))
    app.add_handler(CommandHandler("strike", _strikethrough_handler))
    app.add_handler(CommandHandler("code", _code_handler))
    app.add_handler(CommandHandler("pre", _pre_handler))
    app.add_handler(CommandHandler("link", _link_handler))
    app.add_handler(CommandHandler("spoiler", _spoiler_handler))
    app.add_handler(CommandHandler("tgspoiler", _tg_spoiler_handler))
    app.add_handler(CommandHandler("nested", _nested_handler))
    app.add_handler(CommandHandler("mixed", _mixed_handler))
    return app
