import json
import socket
import time
from typing import Any, Dict

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

def send_cached_response(client: socket.socket, response: bytes) -> None:
    client.sendall(response)
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

def fetch_body(req: str) -> Dict[str, str]:
    content_type = req.split("Content-Type: ")[1].split(";")[0] if "Content-Type: " in req else ""

    if content_type == "multipart/form-data":
        boundary = req.split("boundary=")[1].split()[0]
        splitarr = req.split(boundary)[2:-1]
        data = {el.split("\"")[1]: el.split("\r\n")[-2] for el in splitarr}
        return data
    
    return {}

def respond_with_benchmark(
    client: socket.socket,
    data: Any,
    parsing_ms: float,
    routing_ms: float,
    operation_ms: float
) -> None:
    placeholder = '"__SEND_TIME_PLACEHOLDER__"'
    body: Dict[str, Any] = {
        "data": data,
        "benchmark": {
            "parsing_ms": parsing_ms,
            "routing_ms": routing_ms,
            "operation_ms": operation_ms,
            "response_send_ms": "__SEND_TIME_PLACEHOLDER__"
        }
    }
    body_str = json.dumps(body)

    response = (
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: application/json\r\n"
        f"Content-Length: {len(body_str.encode())}\r\n"
        "Connection: close\r\n"
        "\r\n"
        f"{body_str}"
    )

    parts = response.split(placeholder)
    if len(parts) == 2:
        part1 = parts[0].encode()
        part2 = parts[1].encode()

        t_start = time.perf_counter()
        client.sendall(part1)
        t_end = time.perf_counter()

        send_ms = (t_end - t_start) * 1000

        val = f'"{send_ms:.6f}"'
        val_padded = val[:-1] + " " * (len(placeholder) - len(val)) + '"'

        client.sendall(val_padded.encode() + part2)
        print(f"[BENCHMARK] Parsing: {parsing_ms:.3f}ms | Routing: {routing_ms:.3f}ms | Operation: {operation_ms:.3f}ms | Send: {send_ms:.3f}ms")
    else:
        client.sendall(response.encode())
        print(f"[BENCHMARK] Split failed. Parsing: {parsing_ms:.3f}ms | Routing: {routing_ms:.3f}ms | Operation: {operation_ms:.3f}ms")
    
    client.close()

