import pandas as pd
import os
import json
import csv
import requests
from validation import is_valid_voxel
from constants import headers

# filters out the p4 complete brain (structures and genes) and gets only the brainstem
def filter_p4_data() -> None:
    '''
    Filters out the P_4 structures in order to seclude the brainstem structure.
    '''
    fil = pd.read_csv(r'C:\Users\jojoa\Downloads\Motorola_Research\ExcelScript\Datasets\Outputs\P4_Complete_Brain.csv')
    answer = fil.loc[fil['structure_id'] > 17290]
    answer.to_csv("./Datasets/Outputs/P4_Complete_Brainstem.csv", index=False)
    with open(r'./result.txt', mode ="w") as ff:
        ff.write(str(answer.shape[0]))

def get_dataset_id() -> None:
    '''
    deprecated
    '''
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

def retrieve_gene_from_section_id(section_dataset_id: int) -> str:
    '''
    takes in a section dataset id and returns the corresponding gene acronym for that id
    '''
    url = rf"https://developingmouse.brain-map.org/api/v2/data/query.json?criteria=model::Structure,rma::criteria,structure_sets%5Bid$eq22%5D,pipe::list%5Bxstructures$eq%27id%27%5D,model::SectionDataSet%5Bid$eq{section_dataset_id}%5D,rma::include,genes"
    response = requests.get(url)
    if response.status_code == 200:
        #Note to self: if you want to access data in nested json, put 0 as the index after the first unwrap.
        data = f"{response.json()['msg'][0]['genes'][0]['acronym']}"

        return data        
    else:
        print(f"ISSUE WITH QUERY {url}")

def group_data(voxel: int) -> list[dict]:
    '''
    Retrieves a List of corresponding Section Images for the p_4 mouse for the corresponding p-56 voxel inputted

    I sort of forgot why I have an offset.
    '''
    dataset = pd.read_csv(rf"./Datasets/Outputs/Chunked/P4_Chunk_{voxel}.csv")
    temp = dataset["Section_Image"]

    start = 0
    end = 20
    result = []
    while start <= end:
        j = temp[start]
        j = j.replace("\'","\"")

        try:
            j = json.loads(j)
            result.extend(j)
            start+=1
        except Exception as e:
            print("error")
            start+=1

    return result
    
    
def group_all_data() -> list[dict]:
    result = []
    voxel = 0
    path = rf"./Datasets/Outputs/Chunked/P4_Chunk_{voxel}.csv"
    while os.path.exists(path):
        result.extend(group_data(voxel))
        voxel+=1
        path = rf"./Datasets/Outputs/Chunked/P4_Chunk_{voxel}.csv"

    return result
 
def get_section_image_ids() -> None:
    '''
    Create a singular csv file with the following Columns
    1. Has the section_dataset_id's
    2. Has the gene acryonym for that section_dataset id's
    3. Holds a list of all the section images that belong to that gene
    '''
    heading = [
        "Section_Dataset_Id",
        "Gene",
        "Images"
    ]
    section_images = group_all_data()
    with open(r"./Datasets/Inputs/section_dataset_ids_reference_6_sagittal.txt", "r") as ids, \
    open(rf"./Datasets/Outputs/P4_Section_Data.csv", "w", newline="") as section:
        images = set()
        writer = csv.writer(section)
        writer.writerow(heading) 
        for dataset_id in ids:
            for image in section_images:
                if int(image["image_sync"]["section_data_set_id"]) == int(dataset_id):
                    images.add(image["image_sync"]["section_image_id"])
            #do a call and retrieve what the corresponding gene is for the section_data_set_id
            id = retrieve_gene_from_section_id(dataset_id)
            writer.writerow([int(dataset_id), id, images])
            images = set()

def get_section_dataset_ids() -> list:
    result = []
    with open(r"./Datasets/Inputs/section_dataset_ids_reference_6_sagittal.txt", "r") as file:
        for id in file:
            result.append(int(id))
    return result

def check_length() -> None:
    '''
    checks length
    '''
    mouse = pd.read_csv(r"./Datasets/Outputs/NewDenS_COMB_Genes.csv")
    print(len(mouse.columns))


