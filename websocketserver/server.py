#!/usr/bin/env python
# -*- coding: utf-8 -*-

SERVER_IP = '0.0.0.0'
SERVER_PORT = 8777
STATS_GAUGE_APPNAME = 'app.html5player'

from gevent import monkey; monkey.patch_all()

from ws4py.websocket import WebSocket

import asyncio
#import WebSocket
import dns.resolver
import time
import socket
import requests
import pycurl
#from statsd import StatsClient
#import statsd

from gevent.lock import RLock

#class Stats():
#    """The class to handle stats"""
#
#    def __init__(self):
#        #self.statsd = StatsClient();
#        self.gauge = statsd.gauge(STATS_GAUGE_APPNAME, 1)
#
#        self.topic_list = {}
#
#        self.lock = RLock()
#
#    def update_stats(self):
#        """Update statsd stats"""
#
#        total = 0
#
#        with self.lock:
#            for topic in self.topic_list:
#                self.gauge.send('topic.' + '.'.join(topic.split('/')), self.topic_list[topic])
#                total += self.topic_list[topic]
#
#        self.gauge.send('nb_clients', total)
#
#
#
#    def new_client(self, topic):
#        """Register a new client on a topic"""
#
#        with self.lock:
#            if topic not in self.topic_list:
#                self.topic_list[topic] = 0
#
#            self.topic_list[topic] += 1
#
#        self.update_stats()
#
#    def remove_client(self, topic):
#        """Unregister a client on a topic"""
#
#        with self.lock:
#            self.topic_list[topic] -= 1
#
#        self.update_stats()

#stats = Stats()


