'''Given two strings, str1, and str2, where str1 contains exactly one character more than str2, find the indices of the characters in str1 that can be removed to make str1 equal to str2. Return the array of indices in increasing order. If it is not possible, return the array \[-1\]. 

**Note:** Use 0-based indexing.

**Example**

str1 = "abdgggda"

str2 = "abdggda"

Any "g" character at positions 3, 4, or 5 can be deleted to obtain str2. Return \[3, 4, 5\].'''

def getRemovableIndices(str1, str2):
    # Write your code here

    result=[]
    for i in range(len(str1)):
        new_str=str1[:i]+str1[i+1:]
        if new_str==str2:
            result.append(i)
    if not result:
        return [-1]
    return result

    
if __name__ == '__main__':
    str1 = "abdgggda"

    str2 = "abdggda"

    result = getRemovableIndices(str1, str2)

    print('\n'.join(map(str, result)))
