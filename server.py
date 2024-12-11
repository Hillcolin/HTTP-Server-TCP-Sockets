
from socket import *
import threading
import time
import traceback

#This is the server end, it listens, recieves, and  deals with client connections
class Server:

    def __init__(self, addr, port, timeout):
        self.addr = addr    #the ip address
        self.port = port    #the port
        self.timeout = timeout  #time before server closes to inactivity
        self.sessions = {}  #stores client sessions, stores their name
        self.server_socket = socket(AF_INET, SOCK_STREAM)   #TCP socket connection

        try:
            self.server_socket.bind((addr, port)) #bind the socket to a particular ip and port
            self.server_socket.listen(1) #listen for client connections
            self.last_connection_time = time.time()

        except Exception as e:
            print(f"Failed Socket: {e}")
            raise

#########################################################################################################################

    # STARTS SERVER
    def start_server(self):
        try:
            while True:
                self.server_socket.settimeout(self.timeout)#sets the time it take for the server to shutdown to inactivity
                try:
                    connection_socket, client_addr = self.server_socket.accept()  # accept incoming connections
                    self.last_connection_time = time.time() # get time
                    threading.Thread(target=self.handle_request, args=(connection_socket, client_addr)).start()  # thread when handling requests

                except socket.timeout: #if there is a timeout, double check then stop the server
                    if time.time() - self.last_connection_time > self.timeout:
                        self.stop_server()
                        break

        except Exception as e:
            print(f"Server Error: {e}")
            self.stop_server()

#########################################################################################################################

    #STOPS SERVER
    def stop_server(self):
        self.server_socket.close() #closes the socket
        print("Server Closed")

#########################################################################################################################

    #PARSE REQUEST
    def parse_request(self, request_data):
        lines = request_data.split('\r\n') #splits the data at every \r\n
        request_line = lines[0] #gets the first bit of the split up info
        headers = {} #dictonary for the headers

        for line in lines[1:]: #goes through each line and adds the header to the dictonary
            if line == '':
                break

            header, value = line.split(": ", 1)
            headers[header] = value

        if '' in lines: # make the rest of the lines into a single body
            body_index = lines.index('') + 1
            body = '\r\n'.join(lines[body_index:])  

        else:
            body = ''  # If there is not any blank line then assume it is empty
        return request_line, headers, body

#########################################################################################################################

    #HANDLE REQUEST
    def handle_request(self, connection_socket, client_addr):
        try:
            data = connection_socket.recv(1024).decode() #recieve from client
            request_line, headers, body = self.parse_request(data) #parse the data recieved
            tmp = request_line.split() #temporary variable for spliting data
            
            if (len(tmp) < 3):
                self.handle_unsupported_method(connection_socket, "Invalid Request")
                return
                
            method = tmp[0]
            path = tmp[1]

            if (path == '/'): #make the file into index.html
                path = 'index.html'

            if method == "GET": #summon the GET
                self.handle_get_request(connection_socket, path)

            elif method == "POST": #summon the POST
                self.handle_post_request(connection_socket, path, headers, body)

            else: #summon the UNSUPPORTED
                self.handle_unsupported_method(connection_socket, method)

        except Exception as e:
            print(f"Error handling request: {e}")

        finally:
            connection_socket.close()

#########################################################################################################################

    #HANDLE GET REQUEST
    def handle_get_request(self, connection_socket, file_path):
        try:
            ip_address = self.server_socket.getsockname()[0] #get the current ip address
            try:
                file_path = 'assets/' + file_path # add assets so it can find it in the folder

                with open(file_path, 'r') as file:
                    content = file.read()
                    name = self.sessions.get(ip_address, 'Guest')#get the current session and replace the name
                    content = content.replace('{{name}}', name)
                    response_body = content
                    response_status = "200 OK" #it works

            except FileNotFoundError:
                response_body = "404 Not Found"
                response_status = "HTTP/1.1 404 Not Found"

            # Construct HTTP headers
            response_headers = [response_status,"Content-Type: text/html",f"Content-Length: {len(response_body)}","Connection: close","",""]
            response = "\r\n".join(response_headers) + response_body

            # Send the HTTP response back
            connection_socket.sendall(response.encode())
        except Exception as e:
            print(f"Error handling GET request: {e}")
        finally:
            connection_socket.close()

#########################################################################################################################

    #HANDLE POST REQUEST
    def handle_post_request(self, connection_socket, path, headers, body):
        try:
            ip_address = self.server_socket.getsockname()[0]#ip address

            if path == '/change_name':
                form_data = dict(item.split('=') for item in body.split('&')) #split the data at = and split at the &
                name = form_data.get('name', 'Guest') #get the name of the client
                self.sessions[ip_address] = name #set the name of the current ip address int the session to the clients name
                response_body = "Name updated to {name}"
                response_status = "HTTP/1.1 200 OK" #works wahoo
            else:
                response_body = "404 Not Found"
                response_status = "HTTP/1.1 404 Not Found"

            # Construct HTTP headers
            response_headers = [response_status,"Content-Type: text/html",f"Content-Length: {len(response_body)}","Connection: close","",""]
            response = "\r\n".join(response_headers) + response_body #join them 

            # Send the HTTP response back
            connection_socket.sendall(response.encode()) #encode it
        except Exception as e:
            print(f"Error handling POST request: {e}")
        finally:
            connection_socket.close()

#########################################################################################################################

    #HANDLE UNSUPPORTED METHOD
    def handle_unsupported_method(self, connection_socket, method):
    # This method handles any sort of issue with an unsupported method
    # Helps with user-proofing

        try:
            response_body = f"405 Method Not Allowed The method {method} is not allowed."
            response_status = "HTTP/1.1 405 Method Not Allowed"

            # Construct HTTP headers
            response_headers = [response_status,"Content-Type: text/html",f"Content-Length: {len(response_body)}","Connection: close","",""]
            response = "\r\n".join(response_headers) + response_body

            # Send HTTP response back
            connection_socket.sendall(response.encode())
        except Exception as e:
            print(f"Error handling unsupported method: {e}")
        finally:
            connection_socket.close() #CLOSE CONNECTION SOCKET