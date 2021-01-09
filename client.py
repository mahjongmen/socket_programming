import socket
import select
import errno
import sys

HEADER_LENGTH = 10
IP = "127.0.0.1"
PORT = 1234
ADDR = (IP, PORT)
FORMAT = 'utf-8'
my_username=input("Username: ") #grab from client when join
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(ADDR)
client_socket.setblocking(False) #receive functionality will not be blocking

# Begin to send in the information to the server
username = my_username.encode(FORMAT)
username_header=f"{len(username):<{HEADER_LENGTH}}".encode(FORMAT)
client_socket.send(username_header+username)

while True:
    message=input(f"{my_username} > ")
    message=""
    if message:
        message = message.encode(FORMAT)
        message_header=f"{len(message):<{HEADER_LENGTH}}".encode(FORMAT)
        client_socket.send(message_header+message)
    try:
        while True: #Receive from servers
            username_header = client_socket.recv(HEADER_LENGTH)
            if not len(username_header):
                print("connection closed by the server")
                sys.exit()
            # Get username and username length
            username_length=int(username_header.decode(FORMAT).strip()) # Get how many bits the user name is
            username=client_socket.recv(username_length).decode(FORMAT) # Get the user name

            # Get Message and Message Length
            message_header=client_socket.recv(HEADER_LENGTH)
            message_length=int(message_header.decode(FORMAT).strip()) # Get how many bits the header is
            message=client_socket.recv(message_length).decode(FORMAT)

            print(f"{username} > {message}")

    except IOError as e:
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            print ('Reading Error {}'.format(str(e)))
            sys.exit()
        continue

    except Exception as e:
        print ('Reading Error {}'.format(str(e)))
        sys.exit()
