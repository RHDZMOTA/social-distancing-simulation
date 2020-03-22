import logging
import uuid
from typing import Optional

import fire
import pandas as pd
import matplotlib.pyplot as plt

from core import Simulator, Simulation
from settings import *
from utils import list_dir

logger = logging.getLogger(__name__)


class Main:

    @staticmethod
    def show_strategies():
        return "\n".join(f"* {strategy}" for strategy in SOCIAL_DISTANCING_VAR_STRATEGIES)

    @staticmethod
    def simulate(days=100, show=False, filename=""):
        simulation = Simulation(days=days)
        results_confirmed, results_interactions = simulation.run()
        df = pd.DataFrame(results_confirmed)
        df["day"] = [int(t / 100) for t in df.time]
        if show:
            df.groupby("day")["infected_cases"].max().reset_index().plot(x="day", y="infected_cases")
            plt.title("Confirmed cases")
            plt.xlabel("Days since first case")
            plt.ylabel("Infected people")
            plt.show()
        if filename.endswith(".csv"):
            df.to_csv(filename, index=False)

    @staticmethod
    def simulate_multiple(name: str = "", simulations: int = 1, days: int = 100, show: bool = False):
        output_id = str(uuid.uuid4()) if not name else name
        simulator = Simulator(simulations=simulations)
        simulator.run(days=days, output_path=output_id)
        if show:
            Main.analyze(simulation_name=name, show=True)

    @staticmethod
    def _get_concat_confirmed_df(simulation_name: str):
        csv_files = [filename for filename in list_dir(simulation_name) if filename.endswith(".csv")]
        confirmed = pd.concat(
            [
                (
                    pd.read_csv(filename)
                    .groupby("day")["infected_cases"].max().reset_index()
                    .assign(strategy="distancing" if "distancing" in filename else "interacting")
                )
                for filename in csv_files
                if "confirmed" in filename
            ]
        )
        return confirmed

    @staticmethod
    def analyze(simulation_name: str,
                days: Optional[int] = None, avg_days: int = 10, show: bool = False, save: str = ""):
        confirmed = Main._get_concat_confirmed_df(simulation_name)
        max_day = days if days is not None else confirmed.day.max()
        confirmed_avg = confirmed.query(f"day <= {max_day}")\
            .groupby(["day", "strategy"])["infected_cases"].mean().reset_index()
        # Create confirmed time-series
        confirmed_ts = pd.DataFrame({"day": confirmed_avg.day.unique()})
        for strategy in confirmed_avg.strategy.unique():
            sub_df = confirmed_avg.query(f'strategy == "{strategy}"')
            confirmed_ts = confirmed_ts.set_index("day").join(other=(
                sub_df[["day", "infected_cases"]]
                .rename(columns={"infected_cases": strategy})
                .set_index("day")
            )).reset_index()
        # Create incremental time-series
        incremental_values = {"day": confirmed_ts.day.values}
        for col in ["distancing", "interacting"]:
            values = confirmed_ts[col].values
            incremental_values[col] = [0] + list(values[1:] - values[:-1])
        incremental_ts = pd.DataFrame(incremental_values)
        # Add average to incremental time-series
        incremental_ts = incremental_ts.assign(group=round(incremental_ts.day / avg_days))
        incremental_ts = incremental_ts.groupby("group")[["interacting", "distancing"]].mean().rename(columns={
            "interacting": "avg-interacting",
            "distancing": "avg-distancing"
        }).join(incremental_ts.set_index("group"), how="right").reset_index(drop=True)
        # Plot results!
        fig = plt.figure(figsize=(10, 6))
        plt.suptitle("Confirmed Cases: Normal Social Interactions VS Social Distancing")
        ax_upper = plt.subplot(211)
        confirmed_ts.plot(x="day", ax=ax_upper)
        plt.ylabel("Total Confirmed Cases")
        plt.grid()
        ax_lower = plt.subplot(212)
        incremental_ts.plot(x="day", y="avg-interacting", color="orange", ax=ax_lower, label="avg-interacting")
        incremental_ts.plot(x="day", y="avg-distancing", color="blue", ax=ax_lower, label="avg-distancing")
        incremental_ts.plot.scatter(x="day", y="interacting", color="orange",
                                    alpha=0.3, label="interacting", ax=ax_lower)
        incremental_ts.plot.scatter(x="day", y="distancing", color="blue",
                                    alpha=0.3, label="distancing", ax=ax_lower)
        plt.ylabel("New Confirmed Cases")
        plt.grid()
        if show:
            plt.show()
        if save.endswith(".png"):
            fig.savefig(save)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    fire.Fire(Main)
