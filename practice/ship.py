import random

grid = [[" " for _ in range(10)] for _ in range(10)]

ships = {
    "ship5": 5,
    "ship4": 4,
    "ship3": 3,
    "ship2": 2
}

gridOptions = [".", "#", " "]


def initialiseGrid(grid):
    for i in range(10):
        for j in range(10):
            grid[i][j] = gridOptions[0]  


def displayGrid(grid):
    print("  ", end="")
    for col in range(10):
        print(col, end=" ")
    print()
    for i in range(10):
        print(i, end=" ")
        for j in range(10):
            print(grid[i][j], end=" ")
        print()


def displayHiddenGrid(grid):
    print("  ", end="")
    for col in range(10):
        print(col, end=" ")
    print()
    
    for i in range(10):
        print(i, end=" ")  
        for j in range(10):
            if grid[i][j] == "#": 
                print(".", end=" ")
            else:
                print(grid[i][j], end=" ")  
        print()


def placeShips(grid):
    for _ in range(6):  
        orien = random.choice(["v", "h"])
        shipLen = random.choice(list(ships.values()))
        x, y = random.choice(range(10)), random.choice(range(10))

        if orien == "v":
            for i in range(0, shipLen):
                if x + i >= 10:
                    break
                elif grid[x + i][y] != ".": 
                    break
                grid[x + i][y] = "#"

        elif orien == "h":
            for i in range(0, shipLen):
                if y + i >= 10:
                    break
                elif grid[x][y + i] != ".":
                    break
                grid[x][y + i] = "#"


def main():
    initialiseGrid(grid)
    placeShips(grid)

    print("\n--- Hidden Grid ---")
    displayHiddenGrid(grid)

    cont = True
    while cont: 
        rowCol = input("Enter row and column [row, column]: ")
        row = int(rowCol.split(",")[0])
        col = int(rowCol.split(",")[1])

        if grid[row][col] == "#":
            grid[row][col] = "X"
            print("\nYou hit a ship!\n")
        else:
            print("\nYou missed!\n")

        print("--- Hidden Grid ---")
        displayHiddenGrid(grid)

        if all("#" not in row for row in grid):
            print("All Ships Destroyed! You win!")
            cont = False
        else:
            continue


main()
