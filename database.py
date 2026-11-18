import sqlite3


class DatabaseManager:
    def __init__(self, db_path="bot_data.db"):
        self.db_path = db_path
        self.init_db()

    def connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def init_db(self):
        conn = self.connect()
        c = conn.cursor()

        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS workouts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                exercise TEXT NOT NULL,
                weight_kg REAL NOT NULL,
                reps INTEGER NOT NULL,
                logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS moderation_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target_user_id INTEGER NOT NULL,
                moderator_id INTEGER NOT NULL,
                reason TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (target_user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        """)

        conn.commit()
        conn.close()

    def upsert_user(self, user_id, username):
        conn = self.connect()
        conn.execute("""
            INSERT INTO users (user_id, username, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id) DO UPDATE SET
                username = excluded.username,
                updated_at = CURRENT_TIMESTAMP
        """, (user_id, username))
        conn.commit()
        conn.close()

    def log_workout(self, user_id, username, exercise, weight_kg, reps):
        # user muss existieren wegen foreign key
        self.upsert_user(user_id, username)

        conn = self.connect()
        conn.execute(
            "INSERT INTO workouts (user_id, exercise, weight_kg, reps) VALUES (?, ?, ?, ?)",
            (user_id, exercise.strip().lower(), weight_kg, reps),
        )
        conn.commit()
        conn.close()

    def get_user_fitness_stats(self, user_id):
        conn = self.connect()
        rows = conn.execute("""
            SELECT exercise, MAX(weight_kg), SUM(weight_kg * reps), COUNT(id)
            FROM workouts
            WHERE user_id = ?
            GROUP BY exercise
            ORDER BY MAX(weight_kg) DESC
        """, (user_id,)).fetchall()
        conn.close()
        return rows

    def get_exercise_leaderboard(self, exercise, limit=5):
        conn = self.connect()
        rows = conn.execute("""
            SELECT u.username, MAX(w.weight_kg), SUM(w.weight_kg * w.reps)
            FROM workouts w
            JOIN users u ON w.user_id = u.user_id
            WHERE w.exercise = ?
            GROUP BY u.user_id
            ORDER BY MAX(w.weight_kg) DESC, SUM(w.weight_kg * w.reps) DESC
            LIMIT ?
        """, (exercise.strip().lower(), limit)).fetchall()
        conn.close()
        return rows

    def add_warning(self, target_id, target_name, moderator_id, reason):
        self.upsert_user(target_id, target_name)

        conn = self.connect()
        conn.execute(
            "INSERT INTO moderation_logs (target_user_id, moderator_id, reason) VALUES (?, ?, ?)",
            (target_id, moderator_id, reason),
        )
        conn.commit()

        # wie viele Verwarnungen hat der User jetzt
        count = conn.execute(
            "SELECT COUNT(id) FROM moderation_logs WHERE target_user_id = ?",
            (target_id,),
        ).fetchone()[0]
        conn.close()
        return count

    def get_warnings(self, target_id):
        conn = self.connect()
        rows = conn.execute("""
            SELECT id, moderator_id, reason, created_at
            FROM moderation_logs
            WHERE target_user_id = ?
            ORDER BY created_at DESC
        """, (target_id,)).fetchall()
        conn.close()
        return rows

    def clear_warnings(self, target_id):
        conn = self.connect()
        cur = conn.execute(
            "DELETE FROM moderation_logs WHERE target_user_id = ?",
            (target_id,),
        )
        conn.commit()
        deleted = cur.rowcount
        conn.close()
        return deleted