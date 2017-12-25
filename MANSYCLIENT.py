import socket

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
client.connect(('0.0.0.0', 8082))
response = client.recv(4096)
while True:
    print()
#     client.send("hihellohi")

print(response)