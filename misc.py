import random

# MiscFunctions contains Miscellaneous functions
class MiscFunctions:
    # the decorator @staticmethod allows the function below it to be used without creating an instance of the HelperFunctions class
    @staticmethod
    def hash_password(password):
        # a string of all possible letters and numbers to be used in the salt
        chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        # generates an 8 character random salt
        salt = ""
        for x in range(8):
            salt += random.choice(chars)
        # adds together the ASCII equivalents of each character in the password + salt combination
        # adds this number to num
        num = 0
        for x in password + salt:
            num += ord(x)
        # keeps num between 0 and 999 by doing a modulo operation
        num = num % 1000
        # returns the hash in the format "salt$num", with the num in 4 digit hex
        return f"{salt}${num:04x}"

    @staticmethod
    def verify_password(password, stored_hash):
        # splits the stored hash before and after the '$', into its salt and num (num is stored as a 4 digit hex)
        salt, stored_num = stored_hash.split('$')
        # performs same ASCII adding operation as in hash_password() function
        num = 0
        for c in password + salt:
            num += ord(c)
        # same modulo operation as in num_password() function.
        num = num % 1000
        # if the hash (salt$num) that was just calculated matches the stored hash, return true as password has now been verified
        # otherwise return false
        if f"{salt}${num:04x}" == stored_hash:
            return True
        return False

    @staticmethod
    def split(cards):
        # this is the base case --> if the list has 0 or 1 cards, it means it is already sorted
        if len(cards) <= 1:
            return cards
        # recursively splits the list, until each sublist has 1 card in it
        mid = len(cards) // 2
        left = MiscFunctions.split(cards[:mid])
        right = MiscFunctions.split(cards[mid:])
        # calls merge_sort to sort to recursively combine each left and right sublists into a single sorted list
        return MiscFunctions.merge_sort(left, right)

    @staticmethod
    def merge_sort(left, right):
        result = []
        # continues to compare both lists, left and right while they both still have cards
        # each card is a tuple, and its last element is the easiness factor (ef)
        # lower ef means higher priority (e.g. more difficult card), so it should come first
        while left and right:
            if left[0][-1] < right[0][-1]: # checks which card has lower ef
                # pops the first card from the left list and appends it to result, if this has lower ef
                result.append(left.pop(0))
            else:
                # pops the first card from the right list and appends it to result, if this has lower ef
                result.append(right.pop(0))
        # once one list is empty, the below code adds the remaining cards from the other list to the result
        # extend adds each item from the list individually, unlike append which would add the whole list as one element
        if left:
            result.extend(left)
        else:
            result.extend(right)
        return result


