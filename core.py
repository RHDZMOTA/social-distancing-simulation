import concurrent.futures
import datetime
import itertools
import queue
import logging
import multiprocessing
import random
import uuid
from typing import List, Optional

import pandas as pd

from models.person import Person, PersonFactory
from settings import *
from utils import get_dict_hash_key

STRATEGY = SOCIAL_DISTANCING_VAR_STRATEGY

logger = logging.getLogger(__name__)


class Simulation(object):

    def __init__(self, days: int,  risky_interactions: float = 0.05):
        self.days = days
        self.risky_interactions = risky_interactions
        self.people = [
            *PersonFactory.create_people_with_route_student(
                k=SOCIAL_DISTANCING_VAR_STUDENTS,
                infected_cases=0
            ),
            *PersonFactory.create_people_with_route_worker(
                k=SOCIAL_DISTANCING_VAR_WORKERS,
                infected_cases=1
            ),
            *PersonFactory.create_people_with_route_worker_student(
                k=SOCIAL_DISTANCING_VAR_WORKER_STUDENTS,
                infected_cases=1
            ),
            *PersonFactory.create_people_with_route_stay_home(
                k=SOCIAL_DISTANCING_VAR_STAY_HOME,
                infected_cases=0
            )
        ]

    def _get_places(self, t: int):
        places = {}
        infected_cases = 0
        for person in self.people:
            place = person.position(t)
            key = f"{place.name}-{place.id}"
            places[key] = places.get(key, []) + [person]
            if person.infected:
                infected_cases += 1
        return places, infected_cases

    def _interactions(self, group: List[Person]):
        interactions_total = tuple(itertools.combinations(group, r=2))
        interactions_risky = int(self.risky_interactions * len(interactions_total))
        for a, b in random.choices(interactions_total, k=interactions_risky):
            a.interact(b)
        return len(interactions_total), interactions_risky

    def run(self, item_id: Optional[str] = None):
        item_id = item_id if item_id is not None else str(uuid.uuid4())
        logger.info(f"Simulation {item_id}: STARTED")
        results_confirmed = []
        results_interactions = []
        for t in range(self.days * 100):
            places, infected_cases = self._get_places(t)
            results_confirmed.append(
                {
                    "time": t,
                    "infected_cases": infected_cases
                }
            )
            for place, group in places.items():
                # Run interactions every 10 times a day.
                if t % 10:
                    continue
                total, risky = self._interactions(group)
                results_interactions.append({
                    "time": t,
                    "place": place,
                    "group": len(group),
                    "interactions_total": total,
                    "interactions_risky": risky,
                    "infected": len([p for p in group if p.infected])
                })
        logger.info(f"Simulation {item_id}: ENDED")
        return results_confirmed, results_interactions


class Simulator:
    simulation_queue = queue.Queue()

    def __init__(self, simulations: int = 1, njobs: int = -1):
        self.simulations = simulations
        self.njobs = njobs if not njobs else njobs if njobs > 0 else multiprocessing.cpu_count()

    @staticmethod
    def worker(q: queue.Queue):
        worker_id = str(uuid.uuid4())
        while True:
            try:
                item = q.get(block=False)
                item_id = item.pop("id")
                base_path = item.pop("base_path")
                # Configuration
                now = datetime.datetime.now().strftime("%Y-%m-%d")
                config = get_global_environment_vars()
                config_id = get_dict_hash_key(dictionary=config)
                # Run Simulation
                simulation = Simulation(**item)
                confirmed, interactions = simulation.run(item_id)
                file_path = os.path.join(base_path, STRATEGY, worker_id)
                os.makedirs(file_path, exist_ok=True)
                # Save confirmed data
                filename_confirmed = f"{now}-{item_id}-{config_id}-confirmed.csv"
                df_confirmed = pd.DataFrame(confirmed)
                df_confirmed["day"] = [int(t / 100) for t in df_confirmed.time]
                df_confirmed.to_csv(os.path.join(file_path, filename_confirmed), index=False)
                # Save interactions data
                filename_interactions = f"{now}-{item_id}-{config_id}-interactions.csv"
                df_interactions = pd.DataFrame(interactions)
                df_interactions["day"] = [int(t / 100) for t in df_interactions.time]
                df_interactions.to_csv(os.path.join(file_path, filename_interactions), index=False)
                # Save configuration variables
                with open(os.path.join(file_path, f"{now}-{item_id}-{config_id}-config.json"), "w") as f:
                    f.write(json.dumps(config))
            except Exception as e:
                if str(e):
                    logger.error(f"Worker {worker_id} encountered the following error: {e}")
                return

    def run(self, days: int = 50,  risky_interactions: float = 0.05, output_path: str = ""):
        for _ in range(self.simulations):
            self.simulation_queue.put({
                "id": str(uuid.uuid4()),
                "base_path": output_path,
                "days": days,
                "risky_interactions": risky_interactions
            })
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.njobs) as executor:
            for _ in range(self.njobs):
                executor.submit(self.worker, **{"q": self.simulation_queue})
