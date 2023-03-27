import sqlite3


class Database:
    def __init__(self, path_to_db="main.db"):
        self.path_to_db = path_to_db

    @property
    def connection(self):
        return sqlite3.connect(self.path_to_db)

    def execute(self, sql: str, parameters: tuple = None, fetchone=False, fetchall=False, commit=False):
        if not parameters:
            parameters = ()
        connection = self.connection
        connection.set_trace_callback(logger)
        cursor = connection.cursor()
        data = None
        cursor.execute(sql, parameters)

        if commit:
            connection.commit()
        if fetchall:
            data = cursor.fetchall()
        if fetchone:
            data = cursor.fetchone()
        connection.close()
        return data

    def create_table_districts(self):
        sql = """
        CREATE TABLE district (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(50) NOT NULL
        );
        """
        self.execute(sql, commit=True)

    def create_table_farms(self):
        sql = """
        CREATE TABLE farm (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(50) NOT NULL,
        district INT,
        FOREIGN KEY (district) REFERENCES district(id)
        );
        """
        self.execute(sql, commit=True)


    def create_table_farmer(self):
        sql = """
        CREATE TABLE farmer (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(50) NOT NULL,
        farm INT,
        excel VARCHAR(300) NULL,
        FOREIGN KEY (farm) REFERENCES farm(id)
        );
        """
        self.execute(sql, commit=True)


    def create_table_users(self):
        sql = """
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name varchar(255) NOT NULL,
            username varchar(120) NOT NULL,
            telegram_id BIGINT NOT NULL
            );
"""
        self.execute(sql, commit=True)

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join([
            f"{item} = ?" for item in parameters
        ])
        return sql, tuple(parameters.values())

    def add_user(
            self,
            full_name: str,
            username: str,
            telegram_id: int):
        sql = """
        INSERT INTO users(full_name, username, telegram_id) VALUES(?, ?, ?)
        """
        self.execute(sql, parameters=(full_name, username, telegram_id), commit=True)

    def select_all_users(self):
        sql = """
        SELECT * FROM users
        """
        return self.execute(sql, fetchall=True)

    def select_user(self, **kwargs):
        sql = "SELECT * FROM users WHERE "
        sql, parameters = self.format_args(sql, kwargs)

        return self.execute(sql, parameters=parameters, fetchone=True)

    def count_users(self):
        return self.execute("SELECT COUNT(*) FROM users;", fetchone=True)

    def update_user_email(self, email, id):
        sql = f"""
        UPDATE users SET email=? WHERE id=?
        """
        return self.execute(sql, parameters=(email, id), commit=True)

    def delete_users(self):
        self.execute("DELETE FROM users WHERE TRUE", commit=True)


    def add_district(self, name: str):
        sql = """
        INSERT INTO district(name) VALUES(?);
        """
        self.execute(sql, parameters=(name,), commit=True)

    # district
    def get_district(self):
        return self.execute("SELECT * FROM district;", fetchall=True)



    # farm
    def get_farm(self, district_id: int):
        sql = f"""
        SELECT * FROM farm WHERE district = {district_id};
        """
        return self.execute(sql, fetchall=True)

    # farmer
    def get_farmer(self, farm_id: int):
        sql = f"""
        SELECT * FROM farmer WHERE farm = {farm_id};
        """
        return self.execute(sql, fetchall=True)

def logger(statement):
    print(f"""
_____________________________________________________        
Executing: 
{statement}
_____________________________________________________
""")
