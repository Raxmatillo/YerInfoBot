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
            ON UPDATE CASCADE
            ON DELETE CASCADE
        );
        """
        self.execute(sql, commit=True)


    def create_table_farmer(self):
        sql = """
        CREATE TABLE if not exists farmer  (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(50) NOT NULL,
        farm INT,
        excel VARCHAR(300) NULL,
        word VARCHAR(300) NULL,
        file_name VARCHAR(300) NULL,
        file_name_map VARCHAR(300) NULL,
        FOREIGN KEY (farm) REFERENCES farm(id)
            ON UPDATE CASCADE
            ON DELETE CASCADE
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


    # district 
    def add_district(self, name: str):
        sql = """
        INSERT INTO district(name) VALUES(?);
        """
        self.execute(sql, parameters=(name,), commit=True)

    def get_district(self):
        return self.execute("SELECT * FROM district;", fetchall=True)

    def get_district_one(self, id: int):
        return self.execute(f"SELECT name FROM district WHERE id={id}", fetchall=True)
    
    def delete_district(self, id: int):
        self.execute(f"DELETE FROM district WHERE id={id}", commit=True)

    # farm
    def add_farm(self, name: str, district: int):
        sql = """
        INSERT INTO farm(name, district) VALUES(?, ?);
        """
        self.execute(sql, parameters=(name,district), commit=True)

    def get_farm(self, district_id: int):
        sql = f"""
        SELECT * FROM farm WHERE district = {district_id};
        """
        return self.execute(sql, fetchall=True)
    
    def get_farm_info(self, farm_id: int):
        sql = f"""SELECT farm.id, district.id, farm.name, district.name
        FROM farm INNER JOIN district ON district.id = farm.district WHERE farm.id = {farm_id};"""
        return self.execute(sql, fetchall=True)
    
    def get_farm_one(self, farm_id: int):
        return self.execute(f"SELECT name FROM farm WHERE id={farm_id}", fetchall=True)

    def delete_farm(self, id: int):
        self.execute(f"DELETE FROM farm WHERE id={id}", commit=True)


    # farmer
    def add_farmer(self, name: str, farm: int):
        sql = f"""
        INSERT INTO farmer (name, farm) VALUES (?, ?)
        """
        self.execute(sql, parameters=(name, farm), commit=True)

    def get_farmer(self, farm_id: int):
        sql = f"""
        SELECT * FROM farmer WHERE farm = {farm_id};
        """
        return self.execute(sql, fetchall=True)

    def get_farmer_info(self, farmer_id: int):
        sql = f"""SELECT farmer.id, farmer.name, farm.name, district.name, 
        farmer.excel, farmer.file_name, farmer.file_name_map 
        FROM farmer INNER JOIN farm ON farmer.farm = farm.id INNER JOIN 
        district ON district.id = farm.district WHERE farmer.id = {farmer_id};"""
        return self.execute(sql, fetchall=True)

    def get_farmer_one(self, farmer_id: int):
        return self.execute(f"SELECT * FROM farmer WHERE id={farmer_id}",
                            fetchall=True)
    
    def update_excel(self, excel: str, file_name: str, id: int):
        sql = "UPDATE farmer SET excel=?, file_name=? WHERE id=?"
        self.execute(sql, parameters=(excel, file_name, id), commit=True)

    def update_word(self, word: str, file_name_map: str, id: int):
        sql = "UPDATE farmer SET word=?, file_name_map=? WHERE id=?"
        self.execute(sql, parameters=(word, file_name_map, id), commit=True)

    def clear_farmer(self):
        for i in range(19):
            self.execute("UPDATE farmer SET excel=NULL", commit=True)
    
    def delete_farmer(self, id: int):
        self.execute(f"DELETE FROM farmer WHERE id={id}", commit=True)

def logger(statement):
    print(f"""
_____________________________________________________        
Executing: 
{statement}
_____________________________________________________
""")
