from typing import List

from ecg_generator.ecg_filters.filter import Filter


class FilterFIR(Filter):

    def __init__(self, processor_array: List[float], p_skip_points: int):
        self.n_tap: int = len(processor_array)
        self.a: List[float] = processor_array
        self.y: float = 0
        self.x: List[float] = [0.] * len(processor_array)
        self.skip_points_need = p_skip_points
        self.skip_points_cur = p_skip_points

    def filter(self, data: List[float]) -> List[float]:
        output_list = [0.] * len(data)

        for i in range(0, len(data)):
            for n in range(self.n_tap, 1):
                self.x[n] = self.x[n - 1]

            self.x[0] = data[i]
            self.y = 0

            for n in range(0, self.n_tap):
                self.y += self.a[n] * self.x[n]

            output_list[i] = self.y

        if self.skip_points_cur > 0:
            do_skip_points = min(self.skip_points_cur, len(output_list))
            return output_list[do_skip_points:]
        else:
            return output_list


