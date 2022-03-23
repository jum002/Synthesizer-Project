import pygame
from pygame.locals import *
from Oscillator import Oscillator
from Note import Note
from Filter import Filter
from Envelop import Envelop
from LFO import LFO
from WavePlayer import WavePlayer
import numpy as np

sample_rate = 44100 # Hz
NOTES_TEMPLATE = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
NOTE_POS_W = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
notes_str = []  # stores all notes as strings
notes = []   # stores all notes as Note object

# Initialize the pygame library
pygame.init()

# Set up the drawing window
window = pygame.display.set_mode((1000, 500), DOUBLEBUF)
screen = pygame.display.get_surface()  # For plotting
pygame.display.set_caption('Synthesizer')

# Colors
WHITE = (255, 255, 255)
L_GREY = (200, 200, 200)
D_GREY = (80, 80, 80)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
D_YELLOW = (190, 190, 0)
BLACK = (0, 0, 0)

# Texts
pygame.font.init()  # Use the pygame font module to display text
myfont = pygame.font.SysFont('Comic Sans MS', 25)
texts = ['Sine', 'Square', 'Sawtooth', 'Low Pass', 'Sine']
osc1_text = myfont.render(texts[0], False, BLACK)
osc2_text = myfont.render(texts[1], False, BLACK)
osc3_text = myfont.render(texts[2], False, BLACK)
fil_text = myfont.render(texts[3], False, BLACK)
lfo_text = myfont.render(texts[4], False, BLACK)

"""
Change to next waveform based on previous waveform
"""
def update_waveform(var, ind):
    if var[ind] == 'Sine':
        var[ind] = 'Square'
    elif var[ind] == 'Square':
        var[ind] = 'Sawtooth'
    elif var[ind] == 'Sawtooth':
        var[ind] = 'Sine'


"""
Change to next filter based on current filter
"""
def update_filter(var, ind):
    if var[ind] == 'Low Pass':
        var[ind] = 'High Pass'
    elif var[ind] == 'High Pass':
        var[ind] = 'Low Pass'

# Images
piano_image = pygame.image.load("piano_keys.png")

# Plots
import matplotlib
matplotlib.use("Agg")
import matplotlib.backends.backend_agg as agg
import pylab

fig_pos = 5
fig1_pos = sample_rate // 2

# Time Plot (400x400 pixels)
fig = pylab.figure(figsize=[4, 2], dpi=100)
ax = fig.gca()
wave = np.zeros(1000)
ax.axis([0, fig_pos, -1, 1])
ax.plot(np.linspace(0, 5, 1000), wave)

canvas = agg.FigureCanvasAgg(fig)
canvas.draw()
raw_data = canvas.get_renderer().tostring_rgb()

size = canvas.get_width_height()
surf = pygame.image.fromstring(canvas.get_renderer().tostring_rgb(), size, "RGB")
screen.blit(surf, (0,0))

