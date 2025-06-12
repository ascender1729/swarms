# Deep Research News Aggregator

This example demonstrates how to use the **DeepResearchSwarm** to gather and summarize recent news. The swarm automatically generates search queries, collects information in parallel, and returns a concise summary.

## Installation

```bash
pip install swarms
```

## Code

```python
from swarms.structs.deep_research_swarm import DeepResearchSwarm

swarm = DeepResearchSwarm(
    name="News Research Swarm",
    description="Aggregates and summarizes recent technology and finance news",
    output_type="string",
)

result = swarm.run(
    "Provide a concise summary of today's most important technology and finance news."
)

print(result)
```

Running the script will print a short digest of the latest technology and finance headlines.
