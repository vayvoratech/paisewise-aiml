from dataclasses import dataclass


@dataclass
class BenchmarkPerformance:
    """
    Represents performance information for a benchmark.
    """

    name: str
    return_percentage: float