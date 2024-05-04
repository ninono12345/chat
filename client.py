import socket
import threading
import signal
import pickle
import sys
from abc import ABC, abstractmethod


class UserAbs(ABC):
    @abstractmethod
    def connectToServer(self):
        pass
    
    def serverListen(self):
        pass
    
    def userInput(self):
        pass

class User(UserAbs):
    def __init__(self):
        self.serverSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.inputCondition = threading.Condition()
        self.inputLock = threading.Lock()
        self.waitingForInput = False
        self.stopClient = False
    
    def connectToServer(self, ip, port):
            # print("start connectToServer")
        self.serverSocket.connect((ip, int(port)))
        try:
            username = input("enter username: ")
            self.serverSocket.send(bytes(username, "utf-8"))
            self.serverSocket.recv(1024).decode("utf-8")
            groupname = input("enter groupname: ")
            self.serverSocket.send(bytes(groupname, "utf-8"))
            response = self.serverSocket.recv(1024).decode("utf-8")
            if response == "/accepted":
                print("you have joined ", groupname, " as ",username)
                self.serverSocket.send(b"yes accepted")
            elif response == "/wait":
                print("your request to join is pending")
                self.serverSocket.send(b".")
            elif response == "/adminReady":
                print("you've joined, you are the admin")
            elif response == "/taken":
                print("username already taken")
                self.stopClient = True
                return False
            else:
                self.stopClient = True
                return False
        except Exception or KeyboardInterrupt:
            print("emergencyDisconnect")
            self.serverSocket.send(b"/emergencyDisconnect")
            
        self.username = username
        self.groupname = groupname
        threading.Thread(target=self.userInput, daemon=True).start()
        threading.Thread(target=self.serverListen, daemon=True).start()
        
        # print("end connectToServer")
        return True
    
    def serverListen(self):
        while not self.stopClient:
            # print("start wait serverListen")
            msg = self.serverSocket.recv(1024).decode("utf-8")
            if msg == "/proceedKick":
                print("enter username to kick:")
                self.waitingForInput=True
                with self.inputCondition:
                    self.inputCondition.wait()
                self.waitingForInput=False
                self.serverSocket.send(bytes(self.inp, "utf-8"))
                self.serverSocket.send(b"kicked")
            elif msg == "/proceedApprove":
                print("enter username to approve:")
                self.waitingForInput=True
                with self.inputCondition:
                    self.inputCondition.wait()
                self.waitingForInput=False
                self.serverSocket.send(bytes(self.inp, "utf-8"))
                # self.serverSocket.recv(1024)
                # self.serverSocket.send(b".")
            elif msg == "/accepted":
                print("you have connected")
                self.serverSocket.send(b"received acceptance")
            elif msg == "/disconnect":
                # print("in disconnect")
                # print("after in disconnect send")
                self.stopClient=True
                break
            elif msg == "/messageSend":
                # print("inp serverListen", self.inp)
                self.serverSocket.send(bytes(self.inp, "utf-8"))
            
            elif msg == "/loadMessageHistory":
                # print("start loadMessageHistory")
                self.serverSocket.send(b".")
                history = pickle.loads(self.serverSocket.recv(1024))
                for message in history:
                    print(f"{message['username']}: {message['message']}")
                self.serverSocket.send(b".")
            elif msg == "/sendingData":
                self.serverSocket.send(b".")
                data = pickle.loads(self.serverSocket.recv(1024))
                print(data)
            elif msg == "/attemptConnect":
                # print("/attemptConnect")
                self.serverSocket.send(b"/attemptConnect")
            elif msg == "/sendCommands":
                self.serverSocket.send(b".")
                print("Available commands:")
                print(self.serverSocket.recv(1024).decode("utf-8"))
                self.serverSocket.send(b".")
            else:
                print(msg)
            
        
    def userInput(self):
        while not self.stopClient:
            # print("start userInput", self.waitingForInput)
            
            try:
                with self.inputLock:
                    self.inp = input()
                    # print("inp ",self.inp)
                with self.inputCondition:
                    self.inputCondition.notify()
                if self.inp=="end":
                    self.stopClient = True
                    self.serverSocket.shutdown(socket.SHUT_RDWR)
                    break
                elif self.inp == "/1":
                    self.serverSocket.send(b"/viewRequests")
                elif self.inp == "/2":
                    self.serverSocket.send(b"/approveRequest")
                elif self.inp == "/3":
                    self.serverSocket.send(b"/disconnect")
                    # self.stopClient = True
                    break
                elif self.inp == "/4":
                    self.serverSocket.send(b"/allMembers")
                elif self.inp == "/5":
                    # print("/5 sent to server")
                    self.serverSocket.send(b"/onlineMembers")
                elif self.inp == "/6":
                    self.serverSocket.send(b"/changeAdmin")
                elif self.inp == "/7":
                    self.serverSocket.send(b"/whoAdmin")
                elif self.inp == "/8":
                    self.serverSocket.send(b"/kickMember")
                elif not self.waitingForInput:
                    self.serverSocket.send(b"/messageSend")
            except Exception:
                break
                
            # print("end userInput")
        

def main():
    if len(sys.argv) < 3:
        print("USAGE: python client.py <IP> <Port>")
        print("EXAMPLE: python client.py localhost 8000")
        return
    user = User()
    try:
        user.connectToServer(sys.argv[1], sys.argv[2])
        while not user.stopClient:
            continue
    except KeyboardInterrupt:
        print("done")
        
        user.serverSocket.send(b"/emergencyDisconnect")
        user.stopClient = True
if __name__ == "__main__":
	main()