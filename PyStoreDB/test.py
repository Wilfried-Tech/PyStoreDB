import uuid
from unittest import TestCase

from PyStoreDB import PyStoreDB
from PyStoreDB.conf import PyStoreDBSettings


class PyStoreDBTestCase(TestCase):
    """Test case for PyStoreDB functionality."""

    store_dir = ':memory:'

    @classmethod
    def setUpClass(cls):
        """Set up the test class by initializing PyStoreDB settings and instance."""
        PyStoreDB.settings = PyStoreDBSettings(store_dir=cls.store_dir)
        if not PyStoreDB.is_initialised:
            PyStoreDB.initialize()
        cls.store = PyStoreDB.get_instance(uuid.uuid4().hex)

    def tearDown(self):
        """Clear the store after each test."""
        self.store.clear()

    @classmethod
    def tearDownClass(cls):
        """Tear down the test class by clearing instances and removing the store directory if not in memory."""
        cls.store = None
        PyStoreDB.clear_instances()
        if cls.store_dir != ':memory:':
            import shutil
            shutil.rmtree(cls.store_dir)
