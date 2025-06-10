import importlib.util
import pathlib

spec = importlib.util.spec_from_file_location("agent_module", pathlib.Path(__file__).resolve().parents[2] / "swarms/structs/agent.py")
agent_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agent_module)
Agent = agent_module.Agent


def test_agent_autosave_files(tmp_path):
    workspace = tmp_path / "ws"
    workspace.mkdir()
    Agent(
        llm=object(),
        agent_name="auto_save_agent",
        autosave=True,
        workspace_dir=str(workspace),
    )
    assert (workspace / "auto_save_agent.json").exists()
    assert (workspace / "auto_save_agent.yaml").exists()

