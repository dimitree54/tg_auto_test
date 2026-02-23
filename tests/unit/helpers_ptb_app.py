"""Test helper for building a PTB application with various handlers for testing."""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice, Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    PreCheckoutQueryHandler,
    filters,
)


async def _echo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo back the text message."""
    del context  # Unused but required by handler signature
    if update.message and update.message.text:
        await update.message.reply_text(update.message.text)


async def _start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    del context  # Unused but required by handler signature
    if update.message:
        await update.message.reply_text("Welcome!")


async def _inline_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send inline keyboard with two options."""
    del context  # Unused but required by handler signature
    if update.message:
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Option A", callback_data="opt_a"),
                InlineKeyboardButton("Option B", callback_data="opt_b"),
            ],
        ])
        await update.message.reply_text("Choose:", reply_markup=keyboard)


async def _callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle inline button presses."""
    del context  # Unused but required by handler signature
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        if query.message:
            await query.message.reply_text(f"You chose: {query.data}")


async def _donate_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send Stars invoice for donation."""
    del context  # Unused but required by handler signature
    if update.message:
        prices = [LabeledPrice("Donate", 1)]
        await update.message.reply_invoice(
            title="Donate",
            description="Donate 1 Star",
            payload="donate_1_star",
            currency="XTR",
            prices=prices,
            start_parameter="donate",
        )


async def _pre_checkout_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle pre-checkout query for Stars payment."""
    del context  # Unused but required by handler signature
    if update.pre_checkout_query:
        await update.pre_checkout_query.answer(ok=True)


async def _successful_payment_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle successful payment confirmation."""
    del context  # Unused but required by handler signature
    if update.message:
        await update.message.reply_text("Payment received!")


async def _echo_photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo back the photo."""
    if update.message and update.message.photo:
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        raw = await file.download_as_bytearray()
        await update.message.reply_photo(bytes(raw))


async def _echo_document_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo back the document."""
    if update.message and update.message.document:
        doc = update.message.document
        file = await context.bot.get_file(doc.file_id)
        raw = await file.download_as_bytearray()
        await update.message.reply_document(bytes(raw), filename=doc.file_name)


def build_test_application(builder: ApplicationBuilder) -> Application:
    """Build a test PTB application with various handlers for testing.

    Args:
        builder: Pre-configured ApplicationBuilder with token and request

    Returns:
        Application with handlers for text, commands, media, callbacks, and payments
    """
    app = builder.build()

    # Command handlers
    app.add_handler(CommandHandler("start", _start_handler))
    app.add_handler(CommandHandler("inline", _inline_handler))
    app.add_handler(CommandHandler("donate", _donate_handler))

    # Payment handlers
    app.add_handler(PreCheckoutQueryHandler(_pre_checkout_handler))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, _successful_payment_handler))

    # Media handlers
    app.add_handler(MessageHandler(filters.PHOTO, _echo_photo_handler))
    app.add_handler(MessageHandler(filters.Document.ALL, _echo_document_handler))

    # Callback query handler
    app.add_handler(CallbackQueryHandler(_callback_handler))

    # Text echo handler (must be last to not interfere with commands)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, _echo_handler))

    return app
