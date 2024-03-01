import json
from datetime import datetime

from .constants import INPUT_DATE_FORMAT
from .models import TranslationEvent


def read_event(input_file: str):
    with open(input_file, "r") as file:
        for translation_event in file:
            event_data = json.loads(translation_event)
            translation_event = parse_event(event_data)
            yield translation_event


def parse_event(event_data: dict) -> TranslationEvent:
    timestamp_str = event_data["timestamp"]
    timestamp_datetime = datetime.strptime(timestamp_str, INPUT_DATE_FORMAT)

    return TranslationEvent(
        timestamp=timestamp_datetime,
        translation_id=event_data["translation_id"],
        source_language=event_data["source_language"],
        target_language=event_data["target_language"],
        client_name=event_data["client_name"],
        event_name=event_data["event_name"],
        nr_words=event_data["nr_words"],
        duration=event_data["duration"],
    )
