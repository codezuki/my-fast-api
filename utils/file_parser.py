from abc import ABC, abstractmethod


class FileParser(ABC):

    @abstractmethod
    async def parse(self, file):
        pass