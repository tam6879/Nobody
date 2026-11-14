from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread

import fastrand
import random
import hashlib
import string

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

    
    
        






def main() -> None:
    print("I am Nobody.")
    t_seed: str = input("Enter Inital Seed: ")
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

HOST = ""
PORT = 33000
BUFSIZ = 1024
ADDR = ""
SERVER = None
addresses = {}
clients = {}

def accept_incoming_connections():
    """Sets up handling for incoming clients."""
    while True:
        client, client_address = SERVER.accept()
        print("%s:%s has connected." % client_address)
        client.send(bytes("Sup fucker", "utf8"))
        addresses[client] = client_address
        Thread(target=handle_client, args=(client,)).start()

def receive():
    """Handles receiving of messages."""
    while True:
        try:
            msg = client_socket.recv(BUFSIZ).decode("utf8")
            print(msg)
        except OSError:  # Possibly client has left the chat.
            break

is_host: str = input("Is this the server (y/n): ")

if is_host != 'y':
    HOST = input('Enter host: ')
    if not PORT:
        PORT = 33000
    else:
        PORT = int(PORT)


    ADDR = (HOST, PORT)

    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect(ADDR)

    receive_thread = Thread(target=receive)
    receive_thread.start()
else:
    ADDR = (HOST, PORT)

    SERVER = socket(AF_INET, SOCK_STREAM)
    SERVER.bind(ADDR)
    SERVER.listen(5)
    print("Waiting for connection...")
    ACCEPT_THREAD = Thread(target=accept_incoming_connections)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    SERVER.close()

main()