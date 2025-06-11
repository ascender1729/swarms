import os
import sys
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import importlib.util

root = Path(__file__).resolve().parents[2]

spec_agent = importlib.util.spec_from_file_location("agent", root / "swarms/structs/agent.py")
agent_module = importlib.util.module_from_spec(spec_agent)
spec_agent.loader.exec_module(agent_module)
Agent = agent_module.Agent

spec_reg = importlib.util.spec_from_file_location("agent_registry", root / "swarms/structs/agent_registry.py")
reg_module = importlib.util.module_from_spec(spec_reg)
spec_reg.loader.exec_module(reg_module)
AgentRegistry = reg_module.AgentRegistry


def test_autosave_creates_file_and_registry_lists(tmp_path, monkeypatch):
    monkeypatch.setenv("WORKSPACE_DIR", str(tmp_path))
    dummy_llm = MagicMock()
    dummy_llm.run.return_value = "ok"

    agent = Agent(agent_name="auto_test", llm=dummy_llm, max_loops=1, autosave=True)
    agent.run("hello")

    expected = tmp_path / "agents" / "auto_test.json"
    assert expected.exists(), "Agent state file not created"

    registry = AgentRegistry()
    names = registry.list_agents()
    assert "auto_test" in names
