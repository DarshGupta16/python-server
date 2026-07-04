import socket
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
    req = client.recv(4096).decode()

    reqlines = req.split("\r\n")

    method, path, version = reqlines[0].split()
    route = [route.split("?")[0] for route in path.split("/") if route != ""]
    queryParams = {route.split("?")[1].split("=")[0]: route.split("?")[1].split("=")[1] for route in path.split("/") if route != "" and len(route.split("?")) > 1}

    if len(route) > 0:
        match route[0]:
            case "fetch-todos":
                respond(client, {"todos": (todos.fetch_todos())})
            case "add-todo":
                if method != "POST":
                    reject(client, "400 BAD REQUEST", "Method not allowed")
                    continue
                body = fetch_body(req)
                if "todo" not in body:
                    reject(client, "400 BAD REQUEST", "No todo body param specified")
                    continue
                todo = body["todo"]
                result = todos.add_todo(todo=todo)
                respond(client, result)
            case "remove-todo":
                if method != "POST":
                    reject(client, "400 BAD REQUEST", "Method not allowed")
                    continue
                body = fetch_body(req)
                if "todoId" not in body:
                    reject(client, "400 BAD REQUEST", "No todo body param specified")
                    continue
                todoId = body["todoId"]
                result = todos.remove_todo(todoId=todoId)
                respond(client, result)
            case _:
                reject(client, "404 NOT FOUND", "Page not found")
    else:
        respond(client, {"status": "App is up and running!"})
            