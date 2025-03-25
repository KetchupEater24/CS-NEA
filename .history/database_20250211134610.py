# External Imports
import sqlite3
from datetime import datetime

# My Imports
from misc import MiscFunctions, Session

class Database:
    def __init__(self, db_name="database.db"):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS decks (
            deck_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            deck_name TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
        """)

        
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS cards (
            card_id INTEGER PRIMARY KEY AUTOINCREMENT,
            deck_id INTEGER,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            FOREIGN KEY (deck_id) REFERENCES decks(deck_id)
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS quiz_results (
            result_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            deck_id INTEGER,
            card_id INTEGER,
            is_correct BOOLEAN,
            time_taken FLOAT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (deck_id) REFERENCES decks(deck_id),
            FOREIGN KEY (card_id) REFERENCES cards(card_id)
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS quiz_attempts (
            attempt_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            deck_id INTEGER,
            duration INTEGER,
            score FLOAT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (deck_id) REFERENCES decks(deck_id)
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS session_stats (
            session_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            deck_id INTEGER,
            accuracy FLOAT,
            avg_time FLOAT,
            total_cards INTEGER,
            correct_cards INTEGER,
            total_time FLOAT,
            date DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (deck_id) REFERENCES decks(deck_id)
        )
        """)

        self.conn.commit()

############################AUTHENTICATION##################################
    
    def verify_login(self, username, password):
        try:
            self.cursor.execute(
                "SELECT user_id, password_hash FROM users WHERE username = ?",
                (username,)
            )
            result = self.cursor.fetchone()
            if result and MiscFunctions.verify_password(password, result[1]):
                return result[0]
            return None
        except Exception as e:
            print(f"Login verification error: {e}")
            return None

    def create_session(self, user_id):
        try:
            session = Session()
            session.login(user_id)
            return session
        except Exception as e:
            print(f"Session creation error: {e}")
            return None

    def check_session(self, session):
        try:
            if not session or not session.is_logged_in():
                return False
                
            user_id = session.get_user_id()
            cursor = self.conn.cursor()
            cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
            result = cursor.fetchone()
            
            return result is not None
        except Exception as e:
            print(f"Session check error: {e}")
            return False

    def create_user(self, username, email, password):
        try:
            password_hash = MiscFunctions.hash_password(password)
            self.cursor.execute("""
                INSERT INTO users (username, email, password_hash)
                VALUES (?, ?, ?)
            """, (username, email, password_hash))
            self.conn.commit()
            
            user_id = self.cursor.lastrowid
            
            return user_id
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
        finally:
            self.close()

    def get_username(self, user_id):
        self.cursor.execute("""
        SELECT username FROM users WHERE user_id = ?
        """, (user_id,))
        result = self.cursor.fetchone()
        return result[0] if result else None

##################################DECK OPERATIONS################################
    
    def get_decks(self, user_id):
        self.cursor.execute("""
        SELECT deck_id, deck_name
        FROM decks
        WHERE user_id = ?
        """, (user_id,))
        return self.cursor.fetchall()

    def get_decks_with_card_counts(self, user_id):
        self.cursor.execute("""
        SELECT d.deck_id, d.deck_name, COUNT(c.card_id) as card_count
        FROM decks d
        LEFT JOIN cards c ON d.deck_id = c.deck_id
        WHERE d.user_id = ?
        GROUP BY d.deck_id, d.deck_name
        """, (user_id,))
        return self.cursor.fetchall()

    def create_deck(self, user_id, deck_name):
        self.cursor.execute("""
        INSERT INTO decks (user_id, deck_name)
        VALUES (?, ?)
        """, (user_id, deck_name))
        self.conn.commit()
        return self.cursor.lastrowid

    def update_deck_name(self, deck_id, new_name):
        self.cursor.execute("""
        UPDATE decks SET deck_name = ? WHERE deck_id = ?
        """, (new_name, deck_id))
        self.conn.commit()

    def delete_deck(self, deck_id):
        self.cursor.execute("""
        DELETE FROM decks WHERE deck_id = ?
        """, (deck_id,))
        self.conn.commit()

    def get_deck_info(self, deck_id):
        self.cursor.execute("""
        SELECT d.deck_name, COUNT(c.card_id) as card_count
        FROM decks d
        LEFT JOIN cards c ON d.deck_id = c.deck_id
        WHERE d.deck_id = ?
        GROUP BY d.deck_id, d.deck_name
        """, (deck_id,))
        result = self.cursor.fetchone()
        return {
            "name": result[0],
            "card_count": result[1] if result[1] else 0
        }

    def get_total_decks(self, user_id):
        self.cursor.execute("SELECT COUNT(*) FROM decks WHERE user_id = ?", (user_id,))
        return self.cursor.fetchone()[0]

