import sqlite3
from datetime import datetime

DB_NAME = "scans.db"

class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        self.cursor = self.conn.cursor()

    def init_db(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT,
                processed_filename TEXT,
                extracted_text TEXT,
                expiry_status TEXT,
                expiry_date TEXT,
                damage_status TEXT,
                timestamp TEXT
            )
        """)
        self.conn.commit()

    def save_scan(self, filename, processed_filename, extracted_text,
                  expiry_status, expiry_date, damage_status):

        self.cursor.execute("""
            INSERT INTO scans (filename, processed_filename, extracted_text,
                               expiry_status, expiry_date, damage_status, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            filename,
            processed_filename,
            extracted_text,
            expiry_status,
            expiry_date,
            damage_status,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        self.conn.commit()

    def get_scans_page(self, page, per_page):
        offset = (page - 1) * per_page
        rows = self.cursor.execute("""
            SELECT * FROM scans
            ORDER BY id DESC
            LIMIT ? OFFSET ?
        """, (per_page, offset)).fetchall()

        total = self.cursor.execute("SELECT COUNT(*) FROM scans").fetchone()[0]
        return rows, total

    def get_scans_by_date(self, date_str):
        rows = self.cursor.execute("""
            SELECT * FROM scans
            WHERE DATE(timestamp) = ?
            ORDER BY timestamp DESC
        """, (date_str,)).fetchall()
        return rows, len(rows)

    def get_scans_last_7_days(self):
        rows = self.cursor.execute("""
            SELECT DATE(timestamp), COUNT(*)
            FROM scans
            WHERE timestamp >= DATE('now', '-7 days')
            GROUP BY DATE(timestamp)
            ORDER BY DATE(timestamp)
        """).fetchall()
        return rows

    def get_scans_last_7_days_full(self):
        rows = self.cursor.execute("""
            SELECT * FROM scans
            WHERE timestamp >= DATE('now', '-7 days')
            ORDER BY timestamp DESC
        """).fetchall()
        return rows

    def count_expiry_status(self, status):
        row = self.cursor.execute("""
            SELECT COUNT(*) FROM scans WHERE expiry_status = ?
        """, (status,)).fetchone()
        return row[0]


db = Database()

