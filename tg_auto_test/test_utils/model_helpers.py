"""Helper functions for ServerlessMessage model properties."""

from typing import cast

from telethon.tl.types import MessageMediaPoll, Poll, PollAnswer, PollResults, TextWithEntities

from tg_auto_test.test_utils.json_types import JsonValue


def build_poll_media(poll_data: JsonValue) -> MessageMediaPoll | None:
    """Build a Telethon MessageMediaPoll from poll data."""
    if poll_data is None or not isinstance(poll_data, dict):
        return None

    answers = []
    options = poll_data.get("options")
    if isinstance(options, list):
        for i, opt in enumerate(cast(list[JsonValue], options)):
            if isinstance(opt, dict) and isinstance(opt.get("text"), str):
                text = TextWithEntities(text=cast(str, opt["text"]), entities=[])
                answers.append(PollAnswer(text=text, option=bytes([i])))

    question = poll_data.get("question", "")
    question_text = question if isinstance(question, str) else str(question)

    is_closed = bool(poll_data.get("is_closed", False))
    is_anonymous = bool(poll_data.get("is_anonymous", True))
    allows_multiple = bool(poll_data.get("allows_multiple_answers", False))
    is_quiz = poll_data.get("type") == "quiz"

    poll_id = poll_data.get("id", "")
    poll_id_str = poll_id if isinstance(poll_id, str) else str(poll_id)

    tl_poll = Poll(
        id=hash(poll_id_str) & 0x7FFFFFFFFFFFFFFF,
        question=TextWithEntities(text=question_text, entities=[]),
        answers=answers,
        closed=is_closed,
        public_voters=not is_anonymous,
        multiple_choice=allows_multiple,
        quiz=is_quiz,
        close_period=None,
        close_date=None,
    )

    results = PollResults(results=[], total_voters=0, recent_voters=[])

    return MessageMediaPoll(poll=tl_poll, results=results)
