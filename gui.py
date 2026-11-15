import tkinter as tk
import tkinter.scrolledtext as st
import sys
import hashlib
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
from blob import Blob, Status
from datetime import datetime
from enum import Enum

root = tk.Tk()



class Header():
    JOIN:str = "J"
    MSG:str = "M"
    SOS:str = "S"
    ACK:str = "A"
    CORR:str = "C"
    EXIT:str = "E"

##### SERVER ####

clients = []

def accept_incoming_connections():
    """Sets up handling for incoming clients."""
    while True:
        client, client_address = SERVER.accept()
        print("%s:%s has connected." % client_address)
        addresses[client] = client_address
        if not client in clients: clients.append(client)
        Thread(target=handle_client, args=(client,)).start()

def handle_client(client):  # Takes client socket as argument.
    """Handles a single client connection."""

    while True:
        msg = client.recv(BUFSIZ)
        if not msg: continue
        print("SERVER GOT: ", msg)
        t_decoded = msg.decode("utf8")
        t_header = t_decoded.split(":")[0]
        broadcast(msg, client, (t_header == Header.MSG))
        if t_header == Header.EXIT:
            client.close()
            clients.remove(client)
            print("Removing client")
            break


def broadcast(msg, sender, send_back: bool = False):  # prefix is for name identification.
    """Broadcasts a message to all the clients."""
    for sock in clients: 
        if sock != sender or send_back: sock.send(msg)

### CLIENT ###

pending_acks = {}
failed_message: str = ""
prev_message: str = ""

def send_sos() -> None:
    t_sos_plaintext: str = local_blob.generate_sos()
    t_sos_ciphertext: str = local_blob.encode(t_sos_plaintext)
    t_sos_hash = hashlib.sha256(t_sos_plaintext.encode("utf-8")).hexdigest()
    send(Header.SOS, t_sos_ciphertext)
    pending_acks[t_sos_hash] = t_sos_plaintext

def receive():
    """Handles receiving of messages."""
    while True:
        try:
            msg = client_socket.recv(BUFSIZ).decode("utf8")
            print("Recieved Packet: ", msg)
            t_split = msg.split(":")
            t_header = t_split[0]
            
            match(t_header):
                case Header.MSG: # M:'mappings'
                    t_mappings = t_split[1]
                    t_plaintext = local_blob.decode_as_text(t_mappings)
                    update_past_messages(t_plaintext)
                    local_hash = hashlib.sha256(t_plaintext.encode("utf-8")).hexdigest()
                    if not local_hash in pending_acks.keys(): 
                        send(Header.ACK, local_hash)
                        local_blob.shuffle_blob(t_plaintext)
                    else:
                        print("This is my own packet, ignoring")
                case Header.ACK: # A:'acknowledged_hash'
                    t_hash = t_split[1]
                    if t_hash in pending_acks.keys():
                        local_blob.shuffle_blob(pending_acks[t_hash])
                        
                        pending_acks.pop(t_hash)
                    else:
                        send_sos()
                case Header.SOS: # S:'sos_text_mapping'
                    failed_message = prev_message
                    t_mappings = t_split[1]
                    if (local_blob.restore_blob):
                        print("REVERTED BLOB, TRYING WITH PREVIOUS")
                        t_plaintext = local_blob.decode()
                        send(Header.CORR, t_plaintext)
                case Header.CORR: # C:'sos_text_hash'abs
                    t_hash = t_split[1]
                    if t_hash in pending_acks.keys: # this means they are at a match now
                        t_plaintext = failed_message
                        pending_acks.clear()
                        send(Header.MSG, failed_message)
                    else:
                        send_sos()
                case Header.EXIT:
                    t_plaintext = local_blob.decode(t_mappings)
                    update_past_messages(t_plaintext)
                case default:
                    print("UNKNOWN HEADER: ", t_header, " IGNORING PACKET")

            
            # past_messages.insert(tkinter.END, msg)
        except OSError:  # Possibly client has left the chat.
            break

def get_time() -> str: return str(datetime.now())

