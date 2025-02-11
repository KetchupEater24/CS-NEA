import random
import string

class HelperFunctions:
    @staticmethod
    def hash_password(password):
        # Generate an 8-character salt from letters and digits.
        salt = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(8))
        # Create a simple hash by summing the ASCII values of the password and salt, then modulo 10000.
        hash_val = sum(ord(c) for c in (password + salt)) % 10000
        # Return the salt and hash in a combined format.
        return f"{salt}${hash_val:04x}"

    @staticmethod
    def verify_password(password, stored_hash):
        # Split the stored hash into its salt and hash parts.
        salt, stored_val = stored_hash.split('$')
        # Recalculate the hash using the same method.
        hash_val = sum(ord(c) for c in (password + salt)) % 10000
        return f"{salt}${hash_val:04x}" == stored_hash


# keeps track of who's using the system
class Session:
    # starts with no one logged in
    def __init__(self):
        self._user_id = None

    # signs a user into the system
    def login(self, user_id):
        self._user_id = user_id

    # tells us who's currently using the system
    def get_user_id(self):
        return self._user_id

    # checks if anyone is logged in
    def is_logged_in(self):
        return self._user_id is not None

    # signs the current user out
    def clear_session(self):
        self._user_id = None
