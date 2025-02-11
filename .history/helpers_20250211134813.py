class HelperFunctions:
    @staticmethod
    def _generate_salt(length=8):
        import random
        chars = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        return ''.join(random.choice(chars) for _ in range(length))

    @staticmethod
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
    def hash_password(password):
        salt = HelperFunctions._generate_salt()
        salted_password = password + salt
        
        hashed = salted_password
        for _ in range(3):
            hashed = HelperFunctions._custom_hash(hashed)
        
        return f"{salt}${hashed}"

    @staticmethod
    def verify_password(password, stored_hash):
        salt, hash_value = stored_hash.split('$')
        
        salted_password = password + salt
        hashed = salted_password
        for _ in range(3):
            hashed = HelperFunctions._custom_hash(hashed)
        
        return hashed == hash_value

class Session:
    def __init__(self):
        self._user_id = None

    def login(self, user_id):
        self._user_id = user_id

    def get_user_id(self):
        return self._user_id

    def is_logged_in(self):
        return self._user_id is not None

    def clear_session(self):
        self._user_id = None
