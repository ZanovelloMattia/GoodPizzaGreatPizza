import sqlite3
import datetime
conn = None
c = None

def open():
    global conn, c

    conn = sqlite3.connect('pizzaDatabase.db', detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES) #connette la variabile al database
    c = conn.cursor() #crea un nuovo cursore

def close():
    conn.commit() #Esegue i comandi

    conn.close() #Chiude la connessione

def create_table_pizzerias():    
    #Tabella per la creazione della pizzeria
    c.execute("""CREATE TABLE IF NOT EXISTS pizzerias (   
            ID_pizzeria INTEGER NOT NULL PRIMARY KEY,
            pizzeria_name text NOT NULL UNIQUE,
            owner_name text NOT NULL
            )
            """)

def create_table_employees():
    #Tabella per la creazione dei dipendenti
    c.execute("""CREATE TABLE IF NOT EXISTS employees (    
            ID_employee INTEGER NOT NULL PRIMARY KEY,
            ID_pizzeria INTEGER NOT NULL,
            name text NOT NULL,
            surname text NOT NULL,
            birthdate TIMESTAMP NOT NULL,
            FOREIGN KEY(ID_pizzeria) REFERENCES pizzerias(ID_pizzeria)
            )
            """)
    
def create_table_days():
    #Tabella per la creazione dei giorni
    c.execute("""CREATE TABLE IF NOT EXISTS days (     
            ID_day INTEGER NOT NULL PRIMARY KEY,
            ID_employee1 INTEGER NOT NULL,
            ID_employee2 INTEGER NOT NULL,
            ID_employee3 INTEGER NOT NULL,
            FOREIGN KEY(ID_employee1) REFERENCES employees(ID_employee),
            FOREIGN KEY(ID_employee2) REFERENCES employees(ID_employee),
            FOREIGN KEY(ID_employee3) REFERENCES employees(ID_employee)
            )
            """)

def create_table_shifts():
    #Tabella per la creazione della settimana
    c.execute("""CREATE TABLE IF NOT EXISTS shifts (     
            ID_shift INTEGER NOT NULL PRIMARY KEY,
            timestamp TIMESTAMP NOT NULL UNIQUE,
            ID_pizzeria INTEGER NOT NULL,
            ID_day1 INTEGER NOT NULL,
            ID_day2 INTEGER NOT NULL,
            ID_day3 INTEGER NOT NULL,
            ID_day4 INTEGER NOT NULL,
            ID_day5 INTEGER NOT NULL,
            FOREIGN KEY(ID_pizzeria) REFERENCES pizzeria(ID_pizzeria),
            FOREIGN KEY(ID_day1) REFERENCES days(ID_day),
            FOREIGN KEY(ID_day2) REFERENCES days(ID_day),
            FOREIGN KEY(ID_day3) REFERENCES days(ID_day),
            FOREIGN KEY(ID_day4) REFERENCES days(ID_day),
            FOREIGN KEY(ID_day5) REFERENCES days(ID_day)
            )
            """)

def create_table_session():
    #Tabella per la sessione
    c.execute("""CREATE TABLE IF NOT EXISTS session (
              ID_session INTEGER NOT NULL PRIMARY KEY,
              UUID text NOT NULL UNIQUE,
              ID INTEGER NOT NULL,
              permission INTEGER NOT NULL,
              expire TIMESTAMP NOT NULL
              )
        """)

def create_table_requests():
    c.execute("""CREATE TABLE IF NOT EXISTS requests (
                ID_request INTEGER NOT NULL PRIMARY KEY,
                ID_pizzeria INTEGER NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                ID_questioner INTEGER NOT NULL,
                ID_questioner_day INTEGER NOT NULL,
                questioner_index INTEGER NOT NULL,
                ID_questioned INTEGER NOT NULL,
                ID_questioned_day INTEGER NOT NULL,
                questioned_index INTEGER NOT NULL,
                FOREIGN KEY(ID_pizzeria) REFERENCES pizzeria(ID_pizzeria),
                FOREIGN KEY(ID_questioner_day) REFERENCES days(ID_day),
                FOREIGN KEY(ID_questioned_day) REFERENCES days(ID_day)
                )
                """)

