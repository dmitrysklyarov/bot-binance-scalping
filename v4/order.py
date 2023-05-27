from enum import Enum

class OrderDirection(Enum):
    BUY = "BUY"
    SELL = "SELL"

class Order:
    filled = 0
    status = ""
    price = 0
    id = 0
    reference = 0

    #cursor to a database
    _cursor = None
    _direction:OrderDirection = None

    def __init__(self, cursor, direction:OrderDirection):
        self._cursor = cursor
        self._direction = direction

    def save(self):
        pass

    def update(self):
        pass

    def cancel(self):
        pass

    def delete(self):
        pass