import sqlite3
from datetime import datetime, timezone
from pathlib import Path


class MemoryStore:
    def __init__(self, database_path: Path):
        database_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(database_path)
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                note TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        self.connection.commit()

    def remember(self, note: str) -> None:
        self.connection.execute(
            "INSERT INTO memories (note, created_at) VALUES (?, ?)",
            (note, datetime.now(timezone.utc).isoformat())
        )
        self.connection.commit()

    def list_memories(self, limit: int = 50):
        return self.connection.execute(
            "SELECT id, note FROM memories ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()

    def find_relevant(self, message: str, limit: int = 4) -> list[str]:
        words = {w.lower().strip(".,!?;:()[]{}\"'") for w in message.split()}
        words = {w for w in words if len(w) > 3}
        if not words:
            return []
        rows = self.connection.execute(
            "SELECT note FROM memories ORDER BY id DESC LIMIT 300"
        ).fetchall()
        ranked = []
        for (note,) in rows:
            note_words = {w.lower().strip(".,!?;:()[]{}\"'") for w in note.split()}
            score = len(words & note_words)
            if score:
                ranked.append((score, note))
        ranked.sort(key=lambda item: item[0], reverse=True)
        return [note for _, note in ranked[:limit]]

    def forget(self, memory_id: int) -> bool:
        cursor = self.connection.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
        self.connection.commit()
        return cursor.rowcount > 0

    def close(self):
        self.connection.close()
