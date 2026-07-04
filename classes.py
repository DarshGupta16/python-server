import shortuuid
from typing import List, TypedDict

class TodoItem(TypedDict):
    todoId: str
    todo: str

class TodoNode:
    todo: str
    todoId: str
    prev: "TodoNode | None"
    next: "TodoNode | None"

    def __init__(self, todo: str, todoId: str) -> None:
        self.todo = todo
        self.todoId = todoId
        self.prev = None
        self.next = None

class TodosDoublyLinked:
    head: TodoNode | None
    tail: TodoNode | None

    def __init__(self) -> None:
        self.head = None
        self.tail = None
    
    def append(self, todo: TodoNode) -> TodoNode:
        if self.head is None:
            self.head = todo
            self.tail = todo
            return todo
        
        todo.prev = self.tail
        assert self.tail is not None  
        self.tail.next = todo
        self.tail = todo
        return todo
    
    # For debugging purposes
    def fetchlisttext(self) -> str:
        def fetchNode(node: TodoNode, currStr: str) -> str:
            newStr = currStr + (f"{node.todo} -> " if node.next is not None else f"{node.todo}")
            if node.next is not None:
                return fetchNode(node.next, newStr)
            else:
                return newStr
        if self.head is not None:
            return fetchNode(self.head, "")
        return ""

class Todos:
    list: List[TodoItem]
    doublyLinkedList: TodosDoublyLinked
    map: dict[str, TodoNode]

    def __init__(self) -> None:
        self.list = []
        self.doublyLinkedList = TodosDoublyLinked()
        self.map = {}
    
    def fetch_todos(self) -> List[TodoItem]:
        return self.list

    def add_todo(self, todo: str) -> dict[str, int]:
        try:
            todoId = shortuuid.uuid()
        
            newNode = TodoNode(todo, todoId)
            self.doublyLinkedList.append(newNode)
            self.map[todoId] = newNode
        
            self.list.append({"todoId": todoId, "todo": todo})
            return {"status": 1}
        except Exception:
            return {"status": 0}
    
    def remove_todo(self, todoId: str) -> dict[str, int]:
        try:    
            node: TodoNode = self.map[todoId]

            if node is self.doublyLinkedList.head and node is self.doublyLinkedList.tail:
                self.doublyLinkedList.head = None
                self.doublyLinkedList.tail = None
            
            elif node is self.doublyLinkedList.head: 
                self.doublyLinkedList.head = node.next
                assert self.doublyLinkedList.head is not None
                self.doublyLinkedList.head.prev = None
            elif node is self.doublyLinkedList.tail: 
                self.doublyLinkedList.tail = node.prev
                assert self.doublyLinkedList.tail is not None
                self.doublyLinkedList.tail.next = None
            else:
                precedingNode = node.prev
                succeedingNode = node.next
                assert precedingNode is not None
                assert succeedingNode is not None

                precedingNode.next = succeedingNode
                succeedingNode.prev = precedingNode

            del self.map[todoId]
        
            self.list.remove({"todoId": todoId, "todo": node.todo})

            return {"status": 1}
        except Exception:
            return {"status": 0}
