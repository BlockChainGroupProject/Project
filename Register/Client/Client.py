
import socket
import json
import Encrypt
import queue
import threading
import time
q = queue.Queue()
def receive_data(client):
    while True:
        try:
            data = client.recv(1024).decode()
            if data:
                #print("recieve_data")
                parsed_data = json.loads(data)
                q.put(parsed_data)
            else :
                return 1

        except  Exception as e:
            print(f"{e}\n")
            return 2, None
def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect(("127.0.0.1", 8888))
        print("Connected to the server.")
    except ConnectionRefusedError:
        print("Connection failed. Is the server running?")
        return
    
    try:
        threading.Thread(target = receive_data, args=(client,),daemon = True).start()
        while True:
            # Receiving data from the server

            """
            data = client.recv(1024).decode()
            if not data:
                print("Server closed the connection.")
                break
            parsed_data = json.loads(data)
            print(parsed_data['data'])

            """
            if not q.empty() == True:
                try:
                    parsed_data = q.get_nowait()
                    print(parsed_data["data"])
                except queue.Empty:
                    continue          
            else:
                continue
            if parsed_data['reply_required'] == True:
                # Sending data to the server
                payload = input()
                message = createMessage("response",payload, False)
                if payload.lower() == "exit":
                    print("Closing connection.")
                    break
                client.send(json.dumps(message).encode())
            elif parsed_data['type'] == "prime":
                with open("prime.txt", "w") as file:
                    file.write(str(parsed_data['data']))

            else:
                continue
    except KeyboardInterrupt:
        print("\nConnection interrupted by user.")
    finally:
        client.close()

def createMessage(type, payload, reply_flag):
    message = {
        "type": type,
        "data": payload,
        "reply_required": reply_flag,
        
    }
    return message
if __name__ == "__main__":
    main()