def drop_table_pizzerias():
    c.execute("""DROP TABLE pizzerias""")

def drop_table_employees():
    c.execute("""DROP TABLE employees""")

def drop_table_days():
    c.execute("""DROP TABLE days""")

def drop_table_shifts():
    c.execute("""DROP TABLE shifts""")

def drop_table_session():
    c.execute("""DROP TABLE session""")

def drop_table_requests():
    c.execute("""DROP TABLE requests""")

def insert_pizzeria(pizzeria_name : str, owner_name : str) -> int:
    c.execute("INSERT INTO pizzerias (pizzeria_name, owner_name) VALUES (?, ?)",
              (pizzeria_name, owner_name))
    c.execute("SELECT last_insert_rowid();")
    number = c.fetchone()
    return number[0]

def insert_employee(ID_pizzeria : int, name : str, surname : str, birthdate : str) -> int:
    c.execute("INSERT INTO employees (ID_pizzeria, name, surname, birthdate) VALUES (?, ?, ?, ?)",
              (ID_pizzeria, name, surname, birthdate))
    c.execute("SELECT last_insert_rowid();")
    number = c.fetchone()
    return number[0]

def insert_days(ID_employee1 : int, ID_employee2 : int, ID_employee3 : int) -> int:
    c.execute("INSERT INTO days (ID_employee1, ID_employee2, ID_employee3) VALUES (?, ?, ?)",
              (ID_employee1, ID_employee2, ID_employee3))
    c.execute("SELECT last_insert_rowid();")
    number = c.fetchone()
    return number[0]

def insert_shift(timestamp : str, ID_pizzeria : int, ID_day1 : int, ID_day2 : int, ID_day3 : int, ID_day4 : int, ID_day5 : int) -> int:
    c.execute("INSERT INTO shifts (timestamp, ID_pizzeria, ID_day1, ID_day2, ID_day3, ID_day4, ID_day5) VALUES (?, ?, ?, ?, ?, ?, ?)",
              (timestamp, ID_pizzeria, ID_day1, ID_day2, ID_day3, ID_day4, ID_day5))
    c.execute("SELECT last_insert_rowid();")
    number = c.fetchone()
    return number[0]

def insert_session(UUID : str, ID : int, permission : int, expire : datetime.datetime) -> int:
    c.execute("INSERT INTO session (UUID, ID, permission, expire) VALUES (?, ?, ?, ?)",
              (UUID, ID, permission, expire))
    c.execute("SELECT last_insert_rowid();")
    number = c.fetchone()
    return number[0]
  
def upload_shift(shift_dict, ID_pizzeria) -> int:
    ID_day = []
    for i in range (5):
        insert_days(shift_dict["day" + str(i + 1)]["0"],shift_dict["day" + str(i + 1)]["1"], shift_dict["day" + str(i + 1)]["2"])
        c.execute("SELECT last_insert_rowid();") 
        ID_day_tmp = c.fetchone()
        ID_day.append(ID_day_tmp[0])


    now = datetime.datetime.now()
    ID_shift = insert_shift(now, ID_pizzeria, ID_day[0], ID_day[1], ID_day[2], ID_day[3], ID_day[4])

    return ID_shift
    
def insert_request(ID_pizzeria: int, timestamp: datetime.datetime, ID_questioner: int, ID_questioner_day: int, questioner_index: int, ID_questioned: int, ID_questioned_day: int, questioned_index: int) -> int:
    c.execute("INSERT INTO requests (id_pizzeria, timestamp, ID_questioner, ID_questioner_day, questioner_index, ID_questioned, ID_questioned_day, questioned_index) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
              (ID_pizzeria, timestamp, ID_questioner, ID_questioner_day, questioner_index, ID_questioned, ID_questioned_day, questioned_index))
    c.execute("SELECT last_insert_rowid();")
    number = c.fetchone()
    return number[0]     

