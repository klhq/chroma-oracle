"""Tests for the json2collection module."""

import io
import pathlib
from unittest import TestCase

from chroma_oracle.lib import json2collection
from chroma_oracle.lib.collection import ContainerCollection


class TestJson2Collection(TestCase):
    """Test cases for the json2collection class."""

    def test_load_valid(self):
        """Test loading from a valid json file."""
        expected = ContainerCollection(
            [
                ["RED", "RED", "GREEN", "GREEN"],
                ["RED", "RED", "GREEN", "GREEN"],
                [],
            ]
        )
        with pathlib.Path("./levels/debug.json").open(encoding="utf-8") as reader:
            collection = json2collection.load(reader)
        self.assertEqual(collection, expected)

    def test_load_invalid_ignore(self):
        """Test loading from a invalid json file and not rejecting it."""
        expected = ContainerCollection(
            [
                ["RED", "RED", "GREEN", "GREEN"],
                ["RED", "RED", "RED", "GREEN"],
                [],
            ]
        )
        with pathlib.Path("./levels/bad.json").open(encoding="utf-8") as reader:
            collection = json2collection.load(reader, reject_invalid=False)
        self.assertEqual(collection, expected)

    def test_load_invalid_(self):
        """Test loading from a invalid json file and rejecting it."""
        with self.assertRaises(ValueError):  # noqa: SIM117
            with pathlib.Path("./levels/bad.json").open(encoding="utf-8") as reader:
                _ = json2collection.load(reader, reject_invalid=True)

    def test_tube_exactly_four_accepted(self):
        """Test that tubes with exactly four items are accepted."""
        content = '[["RED", "GREEN", "BLUE", "YELLOW"], []]'
        reader = io.StringIO(content)
        collection = json2collection.load(reader)
        self.assertEqual(len(collection), 2)
        self.assertEqual(len(collection[0]), 4)
        self.assertEqual(len(collection[1]), 0)

    def test_tube_oversized_five_rejected(self):
        """Test that a tube with 5 items is rejected with tube index and length."""
        content = '[["RED"], ["RED", "BLUE", "GREEN", "YELLOW", "ORANGE"]]'
        reader = io.StringIO(content)
        with self.assertRaises(ValueError) as cm:
            json2collection.load(reader)

        msg = str(cm.exception)
        self.assertIn("Tube 1", msg)
        self.assertIn("5", msg)
