import requests
import lxml
import re
from bs4 import BeautifulSoup
from datetime import datetime, time
from enum import Enum
import urllib


class TransportType(Enum):
    BUS = 'avto'
    TROLLEYBUS = 'trol'
    TRAMWAY = 'tram'


class DayType(Enum):
    WEEKDAYS = '1111100'
    WEEKENDS = '0000011'


class Direction(Enum):
    TO_CENTER = 'AB'
    FROM_CENTER = 'BA'


class Schedule:
    def __init__(self, vid: TransportType, number, day: DayType, direction: Direction, waypoint):
        self.vid = vid
        self.day = day
        self.patternbus = r'\s\b\d{1,4}\s'
        self.number = number
        self.waypoint = waypoint
        self.direction = direction

    def encode_to_cp1251(self, string_to_encode):
        encoded_string = string_to_encode.encode('cp1251')
        return urllib.parse.quote_plus(encoded_string)

    def print_route_table(self):
        encoded_number = self.encode_to_cp1251(self.number)
        url_params = f"type={self.vid.value}&way={encoded_number}&date={self.day.value}&direction={self.direction.value}&waypoint={self.waypoint}"
        response = requests.get(f"http://mosgortrans.org/pass3/shedule.php?{url_params}")

        soup = BeautifulSoup(response.text, "lxml")
        cnt = 0
        hour = ''
        schedule_times = []
        schedule_table = soup.find_all('table')[3]
        for h in schedule_table.find_all('span'):
            if h['class'] == ['hour']:
                hour = h.string
            elif h['class'] == ['minutes'] and h.string is not None:
                minute = h.string
                schedule_time = f"{hour}:{minute}"
                schedule_times.append(schedule_time)

        actual_schedules = list(
            filter(
                lambda schedule: datetime.now().time() < datetime.strptime(schedule, '%H:%M').time(),
                schedule_times
            )
        )[:5]

        print(f"Остановка: {soup.h2.text}, Маршрут {self.number}", end=': ')
        print(*actual_schedules, sep=', ')


schedule = Schedule(TransportType.BUS, '299', DayType.WEEKENDS, Direction.TO_CENTER, '13')
schedule.print_route_table()
schedule = Schedule(TransportType.BUS, '608', DayType.WEEKENDS, Direction.TO_CENTER, '17')
schedule.print_route_table()
schedule = Schedule(TransportType.BUS, 'Т67', DayType.WEEKENDS, Direction.TO_CENTER, '10')
schedule.print_route_table()
