#!/usr/bin/env python
# -*- coding: utf-8 -*-

SERVER_IP = '0.0.0.0'
SERVER_PORT = 8777

from gevent import monkey; monkey.patch_all()

from ws4py.websocket import WebSocket
import dns.resolver
import time
import socket

class RadioVisWebSocket(WebSocket):

    def __init__(self, sock, protocols=None, extensions=None, environ=None, heartbeat_freq=None):
        WebSocket.__init__(self, sock, protocols, extensions, environ, heartbeat_freq)

        self.topic = environ['PATH_INFO']
        self.stompsocket = None

    def closed(self, code, reason=None):
        if self.stompsocket:
            self.stompsocket.close()

    def opened(self):
        """Called when a client is connected: send initial message"""
        if self.topic[:7] != '/topic/':
            self.send("RADIOVISWEBSOCKET:ERROR\x00")            
        else:

            # Do the query for radiodns servers
            dns_entry = '.'.join(self.topic[7:].split('/')[::-1]) + '.radiodns.org'

            # Special case with *
            if dns_entry[0] == '*':
                dns_entry = '10800' + dns_entry[1:]

            
            # Find radiodns servers
            ns = str(dns.resolver.query('radiodns.org', 'NS')[0])
            ip = str(dns.resolver.query(ns, 'A')[0])

            # Build a resolver using radiodns.org nameserver, timeout of 2, to be sure to have the latested FQDN
            resolver = dns.resolver.Resolver()
            resolver.lifetime = 2  # Timeout of 2
            resolver.nameservers = [ip]  # Use radiodns.org servers

            try:
                fqdn = str(resolver.query(dns_entry, 'CNAME')[0])
            except:
                self.send("RADIOVISWEBSOCKET:NOFQDN\x00")
                time.sleep(1)
                self.close()
                return

            # Build resolver for others queries using local nameserver
            resolver = dns.resolver.Resolver()
            resolver.lifetime = 2  # Timeout of 2

            try:
                vis = str(resolver.query('_radiovis._tcp.' + fqdn, 'SRV')[0])
            except:
                self.send("RADIOVISWEBSOCKET:NOVIS\x00")
                time.sleep(1)
                self.close()
                return

            (_, _, port, ip) = vis.split()

            # Connect to radiovis server
            self.stompsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.stompsocket.connect((ip, int(port)))

            self.incomingData = ''

            def get_one_frame():
                """Return one stomp frame"""

                while not "\x00" in self.incomingData:
                    data = self.stompsocket.recv(1024)
                    if not data:
                       return None
                    else:
                       self.incomingData += data

                # Get only one frame
                splited_data = self.incomingData.split('\x00', 1)

                # Save the rest for later
                self.incomingData = splited_data[1]

                return splited_data[0]

            self.stompsocket.send('CONNECT\n\n\x00')

            result = get_one_frame()

            if not result:
                self.send("RADIOVISWEBSOCKET:ERROR:Disconnected when connect...\x00")
                time.sleep(1)
                self.close()
                return

            if result[:9] != 'CONNECTED':
                self.send("RADIOVISWEBSOCKET:ERROR:Not connected...\x00")
                time.sleep(1)
                self.close()
                return

            # Send ack to the client
            self.send("RADIOVISWEBSOCKET:HELLO\x00")

            # We're connected. Now we subscrible to the two topics
            self.stompsocket.send('SUBSCRIBE\ndestination:' + self.topic + '/image\n\n\x00')
            self.stompsocket.send('SUBSCRIBE\ndestination:' + self.topic + '/text\n\n\x00')

            # Now just wait for messages
            while True:
                result = get_one_frame()

                if not result:
                    self.send("RADIOVISWEBSOCKET:ERROR:Lost connection...\x00")
                    time.sleep(1)
                    self.close()
                    return

                # Just forward the frame
                try:
                    self.send(result)
                except:
                    # Client is closed
                    self.close()
                    return



    def received_message(self, message):
        """Called when a client send a message."""

        # The client shouldn't send message
        self.send("RADIOVISWEBSOCKET:ERROR:Unexcepted message\x00")
        self.close()

from ws4py.server.geventserver import WebSocketWSGIApplication, WSGIServer

class WebSocketApplication(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.ws = WebSocketWSGIApplication(handler_cls=RadioVisWebSocket)

    def __call__(self, environ, start_response):
        return self.ws(environ, start_response)


    
server = WSGIServer((SERVER_IP, SERVER_PORT), WebSocketApplication(SERVER_IP, SERVER_PORT))


try:
    server.serve_forever()
except KeyboardInterrupt:
    server.server_close()
