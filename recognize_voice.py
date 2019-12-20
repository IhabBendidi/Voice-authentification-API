import pyaudio
from IPython.display import Audio, display, clear_output
import wave
from scipy.io.wavfile import read
from sklearn.mixture import GMM
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import os

import pickle



from sklearn import preprocessing
import python_speech_features as mfcc





#Calculate and returns the delta of given feature vector matrix
def calculate_delta(array):
    rows,cols = array.shape
    deltas = np.zeros((rows,20))
    N = 2
    for i in range(rows):
        index = []
        j = 1
        while j <= N:
            if i-j < 0:
                first = 0
            else:
                first = i-j
            if i+j > rows -1:
                second = rows -1
            else:
                second = i+j
            index.append((second,first))
            j+=1
        deltas[i] = ( array[index[0][0]]-array[index[0][1]] + (2 * (array[index[1][0]]-array[index[1][1]])) ) / 10
    return deltas

#convert audio to mfcc features
def extract_features(audio,rate):
    mfcc_feat = mfcc.mfcc(audio,rate, 0.025, 0.01,20,appendEnergy = True, nfft=1200)
    mfcc_feat = preprocessing.scale(mfcc_feat)
    delta = calculate_delta(mfcc_feat)

    #combining both mfcc features and delta
    combined = np.hstack((mfcc_feat,delta))
    return combined





def recognize(filename,username):
    # Voice Authentication
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    CHUNK = 1024
    RECORD_SECONDS = 3
    #FILENAME = "./test.wav"
    #FILENAME = "./flute.wav"
    #FILENAME = "./piano.wav"
    FILENAME = filename


    modelpath = "./gmm_models/"

    gmm_files = [os.path.join(modelpath,fname) for fname in
                os.listdir(modelpath) if fname.endswith('.gmm')]

    models    = [pickle.load(open(fname,'rb')) for fname in gmm_files]

    speakers   = [fname.split("/")[-1].split(".gmm")[0] for fname
                in gmm_files]

    if len(models) == 0:
        print("No Users in the Database!")
        return

    #read test file
    sr,audio = read(FILENAME)

    # extract mfcc features
    vector = extract_features(audio,sr)
    log_likelihood = np.zeros(len(models))

    #checking with each model one by one
    #scorer = 0
    for i in range(len(models)):
        gmm = models[i]
        scores = np.array(gmm.score(vector))
        log_likelihood[i] = scores.sum()
        if speakers[i] == username:
            scorer = log_likelihood[i]
        print("\n\n\n")
        print(speakers[i])
        print(log_likelihood[i])

    pred = np.argmax(log_likelihood)
    identity = speakers[pred]
    maximum = max(log_likelihood)
    minimum = min(log_likelihood)

    score = (2*(scorer - minimum)/(maximum - minimum)) - 1
    #score = int(score)


    # if voice not recognized than terminate the process
    #if identity == 'unknown':
    #        print("Not Recognized! Try again...")
    #        return

    #print( "Recognized as - ", identity)
    return identity,score



def reconize_with_model(filename,model,username):
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    CHUNK = 1024
    RECORD_SECONDS = 3
    #FILENAME = "./test.wav"
    #FILENAME = "./flute.wav"
    #FILENAME = "./piano.wav"
    FILENAME = filename


    modelpath = model
    #modelpath = "./temp/models/"


    gmm_files = [os.path.join(modelpath,fname) for fname in
                os.listdir(modelpath) if fname.endswith('.gmm')]

    models    = [pickle.load(open(fname,'rb')) for fname in gmm_files]

    speakers   = [fname.split("/")[-1].split(".gmm")[0] for fname
                in gmm_files]

    if len(models) == 0:
        print("No Users in the Database!")
        return

    #read test file
    sr,audio = read(FILENAME)

    # extract mfcc features
    vector = extract_features(audio,sr)
    log_likelihood = np.zeros(len(models))

    #checking with each model one by one
    #scorer = 0
    for i in range(len(models)):
        gmm = models[i]
        scores = np.array(gmm.score(vector))
        log_likelihood[i] = scores.sum()
        if speakers[i] == username:
            scorer = log_likelihood[i]
        print("\n\n\n")
        print(speakers[i])
        print(log_likelihood[i])

    pred = np.argmax(log_likelihood)
    identity = speakers[pred]
    maximum = max(log_likelihood)
    minimum = min(log_likelihood)

    score = (2*(scorer - minimum)/(maximum - minimum)) - 1
    #score = int(score)


    # if voice not recognized than terminate the process
    #if identity == 'unknown':
    #        print("Not Recognized! Try again...")
    #        return

    #print( "Recognized as - ", identity)
    return identity,score

#if __name__ == '__main__':
    #recognize()
