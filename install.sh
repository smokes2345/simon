#!/bin/sh

venv_dir="$HOME/.venv/simple_simon"

sudo apt-get install python3-pip python3-pyaudio swig libportaudio-dev build-essential libpulse-dev libasound2-dev
pip install virtualenv
virualenv --system-site-packages $venv_dir
source $venv_dir/bin/activate
pip install -r requirements.txt
