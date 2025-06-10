import subprocess
import importlib.util
import pathlib

spec = importlib.util.spec_from_file_location("agent_module", pathlib.Path(__file__).resolve().parents[2] / "swarms/structs/agent.py")
agent_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agent_module)
Agent = agent_module.Agent


def test_cli_list_agents(tmp_path):
    workspace = tmp_path / "ws"
    workspace.mkdir()
    Agent(
        llm=object(),
        agent_name="cli_agent",
        autosave=True,
        workspace_dir=str(workspace),
    )
    result = subprocess.run(
        ["python", "-m", "swarms.cli.main", "list-agents", "--workspace", str(workspace)],
        capture_output=True,
        text=True,
    )
    assert "cli_agent" in result.stdout

