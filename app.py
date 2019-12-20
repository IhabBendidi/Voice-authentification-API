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
    output = {}
    record = {}
    if 'audio_file' not in request.files:
        output['trained'] = "failed"
        output['EnrollStatus'] = "REJECTED"
        output['DecisionReason']="AUDIO_FILE_NOT_SENT"
        output['voiceprintId'] = ""
        output['voiceModel'] = ""
        return output


    audio_file = request.files['audio_file']

    if 'username' not  in request.args:
        output['trained'] = "failed"
        output['EnrollStatus'] = "REJECTED"
        output['DecisionReason']="MISSING_ARGUMENTS"
        output['voiceprintId'] = ""
        output['voiceModel'] = ""
        return output
    if audio_file.filename == '':
        output['trained'] = "failed"
        output['EnrollStatus'] = "REJECTED"
        output['DecisionReason']="INEXISTANT_FILENAME"
        output['voiceprintId'] = ""
        output['voiceModel'] = ""
        return output

    username = request.args.get('username')
    if username == '':
        output['trained'] = "failed"
        output['EnrollStatus'] = "REJECTED"
        output['DecisionReason']="INEXISTANT_USERNAME"
        output['voiceprintId'] = ""
        output['voiceModel'] = ""
        return output
    #recording = json.loads(audio_file)
    #print(recording)
    filename = secure_filename(audio_file.filename)
    audio_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    recording = json.load(open(os.path.join(app.config['UPLOAD_FOLDER'], filename),'rb'))
    record1 = recording['record1']
    record2 = recording['record2']
    record3 = recording['record3']
    recording1 = base64.b64decode(record1)
    recording2 = base64.b64decode(record2)
    recording3 = base64.b64decode(record3)
    #print(recording2)
    filename2 = "recording1.wav"
    with open(os.path.join(app.config['UPLOAD_FOLDER'],filename2), 'wb') as recording_file:
        recording_file.write(recording1)

    gmm,gmm_model_path = add_user(username,os.path.join(app.config['UPLOAD_FOLDER'], filename2))
    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    #send_file(gmm_model_path, attachment_filename= 'ma.gmm')
    #model = json.loads(open(gmm_model_path,'rb'))
    if gmm_model_path == '':
        output['trained'] = "failed"
        output['EnrollStatus'] = "REJECTED"
        output['DecisionReason']="ERROR_TRAINING_THE_MODEL"
        output['voiceprintId'] = ""
        output['voiceModel'] = ""
        return output
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

    return output





@app.route('/api/voiceident/enrollments', methods=['GET'])
def check_enroll():
    output = {}
    if 'username' not  in request.args:
        output['trained'] = "failed"
        output['EnrollStatus'] = "REJECTED"
        output['DecisionReason']="MISSING_ARGUMENTS"
        output['voiceprintId'] = ""
        output['voiceModel'] = ""
        return output
    if 'voiceprintId' not  in request.args:
        output['trained'] = "failed"
        output['EnrollStatus'] = "REJECTED"
        output['DecisionReason']="MISSING_ARGUMENTS"
        output['voiceprintId'] = ""
        output['voiceModel'] = ""
        return output
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
        return output
    else:
        with open(gmm_model_path, 'rb') as binary_file:
            binary_file_data = binary_file.read()
            base64_encoded_data = base64.b64encode(binary_file_data)
            output['trained'] = "success"
            output['voiceprintId'] = str(record['_id'])
            output['voiceModel'] = base64_encoded_data
            output['EnrollStatus'] = "ACCEPTED"
            output['DecisionReason']="Accepted"
            return output




@app.route('/api/voiceident/authentication', methods=['POST'])
def authentificate():
    output = {}
    if 'audio_file' not in request.files:
        output['score'] = None
        output['Decision'] = "MISMATCH"
        output['DecisionReason']="AUDIO_FILE_NOT_SENT"
        return output




    audio_file = request.files['audio_file']

    if audio_file.filename == '':
        output['score'] = None
        output['Decision'] = "MISMATCH"
        output['DecisionReason']="INEXISTANT_FILENAME"
        return output
    if 'username' not  in request.args:
        output['score'] = None
        output['Decision'] = "MISMATCH"
        output['DecisionReason']="MISSING_ARGUMENTS"
        return output

    if 'voiceprintId' not  in request.args:
        output['score'] = None
        output['Decision'] = "MISMATCH"
        output['DecisionReason']="MISSING_ARGUMENTS"
        return output

    filename = secure_filename(audio_file.filename)
    audio_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    username = request.args.get('username')
    record = users.find_one({'username':username})
    if record == None:
        output['score'] = None
        output['Decision'] = "MISMATCH"
        output['DecisionReason']="INEXISTANT_USERNAME"
        return output



    if 'voiceModel'  in request.files:

        unknown_path = 'gmm_models/unknown.gmm'
        copyfile(unknown_path, 'temp/models/unknown.gmm')
        gmm = request.files['voiceModel']
        gmm.save("./temp/models/"+username+".gmm")
        identity,score = reconize_with_model(os.path.join(app.config['UPLOAD_FOLDER'], filename),"./temp/models/",username)
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        if identity == username:
            output['score'] = round(score*100,2)
            output['Decision'] = "MATCH"
            output['DecisionReason']="MATCH"
        else :
            output['score'] = round(score*100,2)
            output['Decision'] = "MISMATCH"
            output['DecisionReason']="BIOMETRIC_MISMATCH"
        return output
    else:
        identity,score = recognize(os.path.join(app.config['UPLOAD_FOLDER'], filename),username)
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        if identity == username:
            output['score'] = round(score*100,2)
            output['Decision'] = "MATCH"
            output['DecisionReason']="MATCH"
        else :
            output['score'] = round(score*100,2)
            output['Decision'] = "MISMATCH"
            output['DecisionReason']="BIOMETRIC_MISMATCH"
        return output



app.run()
