import shortuuid
from typing import List, TypedDict

class TodoItem(TypedDict):
    todoId: str
    todo: str

class Todos:
    map: dict[str, str]

    def __init__(self) -> None:
        self.map = {}
    
    def fetch_todos(self) -> List[TodoItem]:
        return [{"todoId": todoId, "todo": todo} for todoId, todo in self.map.items()]

    def add_todo(self, todo: str) -> dict[str, int]:
        try:
            todoId = shortuuid.uuid()
            self.map[todoId] = todo
            return {"status": 1}
        except Exception:
            return {"status": 0}
    
    def remove_todo(self, todoId: str) -> dict[str, int]:
        try:    
            del self.map[todoId]
            return {"status": 1}
        except Exception:
            return {"status": 0}
