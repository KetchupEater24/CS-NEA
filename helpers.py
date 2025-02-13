import random
import string
import math

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
        # return the salt and hash in a combined format in the form salt$hash
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
        return f"{salt}${hash_val:04x}" == stored_hash

    # merge sort implementation for cards based on difficulty
    @staticmethod
    def merge_sort_cards(cards):
        # if the list has one or zero elements, return it
        if len(cards) <= 1:
            return cards
        # find the middle index
        mid = len(cards) // 2
        # recursively sort the left half
        left = HelperFunctions.merge_sort_cards(cards[:mid])
        # recursively sort the right half
        right = HelperFunctions.merge_sort_cards(cards[mid:])
        # merge the two sorted halves
        return HelperFunctions.merge(left, right)

    @staticmethod
    def merge(left, right):
        # merge two sorted lists into one sorted list
        sorted_cards = []
        i, j = 0, 0
        # while both left and right have elements, compare the difficulty value (at index 3)
        while i < len(left) and j < len(right):
            # if left element's difficulty is greater or equal, append it first
            if left[i][3] >= right[j][3]:
                sorted_cards.append(left[i])
                i += 1
            else:
                sorted_cards.append(right[j])
                j += 1
        # add any remaining elements from left
        sorted_cards.extend(left[i:])
        # add any remaining elements from right
        sorted_cards.extend(right[j:])
        return sorted_cards

    # @staticmethod
    # def get_priority_indicator(wrong_count):
    #     # convert the wrong count to a qualitative priority indicator
    #     if wrong_count >= 10:
    #         return "HIGH PRIORITY", "red"
    #     elif wrong_count >= 5:
    #         return "MEDIUM PRIORITY", "orange"
    #     else:
    #         return "LOW PRIORITY", "green"

    @staticmethod
    def get_priority_indicator(diff):
        # if difference is negative (or very low), user is doing poorly → high priority
        if diff < 0:
            return "HIGH PRIORITY", "red"
        # if difference is small (e.g., less than 5), it's medium priority
        elif diff < 5:
            return "MEDIUM PRIORITY", "orange"
        else:
            return "LOW PRIORITY", "green"

    # @staticmethod
    # def assign_radial_positions_star(root, canvas_width=800, canvas_height=600):
    #     if root is None:
    #         return
    #     # Place the root at the center
    #     root.x = canvas_width / 2
    #     root.y = canvas_height / 2
    #     num_children = len(root.children)
    #     if num_children == 0:
    #         return
    #     # radius of the circle on which children will be placed
    #     r = min(canvas_width, canvas_height) / 3
    #     angle_step = 2 * math.pi / num_children
    #     for i, child in enumerate(root.children):
    #         angle = i * angle_step
    #         child.x = root.x + r * math.cos(angle)
    #         child.y = root.y + r * math.sin(angle)


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
