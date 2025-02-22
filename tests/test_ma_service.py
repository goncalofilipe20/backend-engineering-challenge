from unbabel_cli.services import MADeliveryTimeService

from .fixtures import translation_event


class OutputSourceMock:

    def __init__(self) -> None:
        self.output = []

    def write(self, data):
        self.output.append(data)


class TestMovingAverageService:
    def test_events_different_minutes_window_size_1(self):
        """
        Test events on consecutive and different minutes, window size 1.
        """
        events = [
            translation_event("2018-12-26 18:12:08.509654", 10),
            translation_event("2018-12-26 18:13:08.509654", 30),
        ]

        input_source = lambda events: (e for e in events)
        output_source = OutputSourceMock()
        ma_service = MADeliveryTimeService(input_source(events), 1, output_source)
        ma_service.process_events()

        output = output_source.output
        assert len(output) == 3
        self.assert_output_date(output[0], "2018-12-26 18:12:00", 0)
        self.assert_output_date(output[1], "2018-12-26 18:13:00", 10)
        self.assert_output_date(output[2], "2018-12-26 18:14:00", 30)

    def test_events_different_minutes_window_size_10(self):
        """
        Test events on consecutive and different minutes, window size 10.
        Should aggregate both in a single result.
        """
        events = [
            translation_event("2018-12-26 18:12:08.509654", 10),
            translation_event("2018-12-26 18:13:08.509654", 30),
        ]

        input_source = lambda events: (e for e in events)
        output_source = OutputSourceMock()
        ma_service = MADeliveryTimeService(input_source(events), 10, output_source)
        ma_service.process_events()

        output = output_source.output
        assert len(output) == 3
        self.assert_output_date(output[0], "2018-12-26 18:12:00", 0)
        self.assert_output_date(output[1], "2018-12-26 18:13:00", 10)
        self.assert_output_date(output[2], "2018-12-26 18:14:00", 20)

    def test_events_same_minute_window_size_1(self):
        """
        Test events on the same minute, window size 10.
        Should aggregate all in a single result.
        """
        events = [
            translation_event("2018-12-26 18:12:08.509654", 10),
            translation_event("2018-12-26 18:12:09.509654", 30),
            translation_event("2018-12-26 18:12:11.509654", 50),
        ]

        input_source = lambda events: (e for e in events)
        output_source = OutputSourceMock()
        ma_service = MADeliveryTimeService(input_source(events), 10, output_source)
        ma_service.process_events()

        output = output_source.output
        assert len(output) == 2
        self.assert_output_date(output[0], "2018-12-26 18:12:00", 0)
        self.assert_output_date(output[1], "2018-12-26 18:13:00", 30)

    def test_multiple_events_with_gap_window_size_1(self):
        """
        Test events with a time gap higher than window size.
        """
        events = [
            translation_event("2018-12-26 18:12:08.509654", 10),
            translation_event("2018-12-26 18:13:08.509654", 30),
            translation_event("2018-12-26 18:15:08.509654", 30),
            translation_event("2018-12-26 18:15:11.509654", 50),
        ]

        input_source = lambda events: (e for e in events)
        output_source = OutputSourceMock()
        ma_service = MADeliveryTimeService(input_source(events), 1, output_source)
        ma_service.process_events()

        output = output_source.output
        assert len(output) == 5
        self.assert_output_date(output[0], "2018-12-26 18:12:00", 0)
        self.assert_output_date(output[1], "2018-12-26 18:13:00", 10)
        self.assert_output_date(output[2], "2018-12-26 18:14:00", 30)
        self.assert_output_date(output[3], "2018-12-26 18:15:00", 0)
        self.assert_output_date(output[4], "2018-12-26 18:16:00", 40)

    def test_events_timestamps_micro_00(self):
        """
        Test edge case, different events on the exact minute.
        """
        events = [
            translation_event("2018-12-26 18:12:00.000000", 10),
            translation_event("2018-12-26 18:13:00.000000", 30),
        ]

        input_source = lambda events: (e for e in events)
        output_source = OutputSourceMock()
        ma_service = MADeliveryTimeService(input_source(events), 1, output_source)
        ma_service.process_events()

        output = output_source.output
        assert len(output) == 2
        self.assert_output_date(output[0], "2018-12-26 18:12:00", 10)
        self.assert_output_date(output[1], "2018-12-26 18:13:00", 30)

    def test_events_different_minutes_window_size_2(self):
        """
        Test events on consecutive and different minutes, window size 2.
        """
        events = [
            translation_event("2018-12-26 18:12:08.509654", 10),
            translation_event("2018-12-26 18:13:08.509654", 30),
            translation_event("2018-12-26 18:14:08.509654", 20),
            translation_event("2018-12-26 18:15:11.509654", 50),
        ]

        input_source = lambda events: (e for e in events)
        output_source = OutputSourceMock()
        ma_service = MADeliveryTimeService(input_source(events), 2, output_source)
        ma_service.process_events()

        output = output_source.output
        assert len(output) == 5
        self.assert_output_date(output[0], "2018-12-26 18:12:00", 0)
        self.assert_output_date(output[1], "2018-12-26 18:13:00", 10)
        self.assert_output_date(output[2], "2018-12-26 18:14:00", 20)
        self.assert_output_date(output[3], "2018-12-26 18:15:00", 25)
        self.assert_output_date(output[4], "2018-12-26 18:16:00", 35)

    def test_events_different_minutes_window_size_5(self):
        """
        Test events on different minutes, window size 5.
        """
        events = [
            translation_event("2018-12-26 18:12:00.000000", 10),
            translation_event("2018-12-26 18:12:08.509654", 30),
            translation_event("2018-12-26 18:14:08.509654", 20),
            translation_event("2018-12-26 18:20:00.000000", 50),
        ]

        input_source = lambda events: (e for e in events)
        output_source = OutputSourceMock()
        ma_service = MADeliveryTimeService(input_source(events), 5, output_source)
        ma_service.process_events()

        output = output_source.output
        assert len(output) == 9
        self.assert_output_date(output[0], "2018-12-26 18:12:00", 10)
        self.assert_output_date(output[1], "2018-12-26 18:13:00", 20)
        self.assert_output_date(output[2], "2018-12-26 18:14:00", 20)
        self.assert_output_date(output[3], "2018-12-26 18:15:00", 20)
        self.assert_output_date(output[4], "2018-12-26 18:16:00", 20)
        self.assert_output_date(output[5], "2018-12-26 18:17:00", 25)
        self.assert_output_date(output[6], "2018-12-26 18:18:00", 20)
        self.assert_output_date(output[7], "2018-12-26 18:19:00", 20)
        self.assert_output_date(output[8], "2018-12-26 18:20:00", 50)

    def assert_output_date(self, date_result, date, average_delivery_time):
        assert date_result["date"] == date
        assert date_result["average_delivery_time"] == average_delivery_time
