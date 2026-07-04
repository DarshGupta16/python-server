# A Python HTTP Todo List Server

This is a tiny web server built in python that stores and performs operations on a user's todo list.

I built this myself for the purpose of learning and understanding HTTP servers, and how some of these servers and API systems work on a bit of a lower level. The code might not be perfect, but I'm trying to get this working as close to a real server as possible haha.

I'm also using this as a playground to also try to experiment with ways with which an app's backend can be made faster and more performant.

If you have any tips, feel free to share!

# Getting Started

To run the server locally, make sure you've got python installed, and then run:

```bash
# Install dependencies (shortuuid is needed for the todo ids)
.venv/bin/pip install shortuuid

# Start the server
.venv/bin/python server.py
```

You can test the server using curl:

```bash
# Check if the server is running
curl http://localhost:8080/

# Add a todo
curl -X POST http://localhost:8080/add-todo -F "todo=Buy Milk"

# Fetch your todos
curl http://localhost:8080/fetch-todos

# Remove a todo (using the todoId returned from fetch-todos)
curl -X POST http://localhost:8080/remove-todo -F "todoId=uuid-here"
```

# API Endpoints

Here are the endpoints you can hit:

- `GET /` - Just checks if the app is up and running.
- `GET /fetch-todos` - Returns a list of all your current todos.
- `POST /add-todo` - Adds a new todo to the list. Needs a `multipart/form-data` payload containing `todo`.
- `POST /remove-todo` - Removes a todo from the list. Needs a `multipart/form-data` payload containing `todoId`.

# Architectural decisions I've made.

There were initially three data structures that store the todo list itself -

1. A python list
2. A hashmap (just a python dictionary in this case)
3. A doubly linked list

Why?

Well, a list is the fastest to read because the elements are stored in contiguous memory spaces, so the `fetch_todos` method in the `todos` class [here](/classes.py) can quickly read and return the list.

The primary source of truth is the hashmap + linked list combo.

In a linked list, insert and delete ops themselves are O(1), but finding the nodes on which these operations need to be performed is an O(n) task as it requires traversal through the entire list up until the point where the node is found. In order to mitigate this, I have also employed a hashmap (in the form of a python dictionary) to directly store the reference of each todo node and fetch it using the todo id.

As such, I had tried to make this server as fast and performant as possible.

The engineering and maintenance costs of maintaining three data structures and keeping them in sync is recognized, and this is a tradeoff I had accepted.

## However

My decisions on the architecture changed when I learned that python does not actually store the data itself in contiguous memory spaces as I had expected. Rather, it stores pointers in contiguous memory spaces, and as such, iterating over or rebuilding a list in python is an O(n) op anyway.

Thus, maintaining three data structures as I was doing initially, is something that would be better suited to a language such as Rust rather than Python.

In light of this new knowledge I've discovered, the Todos class has been updated to use a simple python dictionary instead, for O(1) insert and delete ops, and O(n) list conversion. The resulting memory footprint is also lower than what I had initially, and the code is much smaller and cleaner.

# Use of AI

As mentioned, this project serves to help me learn about HTTP servers and APIs and familiarize me a bit more with how these things work at a lower level. Thus, the majority of the code in this entire application has been handwritten by me.

I have used AI for reviewing the code I have written and providing me with feedback and guidance. I have also used it for strengthening the typing in this codebase, because that wasn't something that I wanted to deal with right now. I will continue to use it for similar purposes throughout this project.
