import pandas as pd

#Merges the p4 structure annotations with the p4 genes
def merge_genes_annotations() -> None:
    genes = pd.read_csv("Datasets\Inputs\DevelopingMB_Density_P4.csv")
    annotations = pd.read_csv("Datasets\Inputs\P4_structure_annotations.csv")
    merged = pd.merge(annotations, genes, left_on=["voxRowNum"], right_index=True, how="inner")
    merged.to_csv("./Datasets/Outputs/P4_Complete_Brain.csv", index=False)
