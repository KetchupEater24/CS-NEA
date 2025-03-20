def checkPrime(n):
    if n < 2:
        return False

    for x in range(2, int(n)):
        if n % x == 0:
            return False

    return True

go = True
while go:
    n = int(input("Enter a number: "))

    if n < 1:
        print("Not greater than 1")
    else:
        is_prime = checkPrime(n)

        if is_prime:
            print(f"{n} is prime")
        else:
            print(f"{n} is not prime")

    ask = input("Do you want to check another number? (y/n): ").lower()
    if ask == "n":
        go = False
