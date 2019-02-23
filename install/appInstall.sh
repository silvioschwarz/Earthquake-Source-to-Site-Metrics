#! /bin/sh

echo "install and enable apache wsgi"
sudo apt-get install libapache2-mod-wsgi python-dev python3-venv
sudo a2enmod wsgi

#gunicorn
sudo a2enmod proxy proxy_ajp proxy_http rewrite deflate headers proxy_balancer proxy_connect proxy_html

sudo cp /etc/apache2/sites-available/000-default.conf /etc/apache2/sites-available/000-default.conf.old

echo "how to add /earthquake-distances/ to /var/www/html?"

sudo apache2 restart

echo  "setup virtualenv venv"

cd /home/pi/Documents/Earthquake-Distances

#sudo python3.5 -m venv venv

sudo virtualenv venv
source venv/bin/activate

sudo -H pip3 install -r requirements.txt
sudo ./plotlyPreRelease.sh
#sudo pip install flask gunicorn

deactivate

#sudo ./virtualHostInstall.sh

echo '
accesslog = "/home/pi/Documents/Earthquake-Distances/logs/gunicorn_access.log"
errorlog = "/home/pi/Documents/Earthquake-Distances/logs/gunicorn_error.log"' > gunicorn.conf

mkdir logs

SERVICE="
[Unit]
Description=eqdist
After=network.target

[Service]
User=pi
Restart=on-failure
WorkingDirectory=/home/pi/Documents/Earthquake-Distances/app/
ExecStart=/home/pi/Documents/Earthquake-Distances/venv/bin/gunicorn -c /home/pi/Documents/Earthquake-Distances/gunicorn.conf -b 0.0.0.0:6000 app:server

[Install]
WantedBy=multi-user.target
"

echo "$SERVICE" | sudo tee /etc/systemd/system/eqdist.service


systemctl daemon-reload
systemctl enable eqdist
systemctl start eqdist

WSGI="
#!/usr/bin/python
import sys
sys.path.insert(0,"/var/www/html//earthquake-distances//")
from app import app as application
"
echo "$WSGI" | sudo tee /var/www/html/earthquake-distances/eqdistapp.wsgi

