class ATM:
    def __init__(self,balance=0):
        self.balance=balance
    def check_balance(self):
        print(f"The Current Balance in your Account:{self.balance}$")
    def withdraw(self,moneny):
        if moneny<=0:
            print("Invalid Withdraw Amount")
        elif moneny>self.balance:
            print("Insufficient Balance")
        else:
            self.balance-=moneny
            print(f"{moneny}$ withdraw successfully")
    def deposite(self,moneny):
        if moneny<=0:
            print("Invalid Deposite amount")
        else:
            self.balance+=moneny
            print(f"{moneny}$ Deposite Successfully")
atm=ATM(10000)
while True:
    print("\n=====ATM Menu=====")
    print("1.Check Balance")
    print("2.Withdraw")
    print("3.Depoiste")
    print("4.Exit")
    choice=int(input("Enter your Choice:"))
    if choice==1:
        atm.check_balance()
    elif choice==2:
        moneny=int(input("Enter Withdraw Amount:"))
        atm.withdraw(moneny)
    elif choice == 3:
        money = int(input("Enter deposite amount: "))
        atm.deposite(money)
    elif choice == 4:
        print("Thank you for using ATM")
        break
    else:
        print("Invalid Choice")
