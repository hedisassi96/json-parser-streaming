
## Problem statement

This problem was given as a take home exercise as part of a job application.

Develop a Streaming JSON Parser

Objective:
You are required to implement a streaming JSON parser that processes JSON data incrementally in Python.
For this task we consider a subset of JSON, where values consist solely of strings and objects. Escape sequences in strings or duplicate keys in objects are not expected.
The primary motivation for this task is to simulate partial responses as would be encountered in the streaming output of a large language model (LLM).
Even if the input JSON data is incomplete, the parser should be able to return the current state of the parsed JSON object at any given point in time.
This should include partial string-values and objects, but not the keys themselves, i.e. `{"test": "hello", "worl` is a partial representation of `{"test": "hello"}`, but not `{"test": "hello", "worl": ""}`.
Only once the value type of the key is determined should the parser return the key-value pair.
String values on the other hand can be partially returned: `{"test": "hello", "country": "Switzerl` is a partial representation of `{"test": "hello", "country": "Switzerl"}`.

The parser should be efficient in terms of algorithmic complexity.

Create a class named `StreamingJsonParser`.
Implement the following methods within this class:

- `__init__()`: Initializes the parser.
- `consume(buffer: str)`: Consumes a chunk of JSON data.
- `get()`: Returns the current state of the parsed JSON object as an appropriate Python object.



## Tests

Run tests using:

`python3 -m unittest discover -p *test_streaming_json_parser.py`