def get_shift_from_timestamp(ID_pizzeria, timestamp) -> dict: 
    c.execute("""
        SELECT ID_day1, ID_day2, ID_day3, ID_day4, ID_day5
        FROM shifts
        WHERE ID_pizzeria = ? AND timestamp = ?
    """, (ID_pizzeria, timestamp))
    shift = c.fetchone()

    if not shift:
        return None  
    else:
        ID_days = list(shift)
        shift_dict = {}

        for ID_day in ID_days:
            c.execute("""
                SELECT emp1.ID_employee, emp1.name, emp1.surname, emp1.birthdate,
                    emp2.ID_employee, emp2.name, emp2.surname, emp2.birthdate,
                    emp3.ID_employee, emp3.name, emp3.surname, emp3.birthdate
                FROM days
                INNER JOIN employees AS emp1 ON days.ID_employee1 = emp1.ID_employee
                INNER JOIN employees AS emp2 ON days.ID_employee2 = emp2.ID_employee
                INNER JOIN employees AS emp3 ON days.ID_employee3 = emp3.ID_employee
                WHERE days.ID_day = ?
            """, (ID_day,))
            day = c.fetchone()
            if day:
                shift_dict[ID_day] = {
                    "0": {"id": day[0], "name": day[1], "surname": day[2], "birthdate": day[3]},
                    "1": {"id": day[4], "name": day[5], "surname": day[6], "birthdate": day[7]},
                    "2": {"id": day[8], "name": day[9], "surname": day[10], "birthdate": day[11]},
                }

    return shift_dict

def get_all_shifts():

    c.execute("SELECT * FROM shifts;")
    shifts = c.fetchall()

    shift_dict = {}
    for shift in shifts:
        ID_shift, timestamp, ID_pizzeria, *ID_days = shift

        day_data = {}
        i = 0
        for ID_day in ID_days:
            c.execute("SELECT * FROM days WHERE id = ?;", (ID_day,))
            day = c.fetchone()
            day_data["day" + str(i + 1)] = {
                "0": {"id": day[1]},
                "1": {"id": day[2]},
                "2": {"id": day[3]},
            }
            i += 1

        shift_dict[timestamp] = {
            "pizzeria_id": ID_pizzeria,
            "days": day_data,
        }

    return shift_dict

def get_all_pizzeria_shifts(ID_pizzeria: int):

    c.execute("SELECT * FROM shifts WHERE id_pizzeria = ?;", (ID_pizzeria,))
    shifts = c.fetchall()

    shift_dict = {}
    for shift in shifts:
        ID_shift, timestamp, ID_pizzeria, *ID_days = shift

        day_data = {}
        i = 0
        for ID_day in ID_days:
            c.execute("SELECT * FROM days WHERE id = ?;", (ID_day,))
            day = c.fetchone()
            day_data["day" + str(i + 1)] = {
                "0": {"id": day[1]},
                "1": {"id": day[2]},
                "2": {"id": day[3]},
            }
            i += 1

        shift_dict[timestamp] = day_data

    return shift_dict


def get_all_pizzeria_timestamps(ID_pizzeria):

    c.execute("SELECT timestamp FROM shifts WHERE ID_pizzeria = ? ORDER BY timestamp DESC;", (ID_pizzeria,))
    timestamps = c.fetchall()

    timestamp_list = []
    
    for i in timestamps:
        timestamp_list.append(i[0])

    return timestamp_list

def delete_pizzeria(ID_pizzeria):
    c.execute("DELETE FROM pizzerias WHERE ID_pizzeria = ?", (ID_pizzeria,))

def delete_employee(ID_employee):
    c.execute("DELETE FROM employees WHERE ID_employee = ?", (ID_employee,))

def delete_days(ID_day):
    c.execute("DELETE FROM days WHERE ID_day = ?", (ID_day,))

def delete_shift(ID_shift):
    c.execute("DELETE FROM shifts WHERE ID_shift = ?", (ID_shift,))

