n = int(input("How many numbers? "))

arr = []
for x in range(n):
    num = int(input(f"Enter number {x+1}: "))
    arr.append(num)

nodupes = []

for num in arr:
    if num not in nodupes:
        nodupes.append(num)


def main(nodupes):
    freq = [arr.count(digit) for digit in nodupes]
    maxFreq = max(freq)
    countMax = freq.count(maxFreq)

    if countMax > 1:
        print("Data was multimodal")
    else:
        print(f"The most frequent digit was {nodupes[freq.index(maxFreq)]}, and it occurred {maxFreq} times")


main(nodupes)