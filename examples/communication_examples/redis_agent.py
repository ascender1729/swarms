"""Persist agent dialogue using :class:`RedisConversation`.

This example wires an :class:`~swarms.Agent` to a Redis-backed conversation
store so that messages are saved between runs. An embedded Redis server will
start automatically when ``use_embedded_redis=True`` is specified.

Steps to run this example:
    1. From the repository root, install the package in editable mode::

           pip install -e .

    2. Execute this script directly::

           python examples/communication_examples/redis_agent.py

The script prints the agent's reply and then dumps the stored conversation
history retrieved from Redis.
"""

from swarms import Agent
from swarms.communication.redis_wrap import RedisConversation

# Configure an embedded Redis-backed conversation store
memory = RedisConversation(
    use_embedded_redis=True,
    redis_port=6380,  # adjust if needed
    token_count=False,
    cache_enabled=False,
    auto_persist=True,
    name="assistant_convo",
)

# Create an agent that persists its messages in Redis
agent = Agent(
    agent_name="RedisAssistant",
    system_prompt="You are quick and helpful.",
    model_name="gpt-4o-mini",
    long_term_memory=memory,
    max_loops=1,
    autosave=True,
)

response = agent.run("Do you remember my name?")
print(response)

# Display the stored conversation from Redis
print(memory.to_dict())

# The dictionary includes all messages exchanged in this session. Re-running the
# script will append to this same conversation, demonstrating persistence.
