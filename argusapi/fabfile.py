from fabric.api import (
    run,
    cd,
    local
)
from fabric.operations import put

remote_path = '/home/fedor/checkouts/argusapi'
local_path = '.'

def prepare():
    local("python setup.py test")

def deploy():
    put(local_path=local_path, remote_path=remote_path)

def test():
    with cd(remote_path):
        run(". ~/.virtualenvs/web/bin/activate")
        run("python setup.py test")
        run("python setup.py develop")
