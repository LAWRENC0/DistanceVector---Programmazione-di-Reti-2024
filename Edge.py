from typing import List

class Edge:
    __slots__: List[str] = ['name', 'weight']
    
    def __init__ (self, name: str, weight: int) -> None:
        self.name: str = name
        self.weight: int = weight
    def print(self):
        return self.name
    