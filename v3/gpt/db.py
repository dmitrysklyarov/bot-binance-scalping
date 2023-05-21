import psycopg2

class DB:
    def __init__(self, config):
        self.config = config

        self.conn = psycopg2.connect(
            dbname=self.config.get('database', 'name'),
            user=self.config.get('database', 'user'),
            password=self.config.get('database', 'password'),
            host=self.config.get('database', 'host'),
            port=self.config.get('database', 'port')
        )

    def insert_buy_order(self, order_id, created_at, price, amount, status):
        with self.conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO buy_orders (order_id, created_at, updated_at, price, amount, status)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (order_id, created_at, created_at, price, amount, status))
            row = cursor.fetchone()
            return row[0]

    def insert_sell_order(self, order_id, created_at, price, amount, status, buy_order_id):
        with self.conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO sell_orders (order_id, created_at, updated_at, price, amount, status, buy_order_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (order_id, created_at, created_at, price, amount, status, buy_order_id))
            row = cursor.fetchone()
            return row[0]