def find_missing_genes():
    '''
    Realized the number of genes in the P_56 gene text file were less than the P_4 text file
    so I made this method to check
    '''
    with open(r"./Datasets/Outputs/P56_UniqueGenes.txt", "r") as p56_genes, open(r"./Datasets/Outputs/P4_UniqueGenes.txt", "r") as p4_genes:
        p56 = [i[:-1] for i in p56_genes]
        p4 = [i[:-1] for i in p4_genes]
        with open(r"./Datasets/Outputs/P4_Exclusive_Genes.txt", "w") as file:
            for gene in p4:
                if gene not in p56:
                    file.write(str(gene) + "\n")


def get_unique_genes(common_genes: list[str]) -> list[str]:
    '''
    Retrieves all the unique genes by keeping only the genes with the higher experiment number

    In hindsight, probably not the best idea.
    '''
    genes = []
    experiment = []
    for gene in common_genes:
        col = gene.rsplit("-", 1)
        if len(col) == 2: 
            if col[0] in genes:
                exp_index = genes.index(col[0])
                if experiment[exp_index] < int(col[1]):
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
    '''
    Retrieves all section images???
    '''
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
    '''
    Filters out the common genes between a p-56 and p-4 mouse

    Creates a new csv with all the p-56 column data only for genes that exist in both mice
    '''
    p56_file = pd.read_csv(r"./Datasets/Inputs/NewDenS.csv")
    p4_file = pd.read_csv(r"./Datasets/Outputs/p4_NewDenS.csv")

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

def get_all_chunks() -> list:
    '''
    get every single chunk
    '''
    chunks = []
    temp = r"./Datasets/Outputs/Chunked/P4_Chunk_0.csv"
    counter = 1
    while os.path.exists(temp):
        #print(temp)
        chunks.append(pd.read_csv(rf"{temp}"))
        temp = rf"./Datasets/Outputs/Chunked/P4_Chunk_{counter}.csv"
        counter+=1
    return chunks


    #print(json.loads(chunk['Section_Image'][0].replace("\'","\""))[0]['image_sync']['section_image_id'])


def get_path() -> str:
    '''
    Retrieves the path of the P4_Chunk that hasn't been made yet
    '''
    temp = r"./Datasets/Outputs/Chunks/P4_Chunk_0.csv"
    counter = 1
    while os.path.exists(temp):
        temp = rf"./Datasets/Outputs/Chunks/P4_Chunk_{counter}.csv"
        counter+=1
    return temp

def get_missing_ids() -> str:
    '''
    Finds which id's are in the dataset id text file but not in the P4_Chunks
    '''
    ids = []
    with open(r"./Datasets/Inputs/section_dataset_ids_reference_6_sagittal.txt", "r") as file:
        for j in file:
            ids.append(int(j))
    temp = pd.read_csv(r"./Datasets/Outputs/Chunked/P4_Chunk_0.csv")
    temp = temp["Section_Image"]
    start = 0
    end = 20
    res = []
    while start <= end:
        j = temp[start]
        j = j.replace("\'","\"")

        try:
            j = json.loads(j)
            for image in j:
                id = int(image["image_sync"]["section_data_set_id"])
                res.append(id)
            start+=1
        
        except Exception:
            ...
    missing = []
    print(len(res))
    print(len(ids))
    for i in ids:
        if i not in res:
            missing.append(i)
    
    print(missing)




def get_average() -> None:
    '''
    Gets the average of all the section images reference space coordinates
    
    '''
    voxel = 0
    while not is_valid_voxel(voxel):
        file = pd.read_csv(rf".\Datasets\Outputs\Voxels\P4_Voxel_{voxel}.csv")
        with open(rf".\Datasets\Outputs\Averaged_Voxels\P4_Voxel_{voxel}.csv", "w", newline="") as new_file:
            writer = csv.writer(new_file)
            writer.writerow(headers)
            new_X = sum(file['X'])/len(file['X'])
            new_Y = sum(file['Y'])/len(file['Y'])
            new_Z = sum(file['Z'])/len(file['Z'])
            writer.writerow([new_X, new_Y, new_Z])   
        voxel+=1



# Write the cleaned content back to the same file
