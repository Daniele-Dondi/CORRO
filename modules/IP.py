import socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
print("My IP: ",s.getsockname()[0])
BaseAddress=s.getsockname()[0]
s.close()
tmp=BaseAddress.rfind(".")
BaseAddress=BaseAddress[:tmp+1]
Port=80
for scan in range(2,254):
    Host=BaseAddress+str(scan)
    print(".",end="")
    try:
        client_socket=socket.socket()
        client_socket.settimeout(0.1)
        client_socket.connect((Host,Port))
        client_socket.close()         
    except:
        pass
    else:
        print()
        print(Host)
    
    
##host="192.168.1.174"
##
##client_socket=socket.socket()
##client_socket.settimeout(0.2)
##client_socket.connect((host,port))

##message = input(" -> ")  # take input
##
##while message.lower().strip() != 'bye':
##    client_socket.send(message.encode())  # send message
##    data = client_socket.recv(1024).decode()  # receive response
##
##    print('Received from server: ' + data)  # show in terminal
##
##    message = input(" -> ")  # again take input

 # close the connection
