import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox
import sys

IP = '127.0.0.1'
PORT = 12345

client_socket = None
username = ""
is_running = False  # Flag to check if the application is running

def connect_to_server():
    global client_socket, username, is_running
    username = username_entry.get()
    
    if not username:
        messagebox.showerror("Error", "Please enter a username first!")
        return

    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((IP, PORT))
        
        # Update the GUI state
        username_entry.config(state=tk.DISABLED)
        connect_button.config(state=tk.DISABLED, text="Connected")
        recipient_entry.config(state=tk.NORMAL)
        message_entry.config(state=tk.NORMAL)
        send_button.config(state=tk.NORMAL)
        
        is_running = True  # Mark the application as active
        
        # Start listening for messages in a separate thread
        thread = threading.Thread(target=receive_messages, daemon=True)
        thread.start()
        
    except Exception as e:
        messagebox.showerror("Connection Error", f"Could not connect to server.\n{e}")

def receive_messages():
    global is_running
    while is_running:
        try:
            # Receive message
            if client_socket:
                msg = client_socket.recv(1024).decode()
                
                # Check if connection was closed by server (returns empty string)
                if not msg:
                    raise ConnectionError("Server closed connection")

                if msg == "NAME_REQUEST":
                    client_socket.send(username.encode())
                
                elif msg.startswith("ERROR:"):
                    # Error from server - show popup instead of chat display
                    error_content = msg.split(":", 1)[1]
                    messagebox.showerror("Sending Failed", error_content)
                    
                else:
                    # Handle standard message (parsing protocol)
                    if ":" in msg and "|" in msg:
                        sender_info, content_part = msg.split(":", 1)
                        sender_name = sender_info.strip()
                        
                        target_name, actual_msg = content_part.split("|", 1)
                        target_name = target_name.strip()
                        
                        # Determine display format (Sender -> Target)
                        display_sender = sender_name
                        display_target = target_name
                        
                        if sender_name == username:
                            display_sender = "Me"
                        if target_name == username:
                            display_target = "Me"
                        
                        # Write to chat window
                        chat_display.config(state=tk.NORMAL)
                        chat_display.insert(tk.END, f"{display_sender} -> {display_target}\n", 'header_bold')
                        chat_display.insert(tk.END, f"{actual_msg}\n\n")
                        chat_display.config(state=tk.DISABLED)
                        chat_display.yview(tk.END)
                    else:
                        # System messages
                        if "Connected to the server" in msg:
                            chat_display.config(state=tk.NORMAL)
                            chat_display.insert(tk.END, msg + "\n")
                            chat_display.config(state=tk.DISABLED)
                            chat_display.yview(tk.END)

        except (ConnectionError, ConnectionResetError, OSError):
            # Handle disconnection (from server or app closure)
            if is_running:
                # Show alert only if the user didn't close the window intentionally
                messagebox.showwarning("Disconnected", "Lost connection to the server.")
                
                # Reset buttons to allow reconnection (optional)
                try:
                    connect_button.config(state=tk.NORMAL, text="Join")
                    send_button.config(state=tk.DISABLED)
                except:
                    pass  # In case the window is already destroyed
            
            # Close the socket
            if client_socket:
                client_socket.close()
            break
        except Exception as e:
            print(f"Unexpected error: {e}")
            break

def send_message(event=None):
    if not client_socket:
        return
        
    msg = message_entry.get()
    recipient = recipient_entry.get()

    if not recipient:
        recipient = "Everyone"

    if msg:
        try:
            full_msg = f"{recipient}|{msg}"
            client_socket.send(full_msg.encode())
            message_entry.delete(0, tk.END)
        except:
            messagebox.showerror("Error", "Message could not be sent. Connection lost.")

def on_closing():
    """
    Function to handle window closing event (clicking 'X')
    """
    global is_running
    is_running = False  # Stop the thread loop
    
    if client_socket:
        try:
            client_socket.close()  # Proactively close the connection
        except:
            pass
            
    window.destroy()  # Destroy the window
    sys.exit()  # Exit the entire process

# --- GUI Setup ---
window = tk.Tk()
window.title("Messenger App")
window.geometry("500x650")
window.option_add('*Font', 'Arial 10')

# Define protocol for window closing - Very Important!
window.protocol("WM_DELETE_WINDOW", on_closing)

top_frame = tk.Frame(window, bg="#f0f0f0", pady=10)
top_frame.pack(fill=tk.X)
tk.Label(top_frame, text="Username:", bg="#f0f0f0").pack(side=tk.LEFT, padx=10)
username_entry = tk.Entry(top_frame, width=15)
username_entry.pack(side=tk.LEFT, padx=5)
connect_button = tk.Button(top_frame, text="Join", command=connect_to_server, bg="#4CAF50", fg="white", width=10)
connect_button.pack(side=tk.LEFT, padx=10)

chat_display = scrolledtext.ScrolledText(window, state=tk.DISABLED, width=50, height=20, bg="white")
chat_display.pack(padx=15, pady=10, fill=tk.BOTH, expand=True)
chat_display.tag_config('header_bold', font=('Arial', 11, 'bold'), foreground="#333333")

bottom_frame = tk.Frame(window, pady=10)
bottom_frame.pack(fill=tk.X, padx=15)

recipient_frame = tk.Frame(bottom_frame)
recipient_frame.pack(fill=tk.X, pady=2)
tk.Label(recipient_frame, text="To:         ", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
recipient_entry = tk.Entry(recipient_frame, state=tk.DISABLED)
recipient_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

msg_frame = tk.Frame(bottom_frame)
msg_frame.pack(fill=tk.X, pady=5)
tk.Label(msg_frame, text="Message:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
message_entry = tk.Entry(msg_frame, state=tk.DISABLED)
message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
message_entry.bind("<Return>", send_message)
send_button = tk.Button(msg_frame, text="SEND", command=send_message, state=tk.DISABLED, bg="#2196F3", fg="white")
send_button.pack(side=tk.RIGHT)

window.mainloop()