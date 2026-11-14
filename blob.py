from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import tkinter
import fastrand
import random
import hashlib
import string
import sys

from enum import Enum

class Status(Enum):
    UNINITIALIZED = 1
    IDLE = 2
    LISTENING_FOR_MESSAGE = 3
    LISTENING_FOR_ACK = 4
    SHUFFLING = 5


CHARS = string.ascii_letters + string.digits
HASH_LENGTH: int = 64

class Blob:
    def __init__(self, permutations: int = 4):
        self.permutations = permutations
        res: list[int] = []
        self.size = permutations * 256
        for i in range(permutations):
            res += list(range(256))
        self.blob = bytearray(res)
        self.generate_hash()
        self.generate_lookup_table()
        self.history_length: int = 4
        self.blob_history: list = []
        self.sos_length: int = 64
    
    def generate_lookup_table(self) -> None:
        res: dict = {}
        for i in range(256):
            res[i] = []
        for i in range(self.size):
            res[int(self.blob[i])].append(i)
        # print("lookup table: ", res)
        self.lookup_table = res

    def generate_hash(self) -> None:
        self.hash = hashlib.sha256(self.blob).hexdigest()

    def shuffle_blob(self, seed: str) -> None:
        self.store_current_blob()
        random.seed(seed)
        random.shuffle(self.blob)
        random.seed()
        self.generate_hash()
        self.generate_lookup_table()
    
    def get_byte(self, b: int) -> int:
        # t_randy: int = random.randint(0, 3) # fastrand.pcg32randint(0, self.permutations - 1)
        # print("Random: ", t_randy)
        return self.lookup_table[b][random.randint(0, 3)]
    
    def encode(self, plaintext: str) -> list:
        res = []
        for c in plaintext: res.append(self.lookup_table[ord(c)][random.randint(0, self.permutations - 1)])
        return res

    def decode(self, mappings: list) -> bytearray:
        res: bytearray = []
        for m in mappings: res.append(self.blob[m])
        return res
    
    def decode_as_text(self, mappings: list) -> str:
        t_decode: bytearray = self.decode(mappings)
        res = []
        for t_byte in t_decode: res.append(chr(t_byte))
        return ''.join(res)
    
    def store_current_blob(self) -> None:
        if len(self.blob_history) >= self.history_length: self.blob_history.pop(-1)
        self.blob_history.insert(0, [self.blob, self.hash])
    
    def send_sos(self) -> None:
        t_message: str = random.choices(CHARS, self.sos_length)
        print("SOS message: ", t_message)
        t_encoded = self.encode(t_message)

    def send_message(self, plaintext) -> None:
        t_encode = self.encode(plaintext)
        t_message = [hashlib.sha256(plaintext).hexdigest(), t_encode]

    def recieve_message(self, message: list) -> str:
        res = ""
        t_decoded = self.decode(message[1])
        t_hash = hashlib.sha256(t_decoded).hexdigest()
        if t_hash == message[0]: 
            self.send_ack()
            self.ack_recieved(t_decoded)
        else: 
            self.send_sos()
        return res

    def send_ack(self, hash: str) -> None:
        pass

    def ack_recieved(self, plaintext: str) -> None:
        self.shuffle_blob(str(self.hash) + plaintext)
        print("New blob hash: ", self.hash)
def main(t_seed: str) -> None:
    print("I am Nobody.")
    current_blob: Blob = Blob()
    current_blob.shuffle_blob(t_seed)
    # print("Shuffled blob: ", current_blob.blob, " hash: ", current_blob.hash)
    current_blob.generate_lookup_table()
    t_message: str = input("Enter a message: ")
    t_mappings: list = current_blob.encode(t_message)
    print("Encoded mappings: ", t_mappings)
    t_decode: bytearray = current_blob.decode(t_mappings)
    print("Decoded bytes: ", t_decode, " decoded string: ", current_blob.decode_as_text(t_mappings))
    # print("History: ", current_blob.blob_history)
    current_blob.ack_recieved(t_message)

