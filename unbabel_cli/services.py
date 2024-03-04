from collections import OrderedDict
from datetime import datetime, timedelta
from typing import Generator

from .constants import OUTPUT_DATE_FORMAT
from .data import OutputSource
from .models import TranslationEvent, MinuteStats


class MADeliveryTimeService:

    def __init__(
        self,
        input_source: Generator[TranslationEvent, None, None],
        window_size: int,
        output_source: OutputSource,
    ) -> None:
        self.input_source = input_source
        self.output_source = output_source
        self.window_size = window_size

        # algorithm status
        self.current_event: TranslationEvent = None
        self.window: tuple[datetime] = None
        self.window_history = OrderedDict()

        self.window_total = 0
        self.window_counter = 0

    def process_events(self):
        for event in self.input_source:
            self.current_event = event
            changed = self.update_window()

            while changed:
                self.register_minute(self.window[1] - timedelta(minutes=1))
                self.update_window_history()
                changed = self.update_window()

            self.add_event_stats()
            self.save_window_history()

        # last event
        if self.current_event:
            self.register_minute(self.window[1])

    def update_window(self):
        # first event
        if self.window is None:
            rounded_datetime = self.current_event.timestamp.replace(
                second=0, microsecond=0
            )

            if self.current_event.timestamp == rounded_datetime:
                window_max = rounded_datetime
            else:
                window_max = rounded_datetime + timedelta(minutes=1)

            self.window = (window_max - timedelta(minutes=self.window_size), window_max)
            return self.current_event.timestamp > rounded_datetime

        # still within the current window
        time_diff = self.current_event.timestamp - self.window[0]
        minutes_diff = time_diff.total_seconds() / 60
        if minutes_diff <= self.window_size:
            return False

        # event out of window
        window_minute_min = self.window[0] + timedelta(minutes=1)
        window_minute_max = self.window[1] + timedelta(minutes=1)
        self.window = (window_minute_min, window_minute_max)
        return True

    def register_minute(self, minute):
        minute_datetime = minute.strftime(OUTPUT_DATE_FORMAT)
        minute_moving_average = self.current_moving_average()

        minute_data = {
            "date": minute_datetime,
            "average_delivery_time": minute_moving_average,
        }

        self.output_source.write(minute_data)

    def save_window_history(self):
        rounded_datetime = self.current_event.timestamp.replace(second=0, microsecond=0)
        if self.current_event.timestamp == rounded_datetime:
            minute_key = rounded_datetime + timedelta(minutes=1)
        else:
            minute_key = rounded_datetime

        if minute_key in self.window_history:
            minute_stats = self.window_history[minute_key]
            minute_stats.total_duration += self.current_event.duration
            minute_stats.nr_events += 1

        else:
            self.window_history[minute_key] = MinuteStats(
                total_duration=self.current_event.duration,
                nr_events=1,
            )

    def update_window_history(self):
        shift = len(self.window_history) > 0 and self.window[0] > next(
            iter(self.window_history)
        )

        # shift history
        if shift:
            stats_to_remove = self.window_history.popitem(last=False)[1]
            self.window_total -= stats_to_remove.total_duration
            self.window_counter -= stats_to_remove.nr_events

    def current_moving_average(self):
        if self.window_counter == 0:
            return 0
        return self.window_total / self.window_counter

    def add_event_stats(self):
        self.window_total += self.current_event.duration
        self.window_counter += 1
