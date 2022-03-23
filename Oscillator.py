from scipy import signal
import numpy as np

class Oscillator:
    __sample_rate = 44100
    __damping_t = 0.01

    def get_sine_wave(self, freq, duration=5, amplitude=1):
        # Basic Sine Wave
        t = np.linspace(0, duration, int(self.__sample_rate * duration))
        damp = np.linspace(1, 0, int(self.__sample_rate * self.__damping_t))
        damp = np.append(np.ones(len(t)-len(damp)), damp)
        return amplitude * damp * np.sin(2 * np.pi * freq * t)

    def get_square_wave(self, freq, duration=5, amplitude=1):
        t = np.linspace(0, duration, int(self.__sample_rate * duration))
        damp = np.linspace(1, 0, int(self.__sample_rate * self.__damping_t))
        damp = np.append(np.ones(len(t)-len(damp)), damp)
        return amplitude * damp * signal.square(2 * np.pi * freq * t)

    """
    For triangular wave, lean = 0.5
    """
    def get_sawtooth_wave(self, freq, lean=1, duration=5, amplitude=1):
        t = np.linspace(0, duration, int(self.__sample_rate * duration))
        damp = np.linspace(1, 0, int(self.__sample_rate * self.__damping_t))
        damp = np.append(np.ones(len(t)-len(damp)), damp)
        return amplitude * damp * signal.sawtooth(2 * np.pi * freq * t, lean)
