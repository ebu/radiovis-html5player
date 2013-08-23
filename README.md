radiovis-html5player
====================

RadioVis Player using WebSocket

## General architecture

The system is divided in two part: The server and the client. The server is a simple process running on any machine and the client a set of javascript/css files to be included in any part. You can use them in any setup, no PHP or other dynamic web server is needed.

## Installation

### Server

The websocket server is located in websocketserver. To run it, just use `python server.py`. It's possible to change the listening port and ip at the beginning of the file.

The websocket server is written in python. He needs the following packages:

* ws4py
* gevent
* dnspython

You can use `pip install ws4py gevent dnspython` to install them.

### Client

The client part include a javascript file (_radiovis-html5player.js_) and a css file (_radiovis-html5player.css_). You have to include jquery first.

You can use `$('#an_id').radiovisplayer('/topic/bla/bla', ip, port);` to load the player inside a DOM element. The optional parameters ip and port can be used to override defaults parameters (the current host and 8777) to the websocket server.

The file _index.html_ contains a sample implementation.

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