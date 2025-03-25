import sqlite3
from datetime import datetime, timedelta
from misc import MiscFunctions

class Database:
    # initialises database class with the database's name
    # establishes connection to sqlite3 database
    # establishes a cursor, which is used to carry out SQL commands
    # calls create() to make the database tables
    def __init__(self):
        self.db_name = "database.db"
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.create()

    def create(self):
        # users table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
        """)
        # decks table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS decks (
            deck_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            deck_name TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
        """)

        # cards table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS cards (
            card_id INTEGER PRIMARY KEY AUTOINCREMENT,
            deck_id INTEGER NOT NULL,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            FOREIGN KEY (deck_id) REFERENCES decks(deck_id)
        )
        """)

        # quiz table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS quiz (
            result_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            deck_id INTEGER NOT NULL,
            total_cards INTEGER DEFAULT 0,    
            correct_count INTEGER DEFAULT 0, 
            avg_time FLOAT DEFAULT 0.0,       
            deck_time FLOAT DEFAULT 0.0,    
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (deck_id) REFERENCES decks(deck_id)
        )
        """)

        # spaced repetition table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS spaced_rep (
            sr_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            card_id INTEGER NOT NULL,
            repetition INTEGER DEFAULT 0,
            interval INTEGER DEFAULT 2,    
            ef FLOAT DEFAULT 2.5,
            next_review_date DATETIME,
            time_taken FLOAT DEFAULT 0.0,  
            is_correct BOOLEAN,              
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (card_id) REFERENCES cards(card_id)
        )
        """)

        self.conn.commit()

    ##################AUTHENTICATION#######################

    # returns user_id if username/password are correct, otherwise None.

    def verify_login(self, username, password):
        try:
            self.cursor.execute(
                "SELECT user_id, password_hash FROM users WHERE username = ?",
                (username,)
            )
            result = self.cursor.fetchone()
            if result and MiscFunctions.verify_password(password, result[1]):
                #result[0] is the user_id and result[1] is the hashed password
                return result[0]

            return None
        except Exception as e:
            print(f"Login verification error: {e}")
            return None

    def create_user(self, username, email, password):
        """
        Creates a new user with hashed password. Returns the new user_id or None if failed.
        """
        try:
            password_hash = MiscFunctions.hash_password(password)
            self.cursor.execute("""
                INSERT INTO users (username, email, password_hash)
                VALUES (?, ?, ?)
            """, (username, email, password_hash))
            self.conn.commit()
            print(self.cursor.lastrowid)
            return self.cursor.lastrowid
        except Exception as e:
            print(f"Error creating user: {e}")
            return None

    def get_user(self, user_id):
        """
        Returns a dict with {username, email, password=hash} for the user, or None if not found.
        """
        try:
            self.cursor.execute("""
                SELECT username, email, password_hash
                FROM users
                WHERE user_id = ?
            """, (user_id,))
            row = self.cursor.fetchone()
            if row:
                return {"username": row[0], "email": row[1], "password": row[2]}
            return None
        except Exception as e:
            print(f"Error fetching user: {e}")
            return None

    def get_username(self, user_id):
        """
        Returns just the username for the given user_id, or None if not found.
        """
        self.cursor.execute("SELECT username FROM users WHERE user_id = ?", (user_id,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def update_user(self, user_id, new_email=None, new_username=None, new_password=None):
        """
        Updates the user's email, username, and/or password if provided.
        Returns True if an update occurred, otherwise False.
        """
        try:
            current_data = self.get_user(user_id)
            if not current_data:
                return False

            updated_email = new_email if new_email else current_data["email"]
            updated_username = new_username if new_username else current_data["username"]
            if new_password:
                updated_password_hash = MiscFunctions.hash_password(new_password)
            else:
                updated_password_hash = current_data["password"]

            self.cursor.execute("""
                UPDATE users
                SET email = ?, username = ?, password_hash = ?
                WHERE user_id = ?
            """, (updated_email, updated_username, updated_password_hash, user_id))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating user: {e}")
            return False

    def delete_user(self, user_id):
        """
        Permanently deletes the user and all their decks/cards. Returns True if successful.
        """
        try:
            self.cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False

    ############################################################################
    # DECK OPERATIONS
    ############################################################################
    def get_decks(self, user_id):
        """
        Returns a list of (deck_id, deck_name) for all decks belonging to user_id.
        """
        self.cursor.execute("SELECT deck_id, deck_name FROM decks WHERE user_id = ?", (user_id,))
        return self.cursor.fetchall()

    def create_deck(self, user_id, deck_name):
        """
        Creates a new deck for the user and returns the new deck_id.
        """
        self.cursor.execute(
            "INSERT INTO decks (user_id, deck_name) VALUES (?, ?)",
            (user_id, deck_name)
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def update_deck_name(self, deck_id, new_name):
        """
        Renames the specified deck.
        """
        self.cursor.execute(
            "UPDATE decks SET deck_name = ? WHERE deck_id = ?",
            (new_name, deck_id)
        )
        self.conn.commit()

    def delete_deck(self, deck_id):
        """
        Deletes the deck and all its cards (due to foreign key cascade or manual).
        """
        self.cursor.execute("DELETE FROM decks WHERE deck_id = ?", (deck_id,))
        self.conn.commit()

    def get_deck_info(self, deck_id):
        """
        Returns a dict with {name, card_count} for the specified deck_id.
        """
        self.cursor.execute("""
            SELECT d.deck_name, COUNT(c.card_id) as card_count
            FROM decks d
            LEFT JOIN cards c ON d.deck_id = c.deck_id
            WHERE d.deck_id = ?
            GROUP BY d.deck_id, d.deck_name
        """, (deck_id,))
        result = self.cursor.fetchone()
        if result:
            return {"name": result[0], "card_count": result[1]}
        return {"name": "", "card_count": 0}

    ############################################################################
    # CARD OPERATIONS
    ############################################################################
    def get_cards(self, deck_id):
        """
        Returns a list of (card_id, deck_id, question, answer) for the given deck_id.
        """
        self.cursor.execute(
            "SELECT card_id, deck_id, question, answer FROM cards WHERE deck_id = ?",
            (deck_id,)
        )
        return self.cursor.fetchall()

    def get_card(self, card_id):
        """
        Returns a dict with {question, answer} for the given card_id.
        """
        self.cursor.execute(
            "SELECT card_id, question, answer FROM cards WHERE card_id = ?",
            (card_id,)
        )
        row = self.cursor.fetchone()
        if row:
            return {"question": row[1], "answer": row[2]}
        return None

    def create_card(self, deck_id, question, answer):
        """
        Inserts a new card into the specified deck. Returns the new card_id.
        """
        self.cursor.execute(
            "INSERT INTO cards (deck_id, question, answer) VALUES (?, ?, ?)",
            (deck_id, question, answer)
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def update_card(self, card_id, question, answer):
        """
        Updates the question/answer for the specified card.
        """
        self.cursor.execute(
            "UPDATE cards SET question = ?, answer = ? WHERE card_id = ?",
            (question, answer, card_id)
        )
        self.conn.commit()

    def delete_card(self, card_id):
        """
        Deletes the specified card from the database.
        """
        self.cursor.execute("DELETE FROM cards WHERE card_id = ?", (card_id,))
        self.conn.commit()

    def get_card_count(self, deck_id):
        """
        Returns the number of cards in the specified deck.
        """
        self.cursor.execute(
            "SELECT COUNT(*) FROM cards WHERE deck_id = ?",
            (deck_id,)
        )
        result = self.cursor.fetchone()
        return result[0] if result else 0

    def get_card_easiness(self, user_id, card_id):
        """
        Returns the EF (easiness factor) for a given card (default 2.5 if none).
        """
        self.cursor.execute(
            "SELECT ef FROM spaced_rep WHERE user_id = ? AND card_id = ?",
            (user_id, card_id)
        )
        row = self.cursor.fetchone()
        if row and row[0] is not None:
            return row[0]
        return 2.5

    ############################################################################
    # QUIZ RESULTS (SESSION-LEVEL)
    ############################################################################
    def save_quiz_result(self, user_id, deck_id, total_cards, correct_count, avg_time, deck_time):
        """
        Saves one quiz session record to quiz.
         - total_cards: how many cards were reviewed in this session
         - correct_count: how many were answered correctly
         - avg_time: average time per card
         - deck_time: total time for the entire session
        """
        self.cursor.execute("""
            INSERT INTO quiz (
                user_id, deck_id, total_cards, correct_count, avg_time, deck_time, timestamp
            )
            VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
        """, (user_id, deck_id, total_cards, correct_count, avg_time, deck_time))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_quiz_stats(self, user_id):
        """
        Returns overall session-level statistics for a user:
          - total_sessions: how many quiz sessions
          - total_time: sum of deck_time across sessions
          - overall_avg_time_per_card: average of avg_time across sessions
          - total_correct: sum of correct answers across all sessions
          - total_reviewed: sum of total_cards across all sessions
          - overall_accuracy: (total_correct / total_reviewed) * 100
        """
        self.cursor.execute("""
            SELECT
                COUNT(*) AS total_sessions,
                SUM(deck_time) AS total_time,
                AVG(avg_time) AS overall_avg_time,
                SUM(correct_count) AS total_correct,
                SUM(total_cards) AS total_reviewed
            FROM quiz
            WHERE user_id = ?
        """, (user_id,))
        row = self.cursor.fetchone()
        if not row:
            return {
                "total_sessions": 0,
                "total_time": 0.0,
                "overall_avg_time_per_card": 0.0,
                "total_correct": 0,
                "total_reviewed": 0,
                "overall_accuracy": 0.0
            }
        total_sessions = row[0] or 0
        total_time = row[1] or 0.0
        overall_avg_time = row[2] or 0.0
        total_correct = row[3] or 0
        total_reviewed = row[4] or 0
        overall_accuracy = 0.0
        if total_reviewed > 0:
            overall_accuracy = (total_correct / total_reviewed) * 100
        return {
            "total_sessions": total_sessions,
            "total_time": total_time,
            "overall_avg_time_per_card": overall_avg_time,
            "total_correct": total_correct,
            "total_reviewed": total_reviewed,
            "overall_accuracy": overall_accuracy
        }

    def get_deck_stats(self, user_id, deck_id):
        """
        Returns session-level stats for a specific deck:
          - session_count: how many quiz sessions for this deck
          - total_time: sum of deck_time across sessions
          - avg_time_per_card: average of avg_time across sessions
          - total_correct: sum of correct answers
          - total_reviewed: sum of total_cards
          - accuracy: total_correct / total_reviewed * 100
        """
        self.cursor.execute("""
            SELECT
                COUNT(*) AS session_count,
                SUM(deck_time) AS total_time,
                AVG(avg_time) AS avg_time_per_card,
                SUM(correct_count) AS total_correct,
                SUM(total_cards) AS total_reviewed
            FROM quiz
            WHERE user_id = ? AND deck_id = ?
        """, (user_id, deck_id))
        row = self.cursor.fetchone()
        if not row:
            return {
                "session_count": 0,
                "total_time": 0.0,
                "avg_time_per_card": 0.0,
                "total_correct": 0,
                "total_reviewed": 0,
                "accuracy": 0.0
            }
        session_count = row[0] or 0
        total_time = row[1] or 0.0
        avg_time_per_card = row[2] or 0.0
        total_correct = row[3] or 0
        total_reviewed = row[4] or 0
        accuracy = (total_correct / total_reviewed * 100) if total_reviewed else 0.0
        return {
            "session_count": session_count,
            "total_time": total_time,
            "avg_time_per_card": avg_time_per_card,
            "total_correct": total_correct,
            "total_reviewed": total_reviewed,
            "accuracy": accuracy
        }

    ############################################################################
    # ANALYTICS (TIME-SERIES) METHODS
    ############################################################################
    def get_study_history_data(self, user_id):
        """
        Returns the last 7 dates (descending) on which the user had quiz sessions,
        along with a count of how many sessions occurred each day.
        This can be used to plot a simple "Study Activity" bar chart.
        """
        self.cursor.execute("""
            SELECT DATE(timestamp) as study_date,
                   COUNT(*) as session_count
            FROM quiz
            WHERE user_id = ?
            GROUP BY study_date
            ORDER BY study_date DESC
            LIMIT 7
        """, (user_id,))
        results = self.cursor.fetchall()
        dates = [row[0] for row in results]
        counts = [row[1] for row in results]
        return dates, counts

    def get_deck_performance_score(self, user_id, deck_id):
        """
        Returns a deck performance score [0..100] based on average EF of all cards in the deck.
        Lower EF ~ more difficult, so that leads to a lower performance score.
        We map EF from [1.3..3.5] to [0..100].
        """
        # 1) Get all cards for this deck.
        self.cursor.execute("SELECT card_id FROM cards WHERE deck_id = ?", (deck_id,))
        card_ids = [row[0] for row in self.cursor.fetchall()]
        if not card_ids:
            return 0.0

        # 2) Compute the average EF across these cards.
        total_ef = 0.0
        count = 0
        for c_id in card_ids:
            ef = self.get_card_easiness(user_id, c_id)
            total_ef += ef
            count += 1
        avg_ef = total_ef / count

        # 3) Map EF in [1.3..3.5] to a 0..100 scale, clamp if outside range.
        #    EF=1.3 -> 0, EF=3.5 -> 100
        #    formula: score = (avg_ef - 1.3) / (3.5 - 1.3) * 100
        score = ((avg_ef - 1.3) / (3.5 - 1.3)) * 100
        if score < 0:
            score = 0
        elif score > 100:
            score = 100
        return score

    # HELPER: get min/max timestamps for a deck
    ############################################################
    def get_deck_timestamp_range(self, user_id, deck_id):
        """
        Returns (min_ts, max_ts) as datetime objects for quiz for this deck/user.
        If no results, returns (None, None).
        """
        self.cursor.execute("""
               SELECT MIN(timestamp), MAX(timestamp)
               FROM quiz
               WHERE user_id = ? AND deck_id = ?
           """, (user_id, deck_id))
        row = self.cursor.fetchone()
        if row and row[0] and row[1]:
            fmt = "%Y-%m-%d %H:%M:%S"
            return (datetime.strptime(row[0], fmt), datetime.strptime(row[1], fmt))
        return (None, None)

    def add_step(self, dt, group_by, step):
        """Moves dt forward by step hours or days."""
        if group_by == "hour":
            return dt + timedelta(hours=step)
        else:
            # day
            return dt + timedelta(days=step)

        ##################################################
        # 1) Accuracy Over Time
        ##################################################

    def get_deck_accuracy_over_time(self, user_id, deck_id, group_by="day", group_step=1):
        """
        Returns (labels, accuracy_values).
        If group_by="session", group_step is ignored.
        If group_by="hour" or "day", we chunk intervals in increments of group_step hours/days.
        Each chunk's accuracy = (sum of correct) / (sum of total) * 100 for that chunk.
        """
        if group_by == "session":
            # Just one row per quiz entry
            self.cursor.execute("""
                   SELECT result_id, correct_count, total_cards
                   FROM quiz
                   WHERE user_id = ? AND deck_id = ?
                   ORDER BY result_id
               """, (user_id, deck_id))
            rows = self.cursor.fetchall()
            labels = []
            values = []
            for row in rows:
                rid, c_count, t_count = row
                c_count = c_count or 0
                t_count = t_count or 0
                acc = (c_count / t_count * 100) if t_count > 0 else 0
                labels.append(f"Session {rid}")
                values.append(acc)
            return (labels, values)

        # If day/hour grouping
        min_ts, max_ts = self.get_deck_timestamp_range(user_id, deck_id)
        if not min_ts or not max_ts:
            return ([], [])

        # Retrieve all quiz
        self.cursor.execute("""
               SELECT timestamp, correct_count, total_cards
               FROM quiz
               WHERE user_id = ? AND deck_id = ?
               ORDER BY timestamp
           """, (user_id, deck_id))
        all_rows = self.cursor.fetchall()

        fmt = "%Y-%m-%d %H:%M:%S"
        data = []
        for row in all_rows:
            ts_str, c_count, t_count = row
            dt_obj = datetime.strptime(ts_str, fmt)
            data.append((dt_obj, c_count or 0, t_count or 0))

        # Build intervals
        intervals = []
        current = min_ts
        while current <= max_ts:
            nxt = self.add_step(current, group_by, group_step)
            intervals.append((current, nxt))
            current = nxt

        labels = []
        values = []
        for (start_dt, end_dt) in intervals:
            # sum c_count, t_count in [start_dt, end_dt)
            sum_correct = 0
            sum_total = 0
            for (dt_obj, c_count, t_count) in data:
                if start_dt <= dt_obj < end_dt:
                    sum_correct += c_count
                    sum_total += t_count
            if sum_total > 0:
                acc = (sum_correct / sum_total) * 100
            else:
                acc = 0

            if group_by == "hour":
                label_str = start_dt.strftime("%Y-%m-%d %H:00")
            else:
                # day
                label_str = start_dt.strftime("%Y-%m-%d")

            labels.append(label_str)
            values.append(acc)
        return (labels, values)

        ##################################################
        # 2) Avg Time Over Time
        ##################################################

    def get_deck_avg_time_over_time(self, user_id, deck_id, group_by="day", group_step=1):
        if group_by == "session":
            self.cursor.execute("""
                   SELECT result_id, avg_time
                   FROM quiz
                   WHERE user_id = ? AND deck_id = ?
                   ORDER BY result_id
               """, (user_id, deck_id))
            rows = self.cursor.fetchall()
            labels = []
            vals = []
            for row in rows:
                rid, a_time = row
                a_time = a_time or 0
                labels.append(f"Session {rid}")
                vals.append(a_time)
            return (labels, vals)

        min_ts, max_ts = self.get_deck_timestamp_range(user_id, deck_id)
        if not min_ts or not max_ts:
            return ([], [])

        self.cursor.execute("""
               SELECT timestamp, avg_time
               FROM quiz
               WHERE user_id = ? AND deck_id = ?
               ORDER BY timestamp
           """, (user_id, deck_id))
        all_rows = self.cursor.fetchall()

        fmt = "%Y-%m-%d %H:%M:%S"
        data = []
        for row in all_rows:
            ts_str, a_time = row
            dt_obj = datetime.strptime(ts_str, fmt)
            data.append((dt_obj, a_time or 0))

        intervals = []
        current = min_ts
        while current <= max_ts:
            nxt = self.add_step(current, group_by, group_step)
            intervals.append((current, nxt))
            current = nxt

        labels = []
        vals = []
        for (start_dt, end_dt) in intervals:
            sum_time = 0.0
            count = 0
            for (dt_obj, a_time) in data:
                if start_dt <= dt_obj < end_dt:
                    sum_time += a_time
                    count += 1
            if count > 0:
                avg_val = sum_time / count
            else:
                avg_val = 0.0
            if group_by == "hour":
                lb = start_dt.strftime("%Y-%m-%d %H:00")
            else:
                lb = start_dt.strftime("%Y-%m-%d")
            labels.append(lb)
            vals.append(avg_val)
        return (labels, vals)

        ##################################################
        # 3) Cumulative Retention Over Time
        ##################################################

    def get_deck_cumulative_retention(self, user_id, deck_id, group_by="day", group_step=1):
        if group_by == "session":
            self.cursor.execute("""
                   SELECT result_id, correct_count, total_cards
                   FROM quiz
                   WHERE user_id = ? AND deck_id = ?
                   ORDER BY result_id
               """, (user_id, deck_id))
            rows = self.cursor.fetchall()
            cum_correct = 0
            cum_total = 0
            labels = []
            vals = []
            for r in rows:
                rid, c_count, t_count = r
                c_count = c_count or 0
                t_count = t_count or 0
                cum_correct += c_count
                cum_total += t_count
                if cum_total > 0:
                    ret = (cum_correct / cum_total) * 100
                else:
                    ret = 0
                labels.append(f"Session {rid}")
                vals.append(ret)
            return (labels, vals)

        min_ts, max_ts = self.get_deck_timestamp_range(user_id, deck_id)
        if not min_ts or not max_ts:
            return ([], [])

        self.cursor.execute("""
               SELECT timestamp, correct_count, total_cards
               FROM quiz
               WHERE user_id = ? AND deck_id = ?
               ORDER BY timestamp
           """, (user_id, deck_id))
        rows = self.cursor.fetchall()
        fmt = "%Y-%m-%d %H:%M:%S"
        data = []
        for row in rows:
            ts_str, c_count, t_count = row
            dt_obj = datetime.strptime(ts_str, fmt)
            data.append((dt_obj, c_count or 0, t_count or 0))

        intervals = []
        current = min_ts
        while current <= max_ts:
            nxt = self.add_step(current, group_by, group_step)
            intervals.append((current, nxt))
            current = nxt

        # cumulative
        cum_correct = 0
        cum_total = 0
        labels = []
        vals = []
        for (start_dt, end_dt) in intervals:
            # chunk
            chunk_correct = 0
            chunk_total = 0
            for (dt_obj, cc, tc) in data:
                if start_dt <= dt_obj < end_dt:
                    chunk_correct += cc
                    chunk_total += tc
            cum_correct += chunk_correct
            cum_total += chunk_total
            if cum_total > 0:
                ret = (cum_correct / cum_total) * 100
            else:
                ret = 0
            if group_by == "hour":
                lb = start_dt.strftime("%Y-%m-%d %H:00")
            else:
                lb = start_dt.strftime("%Y-%m-%d")
            labels.append(lb)
            vals.append(ret)
        return (labels, vals)
    ############################################################################
    # SPACED REPETITION
    ############################################################################
    def update_spaced_rep(self, user_id, card_id, quality, time_taken, is_correct):
        """
        Updates (or inserts) spaced repetition data for a card attempt.
        Mapping (quality: 0–4):
          Quality 0 ("Very Hard") -> 2 minutes
          Quality 1 ("Hard")      -> 6 minutes
          Quality 2 ("Medium")    -> 10 minutes
          Quality 3 ("Easy")      -> 1 day
          Quality 4 ("Very Easy") -> 3 days
        """
        self.cursor.execute("""
            SELECT repetition, interval, ef
            FROM spaced_rep
            WHERE user_id = ? AND card_id = ?
        """, (user_id, card_id))
        record = self.cursor.fetchone()

        if record:
            repetition, old_interval, ef = record
        else:
            repetition, old_interval, ef = 0, 2, 2.5
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.execute("""
                INSERT INTO spaced_rep (
                    user_id, card_id, repetition, interval, ef, next_review_date, time_taken, is_correct
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, card_id, repetition, old_interval, ef, now_str, time_taken, is_correct))
            self.conn.commit()

        # New mapping:
        # If quality is 0, 1, or 2, use minute-based intervals.
        # If quality is 3 or 4, use day-based intervals.
        if quality <= 2:
            mapping_minutes = {0: 2, 1: 6, 2: 10}
            new_interval = mapping_minutes.get(quality, 10)
            repetition = 0  # Reset repetition for minute intervals.
            next_review_time = datetime.now() + timedelta(minutes=new_interval)
        else:
            mapping_days = {3: 1, 4: 3}
            days = mapping_days.get(quality, 1)
            # Schedule next review at midnight after 'days' days.
            next_day = (datetime.now() + timedelta(days=days)).replace(hour=0, minute=0, second=0, microsecond=0)
            new_interval = int((next_day - datetime.now()).total_seconds() // 60)
            next_review_time = next_day
            repetition += 1

        # Update easiness factor (ef). Adjust formula for maximum quality of 4.
        new_ef = ef + (0.1 - (4 - quality) * (0.08 + (4 - quality) * 0.02))
        if new_ef < 1.3:
            new_ef = 1.3

        next_review_str = next_review_time.strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("""
            UPDATE spaced_rep
            SET repetition = ?, interval = ?, ef = ?, next_review_date = ?, time_taken = ?, is_correct = ?
            WHERE user_id = ? AND card_id = ?
        """, (repetition, new_interval, new_ef, next_review_str, time_taken, is_correct, user_id, card_id))
        self.conn.commit()
        return next_review_time, repetition, new_interval, new_ef

    ############################################################################
    # CLOSE
    ############################################################################
    def close(self):
        """
        Safely commits and closes the database connection.
        """
        try:
            self.conn.commit()
            self.cursor.close()
            self.conn.close()
        except Exception as e:
            print(f"Error closing database: {e}")

    def get_available_for_review(self, deck_id):
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("""
            SELECT COUNT(*)
            FROM cards c
            LEFT JOIN spaced_rep s ON c.card_id = s.card_id AND s.user_id = ?
            WHERE c.deck_id = ?
              AND (s.next_review_date IS NULL OR s.next_review_date <= ?)
        """, (deck_id, now_str))
        result = self.cursor.fetchone()
        return result[0] if result else 0

    def get_due_cards(self, user_id, deck_id, testing=False):
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if testing:
            # In testing mode, return all cards with the current time as the next_review_date.
            self.cursor.execute("""
                SELECT c.card_id, c.question, c.answer, ? as next_review_date
                FROM cards c
                WHERE c.deck_id = ?
            """, (now_str, deck_id))
        else:
            # In production, join with spaced_rep table and filter for cards due for review.
            self.cursor.execute("""
                SELECT c.card_id, c.question, c.answer, COALESCE(s.next_review_date, ?) as next_review_date
                FROM cards c
                LEFT JOIN spaced_rep s ON c.card_id = s.card_id AND s.user_id = ?
                WHERE c.deck_id = ?
                  AND (s.next_review_date IS NULL OR s.next_review_date <= ?)
                ORDER BY next_review_date ASC
                LIMIT 100
            """, (now_str, user_id, deck_id, now_str))
        return self.cursor.fetchall()


if __name__ == "__main__":
    db = Database()
    print("Database created/updated successfully.")
    db.close()
