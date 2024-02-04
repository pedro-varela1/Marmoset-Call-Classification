"""
Utilities for MarmosetCallClassification
"""
def convert_annotation_codes():
    """
    The original annotation codes are as follows:
    49 phee
    50 twitter
    51 trill
    52 cry
    53 subharmonic phee
    54 and 55 cry-phee.
    31, 56 and 57 are unknown.
    """
    converter = {'u': ('unknown', 31, 'tab:blue'),
                 'p': ('phee', 49, 'tab:orange'),
                 't': ('twitter', 50, 'tab:green'),
                 'r': ('trill', 51, 'tab:red'),
                 'c': ('cry', 52, 'tab:purple'),
                 'm': ('mix', 54, 'tab:pink')}

    return converter
