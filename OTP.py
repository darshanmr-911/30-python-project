import random

otp = random.randint(1000, 9999)
print("Your OTP is :",otp)

enter_otp = int(input("Enter Your OTP :"))

if otp == enter_otp:
    print("OTP is Verified")
else:
    print("Invalid OTP...!")