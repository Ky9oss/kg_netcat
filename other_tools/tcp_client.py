import socket


target_host = "blog.csdn.net"
target_port = 80
recv_port = 4096
send_message = b"GET / HTTP/1.1\r\nHost: blog.csdn.net\r\n\r\n"

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((target_host, target_port))
client.send(send_message)
response = client.recv(recv_port)
client.close()

print(response.decode())