def send_message() -> None: # plaintext format for sending: 'message|date_and_time'
    t_plaintext = screen_name + ": " + new_message.get() + " @ " + get_time()
    t_hash = hashlib.sha256(t_plaintext.encode("utf-8")).hexdigest()
    t_packet = local_blob.encode(t_plaintext)
    new_message.set("")  # Clears input field.
    prev_message = t_plaintext
    send(Header.MSG, t_packet)
    pending_acks[t_hash] = t_plaintext
    

def send(header: Header, packet: str):  # event is passed by binders.
    print("Sending Packet: ", header + ":" + packet)
    client_socket.send(bytes(header + ":" + packet, "utf8"))
    if header == Header.EXIT:
        client_socket.close()
        top.quit()


def on_closing(event=None):
    """This function is to be called when the window is closed."""
    t_plaintext = screen_name + " has left the chat"  + " @ " + datetime.now()
    packet = local_blob.encode(t_plaintext)
    send(Header.EXIT, packet)

### EXECUTION STARTS HERE ###

name: str = "Nobody: Secure Messaging"
tagline: str = "\"Nobody - that's my name.\" -Odysseus"
new_message = tk.StringVar()
canvas_bg: str = "bisque"
textbox_bg: str = "cornflower blue"
label_fg: str = "brown4"
label_font: str = "Times New Roman"
label_size: int = 20
label_size_small: int = 15
label_size_smaller: int = 10

root.title(name)
root.geometry("800x600")
root.configure(bg = canvas_bg)

top_lbl = tk.Label(root, text = name, font = (label_font, label_size), bg = canvas_bg, fg = label_fg)
bottom_lbl = tk.Label(root, text = tagline, font = (label_font, label_size), bg = canvas_bg, fg = label_fg)


past_messages = st.ScrolledText(root, width = 100, height = 15, font = (label_font, label_size_small), bg = textbox_bg)

def message_submit():
    if new_message.get() != "":
        update_past_messages(new_message.get())
    new_message.set("")
def update_past_messages(new_message: str) -> ():
    past_messages.configure(state = "normal")
    past_messages.insert(tk.END, new_message + '\n')
    past_messages.configure(state = "disabled")

new_m_frame = tk.Frame(root, bg = canvas_bg)

message_lbl = tk.Label(new_m_frame, text = "New message", font = (label_font, label_size_small), bg = canvas_bg, fg = label_fg)
message_entry = tk.Entry(new_m_frame, textvariable = new_message, bg = textbox_bg, fg = "white", width = 70, font = (label_font, label_size_smaller))
message_btn = tk.Button(new_m_frame, text = "Send", command = send_message, font = (label_font, label_size_smaller))

top_lbl.pack()
past_messages.pack()
new_m_frame.pack()
message_lbl.pack(side="left")
message_entry.pack(side="left")
message_btn.pack(side="left")
bottom_lbl.pack()


HOST = ""
PORT = 33000
BUFSIZ = 1024
ADDR = ""
SERVER = None
addresses = {}
screen_name = ""
STATE = Status.UNINITIALIZED
CLIENT_ARG_LEN = 4 # 'CLIENT', SERVER_HOST, INIT_KEY, SCREEN_NAME
SERVER_ARG_LEN = 3 # 'SERVER', INIT_KEY, SCREEN_NAME
args = sys.argv[1:]
is_host = False

if len(args) < min(CLIENT_ARG_LEN, SERVER_ARG_LEN): 
    print("TO FEW ARGUMENTS PROVIDED! ONLY SAW: ", len(args))
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
if is_host: # Server set up
    ADDR = (HOST, PORT)
    SERVER = socket(AF_INET, SOCK_STREAM)
    SERVER.bind(ADDR)
    SERVER.listen(5)
    print("Waiting for connection...")
    ACCEPT_THREAD = Thread(target=accept_incoming_connections)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    SERVER.close()
else: # Client set up
    ADDR = (HOST, PORT)
    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect(ADDR)
    receive_thread = Thread(target=receive)
    receive_thread.start()

local_blob = Blob()
local_blob.shuffle_blob(init_key)
print("Blob hash: ", local_blob.hash)
root.mainloop()
