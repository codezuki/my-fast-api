import csv
import io

from .file_parser import FileParser


class CsvParser(FileParser):

    async def parse(self, file):

        content = await file.read()

        text = content.decode("utf-8")

        reader = csv.DictReader(io.StringIO(text))

        return list(reader)