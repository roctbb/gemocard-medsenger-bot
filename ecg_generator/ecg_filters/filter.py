from abc import ABC, abstractmethod
from typing import List


class Filter(ABC):

    @abstractmethod
    def filter(self, data: List[float]) -> List[float]: pass
