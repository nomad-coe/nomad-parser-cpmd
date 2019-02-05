# Copyright 2016-2018 Lauri Himanen, Fawzi Mohamed, Ankit Kariryaa
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

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
