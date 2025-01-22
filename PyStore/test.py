import uuid
from unittest import TestCase

from PyStore import PyStore
from PyStore.conf import PyStoreSettings


class PyStoreTestCase(TestCase):
    store_dir = ':memory:'

    @classmethod
    def setUpClass(cls):
        PyStore.settings = PyStoreSettings(store_dir=cls.store_dir)
        if not PyStore.is_initialised:
            PyStore.initialize()
        cls.store = PyStore.get_instance(uuid.uuid4().hex)

    def tearDown(self):
        self.store.clear()

    @classmethod
    def tearDownClass(cls):
        cls.store = None
        PyStore.clear_instances()
