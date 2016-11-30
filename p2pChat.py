#!/usr/bin/env python 
import subprocess
import threading
import time
import re
import socket
import sys
import select
syncFlag=1
serverFlag=1

# avahi-browse -p -rt _workstation._tcp -> get active users
class Peer:
    def __init__(self):
        self.ip_list=[];
        #subprocess.call(['./boot_script']), boot script will be called in boottime
        time.sleep(5)
        #self.initializeBatman(), bootscript will be called in boot
        self.setSelfIp()
      
        #self.chat_proc=subprocess.Popen(['/bin/bash'],shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        #self.t_listen1=threading.Thread(target=self.startListening1)
        #self.t_listen1.setDaemon(True)
        #self.t_listen1.start()
        #self.t_listen2=threading.Thread(target=self.startListening2)
        #self.t_listen2.setDaemon(True)
        #self.t_listen2.start()

    def batctl_o(self):
        prc=subprocess.Popen(['/bin/bash'],shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self.write(prc, "sudo batctl o\n")
        print prc.communicate()
        
    def read(self, subpr):
        print subpr.stdout.readline()

    def write(self,subpr,command):
        subpr.stdin.write(command)      

    def initializeBatman(self):
        print "Initializing...\n"
        self.batman_proc=subprocess.Popen(['/bin/bash'],shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self.write(self.batman_proc,'sudo modprobe batman-adv\n')
        self.write(self.batman_proc,'sudo ip link set up dev eth0\n')
        self.write(self.batman_proc,'sudo ip link set mtu 1532 dev wlan0\n')
        self.write(self.batman_proc,'sudo iwconfig wlan0 mode ad-hoc essid ege-mesh ap 02:12:34:56:78:9A channel 1\n')
        self.write(self.batman_proc,'sudo batctl if add wlan0\n')
        self.write(self.batman_proc,'sudo ip link set up dev wlan0\n')
        self.write(self.batman_proc,'sudo ip link set up dev bat0\n')
        time.sleep(5)
        print "Getting ip"
        self.write(self.batman_proc,'sudo avahi-autoipd -D bat0 \n')
        time.sleep(5)
        
    def setSelfIp(self):
        ip_proc=subprocess.Popen(['/bin/bash'],shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        ip_proc.stdin.write("ifconfig bat0:avahi | grep 'inet ' | awk -F'[: ]+' '{ print $4 }'\n")
        self.ip= ip_proc.stdout.readline().replace("\n", "")
        print "Your IP: " + self.ip + "\n"
        
    def initializeNmap(self):
        print "NMAP THREAD STARTED\n"
        self.nmap_proc=subprocess.Popen(['/bin/bash'],shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self.write(self.nmap_proc, "sudo nmap -sP -n 169.254.0.0/16 -oG - | awk '/Up$/{print $2}'\n")
        while True:
            output=self.read(self.nmap_proc)
            if output!='':
                self.ip_list.append()
                print "nmap: new message\n"

    def getIPList(self):
        print "DISCOVERING HOSTS\n"
        avahi_proc=subprocess.Popen(['/bin/bash'],shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self.write(avahi_proc,"avahi-browse -p -rt _workstation._tcp | awk -F ';' '/169.254/ {print $8}'\n")
        output = avahi_proc.communicate()
        
        output=output[0]
        self.ip_list=output.split('\n')
        self.ip_list = filter(None, self.ip_list)

        for i in self.ip_list:
            if(i!=self.ip):
                command="batctl traceroute "+i+" | wc -l"
                avahi_proc2=subprocess.Popen(['/bin/bash'],shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                self.write(avahi_proc2, command)
                hopcount=avahi_proc2.communicate()
                hopcount=hopcount[0]
                hopcount=re.findall('\d+',hopcount)
                hopcount=str(int(hopcount[0])-1)
                print i+"->"+hopcount+" hops away"
            else:
                print i+"-> self"
                
        
    def startListening1(self):
        print "STARTED LISTENING FOR CHATS\n"
        self.chat_proc.stdin.write("sudo nc -l -p 6663\n")
        print "Exit start listening 1\n"
        
        

    def startListening2(self):
        print "READING FROM LISTEN SOCKET\n"
        while True:
            line = self.chat_proc.stdout.readline()
            print line

    def startWritingToListenSocket(self):
        print "YOU CAN START WRITING\n"
        usr_input=raw_input("You:")
        while usr_input!="exit":
            print "Enter Socket"
            self.chat_proc.stdin.write(self.ip+": "+usr_input+"\n")
            print "write done"
            usr_input=raw_input("You:")

  
    def startListeningSocket(self):
        s = socket.socket()
        host = socket.gethostname()
        port = 12345
        s.bind((host, port))
        print host
        s.listen(5)
        print "Listening"
        while True:
            c, addr = s.accept()
            print addr+": "+s.recv(1024)
            c.send('Received')
            c.close()

    def startPeerMode(self):
        self.t_listen3=threading.Thread(target=self.startWritingToListenSocket)
        self.t_listen3.start()
        self.t_listen3.join()
        print "Joined"

    def chat_peer(self, other_peer): #send one message each time
        command="sudo nc "+other_peer+" 6000\n"
        self.chat_peer_proc=subprocess.Popen(['/bin/bash'],shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        thread0=threading.Thread(target=self.chat_peer_proc.stdin.write,args=(command,))
        thread0.setDaemon(True)
        thread0.start()
        thread=threading.Thread(target=self.listen_chat)
        thread.setDaemon(True)
        thread.start()
        print "YOU CAN START WRITING\n"
        usr_input=raw_input("You:")
        while usr_input!="exit":
            print "Enter CHATPEER socket"
            self.chat_peer_proc.stdin.write(self.ip+": "+usr_input+"\n")
            print "write CHATPEER done"
            usr_input=raw_input("You:")

    def listen_chat(self):
        print "READING FROM CHAT SOCKET\n"
        while True:
            line = self.chat_peer_proc.stdout.readline()
            print line

class serverSide:
    def __init__(self, ip):
        
        self.host=ip
        self.port=6111
        self.backlog=5
        self.size=1024
        self.server=None
        self.threads= []

    def openSocket(self):
        try:
            self.server= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind((self.host, self.port))
            self.server.listen(5)
            print "Socket is opened and listening"
        except socket.error, (value, message):
            if self.server:
                self.server.close()
            print "Could not open the socket: "+ message
            sys.exit(1)

    def run(self):
        global serverFlag
        serverFlag=1
        self.openSocket()
        input=[self.server, sys.stdin]
        running=1
        print "Server Side Is Listening"
        while running and serverFlag:
            try:
                inputready, outputready, exceptready= select.select(input, [], [])

                for s in inputready:
                    if s==self.server:
                        (client,address)= self.server.accept()
                        print "New connection"
                        c=clientSide((client,address))
                        c.start()
                        self.threads.append(c)
                        c2=clientSide_writer((client,address), self.host)
                        c2.start()
                        self.threads.append(c2)
            except KeyboardInterrupt:
                break
            
        self.server.close() 
        for c in self.threads:
            c.join()

        print "SERVER SIDE RUN ENDED"


class clientSide(threading.Thread):
    def __init__(self, (client, address)):
        threading.Thread.__init__(self)
        self.client=client
        self.address= address
        self.size=1024

    def run(self):
        global serverFlag
        global syncFlag
        syncFlag=1
        running=1
        print "Clientside run"
        while running and syncFlag:
            data=self.client.recv(self.size)
            if data:
                print data
            else:
                self.client.close()
                running=0
        print "other thread: i see syncFlag is 0, quit"
        serverFlag=0
        syncFlag=0

class clientSide_writer(threading.Thread):
    def __init__(self, (client, address), ip):
        threading.Thread.__init__(self)
        self.client=client
        self.address= address
        self.size=1024
        self.ip=ip

    def run(self):
        global syncFlag
        print "Clientside_Writer run"
        running=1
        user_input=raw_input(":")
        while(running and user_input!="quit" and syncFlag):
            try:
                self.client.send(self.ip+": "+user_input+"\n")
                print "sent"
                user_input=raw_input(":")
            except socket.error:
                print "writer quit"
                syncFlag=0
                print "syncflag: "+str(syncFlag)
                self.client.close()
                running=0
                break
        print "quit "
        syncFlag=0
        running=0

class cliChat:
    def __init__(self, ip):
        self.host=ip
        self.port=6111
        self.threads= []
        self.sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address=(self.host, self.port)
        

    def run(self):
        global syncFlag
        syncFlag=1
        running=1
        try:
            self.sock.connect(self.server_address)
        except socket.error:
            print "Client is not available"
            syncFlag=0
            return
        r=readCliChat(self.sock)
        r.start()

        while running:
            try:
                self.sock.sendall(raw_input(":"))
                
            except KeyboardInterrupt:
                syncFlag=0
                break
            except socket.error:
                syncFlag=0
                break
            
        self.sock.close() 
        for c in self.threads:
            c.join()

        print "SERVER SIDE RUN ENDED"        
        
        
class readCliChat(threading.Thread):
    def __init__(self, socket):
        threading.Thread.__init__(self)
        self.socket=socket
        self.size=1024

    def run(self):
        global serverFlag
        global syncFlag
        syncFlag=1
        running=1
        print "read cli chat running"
        while running and syncFlag:
            data=self.socket.recv(self.size)
            if data:
                print data
            else:
                running=0
        print "other thread: i see syncFlag is 0, quit"
        serverFlag=0
        syncFlag=0  

class Server: 
    def __init__(self, ip): 
        self.host = ''
        self.port = 6113 
        self.backlog = 5 
        self.size = 1024 
        self.server = ip 
        self.threads = [] 

    def open_socket(self): 
        try: 
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
            self.server.bind((self.host,self.port)) 
            self.server.listen(5) 
        except socket.error, (value,message): 
            if self.server: 
                self.server.close() 
            print "Could not open socket: " + message 
            sys.exit(1) 

    def run(self): 
        self.open_socket() 
        input = [self.server,sys.stdin] 
        running = 1
        print "Echo server waiting."
        while running: 
            inputready,outputready,exceptready = select.select(input,[],[]) 

            for s in inputready: 

                if s == self.server: 
                    # handle the server socket 
                    c = Client(self.server.accept()) 
                    c.start() 
                    self.threads.append(c) 

                elif s == sys.stdin: 
                    # handle standard input 
                    junk = sys.stdin.readline() 
                    running = 0 

        # close all threads 

        self.server.close() 
        for c in self.threads: 
            c.join() 

class Client(threading.Thread): 
    def __init__(self,(client,address)): 
        threading.Thread.__init__(self) 
        self.client = client 
        self.address = address 
        self.size = 1024 

    def run(self): 
        running = 1 
        while running: 
            data = self.client.recv(self.size) 
            if data: 
                self.client.send("Elevator:"+data+" received.") 
            else: 
                self.client.close() 
                running = 0 







p=Peer()            
print "Enter ls to get the list of active users\n"
print "Enter chat to send message to one of the active users\n"
print "Enter quit to quit\n"

user_input=raw_input("Select Mode\n")

while(user_input!="quit"):
    if(user_input=="listen"):
        s=serverSide(p.ip)
        s.run()
    elif(user_input=="ls"):
        p.getIPList()
    elif(user_input=="chat"):
        number=int(raw_input("Which one\n"))
        other_peer=p.ip_list[number]
        print "OTHER PEER: "+other_peer
        c=cliChat(other_peer)
        c.run()
    elif(user_input=="hw"):
        p.batctl_o()
    elif(user_input=="echo"):
        e=Server(p.ip)
        e.run()
        
        
    user_input=raw_input("Select Mode\n")
        
    
sys.exit()







    

        
