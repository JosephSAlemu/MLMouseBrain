import pandas as pd
import os
import json
import csv
import requests
import paramiko
import ast
from validation import (is_valid_voxel, is_valid_dataframe)
from constants import (HEADERS, DISTRIBUTED, GET_IMAGE_IDS, GET_SEED_PIXELS, FILE_START, FILE_END)
from statistics import stdev

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

    '''
    dataset = pd.read_csv(rf"./Datasets/Outputs/Chunked/P4_Chunk_{voxel}.csv")
    temp = dataset["Section_Image"]

    start = 0
    end = 21
    result = []
    while start < end:
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
 
def section_image_mapping() -> None:
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


def read_chunk_files(path: str) -> tuple:
    '''
    Takes in a chunk file path

    Returns a dictionary.
    key: tuple = voxels coordinates (x,y,z)
    value: list[tuple] = gene,section image, and seed pixel coords (gene,section_image_id,x,y)
    '''
    result = {}

    file = pd.read_csv(path)
    key = ast.literal_eval(file["Voxel"][0])
    result[key] = []

    genes = pd.read_csv("Datasets/Outputs/P4_Section_Data.csv")
    #first flatten out the list
    for row in file['Section_Image']:
        new_row = json.loads(row.replace("\'","\""))
        for chunk in new_row:
            voxel = chunk['image_sync']
            image = voxel['section_image_id']
            X = int(voxel["x"])
            Y = int(voxel["y"])
            gene = int(voxel['section_data_set_id'])
            gene = genes.loc[genes["Section_Dataset_Id"] == gene, "Gene"].values[0]

            result[key].append((gene,image,X,Y))

    return result


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
        for p4_column in p4_file.columnus:
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
    p4_df = pd.read_csv("Datasets/Outputs/P4_50_NewDenS.csv")
    print(p4_df.columns)

    threshold = 0.001


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


def get_missing_ids() -> list[int]:
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
    end = 21
    res = []
    while start < end:
        j = temp[start]
        j = j.replace("\'","\"")

        try:
            j = json.loads(j)
            for image in j:
                id = int(image["image_sync"]["section_data_set_id"])
                res.append(id)
            start+=1
        
        except Exception:
            pass
    
    missing = []
    print(len(res))
    print(len(ids))
    for i in ids:
        if i not in res:
            missing.append(i)
    
    return missing


def write_average() -> None:
    '''
    Gets the average of all the section images reference space coordinates
    
    '''
    voxel = 0
    while not is_valid_voxel(voxel):
        file = pd.read_csv(rf".\Datasets\Outputs\Voxels\P4_Voxel_{voxel}.csv")
        with open(rf".\Datasets\Outputs\Averaged_Voxels\P4_Voxel_{voxel}.csv", "w", newline="") as new_file:
            writer = csv.writer(new_file)
            writer.writerow(HEADERS)
            new_X = sum(file['X'])/len(file['X'])
            new_Y = sum(file['Y'])/len(file['Y'])
            new_Z = sum(file['Z'])/len(file['Z'])
            writer.writerow([new_X, new_Y, new_Z])   
        voxel+=1


def partition_section_images(start: int, end: int) -> None:
    header = ["Voxel","Section_Data"]

    for i in range(start, end):
        path = f"Datasets/Outputs/Fill_Negatives/{i}"
        directory = os.fsencode(path)
        chunks = {}
        count = 0
        for file in os.listdir(directory):
            print(count)
            file_name = os.fsdecode(file)
            file_path = f"{path}/{file_name}"
            chunks = chunks | read_chunk_files(file_path)
            count+=1

        with open(f"Datasets/Outputs/Fill_Negatives/laptops/P4_Voxel_Laptop{i}.csv", "w") as file:
            writer = csv.writer(file)
            writer.writerow(header)
            for voxel, section_data in chunks.items():
                writer.writerow([voxel, section_data])


def partition_genes() -> None:
    """
    split genes into 8 files to represent 8 laptops.

    """
    file = pd.read_csv(r"./Datasets/Outputs/P4_Section_Data.csv")
    columns = file.columns.tolist()
    laptop = 1
    count = 1
    writer = None 
    laptop_file = open(rf"./Datasets/Outputs/P4_Section_Laptop{laptop}.csv", "w", newline="")
    writer = csv.writer(laptop_file)
    writer.writerow(columns)
    for row in file.to_numpy():
        if count % DISTRIBUTED == 0:
            writer.writerow(row)
            laptop_file.close()
            laptop+=1
            laptop_file = open(rf"./Datasets/Outputs/P4_Section_Laptop{laptop}.csv", "w", newline="")
            writer = csv.writer(laptop_file)
            writer.writerow(columns)
            count+=1
        else:
            count+=1
            writer.writerow(row)
    laptop_file.close()


def current_files() -> None:
    """
    checks the remote servers files and determines which laptop in the distributed system might've errored

    Why do this?

    I can't access the pc's physically, so if there is an error on one device I can retrieve the rest of the genes locally

    How?

    Each PC is given a P4_Section_Laptop#.csv file. So if I see that one file is barely progressing, I can run it locally
    """
    count = 1
    genes = []
    present = []
    with open(rf"./Datasets/Outputs/result.txt", "r") as file:
        for i in file:
            gene = i.replace(" ", "").replace("\n", "").split(".csv")[:-1:]
            genes.extend(gene)
    while count <= 8:
        out_file = pd.read_csv(rf"Datasets/Outputs/P4_Section_Laptop{count}.csv")
        for gene in out_file["Gene"]:
            if gene in genes:
                present.append(gene)
        with open(rf"./Datasets/Outputs/Loaded/P4_Laptop{count}.txt", "w") as file:
            for gene in present:
                file.write(f"{gene}\n")
        present = []
        count+=1


def get_voxel_dataframe() -> None:
    """
    Creates a text file with the mapping between coordinates and their gene expression across all files

    This way we can easily create a csv file by reading a single, organized text file instead of looking for a specific coordinate across all files
    """
    voxels = {}
    file = pd.read_csv("Datasets/Outputs/P4_Section_Data.csv")
    for gene in file["Gene"]:
        gene_file = pd.read_csv(f"Datasets/Outputs/Binned_Voxels/{gene}.csv")
        for _,row in gene_file.iterrows():
            x = float(row["X"])
            y = float(row["Y"])
            z = int(row["Z"])
            density = float(row["Density_2500"])
            coords = (x,y,z)
            if coords not in voxels:
                voxels[coords] = []
            gene_expression = (gene, density)
            voxels[coords].append(gene_expression)

    with open("Datasets/Outputs/voxels.txt", "w") as res_file:
        for key, value in voxels.items():
            res_file.write(f"{key}: {value}\n\n\n")
    

def create_master_voxel_dataframe() -> None:
    header = ["X","Y","Z"]
    file = pd.read_csv("Datasets/Outputs/P4_Section_Data.csv")
    for gene in file["Gene"]:
        header.append(str(gene))
    vox_info = [-1] * len(header)

    with open("Datasets/Outputs/P4_50_NewDenS.csv", "w") as res_file, open("Datasets/Outputs/voxels.txt", "r") as vox_file:
        writer = csv.writer(res_file)
        writer.writerow(header)
        arr = [j for j in vox_file]
        for voxel in arr:
            coords, expression = voxel.split(": ")
            coords = ast.literal_eval(coords)
            expression = ast.literal_eval(expression)
            vox_info[0] = coords[0]
            vox_info[1] = coords[1]
            vox_info[2] = coords[2]

            for gene_exp in expression:
                gene, exp = gene_exp
                if (exp != 0.0):
                    index = header.index(gene)                    
                    vox_info[index] = exp
            
            writer.writerow(vox_info)

    print(vox_info)
    print(header)


def standard_deviation() -> None:
    """
    extremely specific method just to find the standard deviation of a method to find which coordinate is 140 microns

    Hint: it's the z axis
    """
    path = "Datasets/Outputs/New_Voxels/Pdgfrb.csv"

    file = pd.read_csv(path)
    x_vals = []
    y_vals = []
    z_vals = []

    for _,row in file.iterrows():
        x = row["X"]
        y = row["Y"]
        z = row["Z"]
        if x != "error":
            x_vals.append(float(x))
            y_vals.append(float(y))
            z_vals.append(float(z))
    
    print(f"x std: {stdev(x_vals)}")
    print(f"y std: {stdev(y_vals)}")
    print(f"z std: {stdev(z_vals)}")


def split_section_ids(section_ids: list, chunk_size: int = 100) -> list[list]:
    """
    Split array of section id's into a 2d array of sections of 100
    """
    length = len(section_ids)
    if length <= 100:
        return [section_ids]
    
    result = []
    arr = []
    length = len(section_ids)
    for ind in range(length):
        if ind != 0 and ind%100 == 0:
            result.append(arr)
            arr = []
        if ind == length-1:
            arr.append(section_ids[ind])
            result.append(arr)
            arr = []
        arr.append(section_ids[ind])

    return result


def retrieve_data_from_files(func: int, complete_chunk: int) -> list | dict | None:
    """
    Takes in a constant that represents the caller.
    
    returns either a set of all section images or a list of all the data depending on the function
    """
    if func == GET_IMAGE_IDS:
        result = set()
    else:
        return None
    
    file_path = f"Datasets/Outputs/Fill_Negatives/P4_Complete_Chunk_{complete_chunk}.csv"
        
    chunk = pd.read_csv(file_path)
            
    for row in chunk["Section_Image"]:
        if func == GET_IMAGE_IDS:
            result.add(row)
            
    return result


def remove_dictionary_duplicates(dictionary: dict) -> dict:
    """
    remove duplicate values for a dictionaries values
    """
    """
    result = {}
    for key, value in dictionary.items():

        arr = []
        for item in value:
            if item not in arr:
                arr.append(item)
        result[key] = arr
    
    return result
    """
    a = {}
    for key, value in dictionary.items():
        a[key] = list(set(value))
    return a


def create_sub_voxel_dataframe(file_num: int) -> None:
    """
    creates subdataframes for parallel processing
    """
    path = f"Datasets/Outputs/Fill_Negatives/dataframes/P4_50_NewDenS_Laptop{file_num}.csv"
    if is_valid_dataframe(path):
        #reminder I added the "old" here just to compare the dataframes
        file = pd.read_csv(f"Datasets/Outputs/P4_Section_Laptop{file_num}.csv")
        genes = ["X", "Y", "Z"]
        for gene in file["Gene"]:
            genes.append(gene)
            print(gene)
        target_file = pd.read_csv("Datasets/Outputs/P4_50_NewDenS.csv", usecols=genes)
        target_file.to_csv(path, index=False)


def merge_data_frames() -> None:
    """
    Walks over directory of sub dataframes and merges them into one

    Sorts all the frames so they get merged in order

    To do: just make all negative expressions NaN.
    """
    dir_path = "Datasets/Outputs/Fill_Negatives/new_dataframes"
    directory = sorted(os.listdir(dir_path))
    prev = None

    for file in directory:
        file = os.path.join(dir_path, file)
        df = pd.read_csv(file)

        if prev is not None:
            prev = pd.merge(prev, df, on=["X", "Y", "Z"])
        else:
            prev = df
    prev.to_csv("Datasets/Outputs/P4_50_RE_NewDenS.csv", index=False)


def merge_chunks() -> None:
    """
    merges all chunks in each sub folder into one large chunk
    """
    for dir_num in range(FILE_START, FILE_END):
        result_df = None
        dir_path = f"Datasets/Outputs/Fill_Negatives/{dir_num}"
        directory = sorted(os.listdir(dir_path))
        counter = 0

        for file in directory:
            file_path = os.path.join(dir_path, file)
            df = pd.read_csv(file_path)
            result_df = pd.concat([result_df, df], ignore_index=True)
            counter+=1
            print(len(result_df))
            print(counter)

        result_df.to_csv(f"Datasets/Outputs/Fill_Negatives/P4_Complete_Chunk_{dir_num}.csv", index=False)

    #handle the error folder
    dir_path = "Datasets/Outputs/Fill_Negatives/error"
    directory = os.listdir(dir_path)
    result_df = None

    for file in directory:
        file_path = os.path.join(dir_path, file)
        df = pd.read_csv(file_path)
        result_df = pd.concat([result_df, df], ignore_index=True)

    result_df.to_csv("Datasets/Outputs/Fill_Negatives/P4_Complete_Chunk_error.csv", index=False)


def bin_expression_values() -> None:
    """
    Bins expression values into the following by index
    bins[0] = [0]
    bins[1] = (0, .001]
    bins[2] = (.001, .01]
    bins[3] = (.01, .1]
    bins[4] = (.1, 1]

    returns an array of all the bins
    """
    bins = [0, .001, .01, .1, 1]
    values = []
    df = pd.read_csv("Datasets/Outputs/P4_50_NewDenS.csv")
    for _, row in df.iterrows():
        #    Skip X,Y, and Z
        # drop the columns x,y,z cause they could be in any order
        n_row = row[3:]
        for cell in n_row:
            if cell != -1:
                values.append(cell)

    return (bins, values)


def compare_files() -> None:
    for dir_num in range(FILE_START, FILE_END):
        dataframe = pd.read_csv(f"Datasets/Outputs/Fill_Negatives/dataframes/P4_50_NewDenS_Laptop{dir_num}.csv")
        new_dataframe = pd.read_csv(f"Datasets/Outputs/Fill_Negatives/new_dataframes/P4_50_NewDenS_Laptop{dir_num}.csv")
        print(dir_num)
        print(dataframe.compare(new_dataframe))

