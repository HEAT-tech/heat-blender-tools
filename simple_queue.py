import os
import sqlite3
import json
import tempfile

class SimpleQueue:
    def __init__(self, filename=None):
        appdata_path = os.getenv('APPDATA')
        if filename is None:
            filename = 'HEAT-Blender.db'
            
        filename = os.path.join(appdata_path, "HEATBridge", filename)
        print(filename)
        self.conn = sqlite3.connect(filename)
        self.filename = filename

        self.ensure_exists_or_create()

    def ensure_exists_or_create(self):
        self.create()

    def create(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY,
                task TEXT NOT NULL,
                data TEXT,
                completed BOOLEAN DEFAULT 0,
                running BOOLEAN DEFAULT 0
            )
        """)
        self.conn.commit()

    def push(self, task, data):
        data = json.dumps(data)
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO tasks (task, data) VALUES (?, ?)
        """, (task, data))
        self.conn.commit()

    def pop(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM tasks WHERE completed = 0 AND running = 0 ORDER BY id LIMIT 1
        """)
        task = cursor.fetchone()
        if task is not None:
            self.set_running(task[0])
            return {
                "id": task[0],
                "task": task[1],
                "data": json.loads(task[2])
            }

        return None

    def set_running(self, id):
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE tasks SET running = 1 WHERE id = ?
        """, (id,))
        self.conn.commit()

    def set_completed(self, id):
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE tasks SET completed = 1 WHERE id = ?
        """, (id,))
        self.conn.commit()

    def destroy(self):
        self.conn.close()
        if os.path.exists(self.filename):
            os.remove(self.filename)
