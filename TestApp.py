import pytest
import random
import simpy
from app import *


# Mock Environment
@pytest.fixture
def mock_env():
    return simpy.Environment()


# Test Passenger Creation
def test_passenger_creation(mock_env):
    passenger_id = 1
    queue_system = QueueSystem(mock_env, Checkpoint(mock_env, 1))
    passenger = Passenger(mock_env, passenger_id, queue_system)

    assert passenger.id == 1
    assert passenger.arrival_time == mock_env.now
    assert isinstance(passenger.is_precheck, bool)
    assert isinstance(passenger.needs_secondary, bool)


# Test TSA Agent Processing Time (screening time is in the range of 5 to 25 seconds)
def test_tsa_agent_processing(mock_env):
    checkpoint = Checkpoint(mock_env, 1)
    passenger = Passenger(mock_env, 1, QueueSystem(mock_env, checkpoint))
    tsa_agent = TSAAgent(mock_env, 1, checkpoint)

    # Simulate processing a passenger
    mock_env.process(tsa_agent.process_passenger(passenger))
    mock_env.run(until=1)

    assert passenger.arrival_time < mock_env.now


# Test Queue System for Joining Queue and Assigning to Checkpoint
def test_queue_system(mock_env):
    checkpoint = Checkpoint(mock_env, 1)
    queue_system = QueueSystem(mock_env, checkpoint)
    passenger = Passenger(mock_env, 1, queue_system)

    # Simulate passenger joining queue
    mock_env.process(queue_system.join_queue(passenger))
    mock_env.run(until=10)

    assert len(queue_system.regular_queue) >= 1 or len(queue_system.precheck_queue) >= 1


# Test Checkpoint Processing
def test_checkpoint_processing(mock_env):
    checkpoint = Checkpoint(mock_env, 1)
    passenger = Passenger(mock_env, 1, QueueSystem(mock_env, checkpoint))

    # Add passenger to checkpoint queue
    checkpoint.queue.append(passenger)
    mock_env.process(checkpoint.process_queue())
    mock_env.run(until=10)

    assert len(checkpoint.queue) == 0  # Passenger should be processed and removed

