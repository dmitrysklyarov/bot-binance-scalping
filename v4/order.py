from enum import Enum

class OrderDirection(Enum):
    BUY = "buy"
    SELL = "sell"

class Order:
    #cursor to a database
    _cursor = None
    _connection = None

    #order direction
    _direction:OrderDirection = None

    #database fields
    _id:int = 0
    _type:str = None
    _status:str = None
    _quantity:float = 0
    _filled:float = 0
    _price:float = 0
    _commission:float = 0
    _profit:float = 0
    _satisfied:bool = None
    _buy_id:int = 0

    def __init__(self, connection, direction:OrderDirection, values:tuple):
        self._connection = connection
        self._cursor = connection.cursor()
        self._direction = direction
        self._id = int(values[0])
        self._type = str(values[2])
        self._status = str(values[3])
        self._quantity = float(values[4])
        self._filled = float(values[5])
        self._price = float(values[6])
        self._commission = float(values[7])
        self._profit = float(values[8])
        if direction == OrderDirection.BUY:
            self._satisfied = bool(values[9])
        else:
            self._buy_id = int(values[9])

    #DATABASE METHODS
    def insert(self):
        self._cursor.execute(f'''INSERT INTO {self._direction.value} 
                                 (id, type, status, quantity, filled, price, commission, profit)
                                 VALUES ({self._id}, '{self._type}', '{self._status}', {self._quantity}, {self._filled}, {self._price}, {self._commission}, {self._profit})''')
        if self._direction == OrderDirection.SELL:
            self._cursor.execute(f'''UPDATE {self._direction.value} SET 
                                     buy_id = {self._buy_id}
                                     WHERE id = {self._id}''')

        self._connection.commit()
        return self

    def update(self):
        self._cursor.execute(f'''UPDATE {self._direction.value} 
                                 SET status = '{self._status}', filled = {self._filled}, price = {self._price}, commission = {self._commission}, profit = {self._profit}
                                 WHERE id = {self._id}''')
        #update satisfaction if sell order is completed
        if self._direction == OrderDirection.SELL and self._status == "FILLED":
            self._cursor.execute(f'''UPDATE buy SET 
                                     satisfied = True
                                     WHERE id = {self._buy_id}''')
        self._connection.commit()
        return self

    def delete(self):
        self._cursor.execute(f'''DELETE FROM {self._direction.value} WHERE id = {self._id}''')
        self._connection.commit()
        return self
    
    def getCorrespondingBuyOrder(self):
        if self._direction == OrderDirection.BUY:
            return None
        self._cursor.execute(f'''SELECT * FROM buy WHERE id = {self._buy_id}''')
        return Order(self._connection, OrderDirection.BUY, self._cursor.fetchone())