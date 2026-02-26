do_request  # BaseRequest override called by python-telegram-bot framework

# Public API methods/properties used by test consumers
image_size_from_bytes
image_size_from_path
file_size
document
button_count
download_media
click
sender
sender_id
chat
chat_id
raw_text
reply_to_msg_id
forward
via_bot
sticker
contact
venue
gif
game
web_preview
dice
audio
video
action_entities
geo
is_reply
reply_to_chat
reply_to_sender
to_id
via_input_bot
client
input_chat
input_sender
is_channel
is_group
is_private
get_buttons
get_chat
get_entities_text
get_input_chat
get_input_sender
get_sender
mark_read
pin
respond
unpin
from_reader
serialize_bytes
serialize_datetime
to_dict
to_json
stringify
pretty_format
CONSTRUCTOR_ID
SUBCLASS_OF_ID
ServerlessTelegramClient
ServerlessClientAuthStubs
ServerlessClientAdminStubs
ServerlessClientIterStubs
ServerlessClientMiscStubs
get_input_entity
connect
disconnect
get_me
get_dialogs
conversation
send_message
send_file
get_response
get_reply
get_edit
get_scoped_commands
get_menu_button

# Client stub methods (public API compatibility stubs)
action
add_event_handler
build_reply_markup
catch_up
delete_dialog
delete_messages
disconnected
download_file
download_profile_photo
edit_2fa
edit_admin
edit_folder
edit_message
edit_permissions
end_takeout
forward_messages
get_admin_log
get_drafts
get_participants
get_peer_id
get_permissions
get_profile_photos
get_stats
inline_query
iter_admin_log
iter_dialogs
iter_download
iter_drafts
iter_messages
iter_participants
iter_profile_photos
kick_participant
list_event_handlers
log_out
on
pin_message
qr_login
remove_event_handler
run_until_disconnected
send_code_request
send_read_acknowledge
set_proxy
set_receive_updates
sign_in
sign_up
start
takeout
unpin_message
upload_file


# Test helpers
build_test_application  # Helper function in tests/unit/helpers_ptb_app.py

# Demo UI server - route handlers are dynamically registered
menu_button_type  # Pydantic model field
create_demo_app  # Factory function for demo apps
on_action  # Public API callback parameter
index  # FastAPI route handler
serve_file  # FastAPI route handler
get_state  # FastAPI route handler
send_message  # FastAPI route handler
send_document  # FastAPI route handler
send_voice  # FastAPI route handler
send_photo  # FastAPI route handler
send_video_note  # FastAPI route handler
pay_invoice  # FastAPI route handler
handle_callback  # FastAPI route handler
reset  # FastAPI route handler
vote_poll  # FastAPI route handler
handle_file_upload  # File upload helper function

# Type alias used inside string annotation for JsonValue
JsonPrimitive  # Referenced in JsonValue type alias string

# Mock attributes in tests (vulture false positives)
__aenter__  # Async context manager mock setup
__aexit__  # Async context manager mock setup
return_value  # unittest.mock return value setup

# Protocol method parameters (required for typing but unused in protocol definition)
exc_val  # Context manager protocol parameter
args  # *args parameter in message methods matching Telethon signature
kwargs  # **kwargs parameter in message methods matching Telethon signature

# Reverse conformance test class attributes (used in test parametrization)
IMPLEMENTED_MEMBERS  # Class attribute storing implemented methods for test parametrization

# Puppet recorder - experimental demo server with recording
create_puppet_recorder_app  # Factory function for puppet recorder apps
start_recording  # FastAPI route handler
stop_recording  # FastAPI route handler
clear_recording  # FastAPI route handler
recording_status  # FastAPI route handler
recording_steps  # FastAPI route handler
export_test_code  # FastAPI route handler
generate_test_code  # Public API function for code generation
PuppetRecorderServer  # Public class for puppet recorder server
is_recording  # RecordingSession property
step_count  # RecordingSession property
recorder_server  # FastAPI app.state attribute
