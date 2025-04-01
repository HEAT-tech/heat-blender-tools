import os
import sqlite3
import json
import sys
from pathlib import Path

class SimpleQueue:
    def __init__(self, filename=None):
        appdata_path = self.get_appdata_path("HEATBridge")
        if not appdata_path:
            raise RuntimeError("Could not determine AppData path")

        if filename is None:
            filename = 'simplequeue.db'

        self.filename = os.path.join(appdata_path, filename)
        # Create parent directory if it doesn't exist
        Path(appdata_path).mkdir(parents=True, exist_ok=True)

        self.conn = sqlite3.connect(self.filename)
        self.ensure_exists_or_create()

    def get_appdata_path(self, folder):
        if sys.platform == 'win32':
            appdata_path = os.getenv('APPDATA')
            if appdata_path:
                full_path = os.path.join(appdata_path, folder)
                Path(full_path).mkdir(parents=True, exist_ok=True)
                return full_path
            return None

        elif sys.platform == 'darwin':  # macOS
            app_support = os.path.expanduser('~/Library/Application Support')
            full_path = os.path.join(app_support, folder)
            Path(full_path).mkdir(parents=True, exist_ok=True)
            return full_path

        else:  # Linux
            heat_path = os.path.expanduser('~/.heat')
            full_path = os.path.join(heat_path, folder)
            Path(full_path).mkdir(parents=True, exist_ok=True)
            return full_path

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
