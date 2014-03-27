# -*- coding: utf-8 -*-

import os
import ConfigParser
import time
import subprocess

import alfred


def b2d_exec(command, args=None, binary_path='/usr/local/bin/boot2docker'):
    if not args:
        args = []
    cmdline = ' '.join([binary_path, command] + args)
    ret = subprocess.check_output('{}; exit 0'.format(cmdline), shell=True)
    return ret


class Boot2dockerWorkflow(alfred.AlfredWorkflow):
    _reserved_words = []

    def __init__(self, max_results=20):
        self.max_results = max_results

    def command_autocomplete_iter(self, query):
        status = self.status
        if status == 'unknown':
            yield self.item(title='Boot2Docker is in an unknown state',
                            description='Try to run boot2docker in your '
                            'terminal to investigate', ignore=True)
        elif status == 'running':
            yield self.item(title='stop', description='Stop Boot2Docker',
                            autocomplete=True, arg='stop', match=query)
        elif status == 'stopped':
            yield self.item(title='start', description='Start Boot2Docker',
                            autocomplete=True, arg='start', match=query)

    def do_command_autocomplete(self, query):
        self.write_items(self.command_autocomplete_iter(query))

    def do_command_notify(self, query=None):
        if query == 'start':
            self.write_text('Starting... you will get notified when done')
        elif query == 'stop':
            self.write_text('Stopping... you will get notified when done')

    def do_command_run(self, query=None):
        command = query
        return self.route_action(command, '')

    def do_start(self, query=None):
        if self.status == 'running':
            return
        ret = b2d_exec('start')
        if ret.find('Started.') > -1:
            self.write_text('Boot2Docker is started.')
        else:
            self.write_text('An error has occured when starting.\n'
                            'please run boot2docker from command line')

    def do_stop(self, query=None):
        if self.status != 'running':
            return
        ret = b2d_exec('stop')
        if ret.find('Shutting down') > -1:
            self.write('Boot2Docker is stopped')
        elif ret.find('is not running.') > -1:
            self.write('Boot2Docker was not running')
        else:
            self.write('Error while trying to stop instance')

    @property
    def status(self):
        ret = b2d_exec('status')
        if ret.find('running') > -1:
            return 'running'
        elif ret.find('stopped') > -1:
            return 'stopped'
        else:
            return 'unknown'

    def do_status(self, query=None):
        status = self.status
        if status == 'running':
            self.write_text('Boot2Docker is running')
        elif status == 'stopped':
            self.write_text('Boot2Docker is stopped')
        else:
            self.write_text('Boot2Docker is in an unknown state')



def main(action, query):
    boot2docker = Boot2dockerWorkflow()
    boot2docker.route_action(action, query)


if __name__ == "__main__":
    main(action=alfred.args()[0], query=alfred.args()[1])
