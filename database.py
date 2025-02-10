# External Imports
import sqlite3
from datetime import datetime, timedelta
import os

# My Imports
from helpers import HelperFunctions, Session
from animations.animation_handler import AnimationHandler
from animations.projectile_motion import ProjectileMotionHandler

class Database:
    def __init__(self, db_name="database.db"):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        # Create base tables first
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

        # Create cards table with all columns initially
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS cards (
            card_id INTEGER PRIMARY KEY AUTOINCREMENT,
            deck_id INTEGER,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            FOREIGN KEY (deck_id) REFERENCES decks (deck_id)
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
            FOREIGN KEY (user_id) REFERENCES users (user_id),
            FOREIGN KEY (deck_id) REFERENCES decks (deck_id),
            FOREIGN KEY (card_id) REFERENCES cards (card_id)
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
            FOREIGN KEY (user_id) REFERENCES users (user_id),
            FOREIGN KEY (deck_id) REFERENCES decks (deck_id)
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
            FOREIGN KEY (user_id) REFERENCES users (user_id),
            FOREIGN KEY (deck_id) REFERENCES decks (deck_id)
        )
        """)

        self.conn.commit()

    ################## AUTHENTICATION ##################
    
    def verify_login(self, username, password):
        try:
            self.cursor.execute(
                "SELECT user_id, password_hash FROM users WHERE username = ?",
                (username,)
            )
            result = self.cursor.fetchone()
            if result and HelperFunctions.verify_password(password, result[1]):
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
            password_hash = HelperFunctions.hash_password(password)
            self.cursor.execute("""
                INSERT INTO users (username, email, password_hash)
                VALUES (?, ?, ?)
            """, (username, email, password_hash))
            self.conn.commit()
            
            # Get the user_id of the newly created user
            user_id = self.cursor.lastrowid
            
            # Create default decks for new user
            self.seed_initial_decks(user_id)
            
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

    ################## DECK OPERATIONS ##################

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

    ################## CARD OPERATIONS ##################

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

    ################## QUIZ & ANALYTICS ##################

    def save_quiz_result(self, user_id, deck_id, card_id, is_correct, time_taken):
        query = """
        INSERT INTO quiz_results (user_id, deck_id, card_id, is_correct, time_taken, date)
        VALUES (?, ?, ?, ?, ?, datetime('now'))
        """
        self.cursor.execute(query, (user_id, deck_id, card_id, is_correct, time_taken))
        self.conn.commit()

    def get_user_stats(self, user_id):
        self.cursor.execute("""
            SELECT 
                COUNT(*) as total_cards,
                SUM(CASE WHEN repetitions > 0 THEN 1 ELSE 0 END) as reviewed_cards,
                AVG(CASE WHEN repetitions > 0 THEN easiness ELSE NULL END) as avg_easiness,
                MAX(CASE WHEN repetitions > 0 THEN easiness ELSE NULL END) as max_easiness,
                AVG(CASE WHEN repetitions > 0 THEN interval ELSE NULL END) as avg_interval
            FROM cards c
            JOIN decks d ON c.deck_id = d.deck_id
            WHERE d.user_id = ?
        """, (user_id,))
        
        result = self.cursor.fetchone()
        return {
            'total_cards': result[0] if result[0] else 0,
            'reviewed_cards': result[1] if result[1] else 0,
            'avg_easiness': round(result[2], 2) if result[2] else 0,
            'max_easiness': round(result[3], 2) if result[3] else 0,
            'avg_interval': round(result[4], 1) if result[4] else 0
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
    
        # Basic stats
        total_cards = self.get_total_cards(user_id)
        total_decks = self.get_total_decks(user_id)
        
        # Quiz performance
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
        
        # Calculate study streak
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
        """Get the number of cards in a deck"""
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

    def get_difficulty_distribution(self, user_id):
        self.cursor.execute("""
        SELECT 
            c.difficulty,
            COUNT(*) as count,
            SUM(CASE WHEN qr.correct = 1 THEN 1 ELSE 0 END) as correct_count
        FROM cards c
        JOIN quiz_results qr ON c.card_id = qr.card_id
        WHERE qr.user_id = ?
        GROUP BY c.difficulty
        """, (user_id,))
        return self.cursor.fetchall()

    def get_retention_intervals(self, user_id):
        """Get retention rates at different intervals"""
        self.cursor.execute("""
            WITH ReviewData AS (
                SELECT 
                    c.card_id,
                    CAST(julianday(qr.timestamp) - julianday(c.last_reviewed) AS INTEGER) as days_since_review,
                    qr.is_correct
                FROM cards c
                JOIN quiz_results qr ON c.card_id = qr.card_id
                JOIN decks d ON c.deck_id = d.deck_id
                WHERE d.user_id = ? 
                AND c.last_reviewed IS NOT NULL
            )
            SELECT 
                days_since_review,
                AVG(CASE WHEN is_correct THEN 100.0 ELSE 0 END) as retention_rate
            FROM ReviewData
            GROUP BY days_since_review
            ORDER BY days_since_review
        """, (user_id,))
        return self.cursor.fetchall()

    def seed_initial_decks(self, user_id):
        try:
            # Create animations directory if it doesn't exist
            if not os.path.exists("animations"):
                os.makedirs("animations")
            
            # Generate all animations
            if not (os.path.exists("animations/bfs_animation.gif") and 
                    os.path.exists("animations/dfs_animation.gif")):
                graph_handler = AnimationHandler()
                graph_handler.generate_animations()
            
            # Create CS deck
            cs_deck_id = self.create_deck(user_id, "Computer Science")
            self.seed_cs_deck(cs_deck_id)
            
            # Create Physics deck
            physics_deck_id = self.create_deck(user_id, "Physics")
            self.seed_physics_deck(physics_deck_id)
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error seeding decks: {e}")
            return False

    def seed_cs_deck(self, user_id):
        # Create the Computer Science deck
        deck_id = self.create_deck(user_id, "Computer Science")
        
        # Create cards with algorithm animations
        cards = [
            {
                "question": "Explain Breadth-First Search (BFS) algorithm and its applications.",
                "answer": """BFS is a graph traversal algorithm that explores all vertices at the current depth before moving to vertices at the next depth level.

