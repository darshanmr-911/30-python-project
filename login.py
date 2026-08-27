# login interface using python

User_name = "Darshan01"
user_password = "xyz37"

user_name = input("Enter your Username :")
password = input("Enter your Password :")

if user_name != User_name:
    print("Sorry incorrect Username ...!")


if user_password != password:
    print("Sorry incorrect Password ...!")
    
elif user_name == User_name and user_password == password:
    print("Login Succuesfuly...! Welcome to the system")

