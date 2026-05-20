marks=int(input("Enter your marks :"))
sub=int(input("Enter total subject:"))
if marks>=90:
    print("Grade A")
elif 75<=marks<90:
    print("Grade B")
elif 50<=marks<75:
    print("Grade C")
else:
    print("Fail")
total_marks=sub*100
percentage=(marks/total_marks)*100
print(f"Your marks are {marks} and you got {percentage:.2f}%") # .2f are used to Limit it to 2 decimal places.