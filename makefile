THIS_FILE := $(lastword $(MAKEFILE_LIST))

default:
	@echo $@  # print target name
	@$(MAKE) -f $(THIS_FILE) install

git:
	@echo $@  # print target name
	sudo apt-get install -y git git-core git-gui git-doc
	git config --global user.name "Silvio Schwarz"
	git config --global user.email admin@silvioschwarz.com
install: 
	@echo $@  # print target name
	./install/pythonInstall.sh
	./install/plotlyDash.sh
	sudo apt-get install apache2 mysql-client apache2-dev libapache2-mod-php php php-mysql mysql-server apache2-utils libexpat1 ssl-cert libapache2-mod-wsgi
	./install/modEnable.sh
	#vhosts and gunicorn?
node:
	@echo $@  # print target name
	curl -o- https://raw.githubusercontent.com/creationix/nvm/v0.34.0/install.sh | bash
	nvm install 8
	nvm use 8

.PHONY: update
update:
	@echo $@  # print target name
	sudo apt update && sudo apt upgrade && sudo apt autoremove
	#./updates/managerUpdate.sh

.PHONY: clean
clean:
	@echo $@  # print target name
	sudo apt autoremove

all:
	@echo $@  # print target name
	@$(MAKE) -f $(THIS_FILE) git install node update
