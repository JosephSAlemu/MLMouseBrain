import pandas as pd
import os
import json


# filters out the p4 complete brain (structures and genes) and gets only the brainstem
def filter_p4_data() -> None:
    fil = pd.read_csv(r'C:\Users\jojoa\Downloads\Motorola_Research\ExcelScript\Datasets\Outputs\P4_Complete_Brain.csv')
    answer = fil.loc[fil['structure_id'] > 17290]
    answer.to_csv("./Datasets/Outputs/P4_Complete_Brainstem.csv", index=False)
    with open(r'./result.txt', mode ="w") as ff:
        ff.write(str(answer.shape[0]))

def get_dataset_id() -> None:
    dataset = pd.read_csv(r"Datasets\Inputs\P4_section_images_cleaned.csv")
    temp = dataset["Section Image"]
    res = set()
    for j in temp:
        hold = j.split(",")
        for i in hold:
            id = i.split("\'")
            if id[1] == 'data_set_id':
                res.add(id[3])
    res = list(res)
    print(res)
    with open(r"./result.txt", mode="w") as ff:
        ff.write('\n'.join(str(i) for i in res))


def filter_data(voxel: int, path: str) -> list[dict]:
    """
    Retrieves a List of corresponding Section Images for the p_4 mouse for the corresponding p-56 voxel inputted
    """
    dataset = pd.read_csv(rf"{path}")
    temp = dataset["Section Image"]
    offset = voxel * 21
    end = offset + 20
    result = []
    while offset <= end:
        j = temp[offset]
        j = j.replace("\'","\"")

        try:
            j = json.loads(j)
            result.extend(j)
            offset+=1
        except Exception as e:
            offset+=1

    return result
        
def check_length() -> None:
    mouse = pd.read_csv(r"./Datasets/Outputs/NewDenS_COMB_Genes.csv")
    print(len(mouse.columns))


def find_missing_genes():
    with open(r"./Datasets/Outputs/P56_UniqueGenes.txt", "r") as p56_genes, open(r"./Datasets/Outputs/P4_UniqueGenes.txt", "r") as p4_genes:
        p56 = [i[:-1] for i in p56_genes]
        p4 = [i[:-1] for i in p4_genes]
        with open(r"./Datasets/Outputs/P4_Exclusive_Genes.txt", "w") as file:
            for gene in p4:
                if gene not in p56:
                    file.write(str(gene) + "\n")


def get_unique_genes(common_genes: list[str]) -> list[str]:
    genes = []
    experiment = []
    for gene in common_genes:
        col = gene.rsplit("-", 1)
        if len(col) == 2: 
            if col[0] in genes:
                exp_index = genes.index(col[0])
                if experiment[exp_index] < int(col[1]):
                    #print(f"replaced {col[0]}-{experiment[exp_index]} with {col[0]}-{int(col[1])} ")
                    experiment[exp_index] = int(col[1])
            else:
                genes.append(col[0])
                experiment.append(int(col[1]))
    with open(r"./Datasets/Outputs/P56_UniqueGenes.txt", "w") as file:
        for gene in genes:
            file.write(str(gene) + "\n")
    result = [genes[i] + "-" + str(experiment[i]) for i in range(len(genes))]
    return result


def get_section_images() -> list:
    section_images = {}


    temp = r"./Datasets/Outputs/Test/P4_Chunk_0.csv"
    counter = 1
    while os.path.exists(temp):
        print(temp)
        file = pd.read_csv(rf"{temp}")
        for row in file['Section_Image']:
            new_row = json.loads(row.replace("\'","\""))
            for chunk in new_row:
                image = chunk['image_sync']['section_image_id']
                if image not in section_images:
                    section_images[image] = 1
                else:
                    section_images[image] = section_images[image]+1
        #print(temp)
        temp = rf"./Datasets/Outputs/Test/P4_Chunk_{counter}.csv"
        counter+=1
    print(section_images)


    
    
    return section_images

def filter_common_genes() -> None:
    """
    Filters out the common genes between a p-56 and p-4 mouse

    Creates a new csv with all the p-56 column data only for genes that exist in both mice
    """
    try:
        p56_file = pd.read_csv(r"./Datasets/Inputs/NewDenS.csv")
        p4_file = pd.read_csv(r"./Datasets/Outputs/p4_NewDenS.csv")
    except FileNotFoundError as e:
        print(f"Error: {e}")
        exit()

    common_genes = []
    for p56_column in p56_file.columns:
        temp = p56_column.rsplit("-",1)
        for p4_column in p4_file.columns:
            temp2 = p4_column.rsplit("-", 1)
            if temp[0] == temp2[0]:
                common_genes.append(p56_column)

    unique_genes = []
    unique_genes.extend(p56_file.columns[1:6])
    unique_genes.extend(get_unique_genes(common_genes))

    result = p56_file.filter(items = unique_genes)
    result.to_csv(r"./Datasets/Outputs/NewDenS_COMB_Genes.csv", index=True)

def noise_threshold() -> None:
    '''
    Remove a Column (Gene) if it's values for all rows is below 0.001.
    '''
    p56_file = pd.read_csv(r"./Datasets/Outputs/NewDenS_COMB_Genes.csv")

    threshold = 0.001
    above_threshold = False
    cols = p56_file.shape[1]
    rows = p56_file.shape[0]
    


    saved_rows = []
    saved_rows.extend(p56_file.columns[1:6])

    #start from 6 to end of row length
    count = 0
    for col in range(6, cols):
        gene = p56_file.filter(items = [p56_file.columns[col]])
        print(count)
        for row in range(rows):
            if gene.iloc[row,0] > threshold:
                above_threshold = True
        if above_threshold == True:
            saved_rows.append(p56_file.columns[col])
            above_threshold = False
        count+=1
    
    result = p56_file.filter(items = saved_rows)
    print(len(saved_rows))
    result.to_csv(r"./Datasets/Outputs/Noise_NewDenS_COMB_Genes.csv", index=True)



    ...


def get_all_chunks():
    chunks = []
    temp = r"./Datasets/Outputs/Test/P4_Chunk_0.csv"
    counter = 1
    while os.path.exists(temp):
        #print(temp)
        chunks.append(pd.read_csv(rf"{temp}"))
        temp = rf"./Datasets/Outputs/Test/P4_Chunk_{counter}.csv"
        counter+=1
    return chunks


    #print(json.loads(chunk['Section_Image'][0].replace("\'","\""))[0]['image_sync']['section_image_id'])


def get_path() -> str:
    temp = r"./Datasets/Outputs/Chunks/P4_Chunk_0.csv"
    counter = 1
    while os.path.exists(temp):
        temp = rf"./Datasets/Outputs/Chunks/P4_Chunk_{counter}.csv"
        counter+=1
    return temp

    