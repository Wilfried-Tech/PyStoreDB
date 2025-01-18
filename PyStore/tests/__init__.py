import os
import shutil
from unittest import TestCase

from PyStore import PyStore
from PyStore.conf import PyStoreSettings


class PyStoreTestCase(TestCase):
    test_store_dir = os.path.join(os.path.dirname(__file__), 'store')

    @classmethod
    def setUpClass(cls):
        PyStore.settings = PyStoreSettings(store_dir=cls.test_store_dir)
        if not PyStore.is_initialised:
            PyStore.initialize()
        cls._store = PyStore.get_instance()

    @property
    def store(self):
        return self.__class__._store

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_store_dir):
            shutil.rmtree(cls.test_store_dir)

    def tearDown(self):
        self.store.clear()
