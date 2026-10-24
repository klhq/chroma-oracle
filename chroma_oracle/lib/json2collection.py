"""Module for handling the conversion of json input files to collections."""

import json
from typing import TextIO

# from chroma_oracle.lib.container import Container
from chroma_oracle.lib.collection import ContainerCollection
from chroma_oracle.lib.container import TUBE_CAPACITY


def load(file: TextIO, *, reject_invalid: bool = False) -> ContainerCollection:
    """Load a json file into a `ContainerCollection`."""
    content: list[list[str]] = json.load(file)

    for i, tube in enumerate(content):
        if len(tube) > TUBE_CAPACITY:
            raise ValueError(
                f"Tube {i} has {len(tube)} items, which exceeds the maximum capacity of {TUBE_CAPACITY}"
            )

    if reject_invalid:
        colours: dict[str, int] = {}
        for container_list in content:
            for item in container_list:
                if item in colours:
                    colours[item] = colours[item] + 1
                else:
                    colours[item] = 1
        # Check each colour has a count of four
        if not all(count == 4 for count in colours.values()):
            raise ValueError("Invalid colour count")

    return ContainerCollection(content)
