import numpy as np

class Envelop:
    __sample_rate = 44100

    def amp_envelop(self, wave, attack, decay, sustain, release, sustain_level=0.5, exp=1, duration=1):
        N = int(self.__sample_rate * duration)
        S = attack + decay + sustain + release
        if S == 0:
            return np.zeros(len(wave))

        attack = int(N * attack / S)
        decay = int(N * decay / S)
        sustain = int(N * sustain / S)
        release = int(N * release / S)
        evl = np.linspace(0, 1, attack)
        exp_decay = np.linspace(1, sustain_level ** (-1.0/exp), decay)
        exp_decay = np.array([x ** (-exp) for x in exp_decay])
        evl = np.append(evl, exp_decay)
        evl = np.append(evl, sustain_level * np.ones(sustain))
        evl = np.append(evl, np.linspace(sustain_level, 0, release))
        if len(evl) < len(wave):
            evl = np.append(evl, np.zeros(len(wave)-len(evl)))
        elif len(evl) > len(wave):
            evl = evl[:len(wave)-len(evl)]

        return evl * wave
