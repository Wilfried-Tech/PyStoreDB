import unittest

from PyStoreDB.core import DocumentSnapshot
from PyStoreDB.test import PyStoreDBTestCase


class User:
    def __init__(self, name: str, id: str = None):
        self.id = id
        self.name = name

    @classmethod
    def from_dict(cls, data: DocumentSnapshot):
        return cls(id=data.id, name=data['name'])

    def to_dict(self):
        return {'name': self.name}


class WithConverterDocumentCRUDTestCase(PyStoreDBTestCase):

    @property
    def users(self):
        return self.store.collection('users').with_converter(
            from_json=lambda x: User.from_dict(x),
            to_json=lambda x: x.to_dict()
        )

    def test_create(self):
        user = self.users.doc()
        self.assertFalse(user.get().exists)
        user.set(User(name='John'))
        self.assertTrue(user.get().exists)
        self.assertEqual(user.get().data.name, 'John')

    def test_update(self):
        user_obj = User(name='John')
        user = self.users.add(user_obj)
        user_obj.name = 'Jane'
        user.update(user_obj)
        self.assertEqual(user.get().get('name'), 'Jane')
        user.update(name='John')
        self.assertEqual(user.get().data.name, 'John')

    def test_delete(self):
        user = self.users.add(User(name='John'))
        self.assertTrue(user.get().exists)
        user.delete()
        self.assertFalse(user.get().exists)

    def test_delete_skip_sub_collection(self):
        class Post:
            def __init__(self, title: str):
                self.title = title

            @classmethod
            def from_dict(cls, data: DocumentSnapshot):
                return cls(title=data['title'])

            def to_dict(self):
                return {'title': self.title}

        user = self.users.add(User(name='John'))
        post = user.collection('posts').with_converter(
            from_json=lambda x: Post.from_dict(x),
            to_json=lambda x: x.to_dict()
        ).add(Post(title='Post'))
        self.assertTrue(user.get().exists)
        self.assertTrue(post.get().exists)
        user.delete()
        self.assertFalse(user.get().exists)
        self.assertTrue(post.get().exists)
        self.assertEqual(post.get().data.title, 'Post')

    def test_get(self):
        user = self.users.add(User(name='Joe'))
        user.set(User(name='John'))
        self.assertEqual(user.get().data.name, 'John')
        self.assertEqual(user.get().get('name'), 'John')


if __name__ == '__main__':
    unittest.main()
