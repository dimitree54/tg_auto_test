"""Classification registry for all NotImplementedError stubs in the codebase."""

import enum


class StubCategory(enum.Enum):
    IMPLEMENTABLE = "implementable"
    UNIMPLEMENTABLE = "unimplementable"


U = StubCategory.UNIMPLEMENTABLE
I = StubCategory.IMPLEMENTABLE

STUB_REGISTRY: dict[tuple[str, str], StubCategory] = {
    # --- serverless_telegram_conversation ---
    ("serverless_telegram_conversation", "get_reply"): I,
    ("serverless_telegram_conversation", "cancel"): U,
    ("serverless_telegram_conversation", "cancel_all"): U,
    ("serverless_telegram_conversation", "wait_event"): U,
    ("serverless_telegram_conversation", "wait_read"): U,
    ("serverless_telegram_conversation", "mark_read"): U,
    ("serverless_telegram_conversation", "chat"): I,
    ("serverless_telegram_conversation", "chat_id"): I,
    ("serverless_telegram_conversation", "input_chat"): U,
    ("serverless_telegram_conversation", "is_channel"): I,
    ("serverless_telegram_conversation", "is_group"): I,
    ("serverless_telegram_conversation", "is_private"): I,
    ("serverless_telegram_conversation", "get_chat"): U,
    ("serverless_telegram_conversation", "get_input_chat"): U,
    # --- serverless_message (method stubs) ---
    ("serverless_message", "delete"): U,
    ("serverless_message", "edit"): U,
    ("serverless_message", "reply"): U,
    ("serverless_message", "forward_to"): U,
    ("serverless_message", "get_reply_message"): U,
    ("serverless_message", "get_buttons"): I,
    ("serverless_message", "get_chat"): U,
    ("serverless_message", "get_entities_text"): I,
    ("serverless_message", "get_input_chat"): U,
    ("serverless_message", "get_input_sender"): U,
    ("serverless_message", "get_sender"): U,
    ("serverless_message", "mark_read"): U,
    ("serverless_message", "pin"): U,
    ("serverless_message", "respond"): U,
    ("serverless_message", "unpin"): U,
    # --- serverless_message_metadata ---
    ("serverless_message_metadata", "sender"): U,
    ("serverless_message_metadata", "chat"): U,
    ("serverless_message_metadata", "action_entities"): U,
    ("serverless_message_metadata", "geo"): U,
    ("serverless_message_metadata", "is_reply"): I,
    ("serverless_message_metadata", "reply_to_chat"): U,
    ("serverless_message_metadata", "reply_to_sender"): U,
    ("serverless_message_metadata", "to_id"): U,
    ("serverless_message_metadata", "via_input_bot"): U,
    ("serverless_message_metadata", "client"): U,
    ("serverless_message_metadata", "input_chat"): U,
    ("serverless_message_metadata", "input_sender"): U,
    ("serverless_message_metadata", "is_channel"): I,
    ("serverless_message_metadata", "is_group"): I,
    ("serverless_message_metadata", "is_private"): I,
    # --- serverless_message_serial_stubs ---
    ("serverless_message_serial_stubs", "from_reader"): U,
    ("serverless_message_serial_stubs", "serialize_bytes"): U,
    ("serverless_message_serial_stubs", "serialize_datetime"): U,
    ("serverless_message_serial_stubs", "to_dict"): I,
    ("serverless_message_serial_stubs", "to_json"): I,
    ("serverless_message_serial_stubs", "stringify"): I,
    ("serverless_message_serial_stubs", "pretty_format"): I,
    # --- serverless_client_misc_stubs ---
    ("serverless_client_misc_stubs", "action"): U,
    ("serverless_client_misc_stubs", "add_event_handler"): U,
    ("serverless_client_misc_stubs", "remove_event_handler"): U,
    ("serverless_client_misc_stubs", "list_event_handlers"): U,
    ("serverless_client_misc_stubs", "on"): U,
    ("serverless_client_misc_stubs", "build_reply_markup"): U,
    ("serverless_client_misc_stubs", "catch_up"): U,
    ("serverless_client_misc_stubs", "delete_dialog"): U,
    ("serverless_client_misc_stubs", "edit_folder"): U,
    ("serverless_client_misc_stubs", "end_takeout"): U,
    ("serverless_client_misc_stubs", "get_peer_id"): U,
    ("serverless_client_misc_stubs", "inline_query"): U,
    ("serverless_client_misc_stubs", "takeout"): U,
    # --- serverless_client_admin_stubs ---
    ("serverless_client_admin_stubs", "edit_admin"): U,
    ("serverless_client_admin_stubs", "edit_permissions"): U,
    ("serverless_client_admin_stubs", "kick_participant"): U,
    ("serverless_client_admin_stubs", "get_permissions"): U,
    ("serverless_client_admin_stubs", "get_admin_log"): U,
    ("serverless_client_admin_stubs", "iter_admin_log"): U,
    ("serverless_client_admin_stubs", "get_participants"): U,
    ("serverless_client_admin_stubs", "iter_participants"): U,
    ("serverless_client_admin_stubs", "get_stats"): U,
    ("serverless_client_admin_stubs", "pin_message"): U,
    ("serverless_client_admin_stubs", "unpin_message"): U,
    ("serverless_client_admin_stubs", "edit_message"): U,
    ("serverless_client_admin_stubs", "delete_messages"): U,
    ("serverless_client_admin_stubs", "forward_messages"): U,
    ("serverless_client_admin_stubs", "send_read_acknowledge"): U,
    # --- serverless_client_auth_stubs ---
    ("serverless_client_auth_stubs", "start"): U,
    ("serverless_client_auth_stubs", "sign_in"): U,
    ("serverless_client_auth_stubs", "sign_up"): U,
    ("serverless_client_auth_stubs", "send_code_request"): U,
    ("serverless_client_auth_stubs", "log_out"): U,
    ("serverless_client_auth_stubs", "qr_login"): U,
    ("serverless_client_auth_stubs", "edit_2fa"): U,
    ("serverless_client_auth_stubs", "disconnected"): U,
    ("serverless_client_auth_stubs", "set_proxy"): U,
    ("serverless_client_auth_stubs", "set_receive_updates"): U,
    ("serverless_client_auth_stubs", "run_until_disconnected"): U,
    # --- serverless_client_iter_stubs ---
    ("serverless_client_iter_stubs", "iter_dialogs"): U,
    ("serverless_client_iter_stubs", "iter_messages"): U,
    ("serverless_client_iter_stubs", "iter_drafts"): U,
    ("serverless_client_iter_stubs", "iter_profile_photos"): U,
    ("serverless_client_iter_stubs", "iter_download"): U,
    ("serverless_client_iter_stubs", "download_file"): U,
    ("serverless_client_iter_stubs", "download_profile_photo"): U,
    ("serverless_client_iter_stubs", "upload_file"): U,
    ("serverless_client_iter_stubs", "get_profile_photos"): U,
    ("serverless_client_iter_stubs", "get_drafts"): U,
    # --- serverless_telegram_client_core ---
    ("serverless_telegram_client_core", "get_entity"): U,
    # --- serverless_button ---
    ("serverless_button", "client"): U,
    ("serverless_button", "inline_query"): U,
    ("serverless_button", "url"): U,
    ("serverless_button", "click"): U,
}

IMPLEMENTABLE_COUNT = sum(1 for v in STUB_REGISTRY.values() if v == StubCategory.IMPLEMENTABLE)
