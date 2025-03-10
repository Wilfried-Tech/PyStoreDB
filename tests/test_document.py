import unittest

from PyStoreDB.errors import PyStoreDBPathError
from PyStoreDB.test import PyStoreDBTestCase


class DocumentCRUDTestCase(PyStoreDBTestCase):

    def test_create(self):
        user = self.store.collection('users').doc()
        self.assertFalse(user.get().exists)
        user.set({'name': 'John'})
        self.assertTrue(user.get().exists)
        self.assertEqual(user.get().get('name'), 'John')

    def test_update(self):
        user = self.store.collection('users').add({'name': 'John'})
        user.update({'name': 'Jane'})
        self.assertEqual(user.get().get('name'), 'Jane')
        user.update(name='John')
        self.assertEqual(user.get().get('name'), 'John')

    def test_delete(self):
        user = self.store.collection('users').add({'name': 'John'})
        self.assertTrue(user.get().exists)
        user.delete()
        self.assertFalse(user.get().exists)

    def test_delete_skip_sub_collection(self):
        user = self.store.collection('users').add({'name': 'John'})
        post = user.collection('posts').add({'title': 'Post'})
        self.assertTrue(user.get().exists)
        self.assertTrue(post.get().exists)
        user.delete()
        self.assertFalse(user.get().exists)
        self.assertTrue(post.get().exists)
        self.assertEqual(post.get().get('title'), 'Post')

    def test_get(self):
        user = self.store.collection('users').doc()
        user.set({'name': 'John'})
        self.assertEqual(user.get().data, {'name': 'John'})
        self.assertEqual(user.get().get('name'), 'John')

    def test_reference(self):
        user = self.store.collection('users').doc()
        user.set({'name': 'John'})
        user2 = user.get().reference
        self.assertEqual(user.get().data, user2.get().data)

    def test_parent(self):
        user = self.store.collection('users').doc()
        user.set({'name': 'John'})
        parent = user.get().reference.parent
        self.assertEqual(parent.path, '/users')

    def test_equality(self):
        user = self.store.collection('users').doc()
        user.set({'name': 'John'})
        user2 = self.store.collection('users').doc(user.id)
        user3 = self.store.doc(user.path)

        self.assertEqual(user.get().data, user2.get().data)
        self.assertEqual(user, user2)
        self.assertEqual(user2, user3)

    def test_doc_id(self):
        user = self.store.collection('users').doc('123')
        self.assertEqual(user.id, '123')
        user = self.store.doc('users/1234')
        self.assertEqual(user.id, '1234')

    def test_invalid_document_path(self):
        self.assertRaises(PyStoreDBPathError, self.store.doc, 'users/1234/1234')

    def test_collection(self):
        user = self.store.collection('users').doc()
        collection = user.collection('posts')
        self.assertEqual(collection.path, '/users/{}/posts'.format(user.id))

    def test_get_unknown_document(self):
        user = self.store.collection('users').doc('123')
        self.assertFalse(user.get().exists)
        with self.assertWarns(UserWarning):
            self.assertIsNone(user.get().data)
        with self.assertWarns(UserWarning):
            self.assertIsNone(user.get().get('name'))

    def test_delete_unknown_document(self):
        user = self.store.collection('users').doc('123')
        self.assertFalse(user.get().exists)
        with self.assertWarns(UserWarning):
            user.delete()

    def test_update_unknown_document(self):
        user = self.store.collection('users').doc('123')
        self.assertFalse(user.get().exists)
        with self.assertRaises(PyStoreDBPathError):
            user.update({'name': 'John'})


if __name__ == '__main__':
    unittest.main()
