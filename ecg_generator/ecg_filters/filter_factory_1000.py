from ecg_generator.ecg_filters.compensation_filter import CompensationFilter
from ecg_generator.ecg_filters.filter import Filter
from ecg_generator.ecg_filters.filter_factory import FilterFactory
from ecg_generator.ecg_filters.filter_fir import FilterFIR

aHP1000_1_4 = [
    -0.00140633657001946280,
    -0.00140582669222180680,
    -0.00140508079883122470,
    -0.00140410013240467630,
    -0.00140288598099394490,
    -0.00140143967768570980,
    -0.00139976260012988020,
    -0.00139785617005927570,
    -0.00139572185279610910,
    -0.00139336115675224930,
    -0.00139077563291506190,
    -0.00138796687432706000,
    -0.00138493651555294130,
    -0.00138168623213930650,
    -0.00137821774006345710,
    0.99721703848857624000,
    -0.00137821774006345710,
    -0.00138168623213930650,
    -0.00138493651555294130,
    -0.00138796687432706000,
    -0.00139077563291506190,
    -0.00139336115675224930,
    -0.00139572185279610910,
    -0.00139785617005927570,
    -0.00139976260012988020,
    -0.00140143967768570980,
    -0.00140288598099394490,
    -0.00140410013240467630,
    -0.00140508079883122470,
    -0.00140582669222180680,
    -0.00140633657001946280
]

aLP1000_35_6 = [
    -0.00693795260670703510,
    -0.00430704857669077840,
    -0.00076179198177989886,
    0.00370829061430188920,
    0.00907126464082595380,
    0.01524758250201370600,
    0.02210660933556801700,
    0.02946544715037241800,
    0.03709064354790201500,
    0.04470337404600043700,
    0.05198867277898915800,
    0.05860925434711685600,
    0.06422441976360773700,
    0.06851447239960113700,
    0.07121098682342794100,
    0.07213155043090087300,
    0.07121098682342794100,
    0.06851447239960113700,
    0.06422441976360773700,
    0.05860925434711685600,
    0.05198867277898915800,
    0.04470337404600043700,
    0.03709064354790201500,
    0.02946544715037241800,
    0.02210660933556801700,
    0.01524758250201370600,
    0.00907126464082595380,
    0.00370829061430188920,
    -0.00076179198177989886,
    -0.00430704857669077840,
    -0.00693795260670703510
]

aBS1000_50_4 = [
    0.00045686932087077759,
    0.00164050974382591220,
    0.00267075613793261870,
    0.00344387107028180750,
    0.00388103010869519150,
    0.00393639902217032820,
    0.00360195008657659880,
    0.00290851021319304000,
    0.00192291158230765130,
    0.00074150884001486408,
    -0.00051930423620845975,
    -0.00173463903526012260,
    -0.00278356483685599950,
    -0.00356122025726952590,
    -0.00398936274231273710,
    0.97476754996407611000,
    -0.00398936274231273710,
    -0.00356122025726952590,
    -0.00278356483685599950,
    -0.00173463903526012260,
    -0.00051930423620845975,
    0.00074150884001486408,
    0.00192291158230765130,
    0.00290851021319304000,
    0.00360195008657659880,
    0.00393639902217032820,
    0.00388103010869519150,
    0.00344387107028180750,
    0.00267075613793261870,
    0.00164050974382591220,
    0.00045686932087077759
]

aLP1000_75_6 = [
    0.00856611870868564770,
    0.00738396455248927810,
    0.00364949524963763390,
    -0.00255881493898905050,
    -0.01043174833291989200,
    -0.01834352854938115300,
    -0.02393803110140349200,
    -0.02443003490483617100,
    -0.01712791284123387600,
    -0.00013156688922300847,
    0.02690425872660611900,
    0.06211789133382675900,
    0.10113611233719724000,
    0.13739504775863648000,
    0.16337922083475262000,
    0.17285905611230984000,
    0.16337922083475262000,
    0.13739504775863648000,
    0.10113611233719724000,
    0.06211789133382675900,
    0.02690425872660611900,
    -0.00013156688922300847,
    -0.01712791284123387600,
    -0.02443003490483617100,
    -0.02393803110140349200,
    -0.01834352854938115300,
    -0.01043174833291989200,
    -0.00255881493898905050,
    0.00364949524963763390,
    0.00738396455248927810,
    0.00856611870868564770
]


class FilterFactory1000(FilterFactory):
    def get_comp_filter(self) -> Filter:
        return CompensationFilter(frequency=1000)

    def get_fir_hp_1hz(self) -> Filter:
        return FilterFIR(processor_array=aHP1000_1_4, p_skip_points=50)

    def get_fir_lp_35hz(self) -> Filter:
        return FilterFIR(processor_array=aLP1000_35_6, p_skip_points=50)

    def get_fir_bs_50hz(self) -> Filter:
        return FilterFIR(processor_array=aBS1000_50_4, p_skip_points=50)

    def get_fir_lp_75hz(self) -> Filter:
        return FilterFIR(processor_array=aLP1000_75_6, p_skip_points=50)
