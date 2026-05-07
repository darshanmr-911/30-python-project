# Build a calculator for:

# * +
# * -
# * *
# * /

# Concepts:

# * input()
# * if/elif
# * functions

num1=int(input("Enter the first number:"))
num2=int(input("Enter the second number:"))
op=int(input("Enter the the operator:\n1 for addition\n2 for subtraction\n3 for multiplication\n4 for division\n"))
match op:
    case 1:
        print("result:", num1+num2)
    case 2:
        print("result:", num1-num2)
    case 3:
        print("result:", num1 * num2)
    case 4:
        print("result:", num1 / num2)
    case _:
        print("Invalid operator")
