quiz = {
    "What is the capital of India?": "Delhi",
    "Which language is used for Python programming?": "Python",
    "How many days are there in a week?": "7",
    "How many RCB won the cup":"1"
}
score=0
for question,ans in quiz.items():
    user_ans=input(question+":")
    if user_ans.lower()==ans.lower():
        score+=1
        print("Correct")
    else:
        print("Wrong Answer \nThe correct Answer are",ans)
print(f"Your total score sare",score,"/",len(quiz))
        