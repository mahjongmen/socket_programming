import socket
import select  # manage many connections

HEADER_LENGTH = 10
IP = "127.0.0.1"
PORT = 1234
ADDR = (IP, PORT)
FORMAT = 'utf-8'

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Allows for reconnections
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(ADDR)
server_socket.listen()

# This will be the list sockets (clients connected)
sockets_list = [server_socket]  # first entry in sockets is the server
# {client socket, user info}
clients = {}

print(f'Listening for connections on {ADDR[0]}:{ADDR[1]}')

def receive_message(client_socket):
    try:
        message_header = client_socket.recv(HEADER_LENGTH)

        # client closed connection
        if not len(message_header):
            return False
        # In python do not need to strip, but just have it in case
        message_length = int(message_header.decode(FORMAT).strip())
        # return a dictionary of header and the actual message where the length is equal to what the length told you it would be from the header
        return {"header": message_header, "data": client_socket.recv(message_length)}
    except:
        return False


while True:
    # select.select takes in 3 params, a read list, a write list, sockets that might error on
    # is_readable, is_writable, is_error
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

    for notified_socket in read_sockets:
        # Someone just connected to the server
        if notified_socket == server_socket:
            client_socket, client_address = server_socket.accept()  # returns a socket and a address-->(ip addr, port)
            user = receive_message(client_socket)
            if user is False:
                continue
            # add the new client socket object to teh list of sockets
            # Add the new client/user into the dictionary
            sockets_list.append(client_socket)
            clients[client_socket] = user
            print(f"Accepted new connection from {client_address[0]}:{client_address[1]} username: {user['data'].decode(FORMAT)}")
        else:
            message = receive_message(notified_socket)
            if message is False:
                print(f"Closed connection from {clients[notified_socket]['data'.decode(FORMAT)]}")
                sockets_list.remove(notified_socket)
                del clients[notified_socket]
                continue
            user = clients[notified_socket]
            print(f"Received message from {user['data'].decode(FORMAT)}:{message['data'].decode(FORMAT)}")
            for client_socket in clients:
                # Do not send back to sender
                if client_socket != notified_socket:
                    client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])

    for notified_socket in exception_sockets:
        sockets_list.remove(notified_socket)
        del clients[notified_socket]
