#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import subprocess
import os
import socket
import apt

__version__ = '1.0.0'

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


def check_root(MyOS, OSName):
    """Checking if the user has root privileges. If is True return True"""
    if os.getuid() == 0:
        print("User has root privileges...\n")
        return True  # Return if user is root
    else:
        print("I cannot run as a mortal... Sorry...")
        print(('Run: sudo {} {} {}\n'.format(sys.argv[0], MyOS, OSName)))
        exit(1)  # Return if user is not root


def is_connected():
    IS = "www.google.com"
    try:
        # see if we can resolve the host name -- tells us if there is
        # a DNS listening
        host = socket.gethostbyname(IS)
        socket.create_connection((host, 80), 2)
        print('System has internet connection...\n')
        return True
    except:
        print('System has not internet connection.')
        print('Connect the system to internet...\n')
        return False


def validingOSVersion(_ValidOsVersion, _MyOS, _OSVersion):
    os = False
    ver = False
    for _dict in _ValidOsVersion:
        for key, value in list(_dict.items()):
            if key == _MyOS:
                os = True
                for v in value:
                    if v == _OSVersion:
                        ver = True
    if not os:
        help_app(
            ('"{}" is not a supported OS for this script...\n'.format(_MyOS)))
    if not ver:
        help_app(('"{}" is not a supported OS Version for this script...\n'.format(_OSVersion)))
    return os and ver


class Linux_Cmd():

    def __init__(self, _MyOS, _OSName, stdout=True):
        _sudo = ''
        _MyOS = _MyOS.lower()
        if _MyOS == 'ubuntu' or _MyOS == 'debian':
            cache = apt.Cache()
            self.cache = cache
            self.cache.update()
            self.cache.commit(apt.progress.base.AcquireProgress(),
                            apt.progress.base.InstallProgress())
        if _MyOS == 'ubuntu':
            _sudo = 'sudo'
        self._sudo = _sudo
        self._MyOS = _MyOS
        self.stdout = stdout

    def command(self, _cmd):
        _cmd = _cmd.split()
        if self._MyOS == 'ubuntu':
            _cmd.insert(0, self._sudo)
        if self.stdout:
            subprocess.check_call(_cmd)
        else:
            subprocess.check_call((_cmd), stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT)

    def check_pgk(self, _package):
        if self._MyOS == 'ubuntu' or self._MyOS == 'debian':
            try:
                if self.cache[_package].is_installed:
                    print(('"{}" is already installed...\n'.format(_package)))
                    return True
                else:
                    print(('"{}" is not installed...\n'.format(_package)))
                    return False
            except KeyError:
                print(('"{}" is not installed...\n'.format(_package)))
                return False

    def install_cmd(self, _package):
        if not self.check_pgk(_package):
            if self._MyOS == 'ubuntu' or self._MyOS == 'debian':
                print(('Installing "{}"'.format(_package)))
                try:
                    self.command('apt install -y {}'.format(_package))
                except:
                    try:
                        self.command('aptitude install -y {}'.format(_package))
                    except:
                        self.command('apt-get install -y {}'.format(_package))
                finally:
                    print('OK...\n')

    def multi_install_cmd(self, _packages):
        if type(_packages) is list or type(_packages) is tuple:
            for _package in _packages:
                self.install_cmd(_package)
        else:
            self.install_cmd(_packages)


def help_app(_message=False):
    if _message:
        print(('Error: {} \n'.format(_message)))
    print('Usage:')
    print(('    sudo python3 {} OS OSName\n'.format(sys.argv[0])))

    print('Examples:')
    for _dict in ValidOSVersion:
        for key, value in list(_dict.items()):
            for v in value:
                print(('    sudo python3 {} {} {}'.format(sys.argv[0], key, v)))
    exit(1)


def install_app(MyOS, OSName):
    install = Linux_Cmd(MyOS, OSName)
    if not install.check_pgk(principal_package):
        print('Adding key...\n')
        try:
            install.command(apt_key)
        except subprocess.CalledProcessError:
            print('\nError: Could not download the key... \n')
            exit(1)
        finally:
            if MyOS == 'ubuntu' or MyOS == 'debian':
                print('Adding Source List...\n')
                with open(source_list, "w") as applist:
                    applist.write(deb_line % (MyOS, OSName))
                print('Updating Source List...\n')
                install.command('apt-get update')
            print('Installing Packages...\n')
            install.install_cmd(principal_package)
            if packages:
                install.multi_install_cmd(packages)
                print('Start Dropbox from your session... \n')
                exit(0)


if __name__ == '__main__':
    print(('Running Dropbox Installer\n    Version: {}'.format(__version__)))
    try:
        try:
            if sys.argv[1] and sys.argv[2]:
                MyOS = sys.argv[1].lower()
                OSName = sys.argv[2].lower()
                if check_root(MyOS, OSName):
                    if is_connected():
                        if validingOSVersion(ValidOSVersion, MyOS, OSName):
                            install_app(MyOS, OSName)
        except IndexError:
            help_app('You should indicate you OS and OS Name')
    except KeyboardInterrupt:
        print('\nExit by the user by pressing "Ctrl + c"...\n')
