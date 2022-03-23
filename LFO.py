import numpy as np
from scipy import signal

class LFO:
    __sample_rate = 44100

    def amp_sine_lfo(self, wave, rate=1, intensity=0.5, offset=0.5, duration=1):
        t = np.linspace(0, duration, int(self.__sample_rate * duration))
        lfo_wave = intensity * np.sin(2 * np.pi * rate * t) + offset
        lfo_wave[lfo_wave<0] = 0
        if len(lfo_wave) < len(wave):
            lfo_wave = np.append(lfo_wave, np.zeros(len(wave)-len(lfo_wave)))
        elif len(lfo_wave) > len(wave):
            lfo_wave = lfo_wave[:len(wave)-len(lfo_wave)]

        lfo_wave *=  wave
        return lfo_wave

    def amp_square_lfo(self, wave, rate=1, intensity=0.5, offset=0.5, duration=1):
        t = np.linspace(0, duration, int(self.__sample_rate * duration))
        lfo_wave = intensity * signal.square(2 * np.pi * rate * t) + offset
        lfo_wave[lfo_wave<0] = 0
        for x in range(1, len(lfo_wave)):
            if lfo_wave[x-1]!=1 and lfo_wave[x]!=0:
                lfo_wave[x] = min(1,lfo_wave[x-1] + 0.005)
            elif lfo_wave[x-1]!=0 and lfo_wave[x]!=1:
                lfo_wave[x] = max(0,lfo_wave[x-1] - 0.005)

        if len(lfo_wave) < len(wave):
            lfo_wave = np.append(lfo_wave, np.zeros(len(wave)-len(lfo_wave)))
        elif len(lfo_wave) > len(wave):
            lfo_wave = lfo_wave[:len(wave)-len(lfo_wave)]

        lfo_wave *=  wave
        return lfo_wave

    def amp_sawtooth_lfo(self, wave, rate=1, intensity=0.5, offset=0.5, duration=1):
        t = np.linspace(0, duration, int(self.__sample_rate * duration))
        lfo_wave = intensity * signal.sawtooth(2 * np.pi * rate * t, width=0.98) + offset
        lfo_wave[lfo_wave<0] = 0

        if len(lfo_wave) < len(wave):
            lfo_wave = np.append(lfo_wave, np.zeros(len(wave)-len(lfo_wave)))
        elif len(lfo_wave) > len(wave):
            lfo_wave = lfo_wave[:len(wave)-len(lfo_wave)]

        lfo_wave *=  wave
        return lfo_wave
