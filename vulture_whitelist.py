do_request  # BaseRequest override called by python-telegram-bot framework

# Public API methods/properties used by test consumers
image_size_from_bytes
image_size_from_path
file_size
document
button_count
download_media
click
ServerlessTelegramClient
get_input_entity
connect
disconnect
get_me
get_dialogs
conversation
send_message
send_file
get_response
click_inline_button

# Test helpers
build_test_application  # Helper function in tests/unit/helpers_ptb_app.py

# Demo UI server - route handlers are dynamically registered
menu_button_type  # Pydantic model field
create_demo_app  # Factory function for demo apps
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
