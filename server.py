import socket
import threading
import pickle
import os
import sys
from abc import ABC, abstractmethod
import functools

import json

class Group2(ABC):
    @abstractmethod
    def isAdmin(self) -> bool:
        pass
    
    @abstractmethod
    def disconnect(self):
        pass
        
    @abstractmethod
    def disconnectAll(self):
        pass
    
    @abstractmethod
    def tryKick(self):
        pass
    
    @abstractmethod
    def connect(self) -> int:
        pass
    
    @abstractmethod
    def sendMessage(self) -> bool:
        pass
    
    @abstractmethod
    def approveRequest(self):
        pass
    
    @abstractmethod
    def viewRequests(self):
        pass
    
    @abstractmethod
    def printMessageHistory(self):
        pass

class Server(ABC):
    @abstractmethod
    def handleConnection(self):
        pass
    
    @abstractmethod
    def startServer(self):
        pass
    
    @abstractmethod
    def listener(self):
        pass
    
    @abstractmethod
    def waitServerInput(self):
        pass
    
    @abstractmethod
    def stopServerConnection(self):
        pass
    
    @abstractmethod
    def waitUserInput(self):
        pass

class Group(Group2):
    def __init__(self,admin,client, name):
        self.admin = admin
        self.clients = {}
        self.allMembers = set()
        self.onlineMembers = set()
        self.joinRequests = set()
        self.waitClients = {}
        self.threads = {}
        self.name = name
        self.messageHistory = []

        # self.clients[admin] = client
        self.allMembers.add(admin)
        # self.onlineMembers.add(admin)
        
    def isAdmin(self,username):
        if username == self.admin:
            return True
        else:
            return False
    
    def tryKick(self, requestUsername):
        print("do tryKick")
        if requestUsername == self.admin:
            self.clients[requestUsername].send(b"/proceedKick")
            usernameToKick = self.clients[requestUsername].recv(1024).decode("utf-8")
            # print(self.clients[requestUsername].recv(1024).decode("utf-8"))
            if usernameToKick in self.allMembers:
                self.allMembers.remove(usernameToKick)
                if usernameToKick in self.onlineMembers:
                    self.clients[usernameToKick].send(b"/disconnect")
                    print("sending disconnect ", usernameToKick)
                    # self.clients[usernameToKick].recv(1024)
                    self.onlineMembers.remove(usernameToKick)
                    self.clients[usernameToKick].close()
                    del self.clients[usernameToKick]
                print("User Removed:",usernameToKick,"| Group:",self.name)
                self.clients[requestUsername].send(b"The specified user is removed from the group.")
            else:
                self.clients[requestUsername].send(b"The user is not a member of this group.")
        else:
            self.clients[requestUsername].send(b"You're not an admin.")
        print("handleConnection FINISHED ", self.clients[requestUsername].recv(1024))
    
    def sendMessage(self, message, username):
        print("do sendMessage ", message," ",username)
        print("online members ", self.onlineMembers)
        for member in self.onlineMembers:
            if member != username and username != None:
                self.clients[member].send(bytes(username + ": " + message,"utf-8"))
            elif username == None:
                self.clients[member].send(bytes(message,"utf-8"))
            
    def printMessageHistory(self, username):
        self.clients[username].send(b"/loadMessageHistory")
        self.clients[username].recv(1024)
        self.clients[username].send(pickle.dumps(self.messageHistory))
        self.clients[username].recv(1024)
    
    def disconnect(self, username):
        print("do disconnect ", username)
        if username in self.onlineMembers:
            print("before send")
            try:
                self.clients[username].send(b"/disconnect")
            except Exception:
                print("client already disconnected")
            print("after send")
            self.clients[username].close()
            del self.clients[username]
        elif username in self.waitClients:
            try:
                self.waitClients[username].send(b"/disconnect")
            except Exception:
                print("client already disconnected")
            self.waitClients[username].close()
            del self.waitClients[username]
            print("disconnect non member")
    
    def disconnectAll(self):
        print("online mem ",self.onlineMembers," wait cl ", self.waitClients.keys())
        for username in list(self.onlineMembers):
            self.disconnect(username)
        for c in self.waitClients.values():
            c.send(b"/disconnect")
            c.close()
            del c
            print("disconnecting waiting client ", self.waitClients.keys())
    
    def connect(self, client, username) -> int:
        print("do connect")
        if username in self.allMembers:
            print("in allMembers")
            self.onlineMembers.add(username)
            self.clients[username] = client
            print("send /accepted")
            self.clients[username].send(b"/accepted")
            print("connect from user ",self.clients[username].recv(1024))#.decode("utf-8")
            self.printMessageHistory(username)
            self.clients[username].send(b"/sendCommands")
            self.clients[username].recv(1024)
            if username == self.admin:
                self.clients[username].send(b"/1(Requests), /2(Accept Request), /3(Disconnect), \n/4(All Members), /5(Online Members), /8(Kick Member)")
            else:
                self.clients[username].send(b"/3(Disconnect), /4(All Members), /5(Online Members)")
            self.clients[username].recv(1024)
            print("USER CONNECTED:",username,"| Group:",self.name)
            return 1
        else:
            print("not in allMembers")
            self.joinRequests.add(username)
            self.waitClients[username] = client
            self.sendMessage(username+" has requested to join the group.", None)
            client.send(b"/wait")
            print("Join Request:",username,"| Group:",self.name)
            print("finish connect non member ",client.recv(1024))
            return 2
    
    def approveRequest(self,username):
        print("do approveRequest")
        if self.isAdmin(username):
            self.clients[username].send(b"/proceedApprove")
            usernameToApprove = self.clients[username].recv(1024).decode("utf-8")
            print("proceedApprove username ", usernameToApprove)
            # self.clients[username].send(bytes("server: proceedApprove "+usernameToApprove,"utf-8"))
            if usernameToApprove in self.joinRequests:
                
                self.joinRequests.remove(usernameToApprove)
                self.allMembers.add(usernameToApprove)
                if usernameToApprove in self.waitClients:
                    self.waitClients[usernameToApprove].send(b"/attemptConnect")
                    del self.waitClients[usernameToApprove]
                print("Member Approved:",usernameToApprove,"| Group:",self.name)
                self.clients[username].send(b"User has been added to the group.")
                
            else:
                self.clients[username].send(b"The user has not requested to join.")
        else:
            self.clients[username].send(b"You're not an admin.")
        print("approveRequest FINISHED")
    
    def viewRequests(self, username):
        print("do viewRequests")
        if self.isAdmin(username):
            self.clients[username].send(b"/sendingData")
            self.clients[username].recv(1024)
            self.clients[username].send(pickle.dumps(self.joinRequests))
        else:
            self.clients[username].send(b"You're not an admin.")
        print("viewRequests FINISHED")
    
    # def save_data(self):
        # print("save_data ", self.joinRequests)
        # data = {
            # 'admin': self.admin,
            # 'allMembers': list(self.allMembers), 
            # 'joinRequests': list(self.joinRequests),  
            # 'name': self.name,
            # 'messageHistory': self.messageHistory
        # }
        # with open('group_data.json', 'w') as f:
            # json.dump(data, f, indent=4)
    
    # @classmethod
    # def load_data(cls):
        # try:
            # with open('group_data.json', 'r') as f:
                # data = json.load(f)
                # group = cls(
                    # admin=data['admin'],
                    # client=None,  # assume client is not serialized
                    # name=data['name']
                # )
                # group.allMembers = set(data['allMembers'])  
                # group.joinRequests = set(data['joinRequests']) 
                # group.messageHistory = data['messageHistory']
                # return group
        # except FileNotFoundError:
            # return None
    
