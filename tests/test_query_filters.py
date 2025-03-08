import unittest

from PyStore.constants import Json
from PyStore.core import QuerySnapshot
from PyStore.core.filters import Q, F
from PyStore.test import PyStoreTestCase


class FiltersTestCase(PyStoreTestCase):

    def assertQueryContains(self, query: QuerySnapshot[Json], subset: Json, msg=None):
        self.assertTrue(any(
            all(doc.get(key) == value for key, value in subset.items())
            for doc in query.docs
        ), msg=msg)

    def filter(self, *args, **kwargs):
        users = self.store.collection('users')
        return users.where(*args, **kwargs).get()

    def exclude(self, *args, **kwargs):
        users = self.store.collection('users')
        return users.exclude(*args, **kwargs).get()

    def test_isnull_lookup(self):
        query = self.filter(country__isnull=True)
        self.assertEqual(len(query), 1)
        self.assertQueryContains(query, {'name': 'Jane', 'age': 20})

        query = self.filter(country__isnull=False)
        self.assertEqual(len(query), 2)
        self.assertQueryContains(query, {'name': 'John', 'age': 25})
        self.assertQueryContains(query, {'name': 'Alice', 'age': 30})

        query = self.filter(~Q(country__isnull=True))
        self.assertEqual(len(query), 2)
        self.assertQueryContains(query, {'name': 'John', 'age': 25})
        self.assertQueryContains(query, {'name': 'Alice', 'age': 30})

        with self.assertRaises(ValueError, msg='isnull lookup only accepts True or False'):
            docs = self.filter(country__isnull='True').docs

    def test_f_expression(self):
        query = self.filter(age=F('age'))
        self.assertEqual(len(query), 3)

        query = self.filter(bio__contains=F('name'))
        self.assertEqual(len(query), 2)

        query = self.filter(bio__endswith=F('name'))
        self.assertEqual(len(query), 1)

    def test_filter_and(self):
        query = self.filter(name='John')
        self.assertEqual(len(query), 1)
        self.assertQueryContains(query, {'name': 'John', 'age': 25})

        query = self.filter(name='John', age__lt=20)
        self.assertEqual(len(query), 0)

        query = self.filter(age__in=[20, 25])
        self.assertEqual(len(query), 2)
        self.assertQueryContains(query, {'name': 'John', 'age': 25})
        self.assertQueryContains(query, {'name': 'Jane', 'age': 20})

        query = self.filter(~Q(name='John'), age__lt=30)
        self.assertEqual(len(query), 1)
        print(query)
        self.assertQueryContains(query, {'name': 'Jane', 'age': 20})

    def test_filter_or(self):
        query = self.filter(Q(name='John') | Q(age__lt=20))
        self.assertEqual(len(query), 1)
        self.assertQueryContains(query, {'name': 'John', 'age': 25})

        query = self.filter(Q(name='John') | Q(age__gte=30))
        self.assertEqual(len(query), 2)
        self.assertQueryContains(query, {'name': 'John', 'age': 25})
        self.assertQueryContains(query, {'name': 'Alice', 'age': 30})

    def test_filter_exclude(self):
        query = self.exclude(name='John')
        self.assertEqual(len(query), 2)
        self.assertQueryContains(query, {'name': 'Jane', 'age': 20})
        self.assertQueryContains(query, {'name': 'Alice', 'age': 30})

        query = self.exclude(Q(name='John') | Q(age__lt=20))
        self.assertEqual(len(query), 2)
        self.assertQueryContains(query, {'name': 'Jane', 'age': 20})
        self.assertQueryContains(query, {'name': 'Alice', 'age': 30})

        query = self.exclude(Q(name='John') | Q(age__gte=30))
        self.assertEqual(len(query), 1)
        self.assertQueryContains(query, {'name': 'Jane', 'age': 20})

    def test_filter_inexistant_field(self):
        with self.assertRaises(ValueError, msg='Field `email` does not exist'):
            docs = self.filter(email='john@pystore.com').docs

    def setUp(self):
        super().setUp()
        self.store.collection('users').add({'name': 'John', 'age': 25, 'country': 'USA', 'bio': 'John Doe a developer'})
        self.store.collection('users').add({'name': 'Jane', 'age': 20, 'country': None, 'bio': 'Designer, Jane'})
        self.store.collection('users').add({'name': 'Alice', 'age': 30, 'country': 'UK', 'bio': 'I am a manager'})


if __name__ == '__main__':
    unittest.main()
