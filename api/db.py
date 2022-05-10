import sqlite3

def row_to_dict(cursor, row):
    data = {}
    for idx, col in enumerate(cursor.description):
        data[col[0]] = row[idx]
    return data

class DB:
    
    @classmethod
    def get_connection(cls):
        conn = sqlite3.connect('database.db')
        conn.row_factory = row_to_dict
        return conn

    @classmethod
    def create(cls):
        conn = cls.get_connection()
        c = conn.cursor()
        sql_file = open("create_db.sql")
        sql_as_string = sql_file.read()
        c.execute(sql_as_string)
        conn.commit()
        conn.close()

    @classmethod
    def one(cls, query, params = ()):
        conn = cls.get_connection()
        c = conn.cursor()
        c.execute(query, params)
        row = c.fetchone()
        conn.close()
        return row

    @classmethod
    def all(cls, query, params=()):
        conn = cls.get_connection()
        cur = conn.cursor()
        cur.execute(query, params)
        rows = cur.fetchall()
        conn.close()
        return rows
    
    @classmethod
    def insert(cls, query, params=()):
        conn = cls.get_connection()
        cur = conn.cursor()
        cur.execute(query, params)
        id = cur.lastrowid
        conn.commit()
        conn.close()
        return id
    
    @classmethod
    def update(cls, query, params=()):
        conn = cls.get_connection()
        cur = conn.cursor()
        cur.execute(query, params)
        conn.commit()
        conn.close()

    @classmethod
    def delete(cls, query, params=()):
        conn = cls.get_connection()
        cur= conn.cursor()
        cur.execute(query, params)
        conn.commit()
        conn.close()
