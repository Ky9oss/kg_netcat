import socket


target_host = "127.0.0.1"
target_port = 9997
recv_port = 4096
send_message = b"Hello, Icarus!"

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.sendto(send_message,(target_host, target_port))
data, addr = client.recvfrom(recv_port)
client.close()

print(data.decode())

