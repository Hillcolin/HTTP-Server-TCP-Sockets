# Simple HTTP Server in Python

The server will listen for incoming connections on the specified address and port. The default address is `127.0.0.1` (localhost), and the default port is `8080`.

## Sample Usage

### GET Request:
1. Open a browser and navigate to `http://127.0.0.1:8080/`.
2. The server will return the `index.html` file (or another file based on the URL path).
3. The HTML content will display the session name (default "Guest").

### POST Request:
1. You can use a tool like [Postman](https://www.postman.com/) or a simple HTML form to make a `POST` request to `http://127.0.0.1:8080/change_name`.
2. Submit form data with the field `name=YourName`.
3. The server will update the session name and respond with a success message.

## Code Explanation

### Server Class
The main class `Server` contains the following methods:

- `__init__(self, addr, port, timeout)`: Initializes the server with an address, port, and timeout duration.
- `start_server(self)`: Starts the server, listening for client connections.
- `stop_server(self)`: Gracefully shuts down the server.
- `parse_request(self, request_data)`: Parses incoming requests, splitting them into request lines, headers, and body.
- `handle_request(self, connection_socket, client_addr)`: Handles the incoming request, processes it based on the HTTP method (`GET` or `POST`), and delegates to the appropriate handler method.
- `handle_get_request(self, connection_socket, file_path)`: Handles the `GET` request and serves static files from the `assets/` directory.
- `handle_post_request(self, connection_socket, path, headers, body)`: Handles `POST` requests, including updating the session name.
- `handle_unsupported_method(self, connection_socket, method)`: Handles unsupported HTTP methods by responding with a "405 Method Not Allowed" error.

### Error Handling
- The server catches exceptions and logs errors related to socket creation, request handling, and file serving.
- It sends appropriate HTTP status codes back to the client for errors (`404` for "Not Found", `405` for "Method Not Allowed").

### Session Management
- The server uses the client's IP address to track their session and stores their name in a dictionary `self.sessions`.
- If a client submits a form via `POST` to `/change_name`, their session name is updated.

## File Structure

```bash
server.py           # The server code
assets/             # Folder containing HTML files (e.g., index.html)
README.md           # This documentation file
