import sqlite3

class botdb:
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cur = self.conn.cursor()

    def user_exists(self, user_id):
        result = self.cur.execute(f"SELECT user_id FROM users WHERE user_id = {user_id}")
        return bool(len(result.fetchall()))

    def get_name(self, user_id):
        result = self.cur.execute(f"SELECT name FROM users WHERE user_id = {user_id}")
        return str(result.fetchone()[0])

    def get_status(self, user_id):
        result = self.cur.execute(f"SELECT status FROM users WHERE user_id = {user_id}")
        return str(result.fetchone()[0])

    def new_user(self, user_id):
        user_id
        self.cur.execute(f"INSERT INTO 'users' ('user_id') VALUES ({user_id})")
        return self.conn.commit()

    def set_status(self, user_id, status):
        user_id
        self.cur.execute(f"Update users set status = '{status}' where user_id = {user_id}")
        return self.conn.commit()

    def set_name(self, user_id, name):
        user_id
        self.cur.execute(f"Update users set name = '{name}' where user_id = {user_id}")
        return self.conn.commit()

    def get_prices(self):
        result = self.cur.execute("SELECT * FROM prices")
        return result.fetchall()

    def get_categorys(self):
        result = self.cur.execute("SELECT Category FROM prices")
        return list(set(result.fetchall()))

    def new_order(self, user_id, order, price):
        user_id = int(user_id)
        self.cur.execute(f"INSERT INTO 'orders' VALUES ({user_id}, '{order}', {price})")
        return self.conn.commit()

    def get_orders(self):
        result = self.cur.execute("SELECT * FROM orders")
        return result.fetchall()
    def is_order_in_process(self, user_id):
        result = self.cur.execute(f"SELECT user_id FROM orders").fetchall()
        p = True
        for i in range(len(result)):
            if result[i][0] == user_id:
                p = False
        return p

    def clear_orders(self):
        self.cur.execute("DELETE FROM orders")
        return self.conn.commit()