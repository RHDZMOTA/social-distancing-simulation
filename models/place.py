import random
import uuid

from settings import *


class Place:

    def __init__(self, name, obj_id=None):
        self.id = obj_id if obj_id is not None else str(uuid.uuid4())
        self.name = name
        self.key = f"{name}-{self.id}"

    def __repr__(self):
        return f"Place(id={self.id}, name={self.name})"


class PlaceFactory:
    VALUES = {}

    class CHOICE:
        TAG_HOME = "home"
        TAG_WORKPLACE = "workplace"
        TAG_UNIVERSITY = "university"
        TAG_PUBLIC = "public"

    def __init__(self, name, n_options):
        self.name = name
        self.options = [
            Place(obj_id=i, name=self.name)
            for i in range(n_options)
        ]
        PlaceFactory.VALUES[name] = self

    def add_option(self, place: Place):
        self.options.append(place)
        return self

    def get_option(self, place_id):
        return self.options[place_id]

    def get_random_place(self):
        return random.choice(self.options)

    def get_random_places(self, n):
        return random.choices(self.options, k=n)

    @property
    def n_options(self):
        return len(self.options)

    @staticmethod
    def get_or_create(name, n_options=None):
        if name in PlaceFactory.VALUES:
            return PlaceFactory.VALUES[name]
        if n_options is not None:
            return PlaceFactory(name=name, n_options=n_options)
        raise ValueError("")


PLACE_FACTORY_HOME = PlaceFactory(
    name=PlaceFactory.CHOICE.TAG_HOME,
    n_options=SOCIAL_DISTANCING_VAR_FACTORY_NUM_HOMES
)
PLACE_FACTORY_WORKPLACE = PlaceFactory(
    name=PlaceFactory.CHOICE.TAG_WORKPLACE,
    n_options=SOCIAL_DISTANCING_VAR_FACTORY_NUM_WORKPLACE
)
PLACE_FACTORY_UNIVERSITY = PlaceFactory(
    name=PlaceFactory.CHOICE.TAG_UNIVERSITY,
    n_options=SOCIAL_DISTANCING_VAR_FACTORY_NUM_UNIVERSITY
)
PLACE_FACTORY_PUBLIC = PlaceFactory(
    name=PlaceFactory.CHOICE.TAG_PUBLIC,
    n_options=SOCIAL_DISTANCING_VAR_FACTORY_NUM_PUBLIC
)
