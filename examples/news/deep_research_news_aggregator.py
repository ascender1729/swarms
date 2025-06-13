from swarms.structs.deep_research_swarm import DeepResearchSwarm


def main() -> None:
    """Gather and summarize current technology and finance news."""
    swarm = DeepResearchSwarm(
        name="News Research Swarm",
        description="Aggregates and summarizes recent technology and finance news",
        output_type="string",
    )

    query = (
        "Provide a concise summary of today's most important technology and finance news."
    )

    result = swarm.run(query)

    print("\nNews Summary:\n")
    print(result)


if __name__ == "__main__":
    main()
