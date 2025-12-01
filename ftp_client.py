from socket import socket, AF_INET, SOCK_STREAM


buffer = bytearray(512)

def ftp_command(s, cmd):
    print(f"Sending command {cmd}")
    buff = bytearray(512)
    s.sendall((cmd + "\r\n").encode())
    # TODO: Fix this part to parse multiline responses
    response = "" #stores the server response
    done = False #boolean to indicate if the response is complete
    while not done: # loops until the full response is received
        nbytes = s.recv_into(buff) # reads bytes into the socket
        if nbytes == 0: #checks to see if the connection is closed
            done = True
        else:
            response += buff[:nbytes].decode() # adds the received bytes to the response string
            lines = response.split("\r\n") # splits the response into lines
            if len(lines) > 0: # checks to see if there are any lines in the response
                last = lines[-2] # gets the last line of the response
                if len(last) >= 4 and last[:3].isdigit():
                    if last[3] == ' ': #checks to see if this is the end of the response
                        done = True
    return response


def ftp_open(FTP_SERVER):

    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect((FTP_SERVER, 21))
    length = sock.recv_into(buffer)
    print(f"Server response {length} bytes: {buffer.decode()}")



    response = buffer.decode()
    code = response[:3]
    if code == "220":
    #this = True
    #if this is True:
        user = input("Enter Username: ")
        response = (ftp_command(sock,f"USER {user}"))
        print(response)
        code = response[:3]

        if code == "331":
            password = input("Enter Password:")
            response = ftp_command(sock,f"PASS {password}")
            print(response)
            code = response[:3]
         
        elif code == "332":
            print("Account required")
            
        elif code in ["421", "500", "501", "530"]:
            print("Error:", response)
    return sock

def ftp_dir(sock,ip):
    port = 12345
    # Use the "receptionist" to accept incoming connections
    data_receptionist = socket(AF_INET, SOCK_STREAM)
    data_receptionist.bind(("0.0.0.0", port))
    data_receptionist.listen(1)         # max number of pending request

    hi = port // 256  # Use integer division
    lo = port % 256

    a,b,c,d = ip.split(".")
    port_command = f"PORT {a},{b},{c},{d},{hi},{lo}"
    print(ftp_command(sock, port_command))
    print(ftp_command(sock, 'TYPE A'))
    prelim = ftp_command(sock, 'LIST')
    print(prelim)
    if prelim[:3] not in ("125","150"):
        print("ERROR: no preliniminary reply from server.")
        data_receptionist.close()
        return

    # Use the "data_socket" to perform the actual byte transfer
    (data_socket,address) = data_receptionist.accept()
    data = data_socket.recv(4096).decode()
    print(data)

    data_socket.close()
    data_receptionist.close()
    secondary = ftp_command(sock, "")
    if secondary[:3] == "226" or secondary[:3] == "250":
        print(f"Command Successful.")
    else:
        print("secondary reponse shows error.")

def ftp_cd(sock,dir):
    response = ftp_command(sock,f"CWD {dir}")
    print(response)
 
def ftp_get(sock,ip,filename):
    port = 12345
    # Use the "receptionist" to accept incoming connections
    data_receptionist = socket(AF_INET, SOCK_STREAM)
    data_receptionist.bind(("0.0.0.0", port))
    data_receptionist.listen(1)         # max number of pending request

    hi = port // 256  # Use integer division
    lo = port % 256

    a,b,c,d = ip.split(".")
    port_command = f"PORT {a},{b},{c},{d},{hi},{lo}"
    print(ftp_command(sock, port_command))
    print(ftp_command(sock, 'TYPE I'))
    prelim = ftp_command(sock, f"RETR {filename}")
    print(prelim)
    if prelim[:3] not in ("125","150"):
        print("ERROR: no preliniminary reply from server.")
        return

    print("1")
    # Use the "data_socket" to perform the actual byte transfer
    data_socket, _ = data_receptionist.accept()
    print("2")

    fw = open(filename, 'wb')
    
    while True:
        buff_w = data_socket.recv(1024)     # recieves bytes from server
        if not buff_w:
            break
        fw.write(buff_w)  # writes bytes to file


    fw.close()
    data_socket.close()
    data_receptionist.close()
    print("3")
    secondary = ftp_command(sock, "")
    if secondary[:3] in ("226","250"):
        print(f"{filename} downloaded successfully.")
    else:
        print("secondary reponse shows error.")

def ftp_put(sock,ip,filename):
    port = 12345
    # Use the "receptionist" to accept incoming connections
    data_receptionist = socket(AF_INET, SOCK_STREAM)
    data_receptionist.bind(("0.0.0.0", port))
    data_receptionist.listen(1)         # max number of pending request

    hi = port // 256  # Use integer division
    lo = port % 256

    a,b,c,d = ip.split(".")
    port_command = f"PORT {a},{b},{c},{d},{hi},{lo}"
    print(f"sending PORT command {ftp_command(sock, port_command)}")
    print(ftp_command(sock, 'TYPE I'))
    prelim = ftp_command(sock, f"STOR {filename}")
    print(f"sending STOR command {prelim}")
    if prelim[:3] not in ("125","150"):
        print("ERROR: no preliniminary reply from server.")
        return

    # Use the "data_socket" to perform the actual byte transfer
    data_socket = data_receptionist.accept()

    fr = open(filename, 'rb')

    while True:
        buff_r = fr.read(1024)     # reads bytes from file
        if not buff_r:
            break
        data_socket.sendall(buff_r)  # sends bytes to server
    fr.close()

    data_socket.close()
    data_receptionist.close()
    secondary = ftp_command(sock, "")
    if secondary[:3] in ("226","250"):
        print(f"{filename} Uploaded successfully.")
    else:
        print("secondary reponse shows error.")

def ftp_close(sock):
    print(ftp_command(sock, "QUIT"))
    sock.close()

def ftp_quit(sock):
    sock.close()

def main():
    try:
        command_sock = ftp_open(input("Enter FTP Server: "))
        my_ip, my_port = command_sock.getsockname()
    except Exception as e:
        print(f"Error connecting to server: {e}")
        return


    while True:
        user_input = input("ftp> ")
        if not user_input:
            continue

        parts = user_input.split()
        command = parts[0].lower()

        if command == "quit":
            break
        elif command == "open":
            ftp_open(command_sock)
        elif command == "dir" or command == "ls":
            ftp_dir(command_sock, my_ip)
        elif command == "cd" and len(parts) > 1:
            ftp_cd(command_sock, parts[1])
        elif command == "get" and len(parts) > 1:
            ftp_get(command_sock, my_ip, parts[1])
        elif command == "put" and len(parts) > 1:
            ftp_put(command_sock, my_ip, parts[1])
        elif command == "close":
            ftp_close(command_sock)
        else:
            print("Unknown command")

if __name__ == "__main__":
    main()