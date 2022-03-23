import matplotlib.pyplot as plt
import numpy as np
import pygame
import time
import sounddevice as sd
from scipy import signal
from scipy.fftpack import fft, ifft
import scipy.fft
import math

sample_rate = 44100

def get_sine_wave(freq, duration=1, amplitude=1):
    # Basic Sine Wave
    t = np.linspace(0, duration, int(sample_rate * duration))
    damp = np.linspace(1, 0, int(sample_rate * 0.01))
    damp = np.append(np.ones(int(sample_rate * (duration-0.01))), damp)
    return amplitude * damp * np.sin(2 * np.pi * freq * t)

def get_square_wave(freq, duration=1, amplitude=1):
    t = np.linspace(0, duration, int(sample_rate * duration))
    return amplitude * signal.square(2 * np.pi * freq * t)

"""
For triangular wave, lean = 0.5
"""
def get_sawtooth_wave(freq, lean=1, duration=1, amplitude=1):
    t = np.linspace(0, duration, int(sample_rate * duration))
    return amplitude * signal.sawtooth(2 * np.pi * freq * t, lean)

def get_sinc(c, duration=1, amplitude=1):
    t = np.linspace(0, duration, int(sample_rate * duration))
    y = np.sin(c * t) / (np.pi * c * t)
    y[0] = 1/np.pi
    return y


def plot_wave(wave, title='Wave Plot', duration=1, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration))
    plt.xlabel('time')
    plt.ylabel('amp')
    plt.title(title)
    plt.plot(t, wave)

