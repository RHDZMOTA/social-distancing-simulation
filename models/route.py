import itertools
import random
from typing import List

from models.place import (
    Place,
    PLACE_FACTORY_HOME,
    PLACE_FACTORY_PUBLIC,
    PLACE_FACTORY_UNIVERSITY,
    PLACE_FACTORY_WORKPLACE
)


class Stop:

    def __init__(self, place: Place, duration: int):
        self.place = place
        self.duration = duration

    def __repr__(self):
        place = self.place.__repr__()
        return f"Stop(place={place}, time={self.duration})"


class Route:

    def __init__(self, stops: List[Stop], weight: float = 1):
        self.weight = weight
        self.stops = stops
        time_position_accum = list(itertools.accumulate([stop.duration for stop in stops]))
        if time_position_accum[-1] != 100:
            raise ValueError("Total duration must be 100.")
        time_position_init = [0] + time_position_accum[:-1]
        self._position = {
            start + incr: stop.place
            for stop, start in zip(stops, time_position_init)
            for incr in range(stop.duration)
            }

    def __repr__(self):
        return f"Route(stops={[s.__repr__() for s in self.stops]})"

    def get_place(self, t: int):
        # TODO: consider calculating the position given a "t" (compute VS memory)
        return self._position[t]

    @staticmethod
    def create_home_route(home: Place, weight: float = 1):
        return Route(
            stops=[
                Stop(place=home, duration=100)
            ],
            weight=weight
        )

    @staticmethod
    def create_home_to_outside_route(home: Place, outside: Place, weight: float, outside_duration: int = 60):
        stop_home_duration = int(50 - outside_duration / 2)
        return Route(
            stops=[
                Stop(place=home, duration=stop_home_duration),
                Stop(place=outside, duration=outside_duration),
                Stop(place=home, duration=stop_home_duration)
            ],
            weight=weight
        )

    @staticmethod
    def create_home_to_public_routes(
            home: Place, public_places: List[Place], weight: float, outside_duration: int = 60) -> List['Route']:
        stop_home_duration = int(50 - outside_duration / 2)
        route_weight = weight / len(public_places)
        return [
            Route(
                stops=[
                    Stop(place=home, duration=stop_home_duration),
                    Stop(place=public, duration=outside_duration),
                    Stop(place=home, duration=stop_home_duration)
                ],
                weight=route_weight
            )
            for public in public_places
        ]


class Routes:

    def __init__(self, routes: List[Route]):
        self.routes = routes

    def __repr__(self):
        return f"Route(routes={len(self.routes)})"

    def append_route(self, route):
        self.routes.append(route)
        return self

    def random_choices(self, k=1):
        return random.choices(
            population=self.routes,
            weights=[r.weight for r in self.routes],
            k=k
        )

    @staticmethod
    def get_routes_student():
        home = PLACE_FACTORY_HOME.get_random_place()
        university = PLACE_FACTORY_UNIVERSITY.get_random_place()
        public_regular = PLACE_FACTORY_PUBLIC.get_random_place()
        return Routes(
                routes=[
                    Route.create_home_route(
                        home=home,
                        weight=1
                    ),
                    Route.create_home_to_outside_route(
                        home=home,
                        outside=university,
                        outside_duration=60,
                        weight=3
                    ),
                    *Route.create_home_to_public_routes(
                        home=home,
                        public_places=[public_regular] + [
                            PLACE_FACTORY_PUBLIC.get_random_place()
                            for _ in range(2)
                        ],
                        outside_duration=60,
                        weight=2
                    ),
                    Route(
                        stops=[
                            Stop(place=home, duration=20),
                            Stop(place=university, duration=30),
                            Stop(place=public_regular, duration=30),
                            Stop(place=home, duration=20)
                        ],
                        weight=1
                    )
                ]
            )

    @staticmethod
    def get_routes_worker():
        home = PLACE_FACTORY_HOME.get_random_place()
        workplace = PLACE_FACTORY_WORKPLACE.get_random_place()
        public_regular = PLACE_FACTORY_PUBLIC.get_random_place()
        return Routes(
            routes=[
                Route.create_home_route(
                    home=home,
                    weight=1
                ),
                Route.create_home_to_outside_route(
                    home=home,
                    outside=workplace,
                    outside_duration=60,
                    weight=3
                ),
                *Route.create_home_to_public_routes(
                    home=home,
                    public_places=[public_regular] + [
                        PLACE_FACTORY_PUBLIC.get_random_place()
                        for _ in range(2)
                    ],
                    outside_duration=60,
                    weight=1
                ),
                Route(
                    stops=[
                        Stop(place=home, duration=20),
                        Stop(place=workplace, duration=30),
                        Stop(place=public_regular, duration=30),
                        Stop(place=home, duration=20)
                    ],
                    weight=2
                )
            ]
        )

    @staticmethod
    def get_routes_worker_student():
        home = PLACE_FACTORY_HOME.get_random_place()
        workplace = PLACE_FACTORY_WORKPLACE.get_random_place()
        university = PLACE_FACTORY_UNIVERSITY.get_random_place()
        public_regular = PLACE_FACTORY_PUBLIC.get_random_place()
        return Routes(
                routes=[
                    Route.create_home_route(
                        home=home,
                        weight=1
                    ),
                    *Route.create_home_to_public_routes(
                        home=home,
                        public_places=[public_regular] + [
                            PLACE_FACTORY_PUBLIC.get_random_place()
                            for _ in range(2)
                        ],
                        outside_duration=60,
                        weight=1
                    ),
                    Route(
                        stops=[
                            Stop(place=home, duration=10),
                            Stop(place=university, duration=40),
                            Stop(place=workplace, duration=40),
                            Stop(place=home, duration=10)
                        ],
                        weight=3
                    ),
                    Route(
                        stops=[
                            Stop(place=home, duration=10),
                            Stop(place=university, duration=30),
                            Stop(place=workplace, duration=30),
                            Stop(place=public_regular, duration=20),
                            Stop(place=home, duration=10)
                        ],
                        weight=2
                    )
                ]
            )

    @staticmethod
    def get_routes_stay_home():
        home = PLACE_FACTORY_HOME.get_random_place()
        return Routes(
                routes=[
                    Route.create_home_route(
                        home=home,
                        weight=3
                    ),
                    *Route.create_home_to_public_routes(
                        home=home,
                        public_places=[
                            PLACE_FACTORY_PUBLIC.get_random_place()
                            for _ in range(3)
                        ],
                        outside_duration=60,
                        weight=4
                    )
                ]
            )