########################################CARD OPERATION#######################################
    
    def get_cards(self, deck_id):
        self.cursor.execute("""
        SELECT card_id, deck_id, question, answer
        FROM cards
        WHERE deck_id = ?
        """, (deck_id,))
        return self.cursor.fetchall()

    def get_card(self, card_id):
        self.cursor.execute("""
        SELECT card_id, question, answer
        FROM cards
        WHERE card_id = ?
        """, (card_id,))
        result = self.cursor.fetchone()
        return {
            "question": result[1],
            "answer": result[2],
        }

    def create_card(self, deck_id, question, answer):
        self.cursor.execute("""
        INSERT INTO cards (
            deck_id, 
            question, 
            answer
        )
        VALUES (?, ?, ?)
        """, (deck_id, question, answer))
        self.conn.commit()
        return self.cursor.lastrowid

    def update_card(self, card_id, question, answer):
        self.cursor.execute("""
        UPDATE cards
        SET question = ?, 
            answer = ?
        WHERE card_id = ?
        """, (question, answer, card_id))
        self.conn.commit()

    def delete_card(self, card_id):
        self.cursor.execute("""
        DELETE FROM cards
        WHERE card_id = ?
        """, (card_id,))
        self.conn.commit()

    def get_total_cards(self, user_id):
        self.cursor.execute("""
        SELECT COUNT(c.card_id)
        FROM cards c
        JOIN decks d ON c.deck_id = d.deck_id
        WHERE d.user_id = ?
        """, (user_id,))
        return self.cursor.fetchone()[0]

