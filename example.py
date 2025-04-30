from swarms.structs.agent import Agent
from swarms.structs.swarm_router import SwarmRouter
from swarms.agents.create_agents_from_yaml import (
    create_agents_from_yaml,
)
from swarms.utils.litellm_wrapper import LiteLLM

# Initialize the model
model = LiteLLM(model_name="claude-3-opus-20240229")

# Create agents and return them as a list
agents = create_agents_from_yaml(model=model, yaml_file="agents_config.yaml", return_type="agents")
print(agents)