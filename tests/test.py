import random

while True:
    min_num = int(input("Minimum Number: "))
    max_num = int(input("Maximum Number: "))

    picked_num = random.randint(min_num, max_num)
    print(f"The number I picked is: {picked_num}")

    answer = input("Do you wanna play again?\n")
    if answer.lower() == "yes":
        continue
    elif answer.lower() == "no":
        break
    else:
        print("Bad Answer")