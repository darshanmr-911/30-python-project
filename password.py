import random
password="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijlmnopqrstuvwxyz1234567890!@#$%^&*()_+"
password_list=[]
length=int(input("Enter the Password Lenth:"))
for i in range(length):
    ran_char=random.choice(password)
    password_list.append(ran_char)
password="".join(password_list)
print("Generated Password:",password)