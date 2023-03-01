import socket 
import sys
import threading

IP = '0.0.0.0'
Port = 55555

def main():
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((IP, Port))
        server.listen(5)
        print(f'[*] Listen on {IP}:{Port}')

        client, address = server.accept()
        print(f'[*] Accept connection from {address[0]}:{address[1]}')
        client_handler = threading.Thread(target = handle_client, args = (client,))
        client_handler.start()
        while True:
            if client_handler.is_alive() == False:
                print("再见！")
                sys.exit()


    except (KeyboardInterrupt, BrokenPipeError):
        print("GOODBYE")



def handle_client(client_socket):
    while True:
        request = client_socket.recv(4096)
        if request.decode("utf-8") == 'GOODBYE':
            print(f'Receive: {request.decode("utf-8")}')
            client_socket.send(b'GOODBYE')
            break
        else:
            print(f'Receive: {request.decode("utf-8")}')
            client_socket.send(b'Hello!I can see you!')


if __name__ == '__main__':
    main()