Key characteristics:
- Uses a queue data structure
- Visits neighbors before going deeper
- Finds shortest path in unweighted graphs
- Time complexity: O(V + E)
- Space complexity: O(V)

Watch the animation to see how BFS explores level by level:
- Blue nodes: Unvisited
- Green nodes: Visited
- Red node: Current node being explored
- Edges turn green when both nodes are visited""",
                "answer_image": "animations/bfs_animation.gif"
            },
            {
                "question": "Explain Depth-First Search (DFS) algorithm and its applications.",
                "answer": """DFS is a graph traversal algorithm that explores as far as possible along each branch before backtracking.

Key characteristics:
- Uses a stack data structure (or recursion)
- Goes as deep as possible first
- Memory efficient for deep graphs
- Time complexity: O(V + E)
- Space complexity: O(h) where h is height

Watch the animation to see how DFS explores deeply:
- Blue nodes: Unvisited
- Green nodes: Visited
- Red node: Current node being explored
- Edges turn green when both nodes are visited""",
                "answer_image": "animations/dfs_animation.gif"
            },
            {
                "question": "Compare BFS and DFS traversal strategies.",
                "answer": """Key Differences between BFS and DFS:

1. Strategy:
   - BFS: Level by level exploration
   - DFS: Deep path exploration

2. Data Structure:
   - BFS: Queue (FIFO)
   - DFS: Stack or Recursion (LIFO)

3. Memory Usage:
   - BFS: O(V) - stores all nodes at current level
   - DFS: O(h) - stores path nodes only

4. Best Use Cases:
   BFS:
   - Finding shortest path
   - Level-order traversal
   - Peer-to-peer networks
   
   DFS:
   - Maze solving
   - Path finding
   - Cycle detection""",
                "answer_image": None
            },
            {
                "question": "When should you use BFS vs DFS?",
                "answer": """Choosing Between BFS and DFS:

BFS is better when:
1. Finding shortest path in unweighted graph
2. Level-by-level traversal needed
3. Target is likely closer to source
4. Graph is wide but shallow

DFS is better when:
1. Memory is limited
2. Finding paths in maze-like structures
3. Graph is deep but narrow
4. Detecting cycles
5. Topological sorting needed

Watch both animations to compare their behavior!""",
                "answer_image": "animations/bfs_animation.gif"  # Will show BFS first
            }
        ]
        
        for card in cards:
            self.create_card(
                deck_id,
                card["question"],
                card["answer"],
            )
        
        return deck_id

    def setup_default_decks(self, user_id):
        try:
            self.seed_cs_deck(user_id)
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error creating default decks: {e}")
            return False

    def ensure_cs_deck_exists(self, user_id):
        # Check if user has CS deck
        self.cursor.execute("""
        SELECT deck_id FROM decks 
        WHERE user_id = ? AND name = 'Computer Science'
        """, (user_id,))
        
        result = self.cursor.fetchone()
        if not result:
            # Create CS deck if it doesn't exist
            self.seed_cs_deck(user_id)

    def hash_password(self, password):
        # Simple hash function
        hash_value = 0
        for char in password:
            hash_value = (hash_value * 31 + ord(char)) & 0xFFFFFFFF
        return str(hash_value)

    def seed_physics_deck(self, deck_id):
        deck_id = self.create_deck(1, "Physics")
        
        cards = [
            {
                "question": "Explain projectile motion and its key components.",
                "answer": """Projectile motion is the motion of an object thrown or projected into the air, subject to only gravity and air resistance.

Key components:
- Initial velocity (v0)
- Launch angle (θ)
- Gravity (g = 9.81 m/s²)
- Time of flight
- Maximum height
- Range

Watch the animation to see how these components affect the trajectory!""",
                "answer_image": "animations/projectile_motion.gif"
            },
            {
                "question": "How does launch angle affect projectile motion?",
                "answer": """Launch angle affects several aspects of projectile motion:

1. Maximum Height:
- Higher angles → Greater height
- 90° gives maximum height, zero range

2. Range:
- 45° gives maximum range in vacuum
- Real-world optimal angle slightly < 45°

3. Time of Flight:
- Increases with angle up to 90°
- Symmetric for complementary angles

Watch the animation with different angles!""",
                "answer_image": "animations/projectile_motion.gif"
            }
        ]
        
        for card in cards:
            self.create_card(
                deck_id,
                card["question"],
                card["answer"]
            )
        
        return deck_id

    def get_deck_name(self, deck_id):
        self.cursor.execute("""
            SELECT deck_name FROM decks WHERE deck_id = ?
        """, (deck_id,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def get_card_attachments(self, card_id):
        self.cursor.execute("""
            SELECT question_image_path, answer_image_path 
            FROM cards 
            WHERE card_id = ?
        """, (card_id,))
        return self.cursor.fetchone()

if __name__ == "__main__":
    db = Database()
    print("Database and tables created successfully.")
    db.close()
