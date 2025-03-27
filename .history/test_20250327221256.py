# import random
# from datetime import datetime, timedelta
# from database import Database


# def seed_test_data():
#     db = Database()

#     # 1. Create or retrieve a test user.
#     username = "a"
#     email = "a"
#     password = "a"

#     user_id = db.create_user(username, email, password)
#     if user_id is None:
#         db.cursor.execute("SELECT user_id FROM users WHERE username = ?", (username,))
#         result = db.cursor.fetchone()
#         user_id = result[0] if result else None
#     print("Test user created with id:", user_id)
#     if user_id is None:
#         print("Error: Could not create or fetch test user.")
#         db.close()
#         return

#     # 2. Create four decks.
#     deck_names = ["Math", "History", "Science", "Literature"]
#     deck_ids = []
#     for deck_name in deck_names:
#         deck_id = db.create_deck(user_id, f"{deck_name} Deck")
#         deck_ids.append(deck_id)
#         print(f"Created deck '{deck_name} Deck' with id:", deck_id)

#         # 3. Create five cards per deck.
#         for i in range(1, 6):
#             question = f"{deck_name} Question {i}?"
#             answer = f"{deck_name} Answer {i}"
#             card_id = db.create_card(deck_id, question, answer)
#             print(f"   Created card with id: {card_id} in deck {deck_id}")

#     # 4. Insert session-level quiz results for analytics testing.
#     # For each deck, for each of the last 10 days, insert one quiz session.
#     start_date = datetime.now() - timedelta(days=10)
#     for deck_id in deck_ids:
#         # Get total cards in this deck.
#         card_count = db.get_card_count(deck_id)
#         for day_offset in range(10):
#             current_date = start_date + timedelta(days=day_offset)
#             # Add random hour and minute to simulate session timestamp.
#             random_hour = random.randint(0, 23)
#             random_minute = random.randint(0, 59)
#             timestamp = current_date.replace(hour=random_hour, minute=random_minute)
#             timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")

#             # For the session, simulate:
#             # - correct_count: random number between 0 and total cards.
#             # - avg_time: random average time per card (e.g., between 3 and 15 seconds).
#             # - deck_time: random total session time (e.g., between total_cards*3 and total_cards*15 seconds).
#             correct_count = random.randint(0, card_count)
#             avg_time = random.uniform(3, 15)
#             deck_time = random.uniform(card_count * 3, card_count * 15)

#             # Insert session-level quiz result.
#             db.cursor.execute("""
#                 INSERT INTO quiz (
#                     user_id, deck_id, total_cards, correct_count, avg_time, deck_time, timestamp
#                 )
#                 VALUES (?, ?, ?, ?, ?, ?, ?)
#             """, (user_id, deck_id, card_count, correct_count, avg_time, deck_time, timestamp_str))
#             print(f"Inserted quiz session for deck {deck_id} on {timestamp_str}")

#     # 5. Seed spaced repetition data.
#     # For each deck and each card, insert a spaced_repetition row if not exists.
#     for deck_id in deck_ids:
#         cards = db.get_cards(deck_id)
#         for card in cards:
#             card_id = card[0]
#             # Check if a spaced_repetition record exists.
#             db.cursor.execute("SELECT sr_id FROM spaced_rep WHERE user_id = ? AND card_id = ?",
#                               (user_id, card_id))
#             if not db.cursor.fetchone():
#                 # Weighted random for ef:
#                 r = random.random()
#                 if r < 0.3:
#                     ef = random.uniform(1.3, 1.9)  # High priority (lower ef)
#                 elif r < 0.7:
#                     ef = random.uniform(2.0, 2.4)  # Medium priority
#                 else:
#                     ef = random.uniform(2.5, 3.0)  # Low priority
#                 next_review_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#                 # For the new schema, set default time_taken and is_correct.
#                 time_taken = random.uniform(3, 15)
#                 is_correct = random.choice([True, False])
#                 db.cursor.execute("""
#                     INSERT INTO spaced_rep (user_id, card_id, ef, next_review_date, time_taken, is_correct)
#                     VALUES (?, ?, ?, ?, ?, ?)
#                 """, (user_id, card_id, ef, next_review_date, time_taken, is_correct))
#                 print(f"   Inserted spaced repetition for card {card_id} with ef: {ef:.2f}")
#     db.conn.commit()
#     db.close()
#     print("Test data seeded successfully!")


# if __name__ == "__main__":
#     seed_test_data()

