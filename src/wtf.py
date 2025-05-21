"""
Folder of all the functions I geniunely don't know why I created but may be useful in the future.
"""

def count_missing_expressions() -> None:
    """
    Count the number of missing gene expressions in the 50 micrometer P4 dataframe
    """
    path = "Datasets/Outputs/P4_50_NewDenS.csv"

    file = pd.read_csv(path)
    start = 1
    end = 8

    while start <= end:
        columns = [
            "X",
            "Y",
            "Z"
        ]
        count = 0
        laptop = pd.read_csv(rf"./Datasets/Outputs/P4_Section_Laptop{start}.csv")
        for _,row in laptop.iterrows():
            gene = row["Gene"]
            dataset = row["Section_Dataset_Id"]

            print(f"{gene} and {dataset}")
            
        print(len(columns))
        print(file[columns])
        
        start+=1