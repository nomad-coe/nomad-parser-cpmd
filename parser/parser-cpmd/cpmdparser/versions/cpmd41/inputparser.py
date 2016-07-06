from __future__ import absolute_import
from nomadcore.simple_parser import SimpleMatcher as SM
from nomadcore.baseclasses import SubHierarchicalParser
# from nomadcore.caching_backend import CachingLevel
import logging
logger = logging.getLogger("nomad")


#===============================================================================
class CPMDInputParser(SubHierarchicalParser):
    """Parses the CPMD input file.
    """
    def __init__(self, file_path, parser_context):
        """
        """
        super(CPMDInputParser, self).__init__(file_path, parser_context)

        #=======================================================================
        # Cache levels
        # self.caching_level_for_metaname.update({
            # 'x_cp2k_energy_total_scf_iteration': CachingLevel.ForwardAndCache,
        # })

        #=======================================================================
        # SimpleMatchers
        self.root_matcher = SM("",
            forwardMatch=True,
        )
