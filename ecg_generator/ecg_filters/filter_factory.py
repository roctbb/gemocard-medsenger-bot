from abc import ABC, abstractmethod

from ecg_generator.ecg_filters.filter import Filter


class FilterFactory(ABC):

    @abstractmethod
    def get_comp_filter(self) -> Filter: pass

    @abstractmethod
    def get_fir_hp_1hz(self) -> Filter: pass

    @abstractmethod
    def get_fir_lp_35hz(self) -> Filter: pass

    @abstractmethod
    def get_fir_bs_50hz(self) -> Filter: pass

    @abstractmethod
    def get_fir_lp_75hz(self) -> Filter: pass
