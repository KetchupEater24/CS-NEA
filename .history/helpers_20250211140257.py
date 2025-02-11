import random
import string

class HelperFunctions:
    @staticmethod
    def hash_password(password):
        # generate an 8-character salt from letters and digits.
        salt = ''
        for _ in range(8):
            salt += random.choice(string.ascii_letters + string.digits)

        # create a simple hash by summing the ascii values of the password and salt
        hash_val = 0
        for c in password + salt:
            hash_val += ord(c)
        hash_val = hash_val % 100

        # return the salt and hash in a combined format. in the form salt$hash
        return f"{salt}${hash_val:04x}"

    @staticmethod
    def verify_password(password, stored_hash):
        # split the stored hash into its salt and hash parts.
        salt, stored_val = stored_hash.split('$')

        # recalculate the hash using the same method.
        hash_val = 0
        for c in password + salt:
            hash_val += ord(c)
        hash_val = hash_val % 100

        return f"{salt}${hash_val:04x}" == stored_hash #returns true if calculated hash equals stored hash



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