def delete_session(ID_session):
    c.execute("DELETE FROM session WHERE ID_session = ?", (ID_session,))

def delete_session_from_uuid(UUID):
    c.execute("DELETE FROM session WHERE UUID = ?", (UUID,))
    
def delete_request(ID_request: int):
    c.execute("DELETE FROM requests WHERE ID_request = ?", (ID_request,))    

def update_pizzeria(ID_pizzeria : int, pizzeria_name : str, owner_name : str):
    c.execute("""UPDATE pizzerias
              SET pizzeria_name = ?,
                  owner_name = ?
              WHERE ID_pizzeria = ?""",
                  (pizzeria_name, owner_name, ID_pizzeria))

def update_employee(ID_employee : int, ID_pizzeria : int, name : str, surname : str, birthdate : str):
    c.execute("""UPDATE employees
              SET ID_pizzeria = ?,
                  name = ?,
                  surname = ?,
                  birthdate = ? 
              WHERE ID_employee = ?""",
                  (ID_pizzeria, name, surname, birthdate, ID_employee))
    
def update_day(ID_day : int, ID_employee1 : int, ID_employee2 : int, ID_employee3 : int):
    c.execute("""UPDATE days
              SET ID_employee1 = ?,
                  ID_employee2 = ?,
                  ID_employee3 = ?
              WHERE ID_day = ?""",
                  (ID_employee1, ID_employee2, ID_employee3, ID_day))
    
def update_shift(ID_shift : int, ID_day1 : int, ID_day2 : int, ID_day3 : int, ID_day4 : int, ID_day5 : int):
    c.execute("""UPDATE shifts
              SET ID_day1 = ?,
                  ID_day2 = ?,
                  ID_day3 = ?,
                  ID_day4 = ?,
                  ID_day5 = ?
              WHERE ID_shift = ?""",
                  (ID_day1, ID_day2, ID_day3, ID_day4, ID_day5, ID_shift))

def update_session(ID_session : int, UUID :str, ID : int, permission : int, expire : str):
    c.execute("""UPDATE session
              SET UUID = ?,
                  ID = ?,
                  permission = ?,
                  expire = ?
              WHERE ID_session = ?""",
                  (UUID, ID, permission, expire, ID_session))
    
def get_all_pizzerias() -> dict:
    c.execute("SELECT * FROM pizzerias")
    items = c.fetchall()
    pizzerias_dict = {}

    for item in items:
        pizzeria_id = item[0]
        pizzeria_name = item[1]
        owner_name = item[2]
        pizzerias_dict[pizzeria_id] = {"name": pizzeria_name, "owner_name": owner_name}

    return pizzerias_dict

def get_pizzeria(ID_pizzeria : int) -> dict:
    c.execute("SELECT pizzeria_name, owner_name FROM pizzerias WHERE ID_pizzeria = ?", (ID_pizzeria,))
    item = c.fetchone()

    if item is None:
        return None
    
    pizzeria_name = item[0]
    owner_name = item[1]

    return {"name": pizzeria_name, "owner_name": owner_name}
    

def get_pizzeria_owner(pizzeria_name : str) -> str:
    c.execute("""SELECT owner_name FROM pizzerias WHERE pizzeria_name = ?""", (pizzeria_name,))
    name = c.fetchone()

    if name is None:
        return None
    elif len(name) != 0:
        return name[0]

def get_pizzeria_from_name(pizzeria_name : str) -> dict:
    c.execute("""SELECT ID_pizzeria, owner_name FROM pizzerias WHERE pizzeria_name = ?""", (pizzeria_name,))
    name = c.fetchone()

    if name is None:
        return None
    else:
        pizzadict = {"ID_pizzeria" : name[0], "owner_name" : name[1]}
        return pizzadict

def get_pizzeria_name(ID_pizzeria):
    c.execute("SELECT pizzeria_name FROM pizzerias WHERE ID_pizzeria = ?", (ID_pizzeria,))
    item = c.fetchone()
    if item:
        return item[0]
    else:
        return "Pizzeria non trovata"

