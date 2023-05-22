'''
0 - id bigint PRIMARY KEY NOT NULL,
1 - date timestamp NOT NULL DEFAULT now(), 
2 - type varchar (16) NOT NULL,
3 - status varchar (16) NOT NULL,
4 - quantity real NOT NULL,
5 - price real NOT NULL,
6 - profit profit NOT NULL,
7 - buy_id bigint NOT NULL,
'''

class Order():
    side = None
    id = 0
    type = ''
    status = ''
    quantity = 0
    price = 0
    profit = 0
    buy_id = 0
    satisfied = False

    def __init__(self, side, data):
        if data is None:
            return None
        self.side = side
        self.id = data[0]
        self.type = data[2]
        self.status = data[3]
        self.quantity = data[4]
        self.price = data[5]
        self.profit = data[6]
        if side == 'sell':
            self.buy_id = data[7]
        else:
            self.satisfied = data[7]