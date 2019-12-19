#!/bin/bash
apt-get update
sudo apt-get install -y libasound-dev portaudio19-dev libportaudio2 libportaudiocpp0
sudo apt-get install -y ffmpeg libav-tools
sudo pip install -y pyaudio
python3 -m pip install -r requirements.txt
