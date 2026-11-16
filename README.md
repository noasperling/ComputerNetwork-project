# Multi-Client TCP Chat Application

A concurrent Client-Server chat application developed in **Python** as part of a Computer Networks course (Grade: 100). The system enables multiple users to connect simultaneously, exchange public and private messages, and handles unexpected disconnections gracefully.

## Key Features
* **Concurrent Multi-User Support:** Handles multiple clients simultaneously using Python's `threading` module without blocking network I/O.
* **TCP Socket Communication:** Reliable, connection-oriented communication implemented with Python's `socket` library.
* **Messaging Modes:** Supports both broadcast messaging (to all connected users) and direct private messaging.
* **Graceful Disconnection Handling:** Detects abrupt client exits, cleans up active session dictionaries, and notifies remaining participants.
* **Traffic Validation:** Network packet flow and protocol behavior analyzed and verified using **Wireshark**.

## Technologies Used
* **Language:** Python 3
* **Core Libraries:** `socket`, `threading`
* **Network Analysis:** Wireshark

## Project Structure
* `server.py` – Manages incoming TCP connections, maintains the active users dictionary, and routes messages.
* `client.py` – Handles user authentication (username registration), message sending, and real-time message receiving in separate threads.

## How to Run
1. **Start the Server:** Run `python server.py` in your terminal.
2. **Connect Clients:** Open multiple terminal windows (up to 5+ concurrent users) and run `python client.py`.
3. Enter a unique username when prompted and start chatting.