# Frequency Plot (400x400 pixels)
fig1 = pylab.figure(figsize=[4, 2], dpi=100)
ax1 = fig1.gca()
wavef = np.zeros(sample_rate//2)
ax1.axis([0, fig1_pos, 0, 30000])
ax1.plot(np.linspace(0, sample_rate//2, sample_rate//2), wavef)

canvas1 = agg.FigureCanvasAgg(fig1)
canvas1.draw()

surf1 = pygame.image.fromstring(canvas1.get_renderer().tostring_rgb(), size, "RGB")
screen.blit(surf1, (600,275))

# Initialize keyboard notes and waves: contains octaves 3 - 5
for x in range(1, 9):
    notes_str.extend([s + str(x) for s in NOTE_POS_W])

notes = [Note(s) for s in notes_str]

# Initialize Variables
duration = 5
MAX_DURATION = 5
volume = 1
osc = Oscillator()
osc_states = [True, False, False]
osc_waves = [None] * 3
osc_vol = [0, 0, 0]
osc_oct = [1, 1, 1]
osc_freq = [440, 440, 440]
fil = Filter()
fil_on = False
MAX_FREQ = 15000
fil_c = 0
fil_k = 0
env = Envelop()
env_on = False
env_attack = 0
env_decay = 0
env_sustain = 0
env_release = 0
env_exp = 1
env_sus_level = 0
lfo = LFO()
lfo_on = False
lfo_rate = 1 # 1 to 100
lfo_intensity = 0.5 # increment by 0.1, range: 0 - 1
lfo_offset = 0.5 # increment by 0.1, range: 0 - 1
wp = WavePlayer()
wave = np.zeros(sample_rate * duration)

"""
Based on the position of the mouse click (x, y), determine the Frequency
to play for all three oscillators
"""
def update_freq(x, y):
    if y > 445:            # 445 - the start of white keys in vertical
        ind = (x-23)/27.5  # Map index to the piano keyboard image
        r_ind = round(ind) + (osc_oct[0]-1) * 7
        n = notes[r_ind]
        osc_freq[0] = round(n.get_freq())
        osc_freq[1] = round(notes[r_ind+(osc_oct[1]-osc_oct[0])*7].get_freq())
        osc_freq[2] = round(notes[r_ind+(osc_oct[2]-osc_oct[0])*7].get_freq())

"""
Index mapping:
0: volume, 1: duration, 2: osc1_vol, 3: osc2_vol, 4:osc3_vol,
5: osc1_oct, 6: osc2_oct, 7: osc3_oct, 8: fil_c, 9: fil_k,
10:env_attack, 11: env_decay, 12: env_sustain, 13: env_release
14: env_exp, 15: env_sus_level, 16: lfo_rate, 17: lfo_intensity
18: lfo_offset
"""
control_marker_pos = [220, 220, 210, 210, 210, 295, 295, 295, 430, 430,
                      280, 280, 280, 280, 420, 420, 50, 50, 120]

"""
Overall Procedure:
- Detect Mouse press on a certain key
- Maps key pressed to Note object
- Obtain frequency from Note: get_freq()
- plug frequency into oscillator
- plug result of oscillator into filter
- plug result of filter into LFO
- plug result of LFO into Envelop
- Scale final sound wave by volume
- Play the final sound wave
- Plot the sound wave in Time and Freq Domain
"""

mouse_clicked = False
running = True
while running:
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    # Detect click the window close button
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Background Color
    window.fill(L_GREY)

    """ Oscillator """
    pygame.draw.rect(window, D_YELLOW, (20, 20, 370, 160))
    # On/Off Switches
    pygame.draw.circle(window, GREEN, (45, 50), 10)
    if osc_states[1] == True:
        pygame.draw.circle(window, GREEN, (45, 100), 10)
    else:
        pygame.draw.circle(window, D_GREY, (45, 100), 10)

    if osc_states[2] == True:
        pygame.draw.circle(window, GREEN, (45, 150), 10)
    else:
        pygame.draw.circle(window, D_GREY, (45, 150), 10)

    # Waveform Selector
    pygame.draw.rect(window, WHITE, (70, 35, 130, 30))
    pygame.draw.rect(window, WHITE, (70, 85, 130, 30))
    pygame.draw.rect(window, WHITE, (70, 135, 130, 30))
    # Volume Selector
    pygame.draw.rect(window, D_GREY, (210, 45, 70, 10))
    pygame.draw.circle(window, RED, (control_marker_pos[2], 50), 8)
    pygame.draw.rect(window, D_GREY, (210, 95, 70, 10))
    pygame.draw.circle(window, RED, (control_marker_pos[3], 100), 8)
    pygame.draw.rect(window, D_GREY, (210, 145, 70, 10))
    pygame.draw.circle(window, RED, (control_marker_pos[4], 150), 8)
    # Octave Selctor
    pygame.draw.rect(window, D_GREY, (295, 45, 70, 10))
    pygame.draw.circle(window, RED, (control_marker_pos[5], 50), 8)
    pygame.draw.rect(window, D_GREY, (295, 95, 70, 10))
    pygame.draw.circle(window, RED, (control_marker_pos[6], 100), 8)
    pygame.draw.rect(window, D_GREY, (295, 145, 70, 10))
    pygame.draw.circle(window, RED, (control_marker_pos[7], 150), 8)

    """ Filter """
    pygame.draw.rect(window, D_YELLOW, (400, 20, 180, 160))
    # On/Off Switch
    if fil_on == True:
        pygame.draw.circle(window, GREEN, (425, 45), 15)
    else:
        pygame.draw.circle(window, D_GREY, (425, 45), 15)

    # Filter Selector
    pygame.draw.rect(window, WHITE, (420, 80, 140, 30))
    # Cut-off Selector
    pygame.draw.rect(window, D_GREY, (430, 125, 120, 10))
    pygame.draw.circle(window, RED, (control_marker_pos[8], 130), 8)
    # k Selector
    pygame.draw.rect(window, D_GREY, (430, 155, 120, 10))
    pygame.draw.circle(window, RED, (control_marker_pos[9], 160), 8)

    """ LFO """
    pygame.draw.rect(window, D_YELLOW, (20, 190, 180, 160))
    # On/Off Switch
    if lfo_on == True:
        pygame.draw.circle(window, GREEN, (45, 225), 15)
    else:
        pygame.draw.circle(window, D_GREY, (45, 225), 15)

    # Waveform Selector
    pygame.draw.rect(window, WHITE, (40, 250, 140, 30))
    # Rate Selector
    pygame.draw.rect(window, D_GREY, (50, 295, 120, 10))
    pygame.draw.circle(window, RED, (control_marker_pos[16], 300), 8)
    # Intensity Selector
    pygame.draw.rect(window, D_GREY, (50, 320, 50, 10))
    pygame.draw.circle(window, RED, (control_marker_pos[17], 325), 8)
    # Offset Selector
    pygame.draw.rect(window, D_GREY, (120, 320, 50, 10))
    pygame.draw.circle(window, RED, (control_marker_pos[18], 325), 8)

    """ Envelop """
    pygame.draw.rect(window, D_YELLOW, (210, 190, 300, 160))
    # On/Off Switch
    if env_on == True:
        pygame.draw.circle(window, GREEN, (235, 225), 15)
    else:
        pygame.draw.circle(window, D_GREY, (235, 225), 15)

    # Selectors
    pygame.draw.rect(window, D_GREY, (280, 235, 120, 10))
    pygame.draw.circle(window, RED, (control_marker_pos[10], 240), 8)
    pygame.draw.rect(window, D_GREY, (280, 265, 120, 10))
    pygame.draw.circle(window, RED, (control_marker_pos[11], 270), 8)
    pygame.draw.rect(window, D_GREY, (280, 295, 120, 10))
    pygame.draw.circle(window, RED, (control_marker_pos[12], 300), 8)
    pygame.draw.rect(window, D_GREY, (280, 325, 120, 10))
    pygame.draw.circle(window, RED, (control_marker_pos[13], 330), 8)
    # Exp Selector
    pygame.draw.rect(window, D_GREY, (420, 265, 60, 10))
    pygame.draw.circle(window, RED, (control_marker_pos[14], 270), 8)
    # Sustain Level Selector
    pygame.draw.rect(window, D_GREY, (420, 295, 60, 10))
    pygame.draw.circle(window, RED, (control_marker_pos[15], 300), 8)

    """ Plot Selectors """
    # Time range up
    pygame.draw.rect(window, D_GREY, (650, 235, 50, 30))
    # Time range down
    pygame.draw.rect(window, D_GREY, (730, 235, 50, 30))
    # Freq range up
    pygame.draw.rect(window, D_GREY, (810, 235, 50, 30))
    # Freq range down
    pygame.draw.rect(window, D_GREY, (890, 235, 50, 30))

    """ Other Selectors """
    # Overall Volume Selectors
    pygame.draw.rect(window, D_GREY, (525, 220, 20, 130))
    pygame.draw.circle(window, RED, (535, control_marker_pos[0]), 10)
    # Duration of Note
    pygame.draw.rect(window, D_GREY, (560, 220, 20, 130))
    pygame.draw.circle(window, RED, (570, control_marker_pos[1]), 10)
    # Key Selector
    window.blit(piano_image, (10, 375))

    """ Mouse Clicks """
    if click[0] == True and mouse_clicked == False:
        mouse_clicked = True
        if mouse[0] in range(70, 200) and mouse[1] in range(35, 65):
            update_waveform(texts, 0)
            osc1_text = myfont.render(texts[0], False, BLACK)
        elif mouse[0] in range(70, 200) and mouse[1] in range(85, 115):
            update_waveform(texts, 1)
            osc2_text = myfont.render(texts[1], False, BLACK)
        elif mouse[0] in range(70, 200) and mouse[1] in range(135, 165):
            update_waveform(texts, 2)
            osc3_text = myfont.render(texts[2], False, BLACK)
        elif mouse[0] in range(420, 560) and mouse[1] in range(80, 110):
            update_filter(texts, 3)
            fil_text = myfont.render(texts[3], False, BLACK)
        elif mouse[0] in range(40, 180) and mouse[1] in range(250, 280):
            update_waveform(texts, 4)
            lfo_text = myfont.render(texts[4], False, BLACK)
        elif mouse[0] in range(35, 55) and mouse[1] in range(90, 110):
            # Osc Switch 2
            osc_states[1] = not osc_states[1]
        elif mouse[0] in range(35, 55) and mouse[1] in range(140, 160):
            # Osc Switch 3
            osc_states[2] = not osc_states[2]
        elif mouse[0] in range(210, 280) and mouse[1] in range(45, 55):
            # Osc Vol Slider 1
            vol_ratio = (mouse[0]-210)/70
            osc_vol[0] = vol_ratio * vol_ratio
            control_marker_pos[2] = mouse[0]
        elif mouse[0] in range(210, 280) and mouse[1] in range(95, 105):
            # Osc Vol Slider 2
            vol_ratio = (mouse[0]-210)/70
            osc_vol[1] = vol_ratio * vol_ratio
            control_marker_pos[3] = mouse[0]
        elif mouse[0] in range(210, 280) and mouse[1] in range(145, 155):
            # Osc Vol Slider 3
            vol_ratio = (mouse[0]-210)/70
            osc_vol[2] = vol_ratio * vol_ratio
            control_marker_pos[4] = mouse[0]
        elif mouse[0] in range(295, 365) and mouse[1] in range(45, 55):
            # Osc Oct Slider 1
            oct_ratio = (mouse[0]-295)/70
            osc_oct[0] = round(5.5 * oct_ratio) + 1
            control_marker_pos[5] = mouse[0]
        elif mouse[0] in range(295, 365) and mouse[1] in range(95, 105):
            # Osc Oct Slider 2
            oct_ratio = (mouse[0]-295)/70
            osc_oct[1] = round(5.5 * oct_ratio) + 1
            control_marker_pos[6] = mouse[0]
        elif mouse[0] in range(295, 365) and mouse[1] in range(145, 155):
            # Osc Oct Slider 3
            oct_ratio = (mouse[0]-295)/70
            osc_oct[2] = round(5.5 * oct_ratio) + 1
            control_marker_pos[7] = mouse[0]
        elif mouse[0] in range(410, 440) and mouse[1] in range(30, 60):
            # Filter Switch
            fil_on = not fil_on
        elif mouse[0] in range(430, 550) and mouse[1] in range(125, 135):
            # Fil_c Slider
            c_ratio = (mouse[0]-430)/120
            c_ratio = c_ratio * c_ratio
            fil_c = int(c_ratio * MAX_FREQ)
            control_marker_pos[8] = mouse[0]
        elif mouse[0] in range(430, 550) and mouse[1] in range(155, 165):
            # Fil_k Slider
            k_ratio = (mouse[0]-430)/120
            k_ratio = k_ratio * k_ratio
            fil_k = int(k_ratio * MAX_FREQ)
            control_marker_pos[9] = mouse[0]
        elif mouse[0] in range(220, 250) and mouse[1] in range(210, 240):
            # Envelop switch
            env_on = not env_on
        elif mouse[0] in range(280, 400) and mouse[1] in range(235, 245):
            # env_attack Slider
            env_attack = (mouse[0]-280)/120
            control_marker_pos[10] = mouse[0]
        elif mouse[0] in range(280, 400) and mouse[1] in range(265, 275):
            # env_decay Slider
            env_decay = (mouse[0]-280)/120
            control_marker_pos[11] = mouse[0]
        elif mouse[0] in range(280, 400) and mouse[1] in range(295, 305):
            # env_sustain Slider
            env_sustain = (mouse[0]-280)/120
            control_marker_pos[12] = mouse[0]
        elif mouse[0] in range(280, 400) and mouse[1] in range(325, 335):
            # env_release Slider
            env_release = (mouse[0]-280)/120
            control_marker_pos[13] = mouse[0]
        elif mouse[0] in range(420, 480) and mouse[1] in range(265, 275):
            # env_exp Slider
            env_exp = 1 + int(10 * (mouse[0]-420)/120)
            control_marker_pos[14] = mouse[0]
        elif mouse[0] in range(420, 480) and mouse[1] in range(295, 305):
            # env_sus_level Slider
            env_sus_level = 0.1 + int((mouse[0]-420)/120 * 10) / 10
            control_marker_pos[15] = mouse[0]
        elif mouse[0] in range(30, 60) and mouse[1] in range(210, 240):
            # LFO Switch
            lfo_on = not lfo_on
        elif mouse[0] in range(50, 170) and mouse[1] in range(295, 305):
            # lfo_rate Slider
            lfo_ratio = (mouse[0]-50)/120
            lfo_ratio = lfo_ratio * lfo_ratio
            lfo_rate = 120 * lfo_ratio
            control_marker_pos[16] = mouse[0]
        elif mouse[0] in range(50, 100) and mouse[1] in range(320, 330):
            # lfo_intensity Slider
            lfo_intensity = int((mouse[0]-50)/50 * 10) / 10
            control_marker_pos[17] = mouse[0]
        elif mouse[0] in range(120, 170) and mouse[1] in range(320, 330):
            # lfo_offset Slider
            lfo_offset = int((mouse[0]-120)/50 * 10) / 10
            control_marker_pos[18] = mouse[0]
        elif mouse[0] in range(525, 545) and mouse[1] in range(220, 350):
            # Volume Slider
            vol_ratio = 1 - (mouse[1]-220)/130
            volume = vol_ratio * vol_ratio
            control_marker_pos[0] = mouse[1]
        elif mouse[0] in range(560, 580) and mouse[1] in range(220, 350):
            # Duration Slider
            dur_ratio = 1 - (mouse[1]-220)/130
            duration = int(dur_ratio * 50) / 10
            if duration == 0:
                duration = 0.1
            control_marker_pos[1] = mouse[1]
        elif mouse[0] in range(650, 700) and mouse[1] in range(235, 265):
            # Time up buttom
            fig_pos = min(5, fig_pos * 5)
            fig.clf()
            ax = fig.gca()
            ax.axis([0, fig_pos, -1, 1])
            ax.plot(np.linspace(0, duration, int(duration*sample_rate)), wave)
            canvas = agg.FigureCanvasAgg(fig)
            canvas.draw()
            renderer = canvas.get_renderer()
            raw_data = renderer.tostring_rgb()
            size = canvas.get_width_height()
            surf = pygame.image.fromstring(raw_data, size, "RGB")
        elif mouse[0] in range(730, 780) and mouse[1] in range(235, 265):
            # Time down buttom
            fig_pos = max(0.05, fig_pos / 5)
            fig.clf()
            ax = fig.gca()
            ax.axis([0, fig_pos, -1, 1])
            ax.plot(np.linspace(0, duration, int(duration*sample_rate)), wave)
            canvas = agg.FigureCanvasAgg(fig)
            canvas.draw()
            renderer = canvas.get_renderer()
            raw_data = renderer.tostring_rgb()
            size = canvas.get_width_height()
            surf = pygame.image.fromstring(raw_data, size, "RGB")
        elif mouse[0] in range(810, 860) and mouse[1] in range(235, 265):
            # Freq up buttom
            fig1_pos = min(sample_rate//2, fig1_pos*2)
            fig1.clf()
            ax1 = fig1.gca()
            wavef = np.fft.rfft(wave)
            ax1.axis([0, fig1_pos, 0, 30000])
            ax1.plot(np.linspace(0, sample_rate//2, len(wavef)), np.abs(wavef))

            canvas1 = agg.FigureCanvasAgg(fig1)
            canvas1.draw()
            renderer1 = canvas1.get_renderer()
            raw_data1 = renderer1.tostring_rgb()

            size1 = canvas1.get_width_height()
            surf1 = pygame.image.fromstring(raw_data1, size1, "RGB")
        elif mouse[0] in range(890, 940) and mouse[1] in range(235, 265):
            # Freq down buttom
            fig1_pos = max(100, fig1_pos//2)
            fig1.clf()
            ax1 = fig1.gca()
            wavef = np.fft.rfft(wave)
            ax1.axis([0, fig1_pos, 0, 30000])
            ax1.plot(np.linspace(0, sample_rate//2, len(wavef)), np.abs(wavef))

            canvas1 = agg.FigureCanvasAgg(fig1)
            canvas1.draw()
            renderer1 = canvas1.get_renderer()
            raw_data1 = renderer1.tostring_rgb()

            size1 = canvas1.get_width_height()
            surf1 = pygame.image.fromstring(raw_data1, size1, "RGB")
        elif mouse[0] in range(10, 590) and mouse[1] in range(375, 500):
            update_freq(mouse[0], mouse[1])
            # Generate Wave
            for x in range(0, 3):
                if osc_states[x] == False:
                    continue

                if texts[x] == 'Sine':
                    osc_waves[x] = osc.get_sine_wave(osc_freq[x], duration, osc_vol[x])
                elif texts[x] == 'Square':
                    osc_waves[x] = osc.get_square_wave(osc_freq[x], duration, osc_vol[x])
                elif texts[x] == 'Sawtooth':
                    osc_waves[x] = osc.get_sawtooth_wave(osc_freq[x], 1, duration, osc_vol[x])

            wave = osc_waves[0]
            for x in range(1, 3):
                if osc_states[x] == True:
                    wave = wave + osc_waves[x]

            # Filter Wave
            if fil_on == True:
                if texts[3] == 'Low Pass':
                    wave = fil.lowpass_filter(wave, fil_c, fil_k, duration)
                elif texts[3] == 'High Pass':
                    wave = fil.highpass_filter(wave, fil_c, fil_k, duration)

            # LFO Wave
            if lfo_on == True:
                if texts[4] == 'Sine':
                    wave = lfo.amp_sine_lfo(wave, lfo_rate, lfo_intensity, lfo_offset, duration)
                elif texts[4] == 'Square':
                    wave = lfo.amp_square_lfo(wave, lfo_rate, lfo_intensity, lfo_offset, duration)
                elif texts[4] == 'Sawtooth':
                    wave = lfo.amp_sawtooth_lfo(wave, lfo_rate, lfo_intensity, lfo_offset, duration)

            # Amp Envelop Wave
            if env_on == True:
                wave = env.amp_envelop(wave, env_attack, env_decay, env_sustain, env_release, env_sus_level, env_exp, duration)

            wave = [volume * x for x in wave]

            wp.play_wave_pg(wave)

            if len(wave) < int(duration*sample_rate):
                wave = np.append(wave, np.zeros(int(duration*sample_rate) - len(wave)))
            elif len(wave) > int(duration*sample_rate):
                wave = wave[:int(duration*sample_rate)]

            fig.clf()
            ax = fig.gca()
            ax.axis([0, fig_pos, -1, 1])
            ax.plot(np.linspace(0, duration, int(duration*sample_rate)), wave)
            canvas = agg.FigureCanvasAgg(fig)
            canvas.draw()
            renderer = canvas.get_renderer()
            raw_data = renderer.tostring_rgb()
            size = canvas.get_width_height()
            surf = pygame.image.fromstring(raw_data, size, "RGB")

            fig1.clf()
            ax1 = fig1.gca()
            wavef = np.fft.rfft(wave)
            ax1.axis([0, fig1_pos, 0, 30000])
            ax1.plot(np.linspace(0, sample_rate//2, len(wavef)), np.abs(wavef))

            canvas1 = agg.FigureCanvasAgg(fig1)
            canvas1.draw()
            renderer1 = canvas1.get_renderer()
            raw_data1 = renderer1.tostring_rgb()

            size1 = canvas1.get_width_height()
            surf1 = pygame.image.fromstring(raw_data1, size1, "RGB")

    elif click[0] == False:
        mouse_clicked = False

    """ Texts """
    window.blit(osc1_text,(80,30))
    window.blit(osc2_text,(80,80))
    window.blit(osc3_text,(80,130))
    window.blit(fil_text,(425,75))
    window.blit(lfo_text,(45,245))

    """ Plots """
    screen.blit(surf, (600,25))  # Time PLot
    screen.blit(surf1, (600,275))  # Freq Plot

    # Flip the display
    pygame.display.flip()


pygame.quit()
