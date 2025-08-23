from src.constants import HEADERS_V2, HEADERS_V3
from src.enums.inequality import Inequality
from scripts.script import strip_experiments
from src.utils.utility import Utility
from src.utils.filter import drop_rows, missing_and_empty_distributions_voxels, missing_and_empty_distributions_genes
from src.image.oldimage import histogram, histogram_negative_distribution
from src.enums.actions import Action
from src.enums.dimensions import Dimensions
from src.analysis.kmeans import Kmeans
from src.api.newapi import Api
from src.utils.visualize import Visualize

import pandas as pd


if __name__ == "__main__":
    #util = Utility()
    #util.filter_column("idk", None, Inequality.LESS_THAN)
    #histogram_negative_distribution(Action.GENES, False)
    #util = Utility("Datasets/Outputs/P4_Brainstem_15.csv")
    #other_file = "Datasets/Outputs/P4_Brainstem_15_ZNRM.csv"
    #util.z_score_normalize("Z", other_file, HEADERS_V2)
    #util.file = other_file
    #other_file = "Datasets/Outputs/P4_Brainstem_15_ZNRM_KNN.csv"
    #util.knn_imputation(other_file, HEADERS_V2)

    #util.file = other_file
    #util.k_means_prep("Datasets/Outputs/P4_Brainstem_15_ZNRM_KNN_K.csv", HEADERS_V2)
    #util.k_means_result("/home/jalemu/Motorola/brainstem-project/y/home/jalemu/Motorola/MLMouseBrain/Datasets/Outputs/P4_Brainstem_15_ZNRM_KNN_K.csv", "Datasets/Outputs/P4_Brainstem_15_ZNRM_KNN_COMPLETE.csv", HEADERS_V3)
    #util.count_missing_expressions()
    #util.filter_all(Dimensions.BOTH, None, Inequality.LESS_THAN)
    #kmeans = Kmeans()
    #print(kmeans.elbow_plot(15))
    #api = Api()
    #api.download_section_images()
    #util.substitute_voxels_gene_expressions("Datasets/Outputs/P4_Complete_Brain.csv")

    #histogram_negative_distribution(Action.GENES, False, "Datasets/Outputs/P4_Brainstem_15.csv")
    #drop_rows()
    
    #util = Utility("Datasets/Outputs/P4_50_NewDenS.csv")
    #util.impute("mean", "Datasets/Outputs/P4_50_IM_NewDenS.csv")

    #strip_experiments("Datasets/Outputs/p4_NewDenS.csv", "Datasets/Outputs/p4_NewDenS_NEX.csv")
    #util = Utility("Datasets/Outputs/P4_50_NewDenS.csv")

    #util.get_common_voxels("Datasets/Outputs/p4_NewDenS_NEX.csv", "Datasets/Outputs/p4_match.csv")

    visual = Visualize("Datasets/Outputs/p4_NewDenS.csv", HEADERS_V2)
    visual.histogram("log", "Expression Range", "Frequency", "Distribution of Voxel Gene Expressions", e_bins=True, right=True)
    #get_columns("Datasets/Outputs/P4_50_NewDenS.csv")
    