class mainServer(Server):
    def __init__(self, ip, port):
        self.groups = {}
        self.state = {}
        self.stopServer = False
        
        self.listenSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listenSocket.bind((ip, int(port)))
        self.listenSocket.listen(10)
        
    def save_data(self):
        data = {}
        for group_name, group in self.groups.items():
            group_data = {
                'admin': group.admin,
                'allMembers': list(group.allMembers),  # convert set to list
                'name': group.name,
                'joinRequests': list(group.joinRequests),
                'messageHistory': group.messageHistory
            }
            data[group_name] = group_data
        with open('group_data.json', 'w') as f:
            json.dump(data, f, indent=4)
            
    def load_data(self):
        try:
            with open('group_data.json', 'r') as f:
                data = json.load(f)
                # server = cls(ip, port)
                groups = {}
                for group_name, group_data in data.items():
                    group = Group(
                        admin=group_data['admin'],
                        client=None,  # assume client is not serialized
                        name=group_data['name']
                    )
                    group.allMembers = set(group_data['allMembers'])  # convert list back to set
                    group.joinRequests = set(group_data['joinRequests'])
                    group.messageHistory = group_data['messageHistory']
                    groups[group_name] = group
                    print("load_data ", group_name)
                return groups
        except FileNotFoundError:
            return {}
        
    def handleConnection(self, client):
        print("start handleConnection")
        try:
            username = client.recv(1024).decode("utf-8")
            if username == "/emergencyDisconnect":
                print("user emergently disconnected before typing username")
                return
            client.send(b"/sendGroupname")
            groupname = client.recv(1024).decode("utf-8")
            if groupname == "/emergencyDisconnect":
                print("user emergently disconnected before typing groupname")
                return
        except Exception:
            return
        if groupname in self.groups.keys():
            print("wait clients", self.groups[groupname].waitClients)
            print("online members", self.groups[groupname].onlineMembers)
            if username in self.groups[groupname].onlineMembers or username in self.groups[groupname].waitClients.keys():
                print("username with taken trying to connect")
                client.send(b"/taken")
                return
        if groupname in self.groups:
            if self.groups[groupname].connect(client, username) == 1:
                print("connected, user already a member")
            else:
                print("user waiting for approval")
            self.groups[groupname].threads[username] = threading.Thread(target=self.waitUserInput, args=(client, username, groupname), daemon=True).start()
        else:
            self.groups[groupname] = Group(username, client, groupname)
            self.groups[groupname].clients[username] = client
            self.groups[groupname].onlineMembers.add(username)
            self.groups[groupname].threads[username] = threading.Thread(target=self.waitUserInput, args=(client, username, groupname), daemon=True).start()
            client.send(b"/adminReady")
            print("New Group:",groupname,"| Admin:",username)
        print("handleConnection FINISHED")
    
    def startServer(self):
        print("startServer")
        self.listenerThread = threading.Thread(target=self.listener, args=(self.listenSocket,), daemon=True).start()
        self.groups = self.load_data()
        self.waitServerInput()
        return True
    
    def listener(self, listenSocket):
        print("start listener")
        while not self.stopServer:
            client,_ = listenSocket.accept()
            threading.Thread(target=self.handleConnection, args=(client,), daemon=True).start()
    
    def waitServerInput(self):
        print("start waitServerInput")
        try:
            while True:
                serverInput = input()
                if serverInput == "stop" or serverInput == "clear_all_data":
                    c = False if serverInput == "clear_all_data" else True
                    print("stop server ", c)
                    self.stopServerConnection(c)
                    break
        except KeyboardInterrupt:
            print("stop server")
            self.stopServerConnection(True)
    
    def stopServerConnection(self, c):
        print("start stopServer")
        if c:
            self.save_data()
        elif os.path.exists("group_data.json"):
            os.remove("group_data.json")
        for group in self.groups.values():
            group.disconnectAll()
        self.stopServer=True
    # @handle_connection_reset
    def waitUserInput(self, client, username, groupname):
        print("the beginning of start waitUserInput")
        while not self.stopServer:
            try:
                msg = client.recv(1024).decode("utf-8")
            except Exception:
                return
            print("msg waitUserInput ",msg, " username ", username)
            if msg == "/disconnect":
                print("waitUserInput disconnect")
                self.groups[groupname].disconnect(username)
                break
            elif msg == "/emergencyDisconnect":
                print(username," emergently disconnecting| Group:",groupname)
                client.send(b"/disconnect")
                if username in self.groups[groupname].onlineMembers:
                    self.groups[groupname].onlineMembers.remove(username)
                    self.groups[groupname].clients[username].close()
                    del self.groups[groupname].clients[username]
                elif username in self.groups[groupname].waitClients:
                    self.groups[groupname].waitClients[username].send(b"/disconnect")
                    del self.groups[groupname].waitClients[username]
                break
            if username in self.groups[groupname].allMembers:
                if msg == "/approveRequest":
                    print("waitUserInput approveRequest")
                    self.groups[groupname].approveRequest(username)
                elif msg == "/viewRequests":
                    print("waitUserInput viewRequests")
                    self.groups[groupname].viewRequests(username)
                elif msg == "/messageSend":
                    print("waitUserInput messageSend")
                    client.send(b"/messageSend")
                    message = client.recv(1024).decode("utf-8")
                    print("sendMessage ", message)
                    self.groups[groupname].sendMessage(message,username)
                    self.groups[groupname].messageHistory.append({"username": username, "message": message})
                elif msg == "/allMembers":
                    print("waitUserInput allMembers")
                    client.send(b"/sendingData")
                    client.recv(1024).decode("utf-8")
                    client.send(pickle.dumps(self.groups[groupname].allMembers))
                elif msg == "/onlineMembers":
                    print("waitUserInput onlineMembers")
                    client.send(b"/sendingData")
                    client.recv(1024).decode("utf-8")
                    client.send(pickle.dumps(self.groups[groupname].onlineMembers))
                elif msg == "/kickMember":
                    print("waitUserInput kickMember")
                    self.groups[groupname].tryKick(username)
                elif msg == "/attemptConnect":
                    self.groups[groupname].connect(client, username)
            else:
                client.send(b"you can't do anything, you're not a member yet")

def main():
    if len(sys.argv) < 3:
        print("USAGE: python server.py <IP> <Port>")
        print("EXAMPLE: python server.py localhost 8000")
        return
    server = mainServer(sys.argv[1], sys.argv[2])
    server.startServer()

if __name__ == "__main__":
    main()