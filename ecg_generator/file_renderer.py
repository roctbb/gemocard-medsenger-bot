import io
import json
from typing import List

import matplotlib.pyplot as plt
import numpy as np

from ecg_generator.ecg_filters.ecg_filters import process_data
from ecg_generator.sample_rate import SampleRate

SECONDS_IN_ROW = 5


def render_png(ecg_data: List[int], sample_rate: SampleRate) -> io.BytesIO:
    """Generates PDF file from RAW UBytes got from Acsma Android application."""

    ecg_data = np.array(ecg_data)

    filtered_ecg_data = process_data(ecg_data, sample_rate)

    ecg_seconds_duration = ecg_data.size / sample_rate.value
    rows = (ecg_seconds_duration // SECONDS_IN_ROW) + 1

    split_ecg_data = np.array_split(filtered_ecg_data, rows)

    fig, axes = plt.subplots(len(split_ecg_data), 1, gridspec_kw={'hspace': 0.1}, figsize=(16.6, 23.4))

    for i, (ax, ecg_row) in enumerate(zip(axes, split_ecg_data)):
        plt.setp(ax.spines.values(), color='none')
        # ax.set_xticklabels([])
        ax.set_yticklabels([])
        # ax.xaxis.set_ticks_position('none')
        ax.yaxis.set_ticks_position('none')
        ax.set_ylim(np.min(filtered_ecg_data), np.max(filtered_ecg_data))
        ax.set_xlim(SECONDS_IN_ROW * i, SECONDS_IN_ROW * (i + 1))
        ax.grid(which='both', linewidth='0.5', color=(1, 0.7, 0.7))
        ax.minorticks_on()
        ax.plot(np.linspace(SECONDS_IN_ROW * i, SECONDS_IN_ROW * (i + 1), len(ecg_row)), ecg_row)

    file_buffer = io.BytesIO()
    fig.savefig(file_buffer, bbox_inches='tight')
    return file_buffer


if __name__ == "__main__":
    with open("/Users/tikhon/Downloads/acsma_ecg_data.txt", "r") as f:
        test_data = json.load(f)

    buffer = render_png(test_data, SampleRate.HZ_417_5)

    with open("example.png", "wb") as f:
        f.write(buffer.getbuffer())