def accept_incoming_connections():
    """Sets up handling for incoming clients."""
    while True:
        client, client_address = SERVER.accept()
        print("%s:%s has connected." % client_address)
        client.send(bytes("CHAT OPENED", "utf8"))
        addresses[client] = client_address
        Thread(target=handle_client, args=(client,)).start()

def handle_client(client):  # Takes client socket as argument.
    """Handles a single client connection."""

    name = client.recv(BUFSIZ).decode("utf8")
    welcome = 'Welcome %s! If you ever want to quit, type {quit} to exit.' % name
    client.send(bytes(welcome, "utf8"))
    msg = "%s has joined the chat!" % name
    broadcast(bytes(msg, "utf8"))
    clients[client] = name

    while True:
        msg = client.recv(BUFSIZ)
        if msg != bytes("{quit}", "utf8"):
            broadcast(msg, name+": ")
        else:
            client.send(bytes("{quit}", "utf8"))
            client.close()
            del clients[client]
            broadcast(bytes("%s has left the chat." % name, "utf8"))
            break


def broadcast(msg, prefix=""):  # prefix is for name identification.
    """Broadcasts a message to all the clients."""

    for sock in clients:
        sock.send(bytes(prefix, "utf8")+msg)

def receive():
    """Handles receiving of messages."""
    while True:
        try:
            msg = client_socket.recv(BUFSIZ).decode("utf8")
            if not msg: continue
            print(msg)
        except OSError:  # Possibly client has left the chat.
            break


def send(packet: list):  # event is passed by binders.
    """Handles sending of messages."""
    msg = ''.join(packet)
    client_socket.send(bytes(msg, "utf8"))
    if msg == "{quit}":
        client_socket.close()
        top.quit()


def on_closing(event=None):
    """This function is to be called when the window is closed."""
    my_msg.set("{quit}")
    send()

### EXECUTION STARTS HERE ###


HOST = ""
PORT = 33000
BUFSIZ = 1024
ADDR = ""
SERVER = None
addresses = {}
clients = {}
screen_name = ""
STATE = Status.UNINITIALIZED
CLIENT_ARG_LEN = 4 # 'CLIENT', SERVER_HOST, INIT_KEY, SCREEN_NAME
SERVER_ARG_LEN = 3 # 'SERVER', INIT_KEY, SCREEN_NAME
args = sys.argv[1:]
is_host = False

print("Fucking cunt sack of shit I fucking hate: ", is_host)

if len(args) < min(CLIENT_ARG_LEN, SERVER_ARG_LEN): 
    print("TO FEW ARGUMENTS PROVIDED!")
    sys.exit()
if not (args[0].lower() in ["client", "server"]): 
    print("ARGUMENT 1 NEEDS TO BE 'CLIENT' OR 'SERVER'!")
    sys.exit()
print(is_host)
is_host = (args[0].lower() == 'server')
print("IS SERVER: ", is_host)
if is_host and len(args) != SERVER_ARG_LEN:
    print(f"SERVER REQUIRES {SERVER_ARG_LEN} ARGUMENTS!")
    sys.exit()
elif not is_host and len(args) != CLIENT_ARG_LEN:
    print(f"CLIENT REQUIRES {CLIENT_ARG_LEN} ARGUMENTS!")
    sys.exit()
if is_host:
    init_key = args[1]
    screen_name = args[2]
else:
    HOST = args[1]
    init_key = args[2]
    screen_name = args[3]

print("Cunt: ", is_host)
if is_host: # Client set up
    ADDR = (HOST, PORT)
    SERVER = socket(AF_INET, SOCK_STREAM)
    SERVER.bind(ADDR)
    SERVER.listen(5)
    print("Waiting for connection...")
    ACCEPT_THREAD = Thread(target=accept_incoming_connections)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    SERVER.close()
else: # Server set up
    ADDR = (HOST, PORT)
    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect(ADDR)
    receive_thread = Thread(target=receive)
    receive_thread.start()

main(init_key)