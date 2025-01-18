import unittest

from PyStore.tests import PyStoreTestCase


class CollectionQueryTestCase(PyStoreTestCase):

    def setUp(self):
        self.store.collection('users').add({'name': 'Alice'})
        self.store.collection('users').add({'name': 'Bob'})
        self.store.collection('users').add({'name': 'Charlie'})

    def test_list_documents(self):
        snapshot = self.store.collection('users').get()

        self.assertEqual(snapshot.size, 3)
        docs = list(snapshot.docs)
        self.assertEqual(len(docs), 3)
        self.assertEqual(docs[0].data, {'name': 'Alice'})
        self.assertEqual(docs[1]['name'], 'Bob')

    def test_can_get_ref_from_query_doc_snapshot(self):
        self.store.collection('users').add({'name': 'Alice'})

        snapshot = self.store.collection('users').get()
        user = list(snapshot.docs)[0]
        user.reference.update(name='Joe')

        self.assertEqual(user.data, {'name': 'Joe'})


if __name__ == '__main__':
    unittest.main()
