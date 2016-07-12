from builtins import str
from builtins import object
import logging
from collections import defaultdict
logger = logging.getLogger("nomad")


metainfo_section_prefix = "x_cpmd_section_input_"
metainfo_data_prefix = "x_cpmd_input_"


#===============================================================================
class Section(object):
    """An input section in a CPMD calculation.
    """
    def __init__(self, name, description=None):
        self.accessed = False
        self.name = name
        self.description = description
        self.keywords = defaultdict(list)
        self.subsections = {}
        self.default_keyword = None

    def get_keyword(self, name):
        keyword = self.keywords.get(name)
        if keyword:
            if len(keyword) == 1:
                return keyword[0]
            else:
                logger.error("The keyword '{}' in '{}' does not exist or has too many entries.".format(name, self.name))

    def get_section(self, name):
        return self.subsections.get(name)


#===============================================================================
class Keyword(object):
    """Keyword in a CPMD input file.
    """
    def __init__(self, name, description=None):
        self.accessed = False
        self.name = name
        self.unique_name = None
        self.available_options = []
        self.options = None
        self.parameters = None
        self.description = description