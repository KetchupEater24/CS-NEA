# external imports
import sqlite3
from datetime import datetime, timedelta

# my imports
from misc import MiscFunctions

class Database:
    # initialises the database class, establishes connection and cursor, and creates tables
    def __init__(self):
        self.db_name = "database.db"
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.create()

    # creates the database tables
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

    # verifies login credentials and returns user_id if successful, else None
    def verify_login(self, username, password):
        try:
            self.cursor.execute(
                "SELECT user_id, password_hash FROM users WHERE username = ?",
                (username,)
            )
            result = self.cursor.fetchone()
            if result and MiscFunctions.verify_password(password, result[1]):
                # result[0] is the user_id and result[1] is the hashed password
                return result[0]
            return None
        except Exception as e:
            print(f"Login verification error: {e}")
            return None

    # creates a new user with a hashed password and returns the new user_id or None if failed
    def create_user(self, username, email, password):
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

    # retrieves user information as a dict with keys: username, email, and password (hash)
    def get_user(self, user_id):
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

    # updates user's email, username, and/or password, returns True if update occurred
    def update_user(self, user_id, new_email=None, new_username=None, new_password=None):
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

    # deletes a user and all associated decks/cards, returns True if deletion succeeded
    def delete_user(self, user_id):
        try:
            self.cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False

    # returns a list of decks (deck_id, deck_name) for the given user
    def get_decks(self, user_id):
        self.cursor.execute("SELECT deck_id, deck_name FROM decks WHERE user_id = ?", (user_id,))
        return self.cursor.fetchall()

    # creates a new deck for the user and returns the new deck_id
    def create_deck(self, user_id, deck_name):
        self.cursor.execute(
            "INSERT INTO decks (user_id, deck_name) VALUES (?, ?)",
            (user_id, deck_name)
        )
        self.conn.commit()
        return self.cursor.lastrowid

    # updates the deck name for a given deck_id
    def update_deck_name(self, deck_id, new_name):
        self.cursor.execute(
            "UPDATE decks SET deck_name = ? WHERE deck_id = ?",
            (new_name, deck_id)
        )
        self.conn.commit()

    # deletes a deck and its cards
    def delete_deck(self, deck_id):
        self.cursor.execute("DELETE FROM decks WHERE deck_id = ?", (deck_id,))
        self.conn.commit()

    # retrieves deck information as a dict with keys: name and card_count
    def get_deck_info(self, deck_id):
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
    
    # returns the deck name with the corresponding deck_id
    def get_deck_name(self, deck_id):
        self.cursor.execute(
            "SELECT deck_name FROM decks WHERE deck_id = ?",
            (deck_id,)
        )
        row = self.cursor.fetchone()
        return row[0] if row else ""

    # returns a list of cards for a given deck_id
    def get_cards(self, deck_id):
        self.cursor.execute(
            "SELECT card_id, deck_id, question, answer FROM cards WHERE deck_id = ?",
            (deck_id,)
        )
        return self.cursor.fetchall()

    # retrieves a single card as a dict with keys: question and answer
    def get_card(self, card_id):
        self.cursor.execute(
            "SELECT card_id, question, answer FROM cards WHERE card_id = ?",
            (card_id,)
        )
        row = self.cursor.fetchone()
        if row:
            return {"question": row[1], "answer": row[2]}
        return None

    # creates a new card in a deck and returns the new card_id
    def create_card(self, deck_id, question, answer):
        self.cursor.execute(
            "INSERT INTO cards (deck_id, question, answer) VALUES (?, ?, ?)",
            (deck_id, question, answer)
        )
        self.conn.commit()
        return self.cursor.lastrowid

    # updates an existing card's question and answer
    def update_card(self, card_id, question, answer):
        self.cursor.execute(
            "UPDATE cards SET question = ?, answer = ? WHERE card_id = ?",
            (question, answer, card_id)
        )
        self.conn.commit()

    # deletes a card by its card_id
    def delete_card(self, card_id):
        self.cursor.execute("DELETE FROM cards WHERE card_id = ?", (card_id,))
        self.conn.commit()

    # returns the number of cards in a deck
    def get_card_count(self, deck_id):
        self.cursor.execute(
            "SELECT COUNT(*) FROM cards WHERE deck_id = ?",
            (deck_id,)
        )
        result = self.cursor.fetchone()
        return result[0] if result else 0

    # returns the easiness factor (ef) for a card, defaults to 2.5 if not set
    def get_card_easiness(self, user_id, card_id):
        self.cursor.execute(
            "SELECT ef FROM spaced_rep WHERE user_id = ? AND card_id = ?",
            (user_id, card_id)
        )
        row = self.cursor.fetchone()
        if row and row[0] is not None:
            return row[0]
        return 2.5
        
    # returns the count of cards available for review for a given deck and user
    def get_available_for_review_count(self, user_id, deck_id):
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("""
            SELECT COUNT(*)
            FROM cards c
            LEFT JOIN spaced_rep s ON c.card_id = s.card_id AND s.user_id = ?
            WHERE c.deck_id = ?
              AND (s.next_review_date IS NULL OR s.next_review_date <= ?)
        """, (user_id, deck_id, now_str))
        result = self.cursor.fetchone()
        return result[0] if result else 0

    # returns cards available for review, if testing is True, returns all cards in the deck
    def get_available_for_review(self, user_id, deck_id):
        # returns all cards for the given deck that are due for review (or have no scheduled review date)
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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



    # saves a quiz result in the database and returns the new result id
    def save_quiz_result(self, user_id, deck_id, total_cards, correct_count, avg_time, deck_time):
        self.cursor.execute("""
            INSERT INTO quiz (
                user_id, deck_id, total_cards, correct_count, avg_time, deck_time, timestamp
            )
            VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
        """, (user_id, deck_id, total_cards, correct_count, avg_time, deck_time))
        self.conn.commit()
        return self.cursor.lastrowid

    # returns overall quiz statistics for a user as a dict
    def get_quiz_stats(self, user_id):
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

    # returns quiz statistics for a specific deck as a dict
    def get_deck_stats(self, user_id, deck_id):
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

    # returns study history data for the last 7 days as lists of dates and session counts
    def get_study_history_data(self, user_id):
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

    # calculates and returns a deck performance score from 0 to 100 based on average EF of deck cards
    def get_deck_performance_score(self, user_id, deck_id):
        self.cursor.execute("SELECT card_id FROM cards WHERE deck_id = ?", (deck_id,))
        card_ids = [row[0] for row in self.cursor.fetchall()]
        if not card_ids:
            return 0.0
        total_ef = 0.0
        count = 0
        for c_id in card_ids:
            ef = self.get_card_easiness(user_id, c_id)
            total_ef += ef
            count += 1
        avg_ef = total_ef / count
        score = ((avg_ef - 1.3) / (3.5 - 1.3)) * 100
        if score < 0:
            score = 0
        elif score > 100:
            score = 100
        return score

    # returns the minimum and maximum quiz timestamps for a deck as datetime objects
    def get_deck_timestamp_range(self, user_id, deck_id):
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
    
    # updates the is_correct attribute in spaced_rep table based on if correct button was pressed or incorrect
    # if correct was pressed, set is_correct to 1, otheriwse 0
    def update_card_correctness(self, user_id, card_id, is_correct):
        # set the is_correct flag for a specific user/card
        self.cursor.execute(
            """
            UPDATE spaced_rep
               SET is_correct = ?
             WHERE user_id = ? AND card_id = ?
            """,
            (int(is_correct), user_id, card_id)
        )
        self.conn.commit()
    

    # updates spaced repetition data for a card based on quality rating (difficulty the user selected during quiz session)
    # and time taken and returns new review time info
    def update_spaced_rep(self, user_id, card_id, quality, time_taken):
        # retrieve current spaced repetition record for the user and card
        self.cursor.execute("""
            SELECT repetition, interval, ef
            FROM spaced_rep
            WHERE user_id = ? AND card_id = ?
        """, (user_id, card_id))
        record = self.cursor.fetchone()

        # if a record exists, assign the values; otherwise, initialize default values and insert a new record
        if record:
            repetition, old_interval, ef = record
        else:
            repetition, old_interval, ef = 0, 2, 2.5
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.execute("""
                INSERT INTO spaced_rep (
                    user_id, card_id, repetition, interval, ef, next_review_date, time_taken
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, card_id, repetition, old_interval, ef, now_str, time_taken))
            self.conn.commit()

        # if the quality is low (2 or less), schedule review in minutes and reset repetition count
        if quality <= 2:
            mapping_minutes = {0: 2, 1: 6, 2: 10}
            new_interval = mapping_minutes.get(quality, 10)
            repetition = 0  # reset repetition for minute intervals
            next_review_time = datetime.now() + timedelta(minutes=new_interval)
        # for higher quality responses, schedule review in days and increment repetition count
        else:
            mapping_days = {3: 1, 4: 3}
            days = mapping_days.get(quality, 1)
            next_day = (datetime.now() + timedelta(days=days)).replace(hour=0, minute=0, second=0, microsecond=0)
            new_interval = int((next_day - datetime.now()).total_seconds() // 60)
            next_review_time = next_day
            repetition += 1
        
        # # Below is the same code as above but with adjusted intervals so cards are available for review after the appropiate interval
        # if quality <= 2:
        #     mapping_seconds = {0: 5, 1: 10, 2: 120}
        #     new_interval = mapping_seconds.get(quality, 120)
        #     repetition = 0  # reset repetition for second intervals
        #     next_review_time = datetime.now() + timedelta(seconds=new_interval)
        # else:
        #     mapping_seconds = {3: 300, 4: 600}
        #     new_interval = mapping_seconds.get(quality, 300)
        #     repetition += 1
        #     next_review_time = datetime.now() + timedelta(seconds=new_interval)



        # update the ef (easiness factor) based on quality and ensure it does not fall below 1.3
        new_ef = ef + (0.1 - (4 - quality) * (0.08 + (4 - quality) * 0.02))
        if new_ef < 1.3:
            new_ef = 1.3

        # format the next review time and update the spaced repetition record in the database
        next_review_str = next_review_time.strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("""
            UPDATE spaced_rep
            SET repetition = ?, interval = ?, ef = ?, next_review_date = ?, time_taken = ?
            WHERE user_id = ? AND card_id = ?
        """, (repetition, new_interval, new_ef, next_review_str, time_taken, user_id, card_id))
        self.conn.commit()
        
        # return the updated review time, repetition count, new interval, and new easiness factor
        return next_review_time, repetition, new_interval, new_ef

    # commits any changes and closes the database connection
    def close(self):
        try:
            self.conn.commit()
            self.cursor.close()
            self.conn.close()
        except Exception as e:
            print(f"Error closing database: {e}")

# if this file is run directly, create/update the database and then close the connection
if __name__ == "__main__":
    db = Database()
    print("Database created/updated successfully.")
    db.close()


import random
from datetime import datetime, timedelta
from database import Database

def make_endurance_test_data():
    db = Database()

    # 1. Create or get a main test user
    main_username = "endurance_tester"
    main_email = "endurance@test.com"
    main_password = "EndurancePass123"
    user_id = db.create_user(main_username, main_email, main_password)
    if user_id is None:
        row = db.cursor.execute(
            "SELECT user_id FROM users WHERE username = ?", (main_username,)
        ).fetchone()
        user_id = row[0]

    print(f"Main test user id: {user_id}")

    # 2. Test 1: Add >1000 decks
    deck_ids = []
    for i in range(1, 1002):
        deck_name = f"Deck {i}"
        deck_id = db.create_deck(user_id, deck_name)
        deck_ids.append(deck_id)
    print(f"Created {len(deck_ids)} decks.")

    # 3. Test 2: Add >1000 cards to a single deck
    bulk_deck_id = db.create_deck(user_id, "Bulk Card Deck")
    for i in range(1, 1002):
        question = f"Card Q{i}"
        answer = f"Answer for card {i}"
        db.create_card(bulk_deck_id, question, answer)
    print("Created 1001 cards in 'Bulk Card Deck'.")

    # 4. Test 4: Paragraph‐length Q&A
    para_deck_id = db.create_deck(user_id, "Paragraph QA Deck")
    short_q = "What is Lorem Ipsum?"
    long_ans = (
        "Lorem Ipsum is simply dummy text of the printing and typesetting industry. "
        "Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, "
        "when an unknown printer took a galley of type and scrambled it to make a type specimen book."
    )
    db.create_card(para_deck_id, short_q, long_ans)
    print("Created a paragraph‐length Q&A card.")

    # 5. Test 5: Create >1000 users
    for i in range(1, 1002):
        uname = f"user_{i}"
        email = f"user_{i}@test.com"
        pwd = "TestPass!234"
        db.create_user(uname, email, pwd)
    print("Created 1001 additional users.")

    # 6. Test 6: ≥1000 quiz sessions for main user
    for i in range(1000):
        # cycle through decks
        deck_id = deck_ids[i % len(deck_ids)]
        total_cards = db.get_card_count(deck_id)
        if total_cards == 0:
            total_cards = 1
        correct = random.randint(0, total_cards)
        avg_time = random.uniform(1.0, 5.0)
        deck_time = total_cards * avg_time
        # save quiz result (uses CURRENT_TIMESTAMP internally)
        db.save_quiz_result(user_id, deck_id, total_cards, correct, avg_time, deck_time)
    print("Inserted 1000 quiz sessions for main user.")

    db.close()
    print("Endurance test data seeded successfully.")

if __name__ == "__main__":
    make_endurance_test_data()
