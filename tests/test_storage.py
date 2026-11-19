import unittest
from src.storage import connect, save, recent, search


class StorageTests(unittest.TestCase):
    def test_memory_and_search(self):
        db = connect(":memory:")
        save(db, "user", "inverter warranty")
        save(db, "assistant", "Please provide serial number")
        self.assertEqual(len(recent(db)), 2)
        self.assertEqual(len(search(db, "inverter")), 1)
        db.close()


if __name__ == "__main__":
    unittest.main()
