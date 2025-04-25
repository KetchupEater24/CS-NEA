import random
from datetime import datetime, timedelta
from database import Database

def make_test_data():
    db = Database()

    # 1. Create or retrieve a test user.
    username = "Testuser"
    email = "Test@gmail.com"
    password = "Testpassword"

    user_id = db.create_user(username, email, password)
    if user_id is None:
        db.cursor.execute("SELECT user_id FROM users WHERE username = ?", (username,))
        result = db.cursor.fetchone()
        user_id = result[0] if result else None
    print("Test user created with id:", user_id)
    if user_id is None:
        print("Error: Could not create or fetch test user.")
        db.close()
        return

    # 2. Define subject-specific decks and cards.
    subjects = {
        "CS": [
            ("What is RAM?", "Random Access Memory, a fast volatile storage."),
            ("Define CPU.", "Central Processing Unit, the computer's brain."),
            ("What does \"DFS\" stand for?", "Depth-First Search, a graph traversal method."),
            ("Explain polymorphism.", "Ability of objects to take many forms."),
            ("What is an algorithm?", "A step-by-step problem solving procedure."),
        ],
        "Physics": [
            ("State Newton's second law.", "Force equals mass times acceleration, F=ma."),
            ("What is the kinetic energy formula?", "Kinetic energy Eₖ = ½mv²."),
            ("Define Ohm's law.", "Voltage equals current times resistance, V=IR."),
            ("What is the speed of light constant?", "Approximately 3×10^8 m/s."),
            ("Explain what a watt measures.", "A watt measures power (energy per time)."),
        ],
        "Maths": [
            ("Solve for x: 2x + 3 = 11.", "x = 4."),
            ("Differentiate f(x) = x².", "d/dx x² = 2x."),
            ("Integrate ∫2x dx.", "∫2x dx = x² + C."),
            ("What is the quadratic formula?", "x = [-b ± √(b² - 4ac)] / (2a)."),
            ("Solve: 3x - 5 = 1.", "x = 2."),
        ],
        "Biology": [
            ("What is osmosis?", "Movement of water across a semipermeable membrane."),
            ("Define photosynthesis.", "Conversion of light into chemical energy in plants."),
            ("What is a ribosome?", "Cell organelle that synthesizes proteins."),
            ("Explain mitosis.", "Process of cell division creating two identical cells."),
            ("What is DNA?", "Deoxyribonucleic acid, carrier of genetic information."),
        ],
        "Chemistry": [
            ("What is Avogadro's number?", "6.022×10²³, number of entities in one mole."),
            ("Define oxidation.", "Loss of electrons or increase in oxidation state."),
            ("What is a covalent bond?", "Bond where atoms share pairs of electrons."),
            ("Explain the pH scale.", "Scale measuring acidity or alkalinity from 0 to 14."),
            ("What is the mole concept?", "Amount containing Avogadro's number of particles."),
        ]
    }

    deck_ids = []
    for subject, cards in subjects.items():
        deck_id = db.create_deck(user_id, f"{subject} Deck")
        deck_ids.append(deck_id)
        print(f"Created deck '{subject} Deck' with id:", deck_id)
        for question, answer in cards:
            card_id = db.create_card(deck_id, question, answer)
            print(f"   Created card {card_id} in deck {deck_id}: {question!r}")

    # 3. Insert session-level quiz results for analytics testing.
    start_date = datetime.now() - timedelta(days=10)
    for deck_id in deck_ids:
        card_count = db.get_card_count(deck_id)
        for day_offset in range(10):
            current_date = start_date + timedelta(days=day_offset)
            timestamp = current_date.replace(
                hour=random.randint(0, 23),
                minute=random.randint(0, 59)
            )
            ts_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
            correct_count = random.randint(0, card_count)
            avg_time = random.uniform(3, 15)
            deck_time = random.uniform(card_count * 3, card_count * 15)
            db.cursor.execute("""
                INSERT INTO quiz (
                    user_id, deck_id, total_cards, correct_count, avg_time, deck_time, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, deck_id, card_count, correct_count, avg_time, deck_time, ts_str))
            print(f"Inserted quiz session for deck {deck_id} on {ts_str}")

    # 4. Seed spaced repetition data.
    for deck_id in deck_ids:
        cards = db.get_cards(deck_id)
        for card in cards:
            card_id = card[0]
            db.cursor.execute(
                "SELECT sr_id FROM spaced_rep WHERE user_id = ? AND card_id = ?",
                (user_id, card_id)
            )
            if not db.cursor.fetchone():
                r = random.random()
                if r < 0.3:
                    ef = random.uniform(1.3, 1.9)
                elif r < 0.7:
                    ef = random.uniform(2.0, 2.4)
                else:
                    ef = random.uniform(2.5, 3.0)
                now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                time_taken = random.uniform(3, 15)
                is_correct = random.choice([True, False])
                db.cursor.execute("""
                    INSERT INTO spaced_rep (
                        user_id, card_id, ef, next_review_date, time_taken, is_correct
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (user_id, card_id, ef, now_str, time_taken, is_correct))
                print(f"   Inserted spaced repetition for card {card_id} with ef {ef:.2f}")

    db.conn.commit()
    db.close()
    print("Test data seeded successfully!")
    
    
import random
from datetime import datetime, timedelta
from database import Database


def make_endurance_test_data():
    db = Database()

    # 1. Create (or retrieve) main test user
    username = "endurancetest"
    email    = "endurance@test.com"
    pwd      = "endure"
    user_id  = db.create_user(username, email, pwd) or \
               db.cursor.execute("SELECT user_id FROM users WHERE username = ?", (username,)).fetchone()[0]
    print(f"Main test user id: {user_id}")

    # 2. Create 100 decks
    deck_ids = []
    for i in range(1, 101):
        deck_ids.append(db.create_deck(user_id, f"Deck {i}"))
    print("Created 100 decks.")

    # 3. Add 100 cards to each deck
    for d_id in deck_ids:
        for j in range(1, 101):
            q = f"Deck {d_id} - Card Q{j}"
            a = f"Answer for card {j} in deck {d_id}"
            db.create_card(d_id, q, a)
    print("Added 100 cards to each deck.")

    # 4. Paragraph-length Q&A
    para_deck = db.create_deck(user_id, "Paragraph QA Deck")
    db.create_card(
        para_deck,
        "What is Lorem Ipsum?",
        ("Lorem Ipsum is simply dummy text of the printing and typesetting "
         "industry, used since the 1500s. It has survived five centuries.")
    )
    print("Created one paragraph-length Q&A card.")

    # 5. Create 100 users
    for i in range(1, 101):
        db.create_user(f"user_{i}", f"user_{i}@test.com", "TestPass!234")
    print("Created 100 additional users.")

    # 6. Record 100 quiz sessions for main user
    for _ in range(100):
        deck_id     = random.choice(deck_ids)
        total_cards = db.get_card_count(deck_id) or 1
        correct     = random.randint(0, total_cards)
        avg_time    = random.uniform(1.0, 5.0)
        deck_time   = total_cards * avg_time
        db.save_quiz_result(user_id, deck_id, total_cards, correct, avg_time, deck_time)
    print("Inserted 100 quiz sessions.")

    db.close()
    print("Seeding complete.")



if __name__ == "__main__":
    make_test_data()
    make_endurance_test_data()

