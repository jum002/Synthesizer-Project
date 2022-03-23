import numpy as np

class Filter:
    __sample_rate = 44100

    def lowpass_filter(self, wave, cf, k=0, duration=1):
        wavef = np.fft.rfft(wave)
        N = self.__sample_rate//2
        lpf = np.ones(int(cf*duration))
        if k == 0:
            lpf = np.append(lpf, np.zeros(int((N-cf)*duration)+1))
        else:
            lpf = np.append(lpf, np.linspace(1, 0, k*3))
            lpf = np.append(lpf, np.zeros(max(0, int((N-k-cf)*duration)+1)))

        if len(lpf) < len(wavef):
            lpf = np.append(lpf, np.zeros(len(wavef)-len(lpf)))
        elif len(lpf) > len(wavef):
            lpf = lpf[:len(wavef)-len(lpf)]

        wavef *= lpf
        return np.fft.irfft(wavef)


    def highpass_filter(self, wave, cf, k=0, duration=1):
        wavef = np.fft.rfft(wave)
        N = self.__sample_rate//2
        lpf = np.ones(int((N-cf)*duration)+1)
        if k == 0:
            lpf = np.append(np.zeros(int(cf*duration)), lpf)
        else:
            lpf = np.append(np.linspace(0, 1, k*3), lpf)
            lpf = np.append(np.zeros(max(0, int((N-k-cf)*duration)+1)), lpf)

        if len(lpf) < len(wavef):
            lpf = np.append(lpf, np.zeros(len(wavef)-len(lpf)))
        elif len(lpf) > len(wavef):
            lpf = lpf[:len(wavef)-len(lpf)]

        wavef *= lpf
        return np.fft.irfft(wavef)
