# Imports ##################################################
import sounddevice as sd  # for playing and recording
import compose as cmp	  # compose methods
import curses			  # for keypress detection
import numpy as np
from time import perf_counter as pcounter
import sys

# Global variables and constants ###########################
Mode = 'synth' # 'gen' or 'synth'
datapath = 'data/veena4Octaves.wav' # path to audio file containing sounds of 3 octaves
output_path = 'output/veena.wav' # path to store output
tune = 0 # tuning for generation (changes pitch by these many half-semitones)
F = 174.3 # fundamental tuning for synthesis (Madhya Sthayi Shadja frequency or use resonator natural frequency)
fs = 44100 # default sampling rate
K = 4 # gamaka sweep order


recordCheck = False
if "--record" in sys.argv:
	recordCheck = True
soundArr = []
timeArr = []

# Database #################################################

# we need a new swara mapping since the compose library notations are not easy to type in real-time
# can create mutltiple such mappings which are frequently used for multiple songs

swr1 = {'`':'pa',
		'1':'da1',
		'2':'da2',
		'3':'ni2',
		'4':'ni1',
		'5':'sa-',
		'6':'ri1-',
		'7':'ri2-',
		'8':'ga2-',
		'9':'ga1-',
		'0':'ma1-',
		'-':'ma2-',
		'=':'pa-',
		'q':'sa',
		'w':'ri1',
		'e':'ri2',
		'r':'ga2',
		't':'ga1',
		'y':'ma1',
		'u':'ma2',
		'i':'pa',
		'o':'da1',
		'p':'da2',
		'[':'ni2',
		']':'ni1',
		'\\':'sa-',
	    'a':'pa_',
	    's':'da1_',
	    'd':'da2_',
	    'f':'ni2_',
	    'g':'ni1_',
	    'h':'sa',
	    'j':'ri1',
	    'k':'ri2',
	    'l':'ga2',
	    ';':'ga1',
	    '\'':'ma1'}

swr1_gamaka = {'A':'pa_',
			   'S':'da1_',
			   'D':'da2_',
			   'F':'ni2_',
			   'G':'ni1_',
			   'H':'sa',
			   'J':'ri1',
			   'K':'ri2',
			   'L':'ga2',
			   ':':'ga1',
			   '"':'ma1',
			   'Q':'sa',
			   'W':'ri1',
			   'E':'ri2',
			   'R':'ga2',
			   'T':'ga1',
			   'Y':'ma1',
			   'U':'ma2',
			   'I':'pa',
			   'O':'da1',
			   'P':'da2',
			   '{':'ni2',
			   '}':'ni1',
			   '|':'sa-',
			   '~':'pa',
			   '!':'da1',
			   '@':'da2',
			   '#':'ni2',
			   '$':'ni1',
			   '%':'sa-',
			   '^':'ri1-',
			   '&':'ri2-',
			   '*':'ga2-',
			   '(':'ga1-',
			   ')':'ma1-',
			   '_':'ma2-',
			   '+':'pa-'}

# Methods ##################################################

def main(stdscr):
	
	note_dict = swr1
	gamaka_dict = swr1_gamaka
	if Mode == 'gen':
		print('\nProcessing...')
		cmp.set_gen_params(datapath,tune)
	else:
		cmp.set_synth_params(F,fs,K)
	
	# below code demonstrates the methods compose.gen_music() & compose.synth_music() for generating music file from notes in a text file
	'''
	play = []
	time = []
	
	with open('blindinglights.txt','r') as fin:
		for line in fin:
			play = play + line.split()
	
	with open('timing.txt','r') as fin:
		for line in fin:
			time = time + line.split()
	
	#time = 0.5*np.array(range(0,len(play)))
	
	time = time[0:len(play)]
	if Mode == 'synth':
		out = cmp.synth_music(play,time)
	else:
		out = cmp.gen_music(play,time)
	
	cmp.save(output_path,out)
	'''
	# below code demonstrates the methods compose.gen_note() & compose.synth_note() for playing individual notes typed in real-time
	
	stdscr.addstr('Turn Caps Lock OFF\n')
	stdscr.addstr('Press Shift for gamaka\n')
	stdscr.addstr('press x to exit\n')
	stdscr.nodelay(False) # blocking till input
	k = note_dict.keys()
	g = gamaka_dict.keys()
	prev_note = None
	check = True
	while check:
		c = stdscr.getkey() # wait and get keyboard input
		if c in k:
			note = note_dict[c]
			if Mode == 'synth':
				sound = cmp.synth_note(note,prev_note)
			else:
				sound = cmp.gen_note(note)
			prev_note=None
			sd.play(sound,fs)
			if recordCheck:
				soundArr.append([sound])
				timeArr.append(pcounter())
		elif c in g:
			prev_note = gamaka_dict[c]
			continue # skip this iteration
		else:
			if c == 'x': check = False # x is used to exit
	
	return

# Program ##################################################

if __name__ == '__main__':
	curses.wrapper(main)
	print('Thank You!')
if recordCheck:
	timeArr = [i - timeArr[0] for i in timeArr]
	finalMusic = np.zeros((int(fs*timeArr[-1]+len(soundArr[-1][0])),1))
	for i in range(len(soundArr)):
		finalMusic[int(fs*timeArr[i]):int(fs*timeArr[i])+len(soundArr[i][0]),0] = soundArr[i][0]
	cmp.save(output_path,finalMusic)
