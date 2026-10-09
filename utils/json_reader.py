import json
from pathlib import Path


class JsonReader:
    ROOT_PATH = Path(__file__).resolve().parent.parent

    @staticmethod
    def read_json(file_name):
        file_path = JsonReader.ROOT_PATH / "testdata" / file_name

        with open(file_path) as file:
            return json.load(file)