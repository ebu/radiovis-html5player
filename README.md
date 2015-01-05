radiovis-html5player
====================

RadioVis Player using WebSocket

## General architecture

The system is divided in two part: The server and the client. The server is a simple process running on any machine and the client a set of javascript/css files to be included in any part. You can use them in any setup, no PHP or other dynamic web server is needed.

## Installation

### Server

The websocket server is located in websocketserver. To run it, just use `python server.py`. It's possible to change the listening port and ip at the beginning of the file.

The websocket server is written in python. He needs the following packages:

* ws4py==0.3.0-beta
* gevent
* dnspython
* python-statsd (BSD license)

You can use `pip install ws4py==0.3.0-beta gevent dnspython python-statsd ` to install them.


The server use statsd to send some stats about the number of connections. You can setup a local statsd server to collect them.

### Client

The client part include a javascript file (_radiovis-html5player.js_) and a css file (_radiovis-html5player.css_). You have to include jquery first.

You can use `$('#an_id').radiovisplayer('/topic/bla/bla', ip, port);` to load the player inside a DOM element. The optional parameters ip and port can be used to override defaults parameters (the current host and 8777) to the websocket server.

The file _index.html_ contains a sample implementation.

## Running HTML Player

### HTTP Server

Run the HTTP Server to serve the `index.html` using SimpleHTTPServer with python.
```
cd website
python -m SimpleHTTPServer 8080
```

If you want to run the HTTP Server using supervisord use the following commands.
```
cd website

# Start the Server
supervisord -c supervisord-simpleserver.conf

# Stop the Server
supervisorctl -c supervisord-simpleserver.conf stop simpleserver
supervisorctl -c supervisord-simpleserver.conf shutdown

# Restart the Server
supervisorctl -c supervisord-simpleserver.conf restart simpleserver
```

### WebSocket Server

Run the Websocket Server using the following commands
```
python server.py
```

If you want to run the Websocket Server using supervisord use the following commands.
```
cd websocketserver/

# Start the Server
supervisord -c supervisord-websocketserver.conf

# Stop the Server
supervisorctl -c supervisord-websocketserver.conf stop websocketserver
supervisorctl -c supervisord-websocketserver.conf shutdown

# Restart the Server
supervisorctl -c supervisord-websocketserver.conf restart websocketserver
```

## License (BSD)

Copyright (c) 2013, EBU
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

3. Neither the name of the EBU nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


## Core contributors

* Maximilien Cuony [@the-glu](https://github.com/the-glu)
* Michael Barroco [@barroco](https://github.com/barroco)
