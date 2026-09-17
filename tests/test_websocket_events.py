from app.api.v1.events import (
    MessageSendEvent,
    SessionEndEvent,
    incoming_event_adapter,
)


def test_message_send_event_is_typed():
    event = incoming_event_adapter.validate_json(
        '{"type":"message.send","text":"Bugün ne çalışmalıyım?"}'
    )

    assert isinstance(event, MessageSendEvent)
    assert event.text == "Bugün ne çalışmalıyım?"


def test_session_end_event_is_typed():
    event = incoming_event_adapter.validate_json('{"type":"session.end"}')

    assert isinstance(event, SessionEndEvent)


def test_unknown_event_is_rejected():
    invalid_event = '{"type":"message.unknown","text":"test"}'

    try:
        incoming_event_adapter.validate_json(invalid_event)
    except ValueError:
        pass
    else:
        raise AssertionError("Unknown event type must be rejected")


def test_extra_event_fields_are_rejected():
    invalid_event = '{"type":"message.send","text":"test","student_id":"other"}'

    try:
        incoming_event_adapter.validate_json(invalid_event)
    except ValueError:
        pass
    else:
        raise AssertionError("Extra event fields must be rejected")