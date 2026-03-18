import socket

general_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
general_sock.bind(('0.0.0.0', 5005))
general_sock.listen(2)
while True:
    conn, addr = general_sock.accept()
    data= conn.recv(1024).decode("ascii") 
    print("accepted ", data)