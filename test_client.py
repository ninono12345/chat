# import client
from server import *
import pytest

def testConn():
    listenSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("ok")
    listenSocket.bind(('localhost', int(8000)))
    listenSocket.listen(10)
    
    assert listener(listenSocket, True) == True
    assert listener(listenSocket, False) == True

def listener(listenSocket, b):
    print("start listener")
    while True:
        client,_ = listenSocket.accept()
        if handleConnection(client, b) == 1:
            client.send(b"/disconnect")
            return True
        else:
            client.send(b"/disconnect")
            return False
    
def handleConnection(client, b):
    print("start handleConnection")
    try:
        username = client.recv(1024).decode("utf-8")
        if username == "/emergencyDisconnect":
            return 0
        # print("hc2")
        client.send(b"/sendGroupname")
        groupname = client.recv(1024).decode("utf-8")
    except Exception:
        return 0
    if groupname == "/emergencyDisconnect":
        return 0
    
    if b:
        conn1 = connect(client, username, True)
        return 1
    else:
        conn2 = connect(client, username, False)
        return 1
    # if conn1 and conn2:
        # print("done final")
        # return 1
    # print("hc3")
    # if groupname in self.groups:
        # # if username in groups[groupname].allMembers:
        # if self.groups[groupname].connect(client, username) == 1:
            # print("connected, user already a member")
        # else:
            # print("user waiting for approval")
        
    # else:
        # self.groups[groupname] = Group(username, client, groupname)
        # self.groups[groupname].threads[username] = threading.Thread(target=self.waitUserInput, args=(client, username, groupname), daemon=True).start()
        # client.send(b"/adminReady")
        # print("New Group:",groupname,"| Admin:",username)
    # print("handleConnection FINISHED")

def connect(client, username, allMembers):
        print("do connect")
        try:
            if allMembers:
                print("in allMembers")
                # self.onlineMembers.add(username)
                # self.clients[username].recv(1024)
                print("send /accepted")
                client.send(b"/accepted")
                print("connect from user ",client.recv(1024))#.decode("utf-8")
                printMessageHistory(username, client)
                client.send(b"/sendCommands")
                client.recv(1024)
                # if username == self.admin:
                client.send(b"/1(Requests), /2(Accept Request), /3(Disconnect), \n/4(All Members), /5(Online Members), /8(Kick Member)")
                # else:
                    # client.send(b"/3(Disconnect), /4(All Members), /5(Online Members)")
                client.recv(1024)
                print("USER CONNECTED:",username,"| Group:", "groupname")
                return True
            else:
                print("not in allMembers")
                # self.onlineMembers.add(username)
                # self.joinRequests.add(username)
                # self.waitClients[username] = client
                # self.sendMessage(username+" has requested to join the group.", self.admin)
                client.send(b"/wait")
                print("Join Request:",username,"| Group:","groupname")
                print("finish connect non member ",client.recv(1024))
                return True
        except Exception:
            return False

def printMessageHistory(username, client):
    client.send(b"/loadMessageHistory")
    client.recv(1024)
    client.send(pickle.dumps([{"username": "ushis", "message":"mhis"}]))
    client.recv(1024)

testConn()