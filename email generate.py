'''🐍 Problem 4 — Simple Email Generator ⭐⭐

Enter first name: Darshan
Enter last name: MR

Email: darshan.mr@gmail.com

Write a program that:

Takes the user's first name.
Takes the user's last name.
Converts both to lowercase.
Creates an email using this format:'''


import random
f_name = str(input("Enter your first name :"))
l_name = str(input("Enter your last name :"))
num = random.randint(1,100)

print(f"Email : {f_name.lower()}{l_name.lower()}{num}@gmail.com")
