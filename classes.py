import json
import shortuuid
from typing import List, TypedDict

class TodoItem(TypedDict):
    todoId: str
    todo: str

class Todos:
    map: dict[str, str]
    cached_response: bytes

    def __init__(self) -> None:
        self.map = {}
        self.cached_response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: application/json\r\n"
            f"Content-Length: {len(json.dumps([]).encode())}\r\n"
            "Connection: close\r\n"
            "\r\n"
            f"{json.dumps([])}"
        ).encode()
    
    def update_cache(self) -> None:
        todolist = json.dumps(self.fetch_todos())
        self.cached_response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: application/json\r\n"
            f"Content-Length: {len(todolist.encode())}\r\n"
            "Connection: close\r\n"
            "\r\n"
            f"{todolist}"
        ).encode()

    def fetch_todos(self) -> List[TodoItem]:
        return [{"todoId": todoId, "todo": todo} for todoId, todo in self.map.items()]

    def add_todo(self, todo: str) -> dict[str, int]:
        try:
            todoId = shortuuid.uuid()
            self.map[todoId] = todo
            self.update_cache()
            return {"status": 1}
        except Exception:
            return {"status": 0}
    
    def remove_todo(self, todoId: str) -> dict[str, int]:
        try:    
            del self.map[todoId]
            self.update_cache()
            return {"status": 1}
        except Exception:
            return {"status": 0}
