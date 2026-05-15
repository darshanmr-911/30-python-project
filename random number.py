import random
gen=random.randint(1,100)
while True:
    
    num=int(input("Enter the number guess(1-100):"))
    if num==gen:
        print("Correct your Win")
        break
    elif num<gen:
        print("Too Low")
    else:
        print("Too High")
print("The generated Number are",gen)
    