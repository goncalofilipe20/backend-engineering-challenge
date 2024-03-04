import uuid
from datetime import datetime
from random import randint

from unbabel_cli.constants import INPUT_DATE_FORMAT
from unbabel_cli.models import TranslationEvent


def translation_event(timestamp: str, duration: int):
    timestamp_datetime = datetime.strptime(timestamp, INPUT_DATE_FORMAT)
    return TranslationEvent(
        timestamp=timestamp_datetime,
        translation_id=str(uuid.uuid4()),
        source_language="en",
        target_language="fr",
        client_name="airliberty",
        event_name="translation_delivered",
        nr_words=randint(0, 100),
        duration=duration,
    )
