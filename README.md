# PyStore

PyStore is a simple NoSQL database greatly inspired by the Firebase Firestore
and [LiteJsonDB](https://github.com/codingtuto/LiteJsonDB). It is a JSON-based
database that allows you to store and retrieve data in a simple and easy way.

## :hammer: Installation

package is not yet available on PyPI, but you can install it from the source code:

```bash
git clone https://github.com/Wilfried-Tech/PyStore
cd PyStore
python setup.py install
```

## :book: Usage

### :gear: Initialize the database

```python
from Pystore import PyStore
from Pystore.engines import PyStoreRawEngine
from Pystore.conf import PyStoreSettings

# Initialize the database
# engine_class is optional, default is PyStoreRawEngine
PyStore.settings = PyStoreSettings(store_dir="data", engine_class=PyStoreRawEngine)
PyStore.initialize()

store = PyStore.get_instance(name="my_store") # name is optional
```

### Create a document in a collection

```python
# Create a document

user1 = store.collection("users").add({"name": "John Doe", "age": 25})
user2 = store.collection("users").doc().set({"name": "Jane Doe", "age": 22})
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
user.delete() # note that delete document does not delete subcollections
```

### Working with collections

```python
# Get a collection reference

users = store.collection("users")
# Get all documents in a collection
all_users = users.get()
```

### Working with subcollections

```python
# Get a document reference
user = store.collection("users").doc('ID')
# Get a subcollection reference
posts = user.collection("posts")
# Add a document to the subcollection
post1 = posts.add({"title": "My first post", "content": "Hello, World!"})
```

### Querying

collections query are not yet implemented


## :rocket: Features

- [x] Simple and easy to use
- [x] NoSQL database
- [x] JSON-based
- [x] Subcollections
- [x] Document CRUD operations
- [ ] Collection CRUD operations
- [ ] Querying
- [ ] Indexing
- [ ] Transactions
- [ ] multi-threading support
- [ ] multi-engine support

## :warning: Disclaimer

This project is still in development and should not be used in production.

## :page_facing_up: License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## :handshake: Contributing

Contributions are welcome! Feel free to contribute to this project.