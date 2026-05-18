#Create an empty list to store thire tasks and their status
from re import search


sample_list=[]

#Function added to add_task()
def add_task():
    task=input("Enter a task:\t")
    sample_list.append({"Task":task,"Status":"Pending"})
    print("New Task add succesfully...!\n") 


#Function to view a all task
def view_task():
    print("Your Sample list:")
    if len(sample_list)==0:
        print("No Pending tasks")
    else:
        for index,task in enumerate(sample_list,1):
            print(f"{index}:{task['Task']}-{task['Status']}")


#Function to Remove a Task
def remove_task():
    if sample_list==0:
        print("\n Your sample list is Empty")
    else:
        try:
            search_index=int(input("Enter the task Number that you want to remove:\t"))-1
            if 0<=search_index<len(sample_list):
                remove_index=sample_list.pop(search_index )
                print(f"Task is removed:{remove_index['Task']}")
            else:
                print("Invalid Task Number...!")
        except ValueError:
            print("Please Enter valid Number...!")


#Function Marks as done
def mark_done():
        if sample_list==0:
            print("\n Your sample list is Empty")
        else:
            try:
                search_index=int(input("Enter the task Number that you want to mark as complete:\t"))-1
                if 0<=search_index<len(sample_list):
                    sample_list[search_index]['Status']=='done'
                    print(f"Task {sample_list[search_index]['Task']} has been marks done")
                else:
                    print("Invalid Task Number...!")
            except ValueError:
                print("Please Enter valid Number...!")


#Function Display menu
def menu():
    while(True):
        print("\n")
        print("***Menu***")
        print("1. Add a new task")
        print("2. View a all task")
        print("3. Remove all task")
        print("4. Marks as task completed") 
        print("5.Exit")
        choice=input("Enter your choice(1-5):") 
        if choice=='1':
            add_task()
        elif choice=='2':
            view_task()
        elif choice=='3':
            remove_task()
        elif choice=='4':
            mark_done()
        elif choice=='5':
            print("Exiting this application")
            exit()
        else:
            print("Invalid choice \n Please Enter the valid choice")

if __name__ == "__main__":
    menu()