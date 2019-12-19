import pyaudio
from IPython.display import Audio, display, clear_output
import wave
from scipy.io.wavfile import read
from sklearn.mixture import GMM
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import os

import pickle,json



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



def add_user(name,path):

    #Voice authentication
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100
    CHUNK = 1024
    RECORD_SECONDS = 5

    path = "./"+ path
    #source = "./voice_database"


    #os.mkdir(source)



    dest =  "./gmm_models/"
    #count = 1
    #max_count = len(os.listdir(source))

    #for path in os.listdir(source):
        #path = os.path.join(source, path)


    features = np.array([])

    # reading audio files of speaker
    (sr, audio) = read(path)

    # extract 40 dimensional MFCC & delta MFCC features
    vector   = extract_features(audio,sr)

    if features.size == 0:
        features = vector
    else:
        features = np.vstack((features, vector))

    # when features of 3 files of speaker are concatenated, then do model training
    #if count == max_count:
    gmm = GMM(n_components = 16, n_iter = 200, covariance_type='diag',n_init = 3)
    gmm.fit(features)


    # saving the trained gaussian model
    pickle.dump(gmm, open(dest + name + '.gmm', 'wb'))
    #json.dump(gmm, a)
    print(name + ' added successfully')

    features = np.asarray(())
    return gmm,dest + name + '.gmm'
    #count = 0
    #else :
        #    print ("not done")
        #count = count + 1

#if __name__ == '__main__':
    #add_user("unknown")
