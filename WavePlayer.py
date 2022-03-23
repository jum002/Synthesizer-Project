import sounddevice as sd
import pygame
import time
import matplotlib.pyplot as plt
import numpy as np

"""
Play piano note or notes from input notes
"""
class WavePlayer:

    __sample_rate = 44100
    __attenuation = 0.3

    def __init__(self):
        pygame.mixer.pre_init(self.__sample_rate, size=-16, channels=1)
        pygame.mixer.init()
        pygame.mixer.set_num_channels(4)

    """
    Play wave (not note). To play note: play_wave(get_wave(note))
    """
    def play_wave_sd(self, wave):
        sd.play(wave, self.__sample_rate)

    def play_wave_pg(self, wave):
        wave = np.array(wave)
        wave = np.repeat(wave.reshape(len(wave), 1), 2, axis = 1)
        wave = (wave*30000).astype(np.int16)
        #wave1 = np.array(wave1, dtype="int8")
        sound = pygame.sndarray.make_sound(wave)
        sound.play()


    """
    Plot wave for testing and designing purposes
    """
    def plot_wave(self, wave, duration=1):
        t = np.linspace(0, duration, int(self.__sample_rate * duration))
        plt.xlabel('time')
        plt.ylabel('amp')
        plt.title('Wave Plot')
        plt.plot(t, wave)
        plt.show()
