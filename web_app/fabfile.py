#!/usr/bin/env python
"""
    Author : Bancal Samuel

    Fabric file to deploy web_app enacdrives
    usage :
    $ pww
    $ fab -H test --password=${PASS} deploy
    $ fab -H prod --password=${PASS} deploy
"""


from fabric.utils import abort
from fabric.api import run, env, task
from fabric.contrib.project import rsync_project
from fabric.operations import sudo


HOSTS = {
    "test": "sbancal@enacit1sbtest4",
    # "prod": "bancal@enacit1srv3",
}

try:
    env.hosts = [HOSTS[h] for h in env.hosts]
except KeyError:
    abort("""\
Unknown host.
Supported hosts are :
{allowed_hosts}
""".format(
            allowed_hosts="\n".join(["+ '%s' for %s" % (k, HOSTS[k]) for k in HOSTS])
        )
    )


def sub(s):
    if env.host == "enacit1sbtest4":
        return s.format(
            local_dir="/home/sbancal/Projects/enacdrives/web_app/enacdrives/",
            code_dir="/django_app/enacdrives",
            server_config_dir="/django_app/enacdrives/server_config/enacit1sbtest4",
            virtualenv_dir="/django_app/venv/py3",
            python="/django_app/venv/py3/bin/python",
            pip="/django_app/venv/py3/bin/pip",
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
    sudo("mkdir -p /var/www/enacdrives.epfl.ch/public_html")
    sudo("chown www-data\\: /var/www/enacdrives.epfl.ch/public_html")
    sudo("mkdir -p /var/www/enacdrives.epfl.ch/private")
    sudo("chown www-data\\: /var/www/enacdrives.epfl.ch/private")
    sudo("mkdir -p /var/www/enacdrives.epfl.ch/upload")
    sudo("chown www-data\\: /var/www/enacdrives.epfl.ch/upload")
    sudo("mkdir -p /var/log/apache/django")
    sudo("chown www-data\\: /var/log/apache/django")
    sudo(sub("cp {server_config_dir}/etc/apache2/sites-available/enacdrives_app.conf /etc/apache2/sites-available/enacdrives_app.conf"))
    sudo(sub("cp {server_config_dir}/etc/apache2/tequila_admins_rules.conf /etc/apache2/tequila_admins_rules.conf"))
    sudo("a2ensite enacdrives_app")
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
        exclude=("*.sqlite", "/static/*", "*.pyc"),
        delete=True,
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
    migrate()
    admin_staff_setup()
    mod_wsgi_express_setup()
    apache_setup()
    apache_restart()
