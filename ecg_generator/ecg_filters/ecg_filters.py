from functools import reduce
from typing import List

from ecg_generator.ecg_filters.filter import Filter
from ecg_generator.ecg_filters.filter_factory import FilterFactory
from ecg_generator.ecg_filters.filter_factory_1000 import FilterFactory1000
from ecg_generator.ecg_filters.filter_factory_418 import FilterFactory418
from ecg_generator.ecg_filters.filter_factory_500 import FilterFactory500
from ecg_generator.sample_rate import SampleRate


def get_filter_factory(sample_rate: SampleRate) -> FilterFactory:
    if sample_rate == SampleRate.HZ_417_5:
        return FilterFactory418()
    elif sample_rate == SampleRate.HZ_500:
        return FilterFactory500()
    elif sample_rate == SampleRate.HZ_1000:
        return FilterFactory1000()
    else:
        raise ValueError("sample_rate must be one of SampleRate types.")


def get_filter_composition(filter_factory: FilterFactory) -> List[Filter]:
    return [
        filter_factory.get_comp_filter(),
        filter_factory.get_fir_hp_1hz(),
        filter_factory.get_fir_lp_35hz(),
        filter_factory.get_fir_bs_50hz(),
        filter_factory.get_fir_lp_75hz(),
    ]


def apply_filter(data: List[float], f: Filter) -> List[float]:
    return f.filter(data)


def process_data(data: List[int], sample_rate: SampleRate) -> List[float]:
    filters = get_filter_composition(
        get_filter_factory(sample_rate)
    )
    data = filter(lambda a: a != 0, data)
    data = list(map(lambda a: float(a) * 0.000745, data))
    return reduce(apply_filter, filters, data)
