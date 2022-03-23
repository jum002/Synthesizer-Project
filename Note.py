import math

"""
Reused from my Piano Keyboard Project
"""
class Note:
    __name_letter = ''
    __sharp = False
    __octave = 0

    __SCALE_FACTOR = math.pow(2, 1/12)
    __FUND_FREQ = 440
    __NOTE_POS = ['C', '#', 'D', '#', 'E', 'F', '#', 'G', '#', 'A', '#', 'B']
    __NOTE_POS_W = ['C', 'D', 'E', 'F', 'G', 'A', 'B']

    def __init__(self, L, S, O):
        self.__name_letter = L
        self.__sharp = S
        self.__octave = O

    def __init__(self, note_s):
        self.__name_letter = note_s[0:1]
        if len(note_s) == 3:
            self.__sharp = True
        else:
            self.__sharp = False

        self.__octave = int(note_s[-1:])

    def get_name(self):
        return self.__name_letter

    def get_sharp(self):
        return self.__sharp

    def get_octave(self):
        return self.__octave

    def get_freq(self):
        half_steps = (int(self.__octave)-4)*12
        ind = self.get_ind()
        half_steps += (ind-9)
        return self.__FUND_FREQ * math.pow(self.__SCALE_FACTOR, half_steps)

    def get_ind(self):
        for x in range(0, 12):
            if self.__NOTE_POS[x] == self.__name_letter:
                ind = x
                break

        if self.__sharp == True:
            ind += 1

        return ind

    def get_ind_w(self):
        ind = 0
        for x in range(0, 7):
            if self.__name_letter == self.__NOTE_POS_W[x]:
                ind = x

        return ind


    def to_str(self):
        re_str = self.__name_letter
        if self.__sharp == True:
            re_str = re_str + '#'

        re_str = re_str + str(self.__octave)
        return re_str
