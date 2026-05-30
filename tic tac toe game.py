theb={'1':'','2':'','3':'',
    '4':'','5':'','6':'',
    '7':'','8':'','9':''}
def board(b):
    print(b['1']+' | '+b['2']+'|'+b['3'])
    print('-+-+-')
    print(b['4']+' | '+b['5']+'|'+b['6'])
    print('-+-+-')
    print(b['7']+' | '+b['8']+'|'+b['9'])

turn='X'
for i in range(9):
    board(theb)
    print('Turn for',turn,"move which space")
    move=input()
    theb[move]=turn
    if turn=="X":
        turn="O"
    else:
        turn="X"
board(theb)