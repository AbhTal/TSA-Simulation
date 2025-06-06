import simpy
import random
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Simulation parameters
SIM_TIME = 3600*3  # 1 hour in seconds, 3600 sec = 1 hr
ARRIVAL_RATE = 5  # ex: Passengers arrive every ~5 seconds
NUM_TSA_AGENTS = 3
PRECHECK_PROBABILITY = 0.3  # ex: 30% TSA PreCheck passengers
SECONDARY_SCREEN_PROB = 0.1 # ex: 10% of passengers require secondary screening

# Data collection
passenger_data = []
total_wait_time = 0  # Track total wait time
total_passengers = 0  # Track total passengers

class Passenger:
    def __init__(self, env, id, queue_system):
        self.env = env
        self.id = id
        self.arrival_time = env.now
        self.is_precheck = random.random() < PRECHECK_PROBABILITY
        self.needs_secondary = random.random() < SECONDARY_SCREEN_PROB
        env.process(queue_system.join_queue(self))


class TSAAgent:
    def __init__(self, env, id, checkpoint):
        self.env = env
        self.id = id
        self.checkpoint = checkpoint
        self.is_busy = False

    def process_passenger(self, passenger):
        global total_wait_time, total_passengers
        self.is_busy = True
        start_time = self.env.now
        screening_time = random.uniform(5, 15) if passenger.is_precheck else random.uniform(10, 25)
        yield self.env.timeout(screening_time)

        if passenger.needs_secondary:
            yield self.env.timeout(random.uniform(5, 15))  # Secondary screening delay

        end_time = self.env.now
        wait_time = start_time - passenger.arrival_time

        # Update total wait time and count passengers
        total_wait_time += wait_time
        total_passengers += 1

        passenger_data.append(
            [passenger.id, passenger.arrival_time, start_time, end_time, wait_time, passenger.is_precheck,
             passenger.needs_secondary])

        self.is_busy = False


class Checkpoint:
    def __init__(self, env, id):
        self.env = env
        self.id = id
        self.tsa_agents = [TSAAgent(env, i, self) for i in range(NUM_TSA_AGENTS)]
        self.queue = []

    def process_queue(self):
        while True:
            yield self.env.timeout(1)
            if self.queue and any(not agent.is_busy for agent in self.tsa_agents):
                passenger = self.queue.pop(0)
                available_agent = next(agent for agent in self.tsa_agents if not agent.is_busy)
                self.env.process(available_agent.process_passenger(passenger))


class QueueSystem:
    def __init__(self, env, checkpoint):
        self.env = env
        self.checkpoint = checkpoint
        self.regular_queue = []
        self.precheck_queue = []

    def join_queue(self, passenger):
        if passenger.is_precheck:
            self.precheck_queue.append(passenger)
        else:
            self.regular_queue.append(passenger)
        yield self.env.timeout(0)  # Simulate instant queue join

    def assign_to_checkpoint(self):
        while True:
            yield self.env.timeout(1)
            if self.precheck_queue:
                self.checkpoint.queue.append(self.precheck_queue.pop(0))
            elif self.regular_queue:
                self.checkpoint.queue.append(self.regular_queue.pop(0))


class Simulation:
    def __init__(self):
        self.env = simpy.Environment()
        self.checkpoint = Checkpoint(self.env, 1)
        self.queue_system = QueueSystem(self.env, self.checkpoint)

    def passenger_generator(self):
        passenger_id = 0
        while True:
            yield self.env.timeout(random.expovariate(1.0 / ARRIVAL_RATE))
            passenger_id += 1
            Passenger(self.env, passenger_id, self.queue_system)

    def run(self):
        self.env.process(self.passenger_generator())
        self.env.process(self.queue_system.assign_to_checkpoint())
        self.env.process(self.checkpoint.process_queue())
        self.env.run(until=SIM_TIME)

        # Save data to CSV
        now = datetime.now()
        timestamp = now.strftime("%H-%M-%S")
        df = pd.DataFrame(passenger_data,
                          columns=["ID", "Arrival Time", "Screening Start", "Exit Time", "Wait Time", "PreCheck",
                                   "Secondary Screening"])
        df.to_csv(f"simulation_results{timestamp}.csv", index=False)
        print("Simulation data saved to simulation_results.csv")

        # Compute and print the average wait time
        avg_wait_time = 0
        if total_passengers > 0:
            avg_wait_time = total_wait_time / total_passengers
        print(f"\nAverage Wait Time for All Passengers: {avg_wait_time:.2f} seconds")
        print(f"Average Wait Time for All Passengers: {avg_wait_time/60} minutes")

        # Call the visualization function
        self.visualize_data(df)

    def visualize_data(self, df):
        fig, ax = plt.subplots(2, 1, figsize=(10, 8))

        # Plot wait times
        ax[0].hist(df["Wait Time"], bins=20, color="skyblue", edgecolor="black")
        ax[0].set_title("Passenger Wait Times")
        ax[0].set_xlabel("Time (seconds)")
        ax[0].set_ylabel("Number of Passengers")

        # PreCheck vs. Regular Comparison
        precheck_wait = df[df["PreCheck"] == True]["Wait Time"]
        regular_wait = df[df["PreCheck"] == False]["Wait Time"]

        ax[1].boxplot([regular_wait, precheck_wait], labels=["Regular", "PreCheck"])
        ax[1].set_title("Comparison of Wait Times: Regular vs. PreCheck")

        plt.tight_layout()
        plt.show()


# Run the simulation
if __name__ == "__main__":
    simulation = Simulation()
    simulation.run()