#########################QUIZ & ANALYTICS########################################
    
    def save_quiz_result(self, user_id, deck_id, card_id, is_correct, time_taken):
        query = """
        INSERT INTO quiz_results (user_id, deck_id, card_id, is_correct, time_taken, timestamp)
        VALUES (?, ?, ?, ?, ?, datetime('now'))
        """
        self.cursor.execute(query, (user_id, deck_id, card_id, is_correct, time_taken))
        self.conn.commit()

    def get_aggregated_quiz_stats(self, user_id):
        self.cursor.execute("""
            SELECT 
                COUNT(session_id) as session_count,
                SUM(total_cards) as total_cards,
                SUM(correct_cards) as total_correct,
                SUM(total_time) as total_time,
                AVG(accuracy) as avg_accuracy,
                AVG(avg_time) as avg_avg_time
            FROM session_stats
            WHERE user_id = ?
        """, (user_id,))
        result = self.cursor.fetchone()
        if result:
            session_count = result[0] if result[0] else 0
            total_cards = result[1] if result[1] else 0
            total_correct = result[2] if result[2] else 0
            total_time = result[3] if result[3] else 0
            avg_accuracy = result[4] if result[4] else 0
            avg_avg_time = result[5] if result[5] else 0
            overall_avg_time_per_card = (total_time / total_cards) if total_cards > 0 else 0
            return {
                'session_count': session_count,
                'total_cards': total_cards,
                'total_correct': total_correct,
                'total_time': total_time,
                'avg_accuracy': avg_accuracy,
                'avg_avg_time': avg_avg_time,
                'overall_avg_time_per_card': overall_avg_time_per_card
            }
        else:
            return {
                'session_count': 0,
                'total_cards': 0,
                'total_correct': 0,
                'total_time': 0,
                'avg_accuracy': 0,
                'avg_avg_time': 0,
                'overall_avg_time_per_card': 0
            }

    def get_user_stats(self, user_id):
        self.cursor.execute("""
            SELECT accuracy, avg_time, total_cards, correct_cards, total_time 
            FROM session_stats 
            WHERE user_id = ?
            ORDER BY date DESC
            LIMIT 1
        """, (user_id,))
        result = self.cursor.fetchone()
        if result:
            return {
                'accuracy': result[0],
                'avg_time': result[1],
                'total_cards': result[2],
                'correct_cards': result[3],
                'total_time': result[4]
            }
        else:
            return {
                'accuracy': 0,
                'avg_time': 0,
                'total_cards': 0,
                'correct_cards': 0,
                'total_time': 0
            }

    def get_quiz_stats(self, user_id):
        self.cursor.execute("""
        SELECT COUNT(*) as total_attempts,
               SUM(CASE WHEN is_correct THEN 1 ELSE 0 END) as correct_attempts
        FROM quiz_results
        WHERE user_id = ?
        """, (user_id,))
        result = self.cursor.fetchone()
        
        total_attempts = result[0] or 0
        correct_attempts = result[1] or 0
        success_rate = (correct_attempts / total_attempts * 100) if total_attempts > 0 else 0
        
        return {
            'total_attempts': total_attempts,
            'success_rate': success_rate
        }

    def get_analytics_data(self, user_id):
        total_cards = self.get_total_cards(user_id)
        total_decks = self.get_total_decks(user_id)
        
        self.cursor.execute("""
            SELECT 
                COUNT(*) as total_attempts,
                AVG(duration) as avg_duration,
                AVG(score) as avg_score,
                MAX(DATE(timestamp)) as last_study_date
            FROM quiz_attempts
            WHERE user_id = ?
        """, (user_id,))
        quiz_stats = self.cursor.fetchone()
        
        streak = self.calculate_study_streak(user_id)
        
        return {
            'total_cards': total_cards,
            'total_decks': total_decks,
            'cards_studied': quiz_stats[0] or 0,
            'avg_time_per_card': quiz_stats[1] or 0,
            'success_rate': quiz_stats[2] or 0,
            'study_streak': streak,
            'last_study': quiz_stats[3]
        }

    def calculate_study_streak(self, user_id, dates=None, index=0):
        if dates is None:
            self.cursor.execute("""
                SELECT DATE(timestamp) as study_date
                FROM quiz_results
                WHERE user_id = ?
                GROUP BY study_date
                ORDER BY study_date DESC
            """, (user_id,))
            dates = self.cursor.fetchall()
            if not dates:
                return 0
        
        if index >= len(dates) - 1:
            return 1
        
        date1 = datetime.strptime(dates[index][0], '%Y-%m-%d').date()
        date2 = datetime.strptime(dates[index+1][0], '%Y-%m-%d').date()
        
        if (date1 - date2).days == 1:
            return 1 + self.calculate_study_streak(user_id, dates, index + 1)
        return 1

    def get_study_history_data(self, user_id):
        self.cursor.execute("""
        SELECT DATE(timestamp) as study_date, COUNT(*) as attempts
        FROM quiz_results
        WHERE user_id = ?
        GROUP BY study_date
        ORDER BY study_date DESC
        LIMIT 7
        """, (user_id,))
        results = self.cursor.fetchall()
        dates = [row[0] for row in results]
        counts = [row[1] for row in results]
        return dates, counts

    def get_deck_distribution_data(self, user_id):
        self.cursor.execute("""
        SELECT d.deck_name, COUNT(c.card_id) as card_count
        FROM decks d
        LEFT JOIN cards c ON d.deck_id = c.deck_id
        WHERE d.user_id = ?
        GROUP BY d.deck_id, d.deck_name
        """, (user_id,))
        results = self.cursor.fetchall()
        labels = [row[0] for row in results]
        sizes = [row[1] for row in results]
        return labels, sizes

    def get_card_count(self, deck_id):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) 
            FROM cards 
            WHERE deck_id = ?
        """, (deck_id,))
        count = cursor.fetchone()[0]
        cursor.close()
        return count

    def close(self):
        try:
            self.conn.commit()
            self.cursor.close()
            self.conn.close()
        except Exception as e:
            print(f"Error closing database: {e}")

    def save_quiz_attempt(self, user_id, deck_id, duration, score):
        self.cursor.execute("""
        INSERT INTO quiz_attempts (user_id, deck_id, duration, score, timestamp)
        VALUES (?, ?, ?, ?, datetime('now'))
        """, (user_id, deck_id, duration, score))
        self.conn.commit()

    def get_cards_for_review(self, deck_id):
        query = """
        SELECT 
            card_id,
            question,
            answer
        FROM cards 
        WHERE deck_id = ?
        ORDER BY RANDOM()
        LIMIT 20
        """
        self.cursor.execute(query, (deck_id,))
        return self.cursor.fetchall()

    def save_session_stats(self, user_id, deck_id, accuracy, avg_time, total_cards, correct_cards, total_time):
        query = """
        INSERT INTO session_stats (user_id, deck_id, accuracy, avg_time, total_cards, correct_cards, total_time, date)
        VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
        """
        self.cursor.execute(query, (user_id, deck_id, accuracy, avg_time, total_cards, correct_cards, total_time))
        self.conn.commit()

    def get_performance_over_time(self, user_id):
        self.cursor.execute("""
        SELECT 
            DATE(timestamp) as date,
            AVG(CASE WHEN correct = 1 THEN 100 ELSE 0 END) as accuracy,
            COUNT(*) as cards_studied
        FROM quiz_results
        WHERE user_id = ?
        GROUP BY DATE(timestamp)
        ORDER BY date DESC
        LIMIT 30
        """, (user_id,))
        return self.cursor.fetchall()

if __name__ == "__main__":
    db = Database()
    print("Database and tables created successfully.")
    db.close()
