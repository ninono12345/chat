To run client side unittest first start server on localhost with port 8000<br>
python server.py localhost 8000<br>
then run python test_client.py<br><br><br>
Instructions:<br><br>

launch server.py and then connect to it as many clients as you like:<br><br>

python server.py <listener_ip> <listener_port><br>
python client.py <server_ip> <server_port><br><br>

example:<br><br>

python server.py localhost 8000<br>
python client.py localhost 8000<br>
<br><br><br>


Once connected select your username and groupname\n
If you are the first user to connect to the group, you become an admin\n
If another user connects to the group, the admin has to approve the connection by typing /2 and username\n
An admin can kick a user by /8 and username\n
Once a user sends a message the entire group receives the same message\n
If user isn't part of the group the message doesn't get sent out\n
Users may disconnect by typing /3 or with Ctrl+C\n
The server may only disconnect by typing stop!!! otherwise data will not be saved\n
Group data admin, members, join requests message history are saved to group_data.json and reloaded once the server restarts, for each newly connected member the chat history gets printed\n
\n
/1 prints a list of usernames waiting for permission to join\n
/2 approve connection\n
/3 disconnect\n
/4 prints a list of all members\n
/5 prints a list of online members\n
/8 kick user\n

to clear all groups histories, type clear_all_data from the server side or delete the group_data.json file\n\n

This app is made bug free, but to add new features, one has to be very carefull
\n\n\n




The design patterns used:

Abstract Factory Pattern:
server.py: The Group and mainServer classes are abstract factories that create objects of different classes.
client.py: The UserAbs abstract class is an abstract factory that defines the interface for creating User objects

Factory Method Pattern:
server.py: The connect method in the Group class is a factory method that creates a new connection with a client
client.py: The User class is a concrete factory that creates User objects using the connectToServer method.

Singleton Pattern:
server.py: The mainServer class is a singleton that ensures only one instance of the server is created
client.py: The User class can be considered a singleton since it has a single instance of the serverSocket and other attributes.

Observer Pattern:
server.py: The Group class observes the state of its members and notifies them when a new message is sent.
client.py: The User class observes the state of the server and reacts to changes by calling the serverListen and userInput methods.

Command Pattern:
server.py: The sendMessage, tryKick, approveRequest, and viewRequests methods in the Group class are commands that encapsulate a request as an object.
client.py: The userInput method uses commands to send messages to the server, such as /viewRequests, /approveRequest, /disconnect, etc.

Template Method Pattern:
server.py: The startServer method in the mainServer class is a template method that provides a way to start the server.
client.py: The connectToServer method in the User class is a template method that provides a way to connect to the server.

Strategy Pattern:
server.py: The disconnect method in the Group class uses a strategy to disconnect a client, which can
client.py: The serverListen method uses a strategy to handle different types of messages from the server.

Facade Pattern:
server.py: The mainServer class provides a facade to the Group class, making it easier to use.

MVC Pattern:
server.py: The code uses a Model-View-Controller pattern, where the Group class is the model, the client is the view, and the mainServer class is the controller.
client.py: The code uses a Model-View-Controller pattern, where the User class is the model, the serverListen method is the controller, and the userInput method is the view.

Thread Pool Pattern:
The code uses threading to handle multiple tasks concurrently, such as listening to the server and handling user input.


4 OOP pillairs:

Polymorphism:
server.py: The code uses polymorphism when it calls the disconnectAll method on an object of type Group or mainServer, the disconnect method on an object of type Group or mainServer, the isAdmin method on an object of type Group, the sendMessage method on an object of type Group, the tryKick method on an object of type Group, the approveRequest method on an object of type Group, and the viewRequests method on an object of type Group, which have different implementations of these methods, demonstrating method overriding and polymorphic behavior
client.py: The code uses polymorphism when it calls the connectToServer method on an object of type User, which has a different implementation than the abstract method in UserAbs, and also when it uses the input function to handle different types of user input, such as strings and commands, and when it uses the serverSocket.recv and serverSocket.send methods to handle different types of messages from the server.

Abstraction:
server.py: The code uses abstraction when it defines abstract methods isAdmin, disconnect, disconnectAll, tryKick, sendMessage, approveRequest, and viewRequests in the Group2 and Server abstract classes, which are implemented by the Group and mainServer classes, respectively, allowing for decoupling and modularization of the code
client.py: The code uses abstraction when it defines abstract methods connectToServer, serverListen, and userInput in the UserAbs abstract class, which are implemented by the User class, and also when it uses abstract classes UserAbs and ABC to define interfaces and abstract methods that are implemented by concrete classes.

Inheritance:
server.py: The code uses inheritance when the Group class inherits from the Group2 abstract class, the mainServer class inherits from the Server abstract class, and the Group class inherits the attributes and methods of the Group2 class, and the mainServer class inherits the attributes and methods of the Server class, allowing for code reuse and a more hierarchical organization of the code
client.py: The code uses inheritance when the User class inherits from the UserAbs abstract class, inheriting its attributes and methods, and also when the UserAbs class inherits from the ABC (Abstract Base Class) class, inheriting its abstract method implementation.

Encapsulation:
server.py: The code uses encapsulation when it defines private attributes admin, clients, allMembers, onlineMembers, joinRequests, waitClients, and threads in the Group class, and private attributes in the mainServer class, which are accessed and modified only through public methods, hiding the implementation details and providing a controlled interface to the outside world.
client.py: The code uses encapsulation when it defines private attributes serverSocket, inputCondition, inputLock, waitingForInput, stopClient, username, and groupname in the User class, which are accessed and modified only through public methods, such as connectToServer, serverListen, and userInput, hiding the implementation details and providing a controlled interface to the outside world.