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
    def __init__(self, permutations: int = 8):
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
        random.seed(self.hash + seed)
        random.shuffle(self.blob)
        random.seed()
        self.generate_hash()
        self.generate_lookup_table()
        print("New blob hash: ", self.hash)
    
    def get_byte(self, b: int) -> int:
        # t_randy: int = random.randint(0, 3) # fastrand.pcg32randint(0, self.permutations - 1)
        # print("Random: ", t_randy)
        return self.lookup_table[b][random.randint(0, 3)]
    
    def encode(self, plaintext: str) -> str:
        res = ""
        for c in plaintext: res = res + str(self.lookup_table[ord(c)][random.randint(0, self.permutations - 1)]) + '|'
        return res[:-1]

    def decode(self, s_mappings: str) -> bytearray:
        t_split = s_mappings.split('|')
        mappings = []
        for c in t_split: mappings.append(int(c))
        res: bytearray = []
        for m in mappings: res.append(self.blob[m])
        return res
    
    def decode_as_text(self, s_mappings: str) -> str:
        t_decode: bytearray = self.decode(s_mappings)
        res = []
        for t_byte in t_decode: res.append(chr(t_byte))
        return ''.join(res)
    
    def store_current_blob(self) -> None:
        if len(self.blob_history) >= self.history_length: self.blob_history.pop(-1)
        self.blob_history.insert(0, [self.blob, self.hash])
    
    def generate_sos(self) -> str:
        return random.choices(CHARS, self.sos_length)

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

    def restore_blob(self) -> bool:
        if len(self.blob_history) <= 0: return False
        self.blob = self.blob_history.pop(0)
        return True