def get_all_employees() -> dict:
    c.execute("SELECT * FROM employees")
    items = c.fetchall()
    employees_dict = {}

    for item in items:
        employee_id = item[0]
        pizzeria_id = item[1]
        name = item[2]
        surname = item[3]
        birthdate = item[4]
        employees_dict[employee_id] = {
            "ID_pizzeria": pizzeria_id,
            "name": name,
            "surname": surname,
            "birthdate": birthdate
        }

    return employees_dict

def get_all_pizzeria_employees(ID_pizzeria : int):
    c.execute("SELECT ID_employee, name, surname, birthdate FROM employees WHERE ID_pizzeria = ?", (ID_pizzeria,))
    items = c.fetchall() 
    employees_dict = {}

    for item in items:
        employee_id = item[0]
        name = item[1]
        surname = item[2]
        birthdate = item[3]
        employees_dict[employee_id] = {"name": name, "surname": surname, "birthdate": birthdate}

    return employees_dict

def get_all_days(): #ho dovuto creare degli alias in quanto se si effettuano più join sulla stessa tabella senza alias da' errore
    c.execute("""SELECT days.ID_day,
                    emp1.name AS name1, emp1.surname AS surname1, emp1.birthdate AS birthdate1,
                    emp2.name AS name2, emp2.surname AS surname2, emp2.birthdate AS birthdate2,
                    emp3.name AS name3, emp3.surname AS surname3, emp3.birthdate AS birthdate3
              FROM days
              INNER JOIN employees AS emp1 ON days.ID_employee1 = emp1.ID_employee
              INNER JOIN employees AS emp2 ON days.ID_employee2 = emp2.ID_employee
              INNER JOIN employees AS emp3 ON days.ID_employee1 = emp3.ID_employee""")
    items = c.fetchall() 
    return items

def get_day(ID_day):
    c.execute("""SELECT ID_employee1, ID_employee2, ID_employee3
              FROM days
              WHERE ID_day = ?""", (ID_day,))
    item = c.fetchone() 

    if item is None:
        return None
    elif len(item) != 0:
        ID_employee1 = item[0]
        ID_employee2 = item[1]
        ID_employee3 = item[2]
        return {
            "ID_employee1" : ID_employee1,
            "ID_employee2" : ID_employee2,
            "ID_employee3" : ID_employee3
        }

def get_employee(ID_employee) -> dict:
    c.execute("SELECT ID_pizzeria, name, surname, birthdate FROM employees WHERE ID_employee = ?", (ID_employee,))
    item = c.fetchone()
    if item is None:
        return None
    elif len(item) != 0:
        employee_dict = {}
        id = item[0]
        name = item[1]
        surname = item[2]
        birthdate = item[3]
        employee_dict = {"id_pizzeria": id, "name": name, "surname": surname, "birthdate": birthdate}

        return employee_dict
    
def get_shift_from_ID_pizzeria(ID_pizzeria : int) -> dict:
    c.execute("SELECT ID_shift, timestamp, ID_day1, ID_day2, ID_day3, ID_day4, ID_day5 FROM shifts WHERE ID_pizzeria = ?", (ID_pizzeria,))
    item = c.fetchone()

    if item is None:
            return None
    elif len(item) != 0:
        shift_dict = {}
        ID_shift = item[0]
        timestamp = item[1]
        ID_day1 = item[2]
        ID_day2 = item[3]
        ID_day3 = item[4]
        ID_day4 = item[5]
        ID_day5 = item[6]
        shift_dict[ID_pizzeria] = {
            "ID_shift": ID_shift,
            "timestamp": timestamp,
            "ID_day1": ID_day1,
            "ID_day2": ID_day2,
            "ID_day3": ID_day3,
            "ID_day4": ID_day4,
            "ID_day5": ID_day5,
        }
        return shift_dict


