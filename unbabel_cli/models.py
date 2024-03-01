from dataclasses import dataclass
from datetime import datetime


@dataclass
class TranslationEvent:
    timestamp: datetime
    translation_id: str
    source_language: str
    target_language: str
    client_name: str
    event_name: str
    nr_words: int
    duration: int

    def __str__(self) -> str:
        return f"Translation Event - {self.client_name} {self.timestamp}"


@dataclass
class MinuteStats:
    total_duration: int
    nr_events: int
