from abc import ABC, abstractmethod

class Parser(ABC):
    @abstractmethod
    def start(self):
        pass
