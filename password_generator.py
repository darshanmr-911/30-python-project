import random

string = "QWERTYUIOPLKJHGFDSAZXCVBNMqwertyuioplkjhgfdsazxcvbnm1234567890"
# for i in range(8):
#     password = random.choice(string)
    
#     print(password,end="")



password = ""

for i in range(8):
    password = password + random.choice(string)

print(password)