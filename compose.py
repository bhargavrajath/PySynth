# Imports #################################################
import numpy as np
import scipy.signal as sg
import soundfile as sf
import librosa

# Database ################################################

Swaras = ['sa_','ri1_','ri2_','ga2_','ga1_','ma1_','ma2_','pa_','da1_','da2_','ni2_','ni1_', # Lower Octave
	      'sa','ri1','ri2','ga2','ga1','ma1','ma2','pa','da1','da2','ni2','ni1',			 # Middle octave
          'sa-','ri1-','ri2-','ga2-','ga1-','ma1-','ma2-','pa-','da1-','da2-','ni2-','ni1-'] # Higher octave
         
Notes  = ['E1',  'F1',  'F1#', 'G1', 'G1#', 'A1',  'A1#', 'B1', 'C1', 'C1#', 'D1',  'D1#', 
          'E2',  'F2',  'F2#', 'G2', 'G2#', 'A2',  'A2#', 'B2', 'C2', 'C2#', 'D2',  'D2#',
          'E3',  'F3',  'F3#', 'G3', 'G3#', 'A3',  'A3#', 'B3',' C3', 'C3#', 'D3',  'D3#'] # The octave numbers here are relative

semiPerOct = np.array([1, 256/243, 9/8, 32/27, 81/64, 4/3, 729/512, 3/2, 128/81, 27/16, 16/9, 243/128])

Semitone = np.concatenate((0.5*semiPerOct,semiPerOct,2*semiPerOct))

F = 174.3 # default fundamental harmonic frequency of Madhya Sthayi Shadja (or resonator natural frequency)

# from harmonic energy distribution research:
Amp = np.array([4.7,32.37,14.47,16.04,3.11,2.97,14.81,2.21,3.5,0.52])/100

H = len(Amp)
T = 2 # default duration of one swara in seconds
F_s = 44100 # default samplerate
x = np.linspace(0,T,int(F_s*T)) # default time vector
y = np.zeros(int(F_s*T)) # default note vector
sounds = []
tempX = np.linspace(-1,1,int(F_s*T))
P = 1
FreqSweeper = np.tanh(tempX*P)

# Methods #################################################

def get_swara(ratio):
	semi = Semitone.tolist()
	index = None
	for r in semi:
		if ratio < 1.1*r and ratio > 0.9*r:
			index = semi.index(r)
	if index == None:
		return None
	else:
		return Swaras[index]

def get_ratio(swara):
	return Semitone[Swaras.index(swara)]

def set_gen_params(path,tune):
	global sounds,F_s
	data,F_s = sf.read(path)
	n = 54 #+ tune # from nth second in the audio
	for swara in Swaras:
		sound = data[n*F_s:(n+1)*F_s]
		n = n+2 # only even seconds contain notes
		if tune:
			sounds.append(librosa.effects.pitch_shift(sound,F_s,n_steps=tune))
		else:
			sounds.append(sound)
	return

def gen_note(n):
    if n in Swaras:
        return sounds[Swaras.index(n)]
    elif n in Notes:
        return sounds[Notes.index(n)]

def set_synth_params(fund,fsamp=F_s,order=P):
	global F_s,x,F,y,FreqSweeper
	if fsamp in [11025,16000,22050,44100,48000,88200,96000]: F_s = fsamp
	F  = fund
	x = np.linspace(0,T,int(F_s*T))
	y = np.zeros(int(F_s*T))
	if type(order) == type(1):
		FreqSweeper = np.tanh(tempX*order)*0.5
	return

def freqArr(note1,prev_note=None):
	global FreqSweeper
	if prev_note == None:
		prev_note = note1
	freq1 = F*get_ratio(prev_note)
	freq2 = F*get_ratio(note1)
	return freq2,(freq2-freq1)*FreqSweeper+(freq1+freq2)/2

def synth_note(note1,prev_note=None):
	global y
	y = y-y
	f,f_vect = freqArr(note1,prev_note)
	m = 0.05
	s = 10/np.sqrt(f)
	for n in range(1,H+1):
		b = np.exp(-((x-m*(n-1))/s)**2)*np.exp(-0.25*x)
		car = Amp[n-1]*np.cos(2*np.pi*n*f_vect*x) # carrier generation for each harmonic
		y = np.add(y,car*b) # final wave
		#y = sg.sosfiltfilt(coefs1,y)
		
	return y/np.max(y)

def synth_music(p,t): 
	if len(p) != len(t):
		print('notes and timestamps length mismatch')
		return 0
	
	notes = []
	
	for i in range(0,len(p)):
		notes.append((p[i],int(float(t[i])*F_s))) # convert time values into array positions
	
	music = np.array([0])
	
	for note in notes:

		sound = synth_note(note[0])
		
		if len(music) <= note[1]: # no overlap
			x = np.linspace(0,len(music),len(music))
			fadout = music*(1/(1+np.exp(0.01*(x-len(music)+500)))) # fadeout
			music = np.concatenate((fadout,np.zeros(note[1]-len(music)),sound))
		elif len(music) > note[1]: # overlap
			x = np.linspace(0,note[1],note[1])
			fadout = music[0:note[1]]*(1/(1+np.exp(0.01*(x-note[1]+500)))) # fadeout
			music = np.concatenate((fadout,sound))
	
	x = np.linspace(0,len(music),len(music))		
	music = music*(1/(1+np.exp(0.01*(x-len(music)+500)))) # fadeout for the end of music
	
	return music/np.max(music)

def gen_music(p,t): 
    
    notes = []
    
    if len(p) != len(t):
        print('notes and timestamps length mismatch')
        return 0
    
    for i in range(0,len(p)):
        notes.append((p[i],int(float(t[i])*F_s)))
	
    inter_clips = []
    max_len = 0
    
    for note in notes: # check which is the largest array while zero padding on the left, use that as max length
        clip = np.concatenate((np.zeros(note[1]),gen_note(note[0])))
        if len(clip) > max_len:
            max_len = len(clip)
        inter_clips.append(clip)
            
    music = np.zeros(max_len)
    
    for inter_clip in inter_clips: # using max length, zero padding on the right, superimpose all clips
        final_clip = np.concatenate((inter_clip,np.zeros(max_len-len(inter_clip))))
        music = music + final_clip
    
    return music

def save(filepath,outarray,f=F_s):
	sf.write(filepath,outarray,f)

def convert(note_string):
	notes = note_string.split()
	conversion = ''
	for note in notes:
		if note in Swaras:
			conversion = conversion + ' ' + Notes[Swaras.index(note)]
		elif note in Notes:
			conversion = conversion + ' ' + Swaras[Notes.index(note)]
	
	return conversion

