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
## License

Copyright (c) 2013 EBU. All rights reserved.

The project radiovis-html5player has been created by the EBU. It consists of software that dynamically links to different existing open source code repositories. It does not incorporate or combines components through copying them (or parts) into the target application and producing a merged object file that is a stand-alone executable. The radiovis-html5player code and documentation is made available by the EBU on the https://github.com/ebu/radiovis-html5player website, under the terms and conditions of the EUPL (European Union Public Licence) v. 1.1

### Latest version of EUPL

The EUPL licence v1.1 is available in 22 languages: 22-07-2013, https://joinup.ec.europa.eu/software/page/eupl/licence-eupl
Whenever a newer version is officially adopted, that version shall apply, and in case of doubt, the English version shall prevail.

### Exceptions

Contact the EBU (Michael Barroco, barroco@ebu.ch) if you are in need of special licence terms/ distribution rights different from the EU Public Licence.

### Disclaimer

For the avoidance of doubt, and in addition to Articles 7 and 8 of the EUPL, this software is provided 'as-is', without any express or implied warranty. In no event will the EBU or the authors be held liable for any damages arising from the use of this software. Furthermore the EBU cannot be held responsible for any use by third parties using the software, for example with a view to produce / manipulate illegal content or not paying for the use of licensed codec's or any other illegal use.

## Project lead

* Michael Barroco [@barroco](https://github.com/barroco)

## Core contributors

* Maximilien Cuony [@the-glu](https://github.com/the-glu)
