#! /bin/sh

PROXY="
<Proxy *>
        Order deny,allow
        Allow from all
    </Proxy>
    ProxyPreserveHost On
    <Location "/earthquake-distances">
          ProxyPass "http://127.0.0.1:6000/"
          ProxyPassReverse "http://127.0.0.1:6000/"
    </Location>"

echo "$PROXY" | sudo tee vhost.txt

FILE="/etc/apache2/sites-available/000-default.conf"
#FILESED="\/etc\/apache2\/sites-available\/000-default.conf"
sudo cp "$FILE" "$FILE".old

sudo sed $'/<\/VirtualHost>/{e cat vhost.txt\n}' /etc/apache2/sites-available/000-default.conf | sudo tee /etc/apache2/sites-available/000-default.conf

#sudo sed $'/<\/VirtualHost>/{e cat vhost.txt\n}' /etc/apache2/sites-available/000-default.conf | sudo tee /etc/apache2/sites-available/000-default.conf

#grep -q "$PROXY" "$FILE" || sudo sed $'/<\/VirtualHost>/{e cat vhost.txt\n}' "$FILE" | sudo tee "$FILE"


