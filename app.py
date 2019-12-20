import flask
from flask import request, jsonify,redirect,send_file
from werkzeug.utils import secure_filename
from trainGMM import *
from recognize_voice import *
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
from pymongo import MongoClient
import base64
from bson.objectid import ObjectId
from shutil import copyfile



client = MongoClient('mongodb://localhost:27017')
db = client.identification
users = db.users

UPLOAD_FOLDER = 'temp'
ALLOWED_EXTENSIONS = {'wav', 'mp3'}

app = flask.Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config["DEBUG"] = True






@app.route('/api/voiceident/enrollments', methods=['POST'])
def enroll():
    status = 200
    output = {}
    record = {}
    if 'audio_file' not in request.files:
        output['trained'] = "failed"
        output['EnrollStatus'] = "REJECTED"
        output['DecisionReason']="AUDIO_FILE_NOT_SENT"
        output['voiceprintId'] = ""
        output['voiceModel'] = ""
        return output,status


    audio_file = request.files['audio_file']

    if 'username' not  in request.args:
        output['trained'] = "failed"
        output['EnrollStatus'] = "REJECTED"
        output['DecisionReason']="MISSING_ARGUMENTS"
        output['voiceprintId'] = ""
        output['voiceModel'] = ""
        return output,status
    if audio_file.filename == '':
        output['trained'] = "failed"
        output['EnrollStatus'] = "REJECTED"
        output['DecisionReason']="INEXISTANT_FILENAME"
        output['voiceprintId'] = ""
        output['voiceModel'] = ""
        return output,status

    username = request.args.get('username')
    if username == '':
        output['trained'] = "failed"
        output['EnrollStatus'] = "REJECTED"
        output['DecisionReason']="INEXISTANT_USERNAME"
        output['voiceprintId'] = ""
        output['voiceModel'] = ""
        return output,status
    #recording = json.loads(audio_file)
    #print(recording)
    filename = secure_filename(audio_file.filename)
    audio_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    recording = json.load(open(os.path.join(app.config['UPLOAD_FOLDER'], filename),'rb'))
    record1 = recording['record1']
    record2 = recording['record2']
    record3 = recording['record3']
    base_records = []
    base_records.append(base64.b64decode(record1))
    base_records.append(base64.b64decode(record2))
    base_records.append(base64.b64decode(record3))

    recordings = []
    filename0 = "recording0.wav"
    filename1 = "recording1.wav"
    for recording1 in base_records:
        with open(os.path.join(app.config['UPLOAD_FOLDER'],filename1), 'wb') as recording_file:
            recording_file.write(recording1)
        w = wave.open(os.path.join(app.config['UPLOAD_FOLDER'],filename1), 'rb')
        recordings.append( [w.getparams(), w.readframes(w.getnframes())] )
        w.close()
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename1))



    outputFile = wave.open(os.path.join(app.config['UPLOAD_FOLDER'], filename0), 'wb')
    outputFile.setparams(recordings[0][0])
    outputFile.writeframes(recordings[0][1])
    outputFile.writeframes(recordings[1][1])
    outputFile.writeframes(recordings[2][1])
    outputFile.close()


    gmm,gmm_model_path = add_user(username,os.path.join(app.config['UPLOAD_FOLDER'], filename0))
    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename0))

    if gmm_model_path == '':
        output['trained'] = "failed"
        output['EnrollStatus'] = "REJECTED"
        output['DecisionReason']="ERROR_TRAINING_THE_MODEL"
        output['voiceprintId'] = ""
        output['voiceModel'] = ""
        return output,status
    else :
        # Saving needed data in mongodb
        record['username'] = username
        record['model_path'] = gmm_model_path
        id = users.insert_one(record)
        #g = pickle.load(open(gmm_model_path,'rb'))
        #encodedBytes = base64.b64encode(gmm.encode("utf-8"))
        #encodedBytes = base64.b64encode(gmm)
        #encodedStr = str(encodedBytes, "utf-8")

        with open(gmm_model_path, 'rb') as binary_file:
            binary_file_data = binary_file.read()
            base64_encoded_data = base64.b64encode(binary_file_data)
            #base64_message = base64_encoded_data.decode('utf-8')



        output['trained'] = "success"
        output['voiceprintId'] = str(id.inserted_id)
        output['voiceModel'] = base64_encoded_data
        output['EnrollStatus'] = "ACCEPTED"
        output['DecisionReason']="Accepted"

    return output,status





