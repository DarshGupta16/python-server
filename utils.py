import json
import socket
from typing import Any

def respond(client: socket.socket, body: Any) -> None:
    body_str = json.dumps(body)

    response = (
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: application/json\r\n"
        f"Content-Length: {len(body_str.encode())}\r\n"
        "Connection: close\r\n"
        "\r\n"
        f"{body_str}"
    )

    client.sendall(response.encode())
    client.close()

def reject(client: socket.socket, status_code: str, message: str) -> None:
    response = (
        f"HTTP/1.1 {status_code}\r\n"
        "Content-Type: text/plain\r\n"
        "Connection: close\r\n"
        "\r\n"
        f"{message}"
    )

    client.sendall(response.encode())
    client.close()

def fetch_body(req: str) -> dict[str, str]:
    content_type = req.split("Content-Type: ")[1].split(";")[0] if "Content-Type: " in req else ""

    if content_type == "multipart/form-data":
        boundary = req.split("boundary=")[1].split()[0]
        splitarr = req.split(boundary)[2:-1]
        data = {el.split("\"")[1]: el.split("\r\n")[-2] for el in splitarr}
        return data
    
    return {}
