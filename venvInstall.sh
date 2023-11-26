#! /bin/sh

sudo apt-get update
sudo apt-get upgrade

echo "install virtual environment and dependencies"
sudo apt-get install python3-venv virtualenv

#sudo python3.5 -m venv venv
sudo virtualenv venv
source venv/bin/activate

pip3 install --user -r requirements.txt
#python -m pip install dash Flask gunicorn pandas plotly scipy numpy

deactivate