@app.route('/api/voiceident/enrollments', methods=['GET'])
def check_enroll():
    status = 200
    output = {}
    if 'username' not  in request.args:
        output['trained'] = "failed"
        output['EnrollStatus'] = "REJECTED"
        output['DecisionReason']="MISSING_ARGUMENTS"
        output['voiceprintId'] = ""
        output['voiceModel'] = ""
        return output,status
    if 'voiceprintId' not  in request.args:
        output['trained'] = "failed"
        output['EnrollStatus'] = "REJECTED"
        output['DecisionReason']="MISSING_ARGUMENTS"
        output['voiceprintId'] = ""
        output['voiceModel'] = ""
        return output,status
    voiceprintId = request.args.get('voiceprintId')
    username = request.args.get('username')
    record = users.find_one({'_id':ObjectId(voiceprintId)})
    gmm_model_path = record.get('model_path')
    if gmm_model_path == '' or gmm_model_path == None:
        output['trained'] = "failed"
        output['EnrollStatus'] = "REJECTED"
        output['DecisionReason']="ERROR_TRAINING_THE_MODEL"
        output['voiceprintId'] = ""
        output['voiceModel'] = ""
        return output,status
    else:
        with open(gmm_model_path, 'rb') as binary_file:
            binary_file_data = binary_file.read()
            base64_encoded_data = base64.b64encode(binary_file_data)
            output['trained'] = "success"
            output['voiceprintId'] = str(record['_id'])
            output['voiceModel'] = base64_encoded_data
            output['EnrollStatus'] = "ACCEPTED"
            output['DecisionReason']="Accepted"
            return output,status




@app.route('/api/voiceident/authentication', methods=['POST'])
def authentificate():
    output = {}
    status = 200
    if 'audio_file' not in request.files:
        status = 403
        output['score'] = None
        output['Decision'] = "MISMATCH"
        output['DecisionReason']="AUDIO_FILE_NOT_SENT"
        return output,status




    audio_file = request.files['audio_file']

    if audio_file.filename == '':
        status = 403
        output['score'] = None
        output['Decision'] = "MISMATCH"
        output['DecisionReason']="INEXISTANT_FILENAME"
        return output,status
    if 'username' not  in request.args:
        status = 464
        output['score'] = None
        output['Decision'] = "MISMATCH"
        output['DecisionReason']="MISSING_ARGUMENTS"
        return output,status

    if 'voiceprintId' not  in request.args:
        status = 464
        output['score'] = None
        output['Decision'] = "MISMATCH"
        output['DecisionReason']="MISSING_ARGUMENTS"
        return output,status

    filename = secure_filename(audio_file.filename)
    audio_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    recording = json.load(open(os.path.join(app.config['UPLOAD_FOLDER'], filename),'rb'))
    auth_record = base64.b64decode(recording['record'])
    filen = "auth.wav"
    with open(os.path.join(app.config['UPLOAD_FOLDER'],filen), 'wb') as recording_file:
        recording_file.write(auth_record)

    try :
        model = recording['voiceModel']
    except:
        model = None



    username = request.args.get('username')
    record = users.find_one({'username':username})
    if record == None:
        status = 464
        output['score'] = None
        output['Decision'] = "MISMATCH"
        output['DecisionReason']="INEXISTANT_USERNAME"
        return output,status



    if model is not None:

        unknown_path = 'gmm_models/unknown.gmm'
        copyfile(unknown_path, 'temp/models/unknown.gmm')
        gmm_model = base64.b64decode(model)
        with open("./temp/models/" + username + '.gmm', 'wb') as model_file:
            model_file.write(gmm_model)
        #gmm = request.files['voiceModel']
        #gmm.save("./temp/models/"+username+".gmm")
        identity,score = reconize_with_model(os.path.join(app.config['UPLOAD_FOLDER'], filen),"./temp/models/",username)
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filen))
        os.remove("./temp/models/" + username + '.gmm')
        if identity == username:
            output['score'] = round(score*100,2)
            output['Decision'] = "MATCH"
            output['DecisionReason']="MATCH"
        else :
            output['score'] = round(score*100,2)
            output['Decision'] = "MISMATCH"
            output['DecisionReason']="BIOMETRIC_MISMATCH"
        return output,status
    else:
        identity,score = recognize(os.path.join(app.config['UPLOAD_FOLDER'], filen),username)
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filen))
        if identity == username:
            output['score'] = round(score*100,2)
            output['Decision'] = "MATCH"
            output['DecisionReason']="MATCH"
        else :
            output['score'] = round(score*100,2)
            output['Decision'] = "MISMATCH"
            output['DecisionReason']="BIOMETRIC_MISMATCH"
        return output,status



app.run()
