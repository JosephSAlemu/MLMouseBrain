from enums.Inequality import Inequality
from utils.utility import Utility
from utils.filter import missing_and_empty_distributions
from image.image import histogram, histogram_negative_distribution

if __name__ == "__main__":
    """util = Utility()
    util.filter_column("idk", None, Inequality.LESS_THAN)"""
    histogram_negative_distribution()