def get_session(ID_session) -> dict:
    c.execute("SELECT UUID, ID, permission, expire FROM session WHERE ID_session = ?", (ID_session,))
    item = c.fetchone()

    if item is None:
        return None
    elif len(item) != 0:
        session_dict = {}
        session_uuid = item[0]
        ID = item[1]
        permission = item[2]
        expire = item[3]
        session_dict[ID_session] = {
            "UUID": session_uuid,
            "ID": ID,
            "permission": permission,
            "expire": expire
        }
        return session_dict
    
def get_session_from_uuid(session_uuid) -> dict:
    c.execute("SELECT ID_session, ID, permission, expire FROM session WHERE UUID = ?", (session_uuid,))
    item = c.fetchone()

    if item is None:
        return None
    elif len(item) != 0:
        session_dict = {}
        ID_session = item[0]
        ID = item[1]
        permission = item[2]
        expire = item[3]
        session_dict[ID_session] = {
            "ID": ID,
            "permission": permission,
            "expire": expire
        }

        return session_dict

def get_request(request_id) -> dict:
    c.execute("SELECT ID_pizzeria, timestamp, ID_questioner, ID_questioner_day, questioner_index, ID_questioned, ID_questioned_day, questioned_index FROM requests WHERE ID_request = ?", (request_id,))
    item = c.fetchone()

    if item is None:
        return None
    elif len(item) != 0:
        ID_pizzeria = item[0]
        timestamp = item[1]
        ID_questioner = item[2]
        ID_questioner_day = item[3]
        questioner_index = item[4]
        ID_questioned = item[5]
        ID_questioned_day = item[6]
        questioned_index = item[7]
        return {'ID_pizzeria': ID_pizzeria, 'timestamp': timestamp, 'ID_questioner': ID_questioner, 'ID_questioner_day': ID_questioner_day, 'questioner_index': questioner_index, 'ID_questioned': ID_questioned, 'ID_questioned_day': ID_questioned_day, 'questioned_index': questioned_index}

def get_questioner_requests(questioner_id: int) -> dict:
    c.execute("SELECT ID_request, timestamp, ID_pizzeria, ID_questioner_day, questioner_index, ID_questioned, ID_questioned_day, questioned_index FROM requests WHERE ID_questioner = ?", (questioner_id,))
    items = c.fetchall() 
    employees_dict = {}

    for item in items:
        ID_request = item[0]
        timestamp = item[1]
        ID_pizzeria = item[2]
        ID_questioner_day = item[3]
        questioner_index = item[4]
        ID_questioned = item[5]
        ID_questioned_day = item[6]
        questioned_index = item[7]
        employees_dict[ID_request] = {'ID_pizzeria': ID_pizzeria, 'timestamp': timestamp, 'ID_questioner_day': ID_questioner_day, 'questioner_index': questioner_index, 'ID_questioned': ID_questioned, 'ID_questioned_day': ID_questioned_day, 'questioned_index': questioned_index}

    return employees_dict

def get_questioned_requests(questioned_id: int) -> dict:
    c.execute("SELECT ID_request, timestamp, ID_pizzeria, ID_questioner, ID_questioner_day, questioner_index, ID_questioned_day, questioned_index FROM requests WHERE ID_questioned = ?", (questioned_id,))
    items = c.fetchall() 
    employees_dict = {}

    for item in items:
        ID_request = item[0]
        timestamp = item[1]
        ID_pizzeria = item[2]
        ID_questioner = item[3]
        ID_questioner_day = item[4]
        questioner_index = item[5]
        ID_questioned_day = item[6]
        questioned_index = item[7]
        employees_dict[ID_request] = { 'ID_pizzeria': ID_pizzeria, 'timestamp': timestamp, 'ID_questioner': ID_questioner, 'ID_questioner_day': ID_questioner_day, 'questioner_index': questioner_index, 'ID_questioned_day': ID_questioned_day, 'questioned_index': questioned_index}

    return employees_dict

def init():
    open()
    create_table_pizzerias()
    create_table_employees()
    create_table_days()
    create_table_shifts()
    create_table_session()
    create_table_requests()

def main():
    open()
    init()
    close()

if __name__ == "__main__":
    main()