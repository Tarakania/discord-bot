class Item:
    def __init__(self, id: int, name: str = ""):
        self.id = id
        self.name = name

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"<Item id={self.id} name={self.name}>"


class Craftable:
    pass
