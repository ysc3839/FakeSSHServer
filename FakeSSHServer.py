#!/usr/bin/env python

from binascii import hexlify
import os
import socket
import sys
import threading
import traceback
import SocketServer
import logging
import random

import paramiko
from paramiko.py3compat import b, u

PORT = 22
LOG_FILE = 'fakessh.log'
#RETURN_MESSAGE = 'no way to hack into my server noob!\r\n'
RETURN_MESSAGE = None
DENY_ALL = True
PR_ALLOW = 20

# setup logging
logger = logging.getLogger("access.log")
logger.setLevel(logging.INFO)
lh = logging.FileHandler(LOG_FILE)
logger.addHandler(lh)
#paramiko.util.log_to_file('ssh_server.log')

host_key = paramiko.RSAKey(filename='test_rsa.key')
#host_key = paramiko.DSSKey(filename='test_dss.key')

print('Read key: ' + u(hexlify(host_key.get_fingerprint())))


class Server (paramiko.ServerInterface):

    def __init__(self, client_address):
        self.event = threading.Event()
        self.client_address = client_address

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        logger.info('IP: %s, User: %s, Password: %s' % (self.client_address[0], username, password))
        if DENY_ALL == True:
            return paramiko.AUTH_FAILED
        random.seed()
        rand = random.randint(0, 99)
        if (username == 'root') and (rand > (100 - PR_ALLOW)):
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    def check_channel_shell_request(self, channel):
        self.event.set()
        return True

    def check_channel_pty_request(self, channel, term, width, height, pixelwidth,
                                  pixelheight, modes):
        return True

class SSHHandler(SocketServer.StreamRequestHandler):
    def handle(self):
        try:
            t = paramiko.Transport(self.connection)
            t.add_server_key(host_key)
            server = Server(self.client_address)
            try:
                t.start_server(server=server)
            except paramiko.SSHException:
                print('*** SSH negotiation failed.')
                return

            # wait for auth
            chan = t.accept(20)
            if chan is None:
                #print('*** No channel.')
                t.close()
                return
            #print('Authenticated!')

            server.event.wait(10)
            if not server.event.is_set():
                #print('*** Client never asked for a shell.')
                t.close()
                return

            if RETURN_MESSAGE != None:
                chan.send(RETURN_MESSAGE)
            chan.close()

        except Exception as e:
            print('*** Caught exception: ' + str(e.__class__) + ': ' + str(e))
            traceback.print_exc()
        finally:
            try:
                t.close()
            except:
                pass

sshserver = SocketServer.ThreadingTCPServer(("0.0.0.0", PORT), SSHHandler)
sshserver.serve_forever()
