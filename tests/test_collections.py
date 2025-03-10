import unittest
from datetime import datetime

from PyStoreDB.test import PyStoreDBTestCase


class CollectionQueryTestCase(PyStoreDBTestCase):

    def setUp(self):
        super().setUp()
        self.alice_data = {'name': 'Alice', 'age': 25, 'active': True, 'birthday': datetime(1996, 1, 1)}
        self.store.collection('users').add(self.alice_data)
        self.store.collection('users').add(
            {'name': 'Bob', 'age': 30, 'active': False, 'birthday': datetime(1991, 1, 1)})
        self.store.collection('users').add(
            {'name': 'John', 'age': 28, 'active': True, 'birthday': datetime(1995, 5, 15)})
        self.jane = self.store.collection('users').add(
            {'name': 'Jane', 'age': 32, 'active': False, 'birthday': datetime(1991, 8, 22)})
        self.store.collection('users').add(
            {'name': 'Mike', 'age': 27, 'active': True, 'birthday': datetime(1996, 3, 10)})
        self.store.collection('users').add(
            {'name': 'Anna', 'age': 35, 'active': False, 'birthday': datetime(1988, 12, 5)})
        self.store.collection('users').add(
            {'name': 'Tom', 'age': 40, 'active': True, 'birthday': datetime(1983, 7, 19)})

    def test_list_documents(self):
        snapshot = self.store.collection('users').get()

        self.assertEqual(snapshot.size, 7)

        docs = list(snapshot.docs)
        self.assertEqual(len(docs), 7)
        self.assertEqual(docs[0].data, self.alice_data)
        self.assertEqual(docs[1]['name'], 'Bob')

    def test_can_get_ref_from_query_doc_snapshot(self):
        snapshot = self.store.collection('users').get()
        user = list(snapshot.docs)[0]

        self.assertEqual(user.data.get('name'), 'Alice')
        user.reference.update(name='Joe')
        self.assertEqual(user.get('name'), 'Joe')

    def test_order_by(self):
        snapshot = self.store.collection('users').order_by('name').get()
        docs = list(snapshot.docs)

        self.assertEqual(docs[0].data['name'], 'Alice')
        self.assertEqual(docs[1].data['name'], 'Anna')
        self.assertEqual(docs[2].data['name'], 'Bob')
        self.assertEqual(docs[3].data['name'], 'Jane')
        self.assertEqual(docs[4].data['name'], 'John')
        self.assertEqual(docs[5].data['name'], 'Mike')
        self.assertEqual(docs[6].data['name'], 'Tom')

        snapshot = self.store.collection('users').order_by('age', descending=True).get()
        docs = list(snapshot.docs)

        self.assertEqual(docs[0].data['name'], 'Tom')
        self.assertEqual(docs[1].data['name'], 'Anna')
        self.assertEqual(docs[2].data['name'], 'Jane')
        self.assertEqual(docs[3].data['name'], 'Bob')
        self.assertEqual(docs[4].data['name'], 'John')
        self.assertEqual(docs[5].data['name'], 'Mike')
        self.assertEqual(docs[6].data['name'], 'Alice')

        snapshot = self.store.collection('users').order_by('birthday').get()
        docs = list(snapshot.docs)

        self.assertEqual(docs[0].data['name'], 'Tom')
        self.assertEqual(docs[1].data['name'], 'Anna')
        self.assertEqual(docs[2].data['name'], 'Bob')
        self.assertEqual(docs[3].data['name'], 'Jane')
        self.assertEqual(docs[4].data['name'], 'John')
        self.assertEqual(docs[5].data['name'], 'Alice')
        self.assertEqual(docs[6].data['name'], 'Mike')

        self.store.collection('users').add(
            {'name': 'Zack', 'age': 40, 'active': True, 'birthday': datetime(1991, 1, 1)})
        self.store.collection('users').add(
            {'name': 'Yvan', 'age': 40, 'active': False, 'birthday': datetime(1991, 1, 1)})

        snapshot = (self.store.collection('users').order_by('birthday').order_by('age', descending=True)
                    .order_by('name', descending=True).get())

        docs = list(snapshot.docs)

        self.assertEqual(docs[0].data['name'], 'Tom')
        self.assertEqual(docs[1].data['name'], 'Anna')
        self.assertEqual(docs[2].data['name'], 'Zack')
        self.assertEqual(docs[3].data['name'], 'Yvan')
        self.assertEqual(docs[4].data['name'], 'Bob')
        self.assertEqual(docs[5].data['name'], 'Jane')
        self.assertEqual(docs[6].data['name'], 'John')
        self.assertEqual(docs[7].data['name'], 'Alice')
        self.assertEqual(docs[8].data['name'], 'Mike')

    def test_limit(self):
        snapshot = self.store.collection('users').order_by('name').limit(3).get()
        docs = list(snapshot.docs)

        self.assertEqual(len(docs), 3)
        self.assertEqual(docs[0].data['name'], 'Alice')
        self.assertEqual(docs[1].data['name'], 'Anna')
        self.assertEqual(docs[2].data['name'], 'Bob')

    def test_limit_to_last(self):
        snapshot = self.store.collection('users').order_by('name').limit_to_last(3).get()
        docs = list(snapshot.docs)

        self.assertEqual(len(docs), 3)
        self.assertEqual(docs[0].data['name'], 'John')
        self.assertEqual(docs[1].data['name'], 'Mike')
        self.assertEqual(docs[2].data['name'], 'Tom')

    def test_limit_and_limit_to_last(self):
        with self.assertRaises(AssertionError,
                               msg='Invalid query. You cannot call limit() after limit_to_last(), these are mutually exclusive'):
            self.store.collection('users').order_by('name').limit(3).limit_to_last(3).get()
        with self.assertRaises(AssertionError,
                               msg='Invalid query. You cannot call limit_to_last() after limit(), these are mutually exclusive'):
            self.store.collection('users').order_by('name').limit_to_last(3).limit(3).get()

    def test_defining_cursor_before_order_raise(self):
        msg = '''Calling start_after(), start_at(), start_at_document(),
        start_after_document(), end_before(), end_at() end_at_document(), end_before_document() 
        before calling order_by() clauses raises'''
        doc = self.jane.get()
        with self.assertRaises(AssertionError, msg=msg):
            self.store.collection('users').start_at().order_by('name')
        with self.assertRaises(AssertionError, msg=msg):
            self.store.collection('users').start_at_document(doc).order_by('name')
        with self.assertRaises(AssertionError, msg=msg):
            self.store.collection('users').start_after().order_by('name')
        with self.assertRaises(AssertionError, msg=msg):
            self.store.collection('users').start_after_document(doc).order_by('name')
        with self.assertRaises(AssertionError, msg=msg):
            self.store.collection('users').end_at().order_by('name')
        with self.assertRaises(AssertionError, msg=msg):
            self.store.collection('users').end_at_document(doc).order_by('name')
        with self.assertRaises(AssertionError, msg=msg):
            self.store.collection('users').end_before().order_by('name')
        with self.assertRaises(AssertionError, msg=msg):
            self.store.collection('users').end_before_document(doc).order_by('name')

    def test_start_at(self):
        snapshot = self.store.collection('users').order_by('age').start_at(35).get()
        docs = list(snapshot.docs)

        self.assertEqual(snapshot.size, 2)
        self.assertEqual(docs[0].data['name'], 'Anna')
        self.assertEqual(docs[1].data['name'], 'Tom')

        snapshot = self.store.collection('users').order_by('age').order_by('name').start_at(28, 'Jane').get()
        docs = list(snapshot.docs)

        self.assertEqual(snapshot.size, 3)
        self.assertEqual(docs[0].data['name'], 'John')
        self.assertEqual(docs[1].data['name'], 'Jane')
        self.assertEqual(docs[2].data['name'], 'Tom')

    def test_start_after(self):
        snapshot = self.store.collection('users').order_by('age').start_after(35).get()
        docs = list(snapshot.docs)

        self.assertEqual(snapshot.size, 1)
        self.assertEqual(docs[0].data['name'], 'Tom')

        snapshot = self.store.collection('users').order_by('age').order_by('name').start_after(28, 'Jane').get()
        docs = list(snapshot.docs)

        self.assertEqual(snapshot.size, 1)
        self.assertEqual(docs[0].data['name'], 'Tom')

    def test_end_at(self):
        snapshot = self.store.collection('users').order_by('name').end_at('Jane').get()
        docs = list(snapshot.docs)

        self.assertEqual(snapshot.size, 4)
        self.assertEqual(docs[0].data['name'], 'Alice')
        self.assertEqual(docs[1].data['name'], 'Anna')
        self.assertEqual(docs[2].data['name'], 'Bob')
        self.assertEqual(docs[3].data['name'], 'Jane')

        snapshot = self.store.collection('users').order_by('name').order_by('age').end_at('Jane', 30).get()
        docs = list(snapshot.docs)

        self.assertEqual(snapshot.size, 2)
        self.assertEqual(docs[0].data['name'], 'Alice')
        self.assertEqual(docs[1].data['name'], 'Bob')

    def test_end_before(self):
        snapshot = self.store.collection('users').order_by('name').end_before('Jane').get()
        docs = list(snapshot.docs)

        self.assertEqual(snapshot.size, 3)
        self.assertEqual(docs[0].data['name'], 'Alice')
        self.assertEqual(docs[1].data['name'], 'Anna')
        self.assertEqual(docs[2].data['name'], 'Bob')

        snapshot = self.store.collection('users').order_by('name').order_by('age').end_before('Jane', 30).get()
        docs = list(snapshot.docs)

        self.assertEqual(snapshot.size, 1)
        self.assertEqual(docs[0].data['name'], 'Alice')

    def test_start_at_document(self):
        snapshot = self.store.collection('users').order_by('name').start_at_document(self.jane.get()).get()
        docs = list(snapshot.docs)

        self.assertEqual(snapshot.size, 4)
        self.assertEqual(docs[0].data['name'], 'Jane')
        self.assertEqual(docs[1].data['name'], 'John')
        self.assertEqual(docs[2].data['name'], 'Mike')
        self.assertEqual(docs[3].data['name'], 'Tom')

    def test_start_after_document(self):
        snapshot = self.store.collection('users').order_by('name').start_after_document(self.jane.get()).get()
        docs = list(snapshot.docs)

        self.assertEqual(snapshot.size, 3)
        self.assertEqual(docs[0].data['name'], 'John')
        self.assertEqual(docs[1].data['name'], 'Mike')
        self.assertEqual(docs[2].data['name'], 'Tom')

    def test_end_at_document(self):
        snapshot = self.store.collection('users').order_by('name').end_at_document(self.jane.get()).get()
        docs = list(snapshot.docs)

        self.assertEqual(snapshot.size, 4)
        self.assertEqual(docs[0].data['name'], 'Alice')
        self.assertEqual(docs[1].data['name'], 'Anna')
        self.assertEqual(docs[2].data['name'], 'Bob')
        self.assertEqual(docs[3].data['name'], 'Jane')

    def test_end_before_document(self):
        snapshot = self.store.collection('users').order_by('name').end_before_document(self.jane.get()).get()
        docs = list(snapshot.docs)

        self.assertEqual(snapshot.size, 3)
        self.assertEqual(docs[0].data['name'], 'Alice')
        self.assertEqual(docs[1].data['name'], 'Anna')
        self.assertEqual(docs[2].data['name'], 'Bob')


if __name__ == '__main__':
    unittest.main()
