import socket
import threading

# Connection settings
IP = '0.0.0.0'
PORT = 12345

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((IP, PORT))
server_socket.listen()

# Dictionary to store connected clients: {client_socket: username}
clients = {}

# Dictionary to track who talked to whom
user_contacts = {}

def broadcast(message, sender_socket=None):
    """
    Sends a message to all connected clients (except the sender).
    """
    for client_socket in list(clients.keys()):
        # This check prevents sending back to the sender if sender_socket is provided
        if client_socket != sender_socket:
            try:
                client_socket.send(message.encode())
            except:
                remove_client(client_socket)

def remove_client(client_socket):
    """
    Handles removing a client.
    Only notifies users who had a private conversation with this person.
    """
    if client_socket in clients:
        username = clients[client_socket]
        
        # 1. Get the list of people this user talked to
        contacts = user_contacts.get(client_socket, set())
        
        disconnect_msg = f"Server : You | {username} has left the chat."
        
        # 2. Notify only those specific people
        for contact_socket in contacts:
            if contact_socket in clients: # Check if they are still online
                try:
                    contact_socket.send(disconnect_msg.encode())
                except:
                    pass

        # 3. Clean up data
        print(f"{username} has disconnected.")
        del clients[client_socket]
        if client_socket in user_contacts:
            del user_contacts[client_socket]
            
        try:
            client_socket.close()
        except:
            pass

def handle_client(client_socket):
    try:
        # Step 1: Request username
        client_socket.send("NAME_REQUEST".encode())
        username = client_socket.recv(1024).decode()
        
        clients[client_socket] = username
        user_contacts[client_socket] = set() # Initialize empty contact list
        
        print(f"New connection: {username}")
        
        # Only send Welcome message to the specific user
        client_socket.send(f"Server : You | Welcome to the chat, {username}!".encode())
        
        # Step 2: Continuous message receiving loop
        while True:
            msg = client_socket.recv(1024).decode()
            
            if not msg:
                break
            
            if "|" in msg:
                recipient, content = msg.split("|", 1)
                sender_name = clients[client_socket]
                full_message = f"{sender_name} : {recipient} | {content}"
                
                print(full_message) # Server log
                
                if recipient == "Everyone":
                    broadcast(full_message, sender_socket=client_socket)
                    
                    try:
                        client_socket.send(full_message.encode())
                    except:
                        pass
                else:
                    # Private message 
                    sent_to_target = False
                    for socket_obj, name in clients.items():
                        if name == recipient:
                            # Send the message
                            socket_obj.send(full_message.encode())
                            sent_to_target = True
                            
                            # Send copy back to sender
                            client_socket.send(full_message.encode())
                            
                            # Record the connection between these two
                            user_contacts[client_socket].add(socket_obj)
                            user_contacts[socket_obj].add(client_socket)
                            break
                    
                    if not sent_to_target:
                        error_msg = f"ERROR:User '{recipient}' not found."
                        client_socket.send(error_msg.encode())
            
    except Exception as e:
        print(f"Error with client: {e}")
    finally:
        remove_client(client_socket)

print(f"Server is listening on {IP}:{PORT}...")

while True:
    client_socket, addr = server_socket.accept()
    thread = threading.Thread(target=handle_client, args=(client_socket,))
    thread.start()