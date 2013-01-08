from fabric.contrib.files import *
from fabric.api import *

env.roledefs = {
	'production': [ '173.204.85.236' ]
}

paths = {
	'testing': '/storage/www/white-label',
	'production': '/store_f/www/white-label.ru'
}

@task
def deploy(env='testing'):
	path = paths[ env ]
	execute(publish, path, roles=[ env ])

def publish(path):
	if not exists(path):
		sudo('git clone https://github.com/skotopes/white-label.git %s')
	with cd(path):
		if not exists('env'):
			sudo('virtualenv env')
		sudo('git pull')
		sudo('. env/bin/activate && pip install -r requirements.txt')
		sudo('. env/bin/activate && ./manage.py StopFCGI || exit 0')
		sudo('. env/bin/activate && ./manage.py UpgradeDB')
		sudo('. env/bin/activate && ./manage.py StartFCGI')
