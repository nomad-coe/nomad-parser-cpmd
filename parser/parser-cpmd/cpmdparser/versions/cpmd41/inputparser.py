from __future__ import absolute_import
from nomadcore.simple_parser import SimpleMatcher as SM
from nomadcore.baseclasses import MainHierarchicalParser
from nomadcore.caching_backend import CachingLevel
from .commonmatcher import CommonMatcher
import logging
logger = logging.getLogger("nomad")


#===============================================================================
class CPMDSinglePointParser(MainHierarchicalParser):
    """The main parser class. Used to parse the CP2K calculation with run types:
        -ENERGY
        -ENERGY_FORCE
    """
    def __init__(self, file_path, parser_context):
        """
        """
        super(CPMDSinglePointParser, self).__init__(file_path, parser_context)
        self.setup_common_matcher(CommonMatcher(parser_context))

        #=======================================================================
        # Cache levels
        self.caching_level_for_metaname.update({
            'x_cp2k_energy_total_scf_iteration': CachingLevel.ForwardAndCache,
            'x_cp2k_energy_XC_scf_iteration': CachingLevel.ForwardAndCache,
            'x_cp2k_energy_change_scf_iteration': CachingLevel.ForwardAndCache,
            'x_cp2k_stress_tensor': CachingLevel.ForwardAndCache,
            'x_cp2k_section_stress_tensor': CachingLevel.ForwardAndCache,
        })

        #=======================================================================
        # SimpleMatchers
        self.root_matcher = SM("",
            forwardMatch=True,
            sections=['section_run', "section_single_configuration_calculation", "section_system", "section_method"],
            otherMetaInfo=["atom_forces"],
            subMatchers=[
                self.cm.header(),
                self.cm.quickstep_header(),
                self.cm.quickstep_calculation(),
            ]
        )
