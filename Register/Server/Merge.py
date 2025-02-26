import pandas as pd
import os
users = ["user1", "user2", "user3"]
file_name = "merge_matrix.xlsx"
def init(file_name):
    if not os.path.exists(file_name):
        matrix = pd.DataFrame()
        matrix.to_excel(file_name, engine="openpyxl")
        print("Matrix Created")
    else:
        print("Matrix Exists")
def addUser(user_name,file_name):
    matrix = pd.read_excel(file_name,index_col=0)
    matrix[user_name] = False
    matrix.loc[user_name] = False
    matrix.to_excel(file_name)
    return 0
def requestMerge(sender,reciever,file_name):
    try:
        matrix = pd.read_excel(file_name, index_col = 0)
        matrix.at[reciever,sender] = True
        return 0
    except KeyError as e:
        return 1
def MergeCheck(sender):
    try:
        matrix  = pd.read_excel(file_name, index_col=0)
        f

    except KeyError as e:
        return 1
def startMergeCheck(sender, reciever, file_name):
    try:
        matrix = pd.read_excel(file_name, index_col = 0)
        if matrix.at[reciever,sender] == matrix.at[sender, reciever] and matrix.at[reciever,sender] == True:
            return True
        else :
            return False
    except KeyError as e:
        print(f"{e}")
        return False

def main():

    init(file_name)

    for val in users:
        addUser(val,file_name)
    matrix  = pd.read_excel(file_name, index_col = 0)
    print(matrix)
    return 0
if __name__ == "__main__":
    main()

    