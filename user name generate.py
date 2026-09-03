# Requirements
# Take the name as input.
# Convert it to lowercase.
# Add 3 random numbers at the end.
# Print the username.

import random

name = str(input("Enter your name :"))

lower = name.lower()

num = random.randint(100,999)

# username = lower + num

print(f"Usre Name : {lower}{num}")