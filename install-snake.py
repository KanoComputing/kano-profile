#! /usr/bin/env python

import os
import subprocess


def run(cmd):
    return subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()


def run_term_on_error(cmd):
    o, e = run(cmd)
    if e:
        print e
        quit(1)


filepath = os.path.realpath(__file__)
dirpath = os.path.dirname(filepath)
os.chdir(dirpath)


snake_python = os.path.abspath('snake')
run_term_on_error('rm -rf /usr/share/make-snake')
run_term_on_error('ln -s {} /usr/share/make-snake'.format(snake_python))

snake_editor = os.path.abspath('snake-editor')
run_term_on_error('rm -rf /usr/share/make-snake/snake-editor')
run_term_on_error('ln -s {} /usr/share/make-snake/'.format(snake_editor))

binfiles = ['make-snake', 'make-video', 'youtube']
for binfile in binfiles:
    fullpath = os.path.abspath('bin/' + binfile)
    run_term_on_error('rm -rf /usr/bin/' + binfile)
    run_term_on_error('ln -s {} /usr/bin'.format(fullpath))

kanoprofile_python = os.path.abspath('kanoprofile')
run_term_on_error('rm -rf /usr/lib/python2.7/kanoprofile')
run_term_on_error('ln -s {} /usr/lib/python2.7'.format(kanoprofile_python))

kanoprofile_cli = os.path.abspath('kano-profile-cli/kano-profile-cli')
run_term_on_error('rm -rf /usr/bin/kano-profile-cli')
run_term_on_error('ln -s {} /usr/bin'.format(kanoprofile_cli))

yt = os.path.abspath('yt')
run_term_on_error('rm -rf /usr/lib/pyshared/yt')
run_term_on_error('ln -s {} /usr/lib/pyshared/yt'.format(yt))
