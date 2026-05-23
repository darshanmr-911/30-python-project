#Using ()

import random 
user=input("Choice:one\nRock \nPaper \nScissors\n")
game_logic=("Rock","Paper","Scissors")
computor=random.choice(game_logic)
if user==computor:
    print("Draw")
elif (user=="Rock" and computor=="Scissors") or\
    (user=="Paper" and computor=="Rock")or\
    (user=="Scissors" and computor=="Paper"):
    print("User Wins")
else:
    print("Computor Wins")
        
#using []

import random 
user=input("Choice:one\nRock \nPaper \nScissors\n")
game_logic=["Rock","Paper","Scissors"]
computor=random.choice(game_logic)
if user==computor:
    print("Draw")
elif (user=="Rock" and computor=="Scissors") or\
    (user=="Paper" and computor=="Rock")or\
    (user=="Scissors" and computor=="Paper"):
    print("User Wins")
else:
    print("Computor Wins")