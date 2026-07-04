# A Python HTTP Todo List Server

This is a tiny web server built in python that stores and performs operations on a user's todo list.

I built this myself for the purpose of learning and understanding HTTP servers, and how some of these servers and API systems work on a bit of a lower level. The code might not be perfect, but I'm trying to get this working as close to a real server as possible haha.

I'm also using this as a playground to also try to experiment with ways with which an app's backend can be made faster and more performant.

If you have any tips, feel free to share!

# A little bit about the architecture

Currently, there's three data structures that store the todo list itself -

1. A python list
2. A hashmap (just a python dictionary in this case)
3. A doubly linked list

Why?

Well, a list is the fastest to read because the elements are stored in contiguous memory spaces, so the `fetch_todos` method in the `todos` class [here](/classes.py) can quickly read and return the list.

The primary source of truth is the hashmap + linked list combo.

In a linked list, insert and delete ops themselves are O(1), but finding the nodes on which these operations need to be performed is an O(n) task as it requires traversal through the entire list up until the point where the node is found. In order to mitigate this, I have also employed a hashmap (in the form of a python dictionary) to directly store the reference of each todo node and fetch it using the todo id.

As such, I have tried to make this server as fast and performant as possible.

The engineering and maintenance costs of maintaining three data structures and keeping them in sync is recognized, and this is a tradeoff I have accepted.

# Use of AI

As mentioned, this project serves to help me learn about HTTP servers and APIs and familiarize me a bit more with how these things work at a lower level. Thus, the majority of the code in this entire application has been handwritten by me.

I have used AI for reviewing the code I have written and providing me with feedback and guidance. I have also used it for strengthening the typing in this codebase, because that wasn't something that I wanted to deal with right now. I will continue to use it for similar purposes throughout this project.
