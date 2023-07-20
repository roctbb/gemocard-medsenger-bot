from abc import ABC, abstractmethod

import numpy as np


class Filter(ABC):

    @abstractmethod
    def filter(self, data: np.ndarray) -> np.ndarray: pass
