import uuid
from unittest import TestCase

from PyStoreDB import PyStoreDB
from PyStoreDB.conf import PyStoreDBSettings


class PyStoreDBTestCase(TestCase):
    store_dir = ':memory:'

    @classmethod
    def setUpClass(cls):
        PyStoreDB.settings = PyStoreDBSettings(store_dir=cls.store_dir)
        if not PyStoreDB.is_initialised:
            PyStoreDB.initialize()
        cls.store = PyStoreDB.get_instance(uuid.uuid4().hex)

    def tearDown(self):
        self.store.clear()

    @classmethod
    def tearDownClass(cls):
        cls.store = None
        PyStoreDB.clear_instances()
        if cls.store_dir != ':memory:':
            import shutil
            shutil.rmtree(cls.store_dir)
