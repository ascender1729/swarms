"""Small demo of autosave and CLI registry usage."""

import os
import subprocess
from swarms.structs.agent import Agent
from swarms.structs.agent_registry import AgentRegistry


def main():
    workspace = "agent_workspace_example"
    os.makedirs(workspace, exist_ok=True)

    # Create two agents that autosave to the workspace
    Agent(
        llm=object(),
        agent_name="agent_one",
        autosave=True,
        workspace_dir=workspace,
    )
    Agent(
        llm=object(),
        agent_name="agent_two",
        autosave=True,
        workspace_dir=workspace,
    )

    # Load agents from the workspace
    registry = AgentRegistry()
    registry.load_from_workspace(workspace)
    print("Loaded agents:", registry.list_agents())

    # List agents via CLI
    result = subprocess.run(
        ["python", "-m", "swarms.cli.main", "list-agents", "--workspace", workspace],
        capture_output=True,
        text=True,
    )
    print("CLI output:\n" + result.stdout)


if __name__ == "__main__":
    main()
