import socket
import time
from typing import Dict
from utils import *
from classes import *

server = socket.socket()
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(("localhost", 8080))

server.listen()

print("Listening on port 8080...")

todos = Todos()


while True:
    client, addr = server.accept()
    t_start = time.perf_counter()
    req = client.recv(4096).decode()
    if not req:
        client.close()
        continue

    reqlines = req.split("\r\n")

    method, path, version = reqlines[0].split()
    route = [route.split("?")[0] for route in path.split("/") if route != ""]
    queryParams = {route.split("?")[1].split("=")[0]: route.split("?")[1].split("=")[1] for route in path.split("/") if route != "" and len(route.split("?")) > 1}

    body: Dict[str, str] = fetch_body(req)
    is_benchmark = body.get("benchmarking") == "yes"

    parsing_ms = (time.perf_counter() - t_start) * 1000

    t_route_start = time.perf_counter()

    if len(route) > 0:
        match route[0]:
            case "fetch-todos":
                routing_ms = (time.perf_counter() - t_route_start) * 1000
                t_op_start = time.perf_counter()
                todos_list = todos.fetch_todos()
                if is_benchmark:
                    op_ms = (time.perf_counter() - t_op_start) * 1000
                    respond_with_benchmark(client, {"todos": todos_list}, parsing_ms, routing_ms, op_ms)
                else:
                    respond(client, {"todos": todos_list})
            case "add-todo":
                routing_ms = (time.perf_counter() - t_route_start) * 1000
                t_op_start = time.perf_counter()
                if method != "POST":
                    reject(client, "400 BAD REQUEST", "Method not allowed")
                    continue
                if "todo" not in body:
                    reject(client, "400 BAD REQUEST", "No todo body param specified")
                    continue
                todo = body["todo"]
                result = todos.add_todo(todo=todo)
                if is_benchmark:
                    op_ms = (time.perf_counter() - t_op_start) * 1000
                    respond_with_benchmark(client, result, parsing_ms, routing_ms, op_ms)
                else:
                    respond(client, result)
            case "remove-todo":
                routing_ms = (time.perf_counter() - t_route_start) * 1000
                t_op_start = time.perf_counter()
                if method != "POST":
                    reject(client, "400 BAD REQUEST", "Method not allowed")
                    continue
                if "todoId" not in body:
                    reject(client, "400 BAD REQUEST", "No todo body param specified")
                    continue
                todoId = body["todoId"]
                result = todos.remove_todo(todoId=todoId)
                if is_benchmark:
                    op_ms = (time.perf_counter() - t_op_start) * 1000
                    respond_with_benchmark(client, result, parsing_ms, routing_ms, op_ms)
                else:
                    respond(client, result)
            case _:
                routing_ms = (time.perf_counter() - t_route_start) * 1000
                reject(client, "404 NOT FOUND", "Page not found")
    else:
        routing_ms = (time.perf_counter() - t_route_start) * 1000
        t_op_start = time.perf_counter()
        res = {"status": "App is up and running!"}
        if is_benchmark:
            op_ms = (time.perf_counter() - t_op_start) * 1000
            respond_with_benchmark(client, res, parsing_ms, routing_ms, op_ms)
        else:
            respond(client, res)