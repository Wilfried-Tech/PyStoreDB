# PyStoreDB

PyStoreDB is a simple NoSQL database greatly inspired by the Firebase Firestore, Django Filters,
and [LiteJsonDB](https://github.com/codingtuto/LiteJsonDB). It is a JSON-based
database that allows you to store and retrieve data in a simple and easy way.

## :bulb: Key Features

- **Simple and easy to use**: PyStoreDB is designed to be simple and easy to use.
- **NoSQL database**: PyStoreDB is a NoSQL database.
- **JSON-based**: PyStoreDB is a JSON-based database.
- **Sub collections**: PyStoreDB supports sub collections.
- **Document CRUD operations**: PyStoreDB supports document CRUD operations.
- **Collection Querying operations**: PyStoreDB supports collection querying operations. and where clause is inspired by
  Django Filters.
- **Firebase Firestore-like**: PyStoreDB is greatly inspired by the Firebase Firestore.

## :hammer: Installation

```bash
# from source
git clone https://github.com/Wilfried-Tech/PyStoreDB
cd PyStoreDB
python setup.py install

# or

pip install PyStoreDB
```

## :book: Usage

### :gear: Initialize the database

```python
from PyStoreDB import PyStoreDB
from PyStoreDB.conf import PyStoreDBSettings
from PyStoreDB.engines import PyStoreDBRawEngine

# Initialize the database
# engine_class is optional, default is PyStoreDBRawEngine
# store_dir can be ':memory:' for in-memory storage
PyStoreDB.settings = PyStoreDBSettings(store_dir="data", engine_class=PyStoreDBRawEngine)
# setting is optional default is PyStoreDBSettings(store_dir="store", engine_class=PyStoreDBRawEngine)
PyStoreDB.initialize()

store = PyStoreDB.get_instance(name="my_store")  # name is optional
```

### Create a document in a collection

```python
# Create a document

user1 = store.collection("users").add({"name": "John Doe", "age": 25})  # auto-generate id
user2 = store.collection("users").doc().set({"name": "Jane Doe", "age": 22})  # auto-generate id
user3 = store.collection("users").doc("user3").set({"name": "Alice Doe", "age": 30})
```

### Working with documents

```python
# Get a document reference by id
user = store.collection("users").doc('ID')
# replace the document with a new one
user.set({"name": "John Doe", "age": 26})
# update the document
user.update({"age": 27}) or user.update(age=27)
# delete the document
user.delete()  # note that delete document does not delete sub collections
```

### Working with collections

```python
# Get a collection reference

users = store.collection("users")
# Get all documents in a collection
all_users = users.get()
```

### Working with sub collections

```python
# Get a document reference
user = store.collection("users").doc('ID')
# Get a sub collection reference
posts = user.collection("posts")
# Add a document to the sub collection
post1 = posts.add({"title": "My first post", "content": "Hello, World!"})
```

### Querying

```python
# Get all documents in a collection with order by age
users = store.collection("users").order_by("age").get()

# Get all documents in a collection with age greater than 25
users = store.collection("users").where(age__gt=25).get()

...
```

## :rocket: Features

- [x] Simple and easy to use
- [x] NoSQL database
- [x] JSON-based
- [x] Sub collections
- [x] Document CRUD operations
- [x] Collection Querying operations
- [ ] Indexing
- [ ] Transactions
- [ ] multi-threading support
- [ ] multi-engine support (partially implemented)

## :warning: Disclaimer

This project is still in development and should not be used in production.

## :page_facing_up: License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## :handshake: Contributing

Contributions are welcome! Feel free to contribute to this project.