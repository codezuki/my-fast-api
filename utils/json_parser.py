import json
from .file_parser import FileParser


class JsonParser(FileParser):

    async def parse(self, file):

        content = await file.read()

        data = json.loads(content.decode("utf-8"))

        if isinstance(data, dict):
            data = [data]

        return data