def plot_spectrum(wavef, title='Freq Spec Plot', sample_rate=44100):
    w = np.linspace(0, sample_rate//2, sample_rate)
    plt.xlabel('freq')
    plt.ylabel('amp')
    plt.title(title)
    plt.plot(w, abs(wavef))

def lowpass_filter(wave, cf, k=0, sample_rate=44100, duration=1):
    wavef = np.fft.rfft(wave)  # Obtain Frequency spectrum
    #wavef = wavef[0:sample_rate//2]
    #wavef = np.append(wavef, np.zeros(sample_rate//2))
    # Digitally cut off high frequencies
    lpf = np.ones(cf)
    if k == 0:
        lpf = np.append(lpf, np.zeros(sample_rate-cf))
    else:
        lpf = np.append(lpf, np.linspace(1, 0, k))
        lpf = np.append(lpf, np.zeros(sample_rate-k-cf))

    wavef *= lpf
    return np.fft.irfft(wavef)  # Inverse FT to Convert Back to Time Domain



def highpass_filter(wave, cf, k=0, sample_rate=44100):
    wavef = fft(wave)  # Obtain Frequency spectrum
    wavef = wavef[0:sample_rate//2]
    wavef = np.append(wavef, np.zeros(sample_rate//2))
    # Digitally cut off low frequencies
    lpf = np.ones(sample_rate-cf)
    if k == 0:
        lpf = np.append(np.zeros(cf), lpf)
    else:
        lpf = np.append(np.linspace(0, 1, k), lpf)
        lpf = np.append(np.zeros(sample_rate-k-cf), lpf)

    wavef *= lpf
    return fft.ifft(wavef)  # Inverse FT to Convert Back to Time Domain

def lowpass_filter_demo(wave, sample_rate=44100):
    unfiltered_ft = fft(wave)
    filtered_wave = lowpass_filter(wave, 400, 1000)
    filtered_ft = fft(filtered_wave)
    unfiltered_ft = unfiltered_ft[0:sample_rate//2]
    unfiltered_ft = np.append(unfiltered_ft, np.zeros(sample_rate//2))
    plt.subplot(4, 1, 1)
    plot_wave(wave, 'Original Wave in Time Domain')
    plt.subplot(4, 1, 2)
    plot_spectrum(unfiltered_ft, 'Original Wave in Freq Domain')
    plt.subplot(4, 1, 3)
    plot_spectrum(filtered_ft, 'Filtered Wave in Freq Domain')
    plt.subplot(4, 1, 4)
    plot_wave(filtered_wave, 'Filtered Wave in Time Domain')
    plt.show()

def highpass_filter_demo(wave, sample_rate=44100):
    unfiltered_ft = fft(wave)
    filtered_wave = highpass_filter(wave, 1000)
    filtered_ft = fft(filtered_wave)
    unfiltered_ft = unfiltered_ft[0:sample_rate//2]
    unfiltered_ft = np.append(unfiltered_ft, np.zeros(sample_rate//2))
    plt.subplot(4, 1, 1)
    plot_wave(wave, 'Original Wave in Time Domain')
    plt.subplot(4, 1, 2)
    plot_spectrum(unfiltered_ft, 'Original Wave in Freq Domain')
    plt.subplot(4, 1, 3)
    plot_spectrum(filtered_ft, 'Filtered Wave in Freq Domain')
    plt.subplot(4, 1, 4)
    plot_wave(filtered_wave, 'Filtered Wave in Time Domain')
    plt.show()

def amp_envelop(wave, attack, decay, sustain, release, sustain_level=0.5, exp=1, duration=1, sample_rate=44100):
    N = sample_rate * duration
    S = attack + decay + sustain + release
    attack = round(N * attack / S)
    decay = round(N * decay / S)
    sustain = round(N * sustain / S)
    release = round(N * release / S)
    evl = np.linspace(0, 1, attack)
    exp_decay = np.linspace(sustain_level ** (1.0/exp), 0, decay)
    exp_decay = np.array([sustain_level + x ** exp for x in exp_decay])
    evl = np.append(evl, exp_decay)
    evl = np.append(evl, sustain_level * np.ones(sustain))
    evl = np.append(evl, np.linspace(sustain_level, 0, release))

    return evl * wave

def amp_envelop_demo(wave):
    evl_wave1 = wave * amp_envelop(wave, 1, 1, 1, 1, exp=1)
    evl_wave2 = wave * amp_envelop(wave, 1, 1, 1, 1, exp=8)
    evl_wave3 = wave * amp_envelop(wave, 1, 1, 0, 0, exp=1)
    evl_wave4 = wave * amp_envelop(wave, 0, 1, 1, 0, exp=1)
    evl_wave5 = wave * amp_envelop(wave, 0, 0, 1, 0, exp=1)
    plt.subplot(3, 2, 1)
    plot_wave(wave, "Original Wave")
    plt.subplot(3, 2, 2)
    plot_wave(evl_wave2, "1, 1, 1, 1, exp = 1")
    plt.subplot(3, 2, 3)
    plot_wave(evl_wave2, "1, 1, 1, 1, exp = 8")
    plt.subplot(3, 2, 4)
    plot_wave(evl_wave3, "1, 1, 0, 0, exp = 1")
    plt.subplot(3, 2, 5)
    plot_wave(evl_wave4, "0, 1, 1, 0, exp = 1")
    plt.subplot(3, 2, 6)
    plot_wave(evl_wave5, "0, 0, 0, 1, exp = 1")
    plt.show()

def amp_sine_lfo(wave, rate=1, intensity=1, offset=0, duration=1, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration))
    lfo_wave = intensity * np.sin(2 * np.pi * rate * t) + offset
    lfo_wave[lfo_wave<0] = 0
    lfo_wave *=  wave
    return lfo_wave

def amp_square_lfo(wave, rate=10, intensity=0.5, offset=0.5, duration=1, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration))
    lfo_wave = intensity * signal.square(2 * np.pi * rate * t) + offset
    lfo_wave[lfo_wave<0] = 0

    for x in range(1, len(lfo_wave)):
        if lfo_wave[x-1]!=1 and lfo_wave[x]!=0:
            lfo_wave[x] = min(1,lfo_wave[x-1] + 0.005)
        elif lfo_wave[x-1]!=0 and lfo_wave[x]!=1:
            lfo_wave[x] = max(0,lfo_wave[x-1] - 0.005)

    plot_wave(lfo_wave, 1)
    plt.show()
    #lfo_wave *=  wave
    return lfo_wave

def amp_sawtooth_lfo(wave, rate=1, intensity=0.5, offset=0.5, duration=1):
    t = np.linspace(0, duration, int(sample_rate * duration))
    lfo_wave = intensity * signal.sawtooth(2 * np.pi * rate * t, width=0.98) + offset
    lfo_wave[lfo_wave<0] = 0

    plot_wave(lfo_wave, 1)
    plt.show()
    #lfo_wave *=  wave
    return lfo_wave

"""
wave1 = get_sine_wave(440, 3)
wave2 = get_sine_wave(800, 3)
wave3 = get_sine_wave(1200, 3)
wave4 = get_sine_wave(6500, 3)
wave = wave1 + wave2 + wave3 + wave4
wave_lfo = amp_sine_lfo(wave1, rate=40, duration=3)

pygame.mixer.pre_init(sample_rate, size=-16, channels=1)
pygame.mixer.init()
pygame.mixer.set_num_channels(4)
#wave = np.array(get_sine_wave(440, 1, 100), dtype="int8")
wave1 = np.append(wave1, np.linspace(wave1[-1], 0, sample_rate*1))
wave1 = np.repeat(wave1.reshape(len(wave1), 1), 2, axis = 1)
wave1 = (wave1*30000).astype(np.int16)
#wave1 = np.array(wave1, dtype="int8")
sound = pygame.sndarray.make_sound(wave1)
plot_wave(wave1, duration=4)
plt.show()

sound.play()
time.sleep(4)
"""

wave = get_sine_wave(440, 3)

import matplotlib
matplotlib.use("Agg")

import matplotlib.backends.backend_agg as agg

import pylab

fig = pylab.figure(figsize=[4, 4], # Inches
                   dpi=100,        # 100 dots per inch, so the resulting buffer is 400x400 pixels
                   )
ax = fig.gca()
ax.plot(np.linspace(0, 3, 1000), wave[:1000])

canvas = agg.FigureCanvasAgg(fig)
canvas.draw()
renderer = canvas.get_renderer()
raw_data = renderer.tostring_rgb()

import pygame
from pygame.locals import *

pygame.init()

window = pygame.display.set_mode((600, 400), DOUBLEBUF)
screen = pygame.display.get_surface()

size = canvas.get_width_height()
surf = pygame.image.fromstring(raw_data, size, "RGB")
screen.blit(surf, (0,0))

hz = 100
crashed = False
while not crashed:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            crashed = True

    pygame.draw.circle(window, (0, 255, 0), (235, 225), 15)

    wave = get_sine_wave(hz, 0.5)
    hz = hz+1
    ax.plot(np.linspace(0, 0.5, 1000), wave[:1000])
    canvas = agg.FigureCanvasAgg(fig)
    canvas.draw()
    renderer = canvas.get_renderer()
    raw_data = renderer.tostring_rgb()
    size = canvas.get_width_height()
    surf = pygame.image.fromstring(raw_data, size, "RGB")
    screen.blit(surf, (0,0))

    pygame.display.flip()
    fig.clf()

pygame.quit()

"""
plt.subplot(2, 1, 1)
plot_wave(wave, duration=3)
plt.subplot(2, 1, 2)
plot_wave(wave_lfo, duration=3)
plt.show()
"""

#highpass_filter_demo(wave)
#amp_envelop_demo(wave)
#wave = amp_envelop(wave1, 1, 1, 1, 1)

"""
wavef = np.fft.rfft(wave)
N = sample_rate//2
w = np.linspace(0, N+1, N*3+1)
t = np.linspace(0, 3, sample_rate*3)
lpf = np.zeros((N-500)*3+1)
lpf = np.append(np.ones(500*3), lpf)
wavef *= lpf
wavet = np.fft.irfft(wavef)
plt.xlabel('freq')
plt.ylabel('amp')
plt.plot(t, wavet)
plt.show()

#wave = lowpass_filter(wave, 1000, 0, sample_rate*3)
#print(len(wave))
#plot_wave(wave, duration=3)
#plt.show()
"""

"""
pygame.mixer.pre_init(sample_rate, size=-16, channels=1)
pygame.mixer.init()
#pygame.mixer.set_num_channels(4)
wave = np.array(get_sine_wave(440, 3000, 1))
wave = np.repeat(wave.reshape(len(wave), 1), 2, axis = 1)
sound = pygame.sndarray.make_sound(wave)
sound.play()
time.sleep(1)
"""
"""
wave1 = get_sine_wave(440, 1, 1)
wave2 = get_sine_wave(800, 1, 1)
wave3 = get_sine_wave(1200, 1, 1)
wave = wave1 + wave2 + wave3
#sinc = get_sinc(160, 1, 1)
#wave = np.convolve(wave, sinc, 'same')
wave_ft = np.fft.fft(wave)
t = np.linspace(0, 1, int(sample_rate * 1))
w = np.linspace(0, 1, int(sample_rate * 1))

plt.xlabel('freq')
plt.ylabel('H')
plt.title('FFT Plot')
plt.plot(w, wave_ft)
plt.show()
"""


#plot_wave(wave, 1)
#sd.play(wave, blocking=True, loop=True)
"""
sd.play(wave1)
time.sleep(1)
sd.play(wave2)
time.sleep(1)
sd.play(wave3)
time.sleep(1)
"""
