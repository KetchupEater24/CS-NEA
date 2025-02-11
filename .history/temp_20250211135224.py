class HelperFunctions:
    @staticmethod
    # creates a random string to make passwords which is added to the password
    def _generate_salt(length=8):
        import random
        chars = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        return ''.join(random.choice(chars) for _ in range(length))

    @staticmethod
    # turns text into a unique code that can't be reversed
    def _custom_hash(input_string):
        ascii_values = [ord(char) for char in input_string]
        
        groups = []
        for i in range(0, len(ascii_values), 4):
            group = ascii_values[i:i+4]
            while len(group) < 4:
                group.append(0)
            groups.append(group)
        
        group_sums = []
        for group in groups:
            weighted_sum = sum(val * (i + 1) for i, val in enumerate(group))
            group_sums.append(weighted_sum)
        
        final_sum = sum(group_sums)
        hash_value = final_sum % 1000
        
        return format(hash_value, '08x')

    @staticmethod
    # scrambles passwords with salt for extra security
    def hash_password(password):
        salt = HelperFunctions._generate_salt()
        salted_password = password + salt
        
        hashed = salted_password
        for _ in range(3):
            hashed = HelperFunctions._custom_hash(hashed)
        
        return f"{salt}${hashed}"

    @staticmethod
    # checks if a password matches its scrambled version
    def verify_password(password, stored_hash):
        salt, hash_value = stored_hash.split('$')
        
        salted_password = password + salt
        hashed = salted_password
        for _ in range(3):
            hashed = HelperFunctions._custom_hash(hashed)
        
        return hashed == hash_value

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
