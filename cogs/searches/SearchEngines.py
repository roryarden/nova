from enum import Enum, unique

@unique
class SearchEngine(Enum):
    """
    A simple enumeration of search engines, their base URL's, and any
    default parameters we may want to specify.
    """
    GOOGLE = {
        'url': 'https://www.google.com/search?',
        'params': {
            'tbm': 'isch',
            'q': None,
            'safe': 'active',    # Can be 'off' or 'active'.
        },
    }

    BING = {
        'url': 'https://www.bing.com/images/search?',
        'params': {
            'q': None,
            'safesearch': 'strict',    # Can be 'off', 'moderate', or 'strict'.
        },
    }
