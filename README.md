To run the server app, run gui.py with the argument "SERVER"

Like: python gui.py SERVER

This will start the server application, it should say "waiting for connections"

To run a client, run gui.py with the argument "CLIENT", then the IP of the Host, the initialization key, and a screen name 

Like: python gui.py CLIENT 127.0.0.1 init-key client1

The client should connect to the server and show the GUI. Open two or more clients before any messages are sent and get to chatting.
Synchronization failures are handled automatically.
