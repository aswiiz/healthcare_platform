import sqlite3

import os

# Use /tmp for SQLite if on Vercel/Render to ensure write access
if os.environ.get('VERCEL') or os.environ.get('RENDER'):
    DB_PATH = '/tmp/users.db'
else:
    DB_PATH = 'users.db'


def get_db_connection():
    conn = sqlite3.connect(
        DB_PATH,
        timeout=30,              # wait for locks instead of failing
        isolation_level=None     # safe autocommit
    )
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db_connection() as conn:
# WAL mode can be problematic on some serverless filesystems
        # conn.execute("PRAGMA journal_mode=WAL;")
        pass

        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                gender TEXT NOT NULL,
                phone TEXT NOT NULL,
                address TEXT NOT NULL,
                blood_group TEXT NOT NULL,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')

        conn.execute('''
            CREATE TABLE IF NOT EXISTS health_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                sex TEXT,
                family_history TEXT,
                smoking TEXT,
                alcohol TEXT,
                activity TEXT,
                diet TEXT,
                sleep REAL,
                height REAL,
                weight REAL,
                bp_systolic INTEGER,
                bp_diastolic INTEGER,
                fasting_glucose INTEGER,
                hba1c REAL,
                cholesterol INTEGER,
                ldl INTEGER,
                hdl INTEGER,
                triglycerides INTEGER,
                environmental TEXT,
                analysis_result TEXT,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')

        conn.execute('''
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                hospital_name TEXT NOT NULL,
                ticket_no TEXT NOT NULL,
                date TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')

        conn.execute('''
            CREATE TABLE IF NOT EXISTS treatments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                condition TEXT NOT NULL,
                treatment_plan TEXT NOT NULL,
                status TEXT DEFAULT 'Ongoing',
                start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')

        conn.execute('''
            CREATE TABLE IF NOT EXISTS health_diary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                mood TEXT,
                steps INTEGER,
                water_intake REAL,
                sleep_hours REAL,
                symptoms TEXT,
                note TEXT,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')


def save_health_data(user_id, data_dict, analysis):
    columns = ['user_id', 'analysis_result'] + list(data_dict.keys())
    placeholders = ', '.join(['?'] * len(columns))
    sql = f'INSERT INTO health_data ({", ".join(columns)}) VALUES ({placeholders})'
    values = [user_id, analysis] + list(data_dict.values())

    with get_db_connection() as conn:
        conn.execute(sql, values)


def get_health_data(user_id):
    with get_db_connection() as conn:
        return conn.execute(
            'SELECT * FROM health_data WHERE user_id = ? ORDER BY id DESC',
            (user_id,)
        ).fetchall()


def save_booking(user_id, hospital_name, ticket_no, date):
    with get_db_connection() as conn:
        conn.execute('''
            INSERT INTO bookings (user_id, hospital_name, ticket_no, date)
            VALUES (?, ?, ?, ?)
        ''', (user_id, hospital_name, ticket_no, date))


def get_user_by_id(user_id):
    with get_db_connection() as conn:
        return conn.execute(
            'SELECT * FROM users WHERE id = ?',
            (user_id,)
        ).fetchone()


def register_user(name, age, gender, phone, address, blood_group, username, password):
    try:
        with get_db_connection() as conn:
            conn.execute('''
                INSERT INTO users (
                    name, age, gender, phone,
                    address, blood_group, username, password
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, age, gender, phone, address, blood_group, username, password))
        return True
    except sqlite3.IntegrityError:
        return False


def check_user(username, password):
    with get_db_connection() as conn:
        return conn.execute(
            'SELECT * FROM users WHERE username = ? AND password = ?',
            (username, password)
        ).fetchone()


def get_all_users():
    with get_db_connection() as conn:
        return conn.execute('SELECT * FROM users').fetchall()


def search_users(query):
    with get_db_connection() as conn:
        q = f"%{query}%"
        return conn.execute('''
            SELECT * FROM users 
            WHERE name LIKE ? OR phone LIKE ? OR username LIKE ?
        ''', (q, q, q)).fetchall()


def add_treatment(user_id, condition, treatment_plan):
    with get_db_connection() as conn:
        conn.execute('''
            INSERT INTO treatments (user_id, condition, treatment_plan)
            VALUES (?, ?, ?)
        ''', (user_id, condition, treatment_plan))


def get_treatments(user_id):
    with get_db_connection() as conn:
        return conn.execute('''
            SELECT * FROM treatments WHERE user_id = ? ORDER BY id DESC
        ''', (user_id,)).fetchall()


def update_health_analysis(record_id, analysis_result):
    with get_db_connection() as conn:
        conn.execute('''
            UPDATE health_data SET analysis_result = ? WHERE id = ?
        ''', (analysis_result, record_id))


def save_diary_entry(user_id, mood, steps, water, sleep, symptoms, note):
    with get_db_connection() as conn:
        conn.execute('''
            INSERT INTO health_diary (user_id, mood, steps, water_intake, sleep_hours, symptoms, note)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, mood, steps, water, sleep, symptoms, note))


def get_diary_entries(user_id):
    with get_db_connection() as conn:
        return conn.execute('''
            SELECT * FROM health_diary WHERE user_id = ? ORDER BY date DESC LIMIT 30
        ''', (user_id,)).fetchall()


if __name__ == '__main__':
    init_db()
    print("Database initialized.")
