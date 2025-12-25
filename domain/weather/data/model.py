from dataclasses import dataclass


@dataclass(frozen=True)
class Weather:
    @dataclass(frozen=True)
    class Condition:
        condition: str
        description: str

    city: str
    conditions: list[Condition]
