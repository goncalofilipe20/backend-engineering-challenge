from datetime import datetime, timedelta
from typing import Generator, List

from .constants import OUTPUT_DATE_FORMAT
from .models import TranslationEvent, MinuteStats


class MADeliveryTimeService:

    def __init__(
        self, input_source: Generator[TranslationEvent, None, None], window_size: int
    ) -> None:
        self.input_source = input_source
        self.window_size = window_size

        # algorithm status
        self.current_event: TranslationEvent = None
        self.window: tuple[datetime] = None
        self.window_history: List[MinuteStats] = []
        self.minute_total = 0
        self.minute_counter = 0

    def process_events(self):
        for event in self.input_source:
            self.current_event = event
            changed = self.update_window()

            while changed:
                self.register_minute(self.window[1] - timedelta(minutes=1))
                self.update_window_stats()
                changed = self.update_window()

            self.add_event_stats()

        # last event
        if self.current_event:
            self.register_minute(self.window[1])

    def update_window(self):
        # first event
        if self.window is None:
            rounded_datetime = self.current_event.timestamp.replace(
                second=0, microsecond=0
            )
            window_max = rounded_datetime + timedelta(minutes=1)
            self.window = (window_max - timedelta(minutes=self.window_size), window_max)
            return True

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
        print(
            f"date: {minute_datetime}, average_delivery_time: {minute_moving_average}"
        )

    def update_window_stats(self):
        minute_history = MinuteStats(
            total_duration=self.minute_total,
            nr_events=self.minute_counter,
        )

        if len(self.window_history) < self.window_size:
            self.window_history.append(minute_history)
            return

        # remove stats from events that are no longer inside the window
        # previous minute
        self.minute_total -= self.window_history[0].total_duration
        self.minute_counter -= self.window_history[0].nr_events
        self.window_history = [*self.window_history[1:], minute_history]

    def current_moving_average(self):
        if self.minute_counter == 0:
            return 0
        return self.minute_total / self.minute_counter

    def add_event_stats(self):
        self.minute_total += self.current_event.duration
        self.minute_counter += 1
