# FakeSSHServer
A fake ssh server written in Python. Uses Paramiko.

# Install
Install Python and [Paramiko](http://www.paramiko.org/installing.html). Then run FakeSSHServer.py.

# Config
```
PORT = 22
LOG_FILE = 'fakessh.log'
#RETURN_MESSAGE = 'no way to hack into my server noob!\r\n'
RETURN_MESSAGE = None
DENY_ALL = True
PR_ALLOW = 20
```

`PORT`: Listen port.

`LOG_FILE`: Log file.

`RETURN_MESSAGE`: The message when user logined in.

`DENY_ALL`: True = Deny all access.

`PR_ALLOW`: The probability a user allowed log in.
