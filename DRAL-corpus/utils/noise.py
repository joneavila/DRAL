import math

import numpy as np
from scipy.io import wavfile


def add_noise(audio_path: str) -> None:
    # [!] This function assumes the audio at `audio_path` is WAV 16-bit.
    # Code for adding noise is adapted from
    # https://github.com/sleekEagle/audio_processing Code for mapping numpy.float32 to
    # numpy.int16 is adapted from https://stackoverflow.com/a/70595072

    desired_SNR = 20  # Signal-to-noise ratio
    sample_rate, signal = wavfile.read(audio_path)

    # `signal` is numpy.int16 and becomes numpy.float32 after interpolation.
    signal_interp = np.interp(signal, (signal.min(), signal.max()), (-1, 1))

    RMS_signal_interp = math.sqrt(np.mean(signal_interp**2))  # Root mean square
    RMS_noise = math.sqrt(RMS_signal_interp**2 / (pow(10, desired_SNR / 10)))
    STD_noise = RMS_noise  # Standard deviation
    noise = np.random.normal(0, STD_noise, signal_interp.shape[0])
    signal_interp_plus_noise = signal_interp + noise

    # The bits per sample of the output WAV depends on the data type of the Numpy array.
    # Map from numpy.float32 (WAV 32-bit) back to numpy.int16 (WAV 16-bit).
    max_16bit = 2**15
    signal_interp_plus_noise_mapped = signal_interp_plus_noise * max_16bit
    signal_interp_plus_noise_16bit = signal_interp_plus_noise_mapped.astype(np.int16)

    # Overwrite the audio at `audio_path`.
    wavfile.write(audio_path, sample_rate, signal_interp_plus_noise_16bit)
