import random
from typing import List

from models.route import Route, Routes
from models.place import Place


class Person(object):

    def __init__(self, routes: Routes, infected: bool = False):
        self.routes = routes
        self.infected = infected
        self.history: List[Route] = []

    @property
    def days(self):
        return len(self.history)

    def get_route(self, t):
        day = int(t / 100) + 1
        if day > self.days:
            route, = self.routes.random_choices(k=1)
            self.history.append(route)
            return route
        return self.history[-1]

    def position(self, t: int) -> Place:
        route = self.get_route(t)
        return route.get_place(t % 100)

    def interact(self, other: 'Person'):
        if other.infected:
            self.infected = True
        elif self.infected:
            other.infected = True


class PersonFactory:

    @staticmethod
    def _infect(group: List[Person], cases: int):
        for person in random.choices(population=group, k=cases):
            person.infected = True
        return group

    @staticmethod
    def create_people(k, route_function, infected_cases=0):
        people = [
            Person(routes=route_function(), infected=False)
            for _ in range(k)
        ]
        return PersonFactory._infect(people, infected_cases) if infected_cases else people

    @staticmethod
    def create_people_with_route_student(k=1, infected_cases=0):
        route_function = Routes.get_routes_worker_student
        return PersonFactory.create_people(k=k, route_function=route_function, infected_cases=infected_cases)

    @staticmethod
    def create_people_with_route_worker(k=1, infected_cases=0):
        route_function = Routes.get_routes_worker
        return PersonFactory.create_people(k=k, route_function=route_function, infected_cases=infected_cases)

    @staticmethod
    def create_people_with_route_worker_student(k=1, infected_cases=0):
        route_function = Routes.get_routes_worker_student
        return PersonFactory.create_people(k=k, route_function=route_function, infected_cases=infected_cases)

    @staticmethod
    def create_people_with_route_stay_home(k=1, infected_cases=0):
        route_function = Routes.get_routes_stay_home
        return PersonFactory.create_people(k=k, route_function=route_function, infected_cases=infected_cases)
