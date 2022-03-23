# Synthesizer Project (ECE 45 Project)
by Junhua (Michael) Ma

## Research
Synthesizers consists of 4 main parts:
- Oscillator: generate fundamental waveforms as the basis for sound
  - Most synths have multiple oscillators that can be combined
    - Mix ratio can be changed when combining
  - Most synths have waveforms like Sine, Square, Sawtooth, Triangle
  - Can change the volume or amplitude of each waveform individually
- Filter: filter out certain range of frequencies in the sound
  - Most synths have Low Pass, High Pass, and Band Pass filters
  - Can set the important cut off points
  - Some can also change resonance: spike in frequency spectrum right before cut-off
- LFO: puts the sound's amplitude in accordance with a certain waveform
  - Most synths have waveforms like Sine, Square, Sawtooth, Triangle
  - Can change the LFO frequency, amplitude, etc
- Amplitude Envelop: puts the sound's overall amplitude in accordance with a certain shape consists of 4 stages: attack, decay, sustain, release
  - Most synths can change the relative period or level (for sustain) in each stage
- In addition, some other basic components of synths include:
  - Piano keyboard with 1 or more octaves
  - knobs for adjusting volume and other attributes
  - Graph of filters, built-in waveform plotters, etc
  - ON/OFF switch for each of the 4 main parts so the effect of each can be tested separately
  - Store created sound (based on the settings on synth) to be used at any time


## Design

### Initial UI Design:
After seeing many software synthesizer program, I came up with this initial design for my synthesizer:  
Synth_Design.png  
This design is very clean and has every controls displayed for the ease of use.

### Overall Code Structure:
The 4 main functions have separate classes: Oscillator.py, Filter.py, LFO.py, and Envelop.py. The piano keyboard and the sound playing functions are performed by WavePlayer.py, which uses Note objects from Note.py. These objects are combined in main.py to form the full synthesizer. More details as follows:

- **Oscillator.py**: have functions to generate different types of waves.
  - The main input required by the functions is a frequency, from which waves will be generated at default amplitude of 1 and duration of 1 second.
  - 3 functions to generate 3 types of waves: Sine, Square, Sawtooth. Waves are generated using Numpy and Scipy library in the form of a Numpy array.
- **Filter.py**: have functions to filter frequencies from the wave using FFT.
  - The main input required by the functions is a Numpy array that represents a signal.
  - 2 functions, one for low pass filter and one for high pass filter
  - Procedure: inputted signal is converted to the frequency domain using Numpy's FFT function, then certain frequencies in the resulting spectrum are removed based on parameters c and k. The method of removal is through the creation of a Numpy array with the same total length as the input signal and with value 1 from 0 to c, and value 0 from c to the end of the signal (the method is more complicated when k is not 0, as a slant needs to be added). This generated "step function" is multiplied by the frequency spectrum to remove all frequency components above c. After this manipulation, the filtered spectrum is transformed back into time domain as a filtered signal through Numpy's inverse FFT function. The same idea can be applied to high pass filter.
- **LFO.py**: have functions that envelop the signal using different waveforms
  - The main input required by the functions is a Numpy array that represents a signal.
  - 3 functions for the three types of LFO waveforms: Sine, Square, and Sawtooth
  - Procedure: After generating a specific waveform, the wave is multiplied by the signal. Since the generated waveform has value ranging from 0 to 1, it scales down the input signal based on its shape, resulting in the desired LFO functionality.
- **Envelop.py**: have a function that put an envelop on the input signal to control its amplitude.
  - The main input required by the function is a Numpy array that represents a signal.
  - 1 function for the amplitude envelop function.
  - Procedure: A Numpy array is generated based on the attack, decay, sustain, and release parameters, with values ranging between 0 and 1. After multiplying the generated array with the input signal, the input signal's amplitude is scaled down based on the shape of the envelop, resulting in the desired functionality.
- **WavePlayer.py**: have functions that play signals represented as Numpy arrays
  - Uses pygame.pmixer to play waves, which allows multiple channels and thus multiple sounds to play simultaneously (set at 4 channels).
  - The main input required by the function is a Numpy array that represents a signal.
  - The function plays the array signal for its full duration
- **main.py**: sets up the application window, Graphical User Interface, receives user input (mouse), and contains the main loop of the program.
  - Contains Matplotlib libraries working together with pygame to put plots on pygame window.
  - Stores all the variables, including the objects mentioned above.

### Filter Design
The low pass and high pass filter functions are designed as shown below:
filter_design.png

### Amplitude Envelop Design
The amplitude envelop function is designed as shown below:


## Testing and Validation
The functionalities of the program are tested separately.

### Filter
The filter requires many steps, and thus comprehensive testing are performed to see how to utilize Numpy's FFT and inverse FFT functions to correctly plot signal in time and frequency domain as well as cutting off certain frequencies.

Low Pass Filter test:  
lowpass_filter_demo.png

As shown above, the low pass filter correctly cuts off frequencies from the frequency domain and transform it back to time domain.

### LFO
LFO Sine test:  
lfo_amp_sine_demo.png

As shown above, the LFO changes the amplitude of the signal based on the LFO waveform.

### Amplitude Envelop
Amplitude Envelop test:  
amp_envelop_demo.png  

As shown above, the envelop correctly shape the input signal in accordance with my design.


## Problems and Challenges
- main.py gets very long and complicated to read, the code can be broken down more.
- For Square wave and Sawtooth wave, the signal generated by Scipy is not differentiable at certain points, and the instantaneous drop in volume results in pop sounds every time a sound finish playing. As a result, I had to make the perfect signal not perfect by adding a small damping signal to the end of every signal to ensure that the sound always goes down gradually instead of immediately.  
  damping_demo.png  
- I did not follow optimal method to program the GUI due to my rush for quick outcomes, so my GUI components all uses hard coded value. Thus, when I realized that there's not enough space to put texts and labels for the sliders and controls, I have to resort to not putting any texts and labels to simplify the project. So the synthesizer doesn't have any labels.
- I was still learning more and more about synthesizer as I was working through this project, since I've never previously know much about synthesizers at all, so certain limitations are due to my lack of understanding of the typical use of synthesizers.


## Summary
Overall, this project is a very fun one to test out the theories of signal transformation using Fourier Transform and Python's amazing capability of data manipulation. It also helps me better understand sound and music in general and how they really work.


## Misc
To see how to use this synthesizer, refer to the user manuel in the output folder.
To see how to setup this synthesizer, refer to the installation manuel in the output folder.
Download Zip: https://drive.google.com/file/d/19jPyXKdCNa2vlooLITXnGaOs9bwWFdsY/view?usp=sharing
