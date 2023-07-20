from enum import Enum, unique


@unique
class SampleRate(Enum):
    """Sample rate configuration. Can be 417.5 Hz, 500 Hz or 1000 Hz."""

    HZ_417_5 = 418
    HZ_500 = 500
    HZ_1000 = 100
