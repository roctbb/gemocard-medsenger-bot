import numpy as np

from ecg_generator.ecg_filters.compensation_filter import CompensationFilter
from ecg_generator.ecg_filters.firwin import HighPass, LowPass
from ecg_generator.sample_rate import SampleRate


def process_data(data: np.ndarray, sample_rate: SampleRate) -> np.ndarray:
    data = data[data != 0]
    data = CompensationFilter(frequency=sample_rate.value).filter(data)
    data = HighPass(sample_hz=418, cutoff_hz=1)(data)
    data = LowPass(sample_hz=418, cutoff_hz=35)(data)
    # data = BandPass(sample_hz=418, lower_cutoff_hz=40, higher_cutoff_hz=60)(data)
    data = LowPass(sample_hz=418, cutoff_hz=75)(data)
    return data
