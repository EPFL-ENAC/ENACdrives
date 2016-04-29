#!/usr/bin/env python
"""
    Author : Bancal Samuel

    Fabric file to deploy web_app enacdrives
    usage :
    $ pww
    $ /home/sbancal/py/2/bin/fab -H enacit1sbtest4 full_deploy
    $ /home/sbancal/py/2/bin/fab -H enacit1vm1 --password=${PASS} full_deploy
"""


from fabric.utils import abort
from fabric.api import run, env, task
from fabric.contrib.project import rsync_project
from fabric.operations import sudo


if env.hosts[0] == "enacit1sbtest4":
    env.hosts = ["vagrant@enacit1sbtest4",]
    env.key_filename = "/home/sbancal/Projects/enacdrives/Vagrant/.vagrant/machines/enacit1sbtest4/virtualbox/private_key"
elif env.hosts[0] == "enacit1vm1":
    env.hosts = ["enacit1@enacit1vm1",]
else:
    abort("Unknown host.",
          "Supported hosts are :",
          "+ 'enacit1vm1' for enacit1@enacit1vm1",
          "+ 'enacit1sbtest4' for vagrant@enacit1sbtest4")

def sub(s):
    if env.host == "enacit1sbtest4":
        return s.format(
            local_dir="/home/sbancal/Projects/enacdrives/web_app/enacdrives/",
            code_dir="/django_app/enacdrives",
            server_config_dir="/django_app/enacdrives/server_config/enacit1sbtest4",
            virtualenv_dir="/django_app/venv/py3",
            python="/django_app/venv/py3/bin/python",
            pip="/django_app/venv/py3/bin/pip",
            installers_dir="/var/www/enacdrives.epfl.ch/installers",
            uploads_dir="/var/www/enacdrives.epfl.ch/uploads",
            logs_dir="/var/log/django-enacdrives",
            apache_vhost="django-enacdrives",
            apache_tequila_admins_conf="/etc/apache2/tequila_admins_rules.conf",
        )
    elif env.host == "enacit1vm1":
        return s.format(
            local_dir="/home/sbancal/Projects/enacdrives/web_app/enacdrives/",
            code_dir="/data/web/django-enacdrives",
            server_config_dir="/data/web/django-enacdrives/server_config/enacit1vm1",
            virtualenv_dir="/data/local/enacdrives/py3",
            python="/data/local/enacdrives/py3/bin/python",
            pip="/data/local/enacdrives/py3/bin/pip",
            installers_dir="/data/local/enacdrives/installers",
            uploads_dir="/data/local/enacdrives/uploads",
            logs_dir="/var/log/django-enacdrives",
            apache_vhost="django-enacdrives",
            apache_tequila_admins_conf="/etc/apache2/enacdrives_tequila_admins_rules.conf",
        )


# SETUP TASKS
@task
def virtualenv_init():
    run(sub("mkdir -p {virtualenv_dir}"))
    # This will fail on active environments because Celery & Apache use the virtualenv
    # run(sub("pyvenv-3.4 {virtualenv_dir}")) # Fails with python3 packaged with Ubuntu14.04
    run(sub("virtualenv -p python3 {virtualenv_dir}"))


@task
def virtualenv_setup():
    run(sub("{pip} install --upgrade -r {code_dir}/pip_requirements.txt"))
    # pip_requirements.txt is prepared this way :
    # . activate
    # pip install ...
    # pip freeze --local > enacdrives/pip_requirements.txt


@task
def mod_wsgi_express_setup():
    sudo(sub("{virtualenv_dir}/bin/mod_wsgi-express install-module"))
    sudo(sub("cp {server_config_dir}/etc/apache2/mods-available/wsgi_express.load /etc/apache2/mods-available/wsgi_express.load"))
    sudo(sub("cp {server_config_dir}/etc/apache2/mods-available/wsgi_express.conf /etc/apache2/mods-available/wsgi_express.conf"))
    sudo("a2enmod wsgi_express")
    apache_restart()


@task
def apache_setup():
    sudo(sub("mkdir -p {installers_dir}"))
    sudo(sub("chown www-data\\: {installers_dir}"))
    sudo(sub("mkdir -p {uploads_dir}"))
    sudo(sub("chown www-data\\: {uploads_dir}"))
    sudo(sub("mkdir -p {logs_dir}"))
    sudo(sub("chown www-data\\: {logs_dir}"))
    sudo(sub("cp {server_config_dir}/etc/apache2/sites-available/{apache_vhost}.conf /etc/apache2/sites-available/{apache_vhost}.conf"))
    sudo(sub("cp {server_config_dir}{apache_tequila_admins_conf} {apache_tequila_admins_conf}"))
    sudo(sub("a2ensite {apache_vhost}"))
    apache_reload()


@task
def apache_reload():
    sudo("service apache2 reload")


@task
def apache_restart():
    sudo("service apache2 restart")


@task
def rm_pyc():
    run(sub(r"find {code_dir} -name '*.pyc' -exec rm -f \{{\}} \;"))


# WEB_APP DEPLOYMENT TASK
@task
def rsync():
    rsync_project(
        local_dir=sub("{local_dir}"),
        remote_dir=sub("{code_dir}"),
        exclude=("*.sqlite", "/static/*", "*.pyc", "venv3/"),
        delete=True,
    )


@task
def rsync_n():
    rsync_project(
        local_dir=sub("{local_dir}"),
        remote_dir=sub("{code_dir}"),
        exclude=("*.sqlite", "/static/*", "*.pyc", "venv3/"),
        delete=True,
        extra_opts="-n"
    )


@task
def migrate():
    sudo(sub("{python} {code_dir}/manage.py migrate"), user="www-data")


@task
def admin_staff_setup():
    run(sub("{python} {code_dir}/tools/admin_staff_setup.py"))


@task
def deploy():
    rsync()
    apache_reload()


@task
def full_deploy():
    rsync()
    rm_pyc()
    virtualenv_init()
    virtualenv_setup()
    mod_wsgi_express_setup()
    apache_setup()
    migrate()
    admin_staff_setup()
    apache_restart()
