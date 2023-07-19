from typing import List

from ecg_generator.ecg_filters.filter import Filter


class CompensationFilter(Filter):
    TIME_FILTER = 2  # 2 sec
    RESET_MV = 25  # 5

    offset = 0

    def __init__(self, frequency: float):
        self.frequency = frequency

    def filter(self, data: List[float]) -> List[float]:
        output_list = [0.] * len(data)
        self.offset = data[0]

        for i in range(0, len(data)):
            if (abs(data[i]) - self.offset) > self.RESET_MV:
                self.offset = data[i]
            else:
                self.offset = self.offset - ((self.offset - data[i]) / (self.TIME_FILTER * self.frequency))
            output_list[i] = data[i] - self.offset

        return output_list