class RadioVisWebSocket(WebSocket):

    def __init__(self, sock, protocols=None, extensions=None, environ=None, heartbeat_freq=None):
        WebSocket.__init__(self, sock, protocols, extensions, environ, heartbeat_freq)

        self.topic = environ['PATH_INFO']
        self.stompsocket = None

    #def send(data, flags=0):
    #    b = bytearray()
    #    b.extend(data.encode())
    #    super().send(b, flags) 

    def closed(self, code, reason=None):
        if self.stompsocket:
            self.stompsocket.close()

        #stats.remove_client(self.topic)

    def opened(self):
        """Called when a client is connected: send initial message"""

        #stats.new_client(self.topic)

        if self.topic[:7] != '/topic/':
            self.send(b"RADIOVISWEBSOCKET:ERROR\x00")            
        else:

            # Do the query for radiodns servers
            dns_entry = '.'.join(self.topic[7:].split('/')[::-1]) + '.radiodns.org'

            # Special case with *
            if dns_entry[0] == '*':
                dns_entry = '10800' + dns_entry[1:]

            
            # Find radiodns servers
            ns = str(dns.resolver.resolve('radiodns.org', 'NS')[0])
            #print(ns)
            #return
            ip = str(dns.resolver.resolve(ns, 'A')[0])

            # Build a resolver using radiodns.org nameserver, timeout of 2, to be sure to have the latested FQDN
            resolver = dns.resolver.Resolver()
            resolver.lifetime = 2  # Timeout of 2
            resolver.nameservers = [ip]  # Use radiodns.org servers
            
            print("DNS ENTRY: " + dns_entry)
            try:
                fqdn = str(resolver.resolve(dns_entry, 'CNAME')[0])
            except:
                self.send(b"RADIOVISWEBSOCKET:NOFQDN\x00")
                time.sleep(1)
                self.close()
                return

            # Build resolver for others queries using local nameserver
            resolver = dns.resolver.Resolver()
            resolver.lifetime = 2  # Timeout of 2
            if self.download_spi_file('_radioepg._tcp.' + fqdn):
                self.download_spi_file('_radiospi._tcp.' + fqdn)
            #response = requests.get()
            #print(response)
            
            try:
                vis = str(resolver.resolve('_radiovis._tcp.' + fqdn, 'SRV')[0])
            except:
                self.send(b"RADIOVISWEBSOCKET:NOVIS\x00")
                time.sleep(1)
                self.close()
                return
                
            print("VIS CONNECT...")
            print(vis)
            (_, _, port, ip) = vis.split()
            
            ip = ip[:-1]
            # Connect to radiovis server
            self.stompsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #self.stompsocket.connect((ip, int(port)))
            try:
                print(f"Connecting to {ip}:{port}")
                self.stompsocket.connect((ip, int(port)))
            except socket.error as msg:
                raise socket.error(f"Failed to connect: {msg}")
            
            print(f"Successfully connected to {ip}:{port}")
            
            self.incomingData = ''

            def get_one_frame():
                """Return one stomp frame"""

                while not "\x00" in self.incomingData:
                    data = self.stompsocket.recv(1024)
                    print ("DATA")
                    print (data)
                    if not data:
                       print ("Nothing received") 
                       return None
                    else:
                       self.incomingData += data.decode("utf8")
                    print("IDATA")
                    print (self.incomingData)

                # Get only one frame
                splited_data = self.incomingData.split('\x00', 1)

                # Save the rest for later
                self.incomingData = splited_data[1]

                return splited_data[0]
            print(self.topic + " CONNECT...")
            self.stompsocket.send(b'CONNECT\n\n\x00')

            result = get_one_frame()
            print("RESULT")
            print(result)
            if not result:
                self.send(b"RADIOVISWEBSOCKET:ERROR:Disconnected when connect...\x00")
                time.sleep(1)
                self.close()
                return

            if result[:9] != 'CONNECTED':
                self.send(b"RADIOVISWEBSOCKET:ERROR:Not connected...\x00")
                time.sleep(1)
                self.close()
                return

            # Send ack to the client
            self.send(b"RADIOVISWEBSOCKET:HELLO\x00")

            # We're connected. Now we subscrible to the two topics
            bstrImg = 'SUBSCRIBE\ndestination:' + self.topic + '/image\n\n\x00'
            bstrTxt = 'SUBSCRIBE\ndestination:' + self.topic + '/text\n\n\x00'
            
            self.stompsocket.send(bstrImg.encode())
            self.stompsocket.send(bstrTxt.encode())

            # Now just wait for messages
            while True:
                result = get_one_frame()

                if not result:
                    self.send(b"RADIOVISWEBSOCKET:ERROR:Lost connection...\x00")
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
    
    def download_spi_file(self, url):
        resolver = dns.resolver.Resolver()
        resolver.lifetime = 2  # Timeout of 2
            
        try:
            epg = str(resolver.resolve(url, 'SRV')[0])
        except:
            self.send(b"RADIOVISWEBSOCKET:NOEPG\x00")
            #time.sleep(1)
            #self.close()
            return 1
        print("EPG CONNECT...")
        print(epg)
        (_, _, _, domain) = epg.split()
        url = "http://" + domain[:-1] + "/radiodns/spi/3.1/SI.xml"
        filename = "SI" + self.topic.replace("/topic", "").replace("/", "_") + ".xml"
        with open(filename, "wb") as fp:
            curl = pycurl.Curl()
            curl.setopt(pycurl.URL, url)
            curl.setopt(pycurl.WRITEDATA, fp)
            curl.setopt(pycurl.FOLLOWLOCATION, 1)
            curl.perform()
            curl.close()
            
        url = "http://" + domain[:-1] + "/radiodns/spi/3.1/20230308_PI.xml"
        filename = "PI" + self.topic.replace("/topic", "").replace("/", "_") + ".xml"
        with open(filename, "wb") as fp:
            curl = pycurl.Curl()
            curl.setopt(pycurl.URL, url)
            curl.setopt(pycurl.WRITEDATA, fp)
            curl.setopt(pycurl.FOLLOWLOCATION, 1)
            curl.perform()
            curl.close()
        return 0
                
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
    server.stop()
