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

from __future__ import absolute_import
from nomadcore.simple_parser import SimpleMatcher as SM
from nomadcore.baseclasses import MainHierarchicalParser
import numpy as np
from .commonparser import CPMDCommonParser
import re
import logging
LOGGER = logging.getLogger("nomad")


class CPMDVibrationParser(MainHierarchicalParser):
    """The main parser class that is called for all run types. Parses the CPMD
    output file.
    """
    def __init__(self, file_path, parser_context):
        """
        """
        super(CPMDVibrationParser, self).__init__(file_path, parser_context)
        self.setup_common_matcher(CPMDCommonParser(parser_context))
        self.n_frames = 0
        self.sampling_method_gid = None
        self.frame_refs = []
        self.energies = []

        #=======================================================================
        # Main structure
        self.root_matcher = SM("",
            forwardMatch=True,
            sections=['section_run', "section_method"],
            subMatchers=[
                self.cm.header(),
                self.cm.method(),
                self.cm.atoms(),
                self.cm.cell(),
                self.cm.initialization(),
                self.cm.footer(),
            ]
        )

    #=======================================================================
    # onClose triggers
    def onClose_section_system(self, backend, gIndex, section):
        self.cache_service.addArrayValues("atom_labels")
        self.cache_service.addArrayValues("simulation_cell", unit="bohr")
        self.cache_service.addValue("number_of_atoms")

    #=======================================================================
    # adHoc
