# Voice authentification with GMM models:

### Installation :
After installing Python 3 and pip3, Please launch the following bash file to install all requirements (it has only been tested on Linux systems):

`sudo bash setup.sh`

Please also install mongodb on your machine, and create a database with the name `identification`, and a collection with the name `users`
### Launching the server
You can launch the server on the terminal with :
`python3 app.py`

### API calls :

All API responses are the same as specified in the specifications

- For the main enrollment, this is an example of the curl request to send :
`curl -X POST -F audio_file=@voice_database/ihab/recording.wav 'http://127.0.0.1:5000/api/voiceident/enrollments?username=ihab'
`

You can specify the username you desire, as well as the path for the audio file you would like to use.


- For checking advancement of enrollement, this is an example of the curl request necessary :
`curl -i -X GET 'http://127.0.0.1:5000/api/voiceident/enrollments?username=ihab&voiceprintId=5df8cb542e276886223cbe36'
`
The voiceprintid is returned in the first API calls


- For authentification, the 1-to-N curl request is :
`curl -X POST -F audio_file=@voice_database/ihab/recording.wav 'http://127.0.0.1:5000/api/voiceident/authentication?username=ihab&voiceprintId=5df8cb542e276886223cbe36'
`

- For the 1-to-1 authentification, the curl request is :
`curl -X POST -F audio_file=@voice_database/unknown/flute.wav -F voiceModel=@gmm_models/ihab.gmm 'http://127.0.0.1:5000/api/voiceident/authentication?username=ihab&voiceprintId=5df8cb542e276886223cbe36'
`








python3 create_enrollement_input.py -a voice_database/ihab/recording.wav -b voice_database/unknown/flute.wav -c voice_database/ihab/recording.wav
