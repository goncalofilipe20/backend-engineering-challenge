import json
import os
from abc import ABC, abstractmethod
from datetime import datetime

from .constants import INPUT_DATE_FORMAT
from .models import TranslationEvent


# ----------------------------- Input --------------------------------------


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


# ----------------------------- Output --------------------------------------


class OutputSource(ABC):

    @abstractmethod
    def write(self, data):
        raise NotImplementedError()


class FileOutputSource(OutputSource):

    def __init__(self, output_file: str) -> None:
        self.output_file = output_file

    def write(self, data):
        mode = "w" if not os.path.exists(self.output_file) else "a"
        appending = mode == "a"

        with open(self.output_file, mode) as file:
            json_str = json.dumps(data)
            if appending:
                file.write("\n")
            file.write(json_str)


def get_output_file_name(input_file_name: str):
    extension_index = input_file_name.rindex(".")
    name = input_file_name[:extension_index]
    extension = input_file_name[extension_index:]
    return f"{name}_output.{extension}"
