## Inputs we need from the user
# Total rent
# Total food ordered for snacking
# Electricity units spend
# Charge per unit 
# Persons living in room/flat

## Output
# Total amount you've to pay is

rent=int(input("Enter your Flat Rent:"))
food=int(input("Enter the ammount for Food orderd:"))
Electricity_bill=int(input("Enter the total Ammount of Electricity Bill: "))
unit_bill=int(input("Enter the charge per unit:"))
person=int(input("Enter the Number of Person living in one Room:"))

ele_bill=Electricity_bill*unit_bill
total_bill=(food+ele_bill+rent)/person
print(f"Total amount you've to pay is:{total_bill}")

