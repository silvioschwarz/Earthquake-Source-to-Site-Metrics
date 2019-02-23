#! /bin/sh

#! /bin/sh

echo "install and enable apache wsgi"
sudo apt-get install libapache2-mod-wsgi python-dev
sudo a2enmod wsgi

#gunicorn
sudo a2enmod proxy proxy_ajp proxy_http rewrite deflate headers proxy_balancer proxy_connect proxy_html


echo "
ServerName silvioschwarz.com
" > /etc/apache2/apache2.conf

sudo cp /etc/apache2/sites-available/000-default.conf /etc/apache2/sites-available/000-default.conf.old

echo "

<VirtualHost *:80>
    # The ServerName directive sets the request scheme, hostname and port that
    # the server uses to identify itself. This is used when creating
    # redirection URLs. In the context of virtual hosts, the ServerName
    # specifies what hostname must appear in the request's Host: header to
    # match this virtual host. For the default virtual host (this file) this
    # value is not decisive as it is used as a last resort host regardless.
    # However, you must set it for any further virtual host explicitly.
    #ServerName www.example.com

    ServerAdmin webmaster@localhost
    DocumentRoot /var/www/html

    # Available loglevels: trace8, ..., trace1, debug, info, notice, warn,
    # error, crit, alert, emerg.
    # It is also possible to configure the loglevel for particular
    # modules, e.g.
    #LogLevel info ssl:warn

    ErrorLog ${APACHE_LOG_DIR}/error.log
    CustomLog ${APACHE_LOG_DIR}/access.log combined

    # For most configuration files from conf-available/, which are
    # enabled or disabled at a global level, it is possible to
    # include a line for only one particular virtual host. For example the
    # following line enables the CGI configuration for this host only
    # after it has been globally disabled with "a2disconf".
    #Include conf-available/serve-cgi-bin.conf

    ProxyPass /static/ !
        ProxyPass / http://localhost:8000/

        <Directory "/var/www/html/eqdistapp/static/">
            Order allow,deny
            Allow from all
            Options Indexes FollowSymLinks MultiViews
            Satisfy Any
            #AllowOverride None
        </Directory>

    <Proxy *>
        Order deny,allow
          Allow from all
    </Proxy>
    ProxyPreserveHost On
    <Location "/eqdistapp">
          ProxyPass "http://127.0.0.1:5000/"
          ProxyPassReverse "http://127.0.0.1:5000/"
    </Location>
</VirtualHost>
" > /etc/apache2/sites-available/eqdistapp.conf

sudo apache2 restart

#http://your-ip-here —> should give you the same standard html page for apache, as before
#http://your-ip-here/flaskapp —> should give you:
#Service Unavailable
#The server is temporarily unable to service your request due to maintenance downtime or capacity problems. Please try again later.

echo  "setup virtualenv venv"

cd /home/pi/documents/Earthquake-Distances

sudo virtualenv venv
source venv/bin/activate

pip install -r requirements.txt
#sudo pip install flask gunicorn

echo '
accesslog = "/home/flaskappuser/flaskapp/logs/gunicorn_access.log"
errorlog = "/home/flaskappuser/flaskapp/logs/gunicorn_error.log"' > gunicorn.conf

mkdir logs

echo "

[Unit]
Description=flaskapp
After=network.target

[Service]
User=flaskappuser
Restart=on-failure
WorkingDirectory=/home/pi/documents/Earthquake-Distances
ExecStart=/home/pi/documents/Earthquake-Distances/venv/bin/gunicorn -c /home/pi/documents/Earthquake-Distances/gunicorn.conf -b 0.0.0.0:5000 app:app

[Install]
WantedBy=multi-user.target
" > /etc/systemd/system/eqdistapp.service
systemctl daemon-reload
systemctl enable flaskapp
systemctl start flaskapp

###other method mod_WSGI


NAME=eqdistapp.conf

sudo mkdir /var/www/html/eqdistapp
sudo mkdir /var/www/html/eqdistapp/static


echo "

<VirtualHost *:80>
    ServerAdmin webmaster@flaskhelloworldsite.com
    ServerName www.silvioschwarz.com/eqdistapp
    ServerAlias eqdistapp
    ErrorLog /var/www/html/eqdistapp/logs/error.log
    CustomLog /var/www/html/eqdistapp/logs/access.log combined

    WSGIDaemonProcess eqdistapp user=www-data group=www-data threads=5
    WSGIProcessGroup eqdistapp
    WSGIScriptAlias / /var/www/html/eqdistapp/eqdistapp.wsgi
    Alias /static/ /var/www/html/eqdistapp/static
    <Directory /var/www/html/eqdistapp/static>
        Order allow,deny
        Allow from all
    </Directory>

</VirtualHost>
" > /etc/apache2/sites-available/eqdistapp.conf
 
sudo a2ensite $NAME

echo "

#!/usr/bin/python
import sys
sys.path.insert(0,"/var/www/html/eqdistapp/")
from helloworldapp import app as application
" > /var/www/html/eqdistapp/eqdistapp.wsgi

echo "127.0.0.1 eqdistapp" > /etc/hosts

sudo mkdir -p /var/www/html/eqdistapp/logs
sudo chown -R www-data:www-data eqdistapp

sudo /etc/init.d/apache2 reload



##########
echo "install and enable apache wsgi"
sudo apt-get install libapache2-mod-wsgi python-dev
sudo a2enmod wsgi

echo  "setup virtualenv venv"

sudo virtualenv venv
source venv/bin/activate

sudo pip install Flask

NAME=flaskhelloworldsite.com.conf


echo "

<VirtualHost *:80>
    ServerAdmin webmaster@flaskhelloworldsite.com
    ServerName www.flaskhelloworldsite.com
    ServerAlias flaskhelloworldsite.com
    ErrorLog /var/www/flaskhelloworldsite.com/logs/error.log
    CustomLog /var/www/flaskhelloworldsite.com/logs/access.log combined

    WSGIDaemonProcess helloworldapp user=www-data group=www-data threads=5
    WSGIProcessGroup helloworldapp
    WSGIScriptAlias / /var/www/FLASKAPPS/helloworldapp/helloworldapp.wsgi
    Alias /static/ /var/www/FLASKAPPS/helloworldapp/static
    <Directory /var/www/FLASKAPPS/helloworldapp/static>
        Order allow,deny
        Allow from all
    </Directory>

</VirtualHost>
" > /etc/apache2/sites-available/flaskhelloworldsite.com.conf
 
sudo a2ensite $NAME

echo "

#!/usr/bin/python
import sys
sys.path.insert(0,"/var/www/FLASKAPPS/")
from helloworldapp import app as application
" > /var/www/html/FLASKAPPS/helloworldapp/helloworldapp.wsgi

echo "127.0.0.1 flaskhelloworldsite.com" > /etc/hosts

sudo mkdir -p /var/www/flaskhelloworldsite.com/logs
sudo chown -R www-data:www-data flaskhelloworldsite.com

sudo /etc/init.d/apache2 reload
