import pipes
import os
from fabric.api import run, put
from fabric.contrib.files import append

site_dir = '/home/alexey/wvpoi.batalex.ru'
listings_dir = '/var/www/wvpoi.batalex.ru/wikivoyage-poi'

def install_apache():
    run('apt-get -y install apache2')
    run('apt-get -y install libapache2-mod-wsgi')

def upload_site():
    run('rm -rf %s' % pipes.quote(site_dir))
    run('mkdir -p %s' % pipes.quote(site_dir))
    put('django-site', site_dir)

def configure_apache():
    config_path = '/etc/apache2/sites-available/001-wvpoi.batalex.ru.conf'

    django_site_dir = os.path.join(site_dir, 'django-site')
    apache_config = """
WSGIPythonPath %s:%s/virtualenv/lib/python2.7/site-packages/

<VirtualHost *:80>
    ServerAdmin webmaster@localhost
    DocumentRoot /var/www/html
    ServerName wvpoi.batalex.ru
    ServerAlias www.wvpoi.batalex.ru

    WSGIScriptAlias / %s/wvpoi/wsgi.py

    <Directory %s/wvpoi>
        <Files wsgi.py>
            Require all granted
        </Files>
    </Directory>
</VirtualHost>

    """ % (django_site_dir, site_dir, django_site_dir, django_site_dir)
    
    run("rm -f %s" % pipes.quote(config_path)) 
    append(config_path, apache_config)
    run("a2ensite 001-wvpoi.batalex.ru")
    run('service apache2 restart')

def configure_virtualenv():
    virtualenv_dir = os.path.join(site_dir, 'virtualenv')
    run('apt-get update')
    run('apt-get -y install python-pip')
    run('pip install virtualenv')
    run('rm -rf %s' % pipes.quote(virtualenv_dir))
    run('virtualenv %s' % pipes.quote(virtualenv_dir))
    run('/bin/bash -c "source %s/bin/activate && pip install django"' % pipes.quote(virtualenv_dir))

def create_listings_dir():
    run('mkdir -p %s' % pipes.quote(listings_dir))
