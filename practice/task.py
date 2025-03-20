
def main():
    ints = input("Enter a list of integers: ")
    ints = ints.split(",")
    arr = []
    for num in ints:
        if num.isdigit() or num.startswith("-") and num[1:].isdigit():
            arr.append(int(num))
    arr = check3(arr)
    if arr == []: 
        print("All Numbers were Divisible by 3")
    arr = square(arr)
    
    print(arr)

def check3(arr):
    new_arr = []
    for x in arr:
        if x % 3 != 0:
            new_arr.append(x)
    return new_arr
def square(arr):
    squared_arr = []
    for x in arr:
        squared_arr.append(x**2)
    return squared_arr


main()
