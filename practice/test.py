def main():
    n = 12
    c = 0
    for x in range(1, 1000000000):
        if isHarshad(x):
            c +=1
            if c == n:
                print(f"{x} is the {c} harshad number")
                break
        else:
            continue

def isHarshad(x):
    arr = list(str(x))
    total = 0
    for num in arr:
        total += int(num)
    if x % total == 0:
        return True
    else:
        return False

main()