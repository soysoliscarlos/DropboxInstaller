# -*- coding: utf-8 -*-
import sys
import subprocess
import os
import socket

ValidOSVersion = ({'ubuntu': ['hardy', 'intrepid', 'jaunty', 'karmic', 'lucid',
                 'maverick', 'natty', 'oneiric', 'precise', 'quantal', 'raring',
                 'saucy', 'trusty', 'utopic', 'vivid', 'wily', 'xenial']},
                 {'debian': ['jessie', 'sid', 'squeeze', 'wheezy']})
app_install = 'Dropbox'
apt_key = 'apt-key adv --keyserver pgp.mit.edu --recv-keys 5044912E'
source_list = '/etc/apt/sources.list.d/dropbox.list'
deb_line = 'deb http://linux.dropbox.com/%s/ %s main'
principal_package = 'dropbox'
packages = ()
lock_file = '/var/run/install_dropbox.lock'


def check_root():
    """Checking if the user has root privileges. If is True return True"""
    if os.getuid() == 0:
        print("User has root privileges...\n")
        return True  # Return if user is root
    else:
        print("I cannot run as a mortal... Sorry...")
        print(('Run: sudo %s \n' % (sys.argv[0])))
        sys.exit(1)  # Return if user is not root


def is_connected():
    IS = "www.google.com"
    try:
        # see if we can resolve the host name -- tells us if there is
        # a DNS listening
        host = socket.gethostbyname(IS)
        # connect to the host -- tells us if the host is actually
        # reachable
        socket.create_connection((host, 80), 2)
        #print(s)
        #data = urllib.urlopen(IS)
        #print(data)
        print('System has internet connection...\n')
        return True
    except:
        print('System has not internet connection.')
        print('Connect the system to internet...\n')
        return False


def lock_process(_lock_file):
    try:
        import psutil
    except ImportError:
        import pip
        pip.main(['install', 'psutil'])
        import psutil  # lint:ok
    if os.path.isfile(_lock_file):
        with open(_lock_file, "r") as lf:
            pid = lf.read()
            pid = int(pid)
        if psutil.pid_exists(pid):
            print('The process is already running...')
            print('Wait until the process is complete or delete the file:')
            print((('%s\n') % (_lock_file)))
            sys.exit(0)
            return True
        else:
            with open(_lock_file, "w") as lf:
                lf.write(str(os.getpid()) + '\n')
            return False
    elif not os.path.isfile(_lock_file):
        with open(_lock_file, "a") as lf:
            lf.write(str(os.getpid()) + '\n')
        return False


def question(_Q, lock_file):
    _count = False
    while _count is False:
        SELECT = input("%s (Y/n)('q' to exit):" % _Q)
        if SELECT == "Y" or SELECT == "y" or SELECT == '':
            return True
        elif SELECT == "N" or SELECT == "n":
            return False
        elif SELECT == "Q" or SELECT == "q":
            os.remove(lock_file)
            sys.exit(0)
        else:
            print('')
            print("You didn't choose a valid option. Select 'Y' or 'N'\n")
            print('')


def del_file(_file):
    if os.path.isfile(_file):
        os.remove(_file)
    return


def validingOSVersion(_ValidOsVersion, _MyOS, _OSVersion):
    for _dict in _ValidOsVersion:
        for key, value in list(_dict.items()):
            if key == _MyOS:
                for v in value:
                    if v == _OSVersion:
                        return True
                    else:
                        print(('"%s" is not a supported OS Version for this script...\n'
                             % (_OSVersion)))
            else:
                print(('"%s" is not a supported OS for this script...\n' %
                     (_MyOS)))
            return False


class Linux_Cmd():

    def __init__(self, _MyOS, _OSName):
        _sudo = ''
        _MyOS = _MyOS.lower()
        if _MyOS == 'ubuntu':
            _sudo = 'sudo'
        self._sudo = _sudo
        self._MyOS = _MyOS

    def command(self, _cmd, stdout=True):
        _cmd = _cmd.split()
        if self._MyOS == 'ubuntu':
            _cmd.insert(0, self._sudo)
        if not stdout:
            subprocess.check_call(_cmd)
        else:
            subprocess.check_call((_cmd), stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT)

    def check_pgk(self, _package):
        try:
            if self._MyOS == 'ubuntu' or self._MyOS == 'debian':
                self.command('dpkg-query -s %s' % (_package))
                return True
        except subprocess.CalledProcessError:
            return False

    def install_cmd(self, _package):
        if not self.check_pgk(_package):
            print(('Installing %s' % (_package)))
            if self._MyOS == 'ubuntu' or self._MyOS == 'debian':
                self.command('apt-get install -y %s' % (_package))
            print('OK...\n')
        else:
            print(('%s is already install' % (_package)))

    def multi_install_cmd(self, _packages):
        if type(_packages) is list or type(_packages) is tuple:
            for _package in _packages:
                self.install_cmd(_package)
        else:
            self.install_cmd(_packages)


def install_app(MyOS, OSName):
    Q = 'Do you want install %s?' % (app_install)
    install = Linux_Cmd(MyOS, OSName)
    if not install.check_pgk(principal_package):
        if question(Q, lock_file):
            install.command(apt_key)
            if MyOS == 'ubuntu' or MyOS == 'debian':
                with open(source_list, "w") as applist:
                    applist.write(deb_line % (MyOS, OSName))
                install.command('apt-get update')
                install.install_cmd(principal_package)
                if packages:
                    install.multi_install_cmd(packages)
    else:
        print(('%s is already install... \n' % (principal_package)))
        exit(0)


if __name__ == '__main__':
    try:
        if sys.argv[1] and sys.argv[2]:
            MyOS = sys.argv[1].lower()
            OSName = sys.argv[2].lower()
            if check_root():
                if not lock_process(lock_file):
                    if is_connected():
                        if validingOSVersion(ValidOSVersion, MyOS, OSName):
                            install_app(MyOS, OSName)
    except KeyboardInterrupt:
        print('\nExit by the user by pressing "Ctrl + c"...\n')
        del_file(lock_file)