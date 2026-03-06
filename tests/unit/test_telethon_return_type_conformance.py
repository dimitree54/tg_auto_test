"""Return-type annotation conformance tests.

Verifies that return-type annotations on our fake classes are semantically
compatible with Telethon's real classes, catching regressions like click()
returning ServerlessMessage instead of ServerlessBotCallbackAnswer.
"""

import inspect

import pytest
from telethon import TelegramClient
from telethon.tl.custom.conversation import Conversation

from tg_auto_test.test_utils.models import ServerlessMessage
from tg_auto_test.test_utils.serverless_bot_callback_answer import ServerlessBotCallbackAnswer
from tg_auto_test.test_utils.serverless_client_public_api import ServerlessClientPublicAPI
from tg_auto_test.test_utils.serverless_client_query_api import ServerlessClientQueryAPI
from tg_auto_test.test_utils.serverless_telegram_client_core import ServerlessTelegramClientCore
from tg_auto_test.test_utils.serverless_telegram_conversation import ServerlessTelegramConversation

_EMPTY = inspect.Parameter.empty


def _return_annotation(cls: type, method_name: str) -> type | str:
    sig = inspect.signature(getattr(cls, method_name))
    return sig.return_annotation


_CONV_MSG_METHODS = ["get_response", "get_edit", "get_reply"]

_CLIENT_METHODS = [
    ("conversation", TelegramClient, ServerlessClientPublicAPI),
    ("get_me", TelegramClient, ServerlessClientQueryAPI),
    ("get_messages", TelegramClient, ServerlessClientQueryAPI),
    ("get_entity", TelegramClient, ServerlessTelegramClientCore),
    ("send_message", TelegramClient, ServerlessClientPublicAPI),
    ("send_file", TelegramClient, ServerlessTelegramClientCore),
    ("download_media", TelegramClient, ServerlessClientPublicAPI),
]


class TestClickReturnTypeRegression:
    def test_click_return_type_is_not_serverless_message(self) -> None:
        sig = inspect.signature(ServerlessMessage.click)
        assert sig.return_annotation is not ServerlessMessage

    def test_click_return_type_is_bot_callback_answer(self) -> None:
        sig = inspect.signature(ServerlessMessage.click)
        assert sig.return_annotation is ServerlessBotCallbackAnswer


class TestMessageReturnAnnotationsExist:
    def test_click_has_return_annotation(self) -> None:
        assert _return_annotation(ServerlessMessage, "click") is not _EMPTY

    def test_download_media_has_return_annotation(self) -> None:
        assert _return_annotation(ServerlessMessage, "download_media") is not _EMPTY


class TestConversationReturnAnnotations:
    @pytest.mark.parametrize("method_name", _CONV_MSG_METHODS)
    def test_our_annotation_is_serverless_message(self, method_name: str) -> None:
        our_ret = _return_annotation(ServerlessTelegramConversation, method_name)
        assert our_ret is ServerlessMessage, (
            f"ServerlessTelegramConversation.{method_name} returns {our_ret}, expected ServerlessMessage"
        )

    @pytest.mark.parametrize("method_name", _CONV_MSG_METHODS)
    def test_telethon_lacks_annotation(self, method_name: str) -> None:
        telethon_ret = _return_annotation(Conversation, method_name)
        assert telethon_ret is _EMPTY, (
            f"Telethon Conversation.{method_name} now has annotation {telethon_ret}; update tests"
        )


class TestClientReturnAnnotations:
    @pytest.mark.parametrize(
        ("method_name", "telethon_cls", "our_cls"),
        _CLIENT_METHODS,
        ids=[t[0] for t in _CLIENT_METHODS],
    )
    def test_telethon_has_return_annotation(
        self,
        method_name: str,
        telethon_cls: type,
        our_cls: type,
    ) -> None:
        del our_cls
        telethon_ret = _return_annotation(telethon_cls, method_name)
        assert telethon_ret is not _EMPTY, (
            f"Expected Telethon {telethon_cls.__name__}.{method_name} to have a return annotation"
        )

    @pytest.mark.parametrize(
        ("method_name", "telethon_cls", "our_cls"),
        _CLIENT_METHODS,
        ids=[t[0] for t in _CLIENT_METHODS],
    )
    def test_our_has_return_annotation(
        self,
        method_name: str,
        telethon_cls: type,
        our_cls: type,
    ) -> None:
        del telethon_cls
        our_ret = _return_annotation(our_cls, method_name)
        assert our_ret is not _EMPTY, f"{our_cls.__name__}.{method_name} is missing a return annotation"


_MSG_RETURNING_CLIENT_METHODS = [
    ("send_message", ServerlessClientPublicAPI),
    ("send_file", ServerlessTelegramClientCore),
]


class TestClientMessageReturnTypes:
    @pytest.mark.parametrize(
        ("method_name", "our_cls"),
        _MSG_RETURNING_CLIENT_METHODS,
        ids=[t[0] for t in _MSG_RETURNING_CLIENT_METHODS],
    )
    def test_returns_serverless_message(self, method_name: str, our_cls: type) -> None:
        our_ret = _return_annotation(our_cls, method_name)
        assert our_ret is ServerlessMessage, (
            f"{our_cls.__name__}.{method_name} returns {our_ret}, expected ServerlessMessage"
        )

    def test_conversation_returns_serverless_conversation(self) -> None:
        our_ret = _return_annotation(ServerlessClientPublicAPI, "conversation")
        assert our_ret is ServerlessTelegramConversation
