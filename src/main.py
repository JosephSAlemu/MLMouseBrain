from enums.inequality import Inequality
from utils.utility import Utility
from utils.filter import missing_and_empty_distributions_voxels, missing_and_empty_distributions_genes
from image.image import histogram, histogram_negative_distribution
from enums.actions import Action
from enums.inequality import Inequality
from enums.dimensions import Dimensions
from analysis.kmeans import Kmeans

if __name__ == "__main__":
    """util = Utility()
    util.filter_column("idk", None, Inequality.LESS_THAN)"""
    #histogram_negative_distribution(Action.GENES, False)
    util = Utility("Datasets/Outputs/P4_50_RE_90_NewDenS.csv")
    util.z_score_normalize("Z", "Datasets/Outputs/P4_50_RE_90_ZNRM_NewDenS.csv")
    #util.filter_all(Dimensions.BOTH, None, Inequality.LESS_THAN)
    #kmeans = Kmeans()
    #print(kmeans.elbow_plot(15))