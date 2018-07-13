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


class CPMDGeoOptParser(MainHierarchicalParser):
    """The main parser class that is called for all run types. Parses the CPMD
    output file.
    """
    def __init__(self, parser_context):
        """
        """
        super(CPMDGeoOptParser, self).__init__(parser_context)
        self.setup_common_matcher(CPMDCommonParser(parser_context))
        self.n_frames = 0
        self.sampling_method_gid = None
        self.frame_refs = []
        self.energies = []

        #=======================================================================
        # Cache levels
        # self.caching_levels.update({
            # 'section_run': CachingLevel.ForwardAndCache,
        # })

        #=======================================================================
        # Main structure
        self.root_matcher = SM("",
            forwardMatch=True,
            sections=['section_run', "section_frame_sequence", "section_sampling_method",  "section_method"],
            subMatchers=[
                self.cm.header(),
                self.cm.method(),
                self.cm.atoms(),
                self.cm.cell(),
                self.cm.initialization(),
                SM( " INITIALIZE EMPIRICAL HESSIAN",
                    sections=["x_cpmd_section_geo_opt_initialization"],
                    subMatchers=[
                        SM("                           <<<<< ASSUMED BONDS >>>>>"),
                        SM("\s+{0}\s+<-->\s+{0}".format(self.regexs.int),
                            repeats=True
                        ),
                        SM(" TOTAL NUMBER OF MOLECULAR STRUCTURES:\s+(?P<x_cpmd_total_number_of_molecular_structures>{})".format(self.regexs.int)),
                        SM(re.escape("   ATOM          COORDINATES            GRADIENTS (-FORCES)"),
                            adHoc=self.cm.ad_hoc_positions_forces("x_cpmd_initialized_positions", "x_cpmd_initialized_forces", "bohr", "hartree/bohr"),
                        ),
                        SM(" CPU TIME FOR INITIALIZATION\s+(?P<x_cpmd_geo_opt_initialization_time>{}) SECONDS".format(self.regexs.float)),
                    ]
                ),
                SM( re.escape(" =                  GEOMETRY OPTIMIZATION                       ="),
                    endReStr=re.escape(" =              END OF GEOMETRY OPTIMIZATION                    ="),
                    subMatchers=[
                        SM(" NFI      GEMAX       CNORM           ETOT        DETOT      TCPU"),
                        SM(" EWALD\| SUM IN REAL SPACE OVER"),
                        SM("\s+{0}\s+{1}\s+{1}\s+{1}\s+{1}\s+{1}".format(self.regexs.int, self.regexs.float),
                            forwardMatch=True,
                            endReStr=re.escape(" *** CNSTR="),
                            repeats=True,
                            sections=["section_single_configuration_calculation", "section_system", "x_cpmd_section_geo_opt_step"],
                            subMatchers=[
                                SM( "\s+(?P<x_cpmd_geo_opt_scf_nfi>{0})\s+(?P<x_cpmd_geo_opt_scf_gemax>{1})\s+(?P<x_cpmd_geo_opt_scf_cnorm>{1})\s+(?P<x_cpmd_geo_opt_scf_etot__hartree>{1})\s+(?P<x_cpmd_geo_opt_scf_detot__hartree>{1})\s+(?P<x_cpmd_geo_opt_scf_tcpu__s>{1})".format(self.regexs.int, self.regexs.float),
                                    sections=["x_cpmd_section_geo_opt_scf_iteration"],
                                    repeats=True,
                                ),
                                SM(" RESTART INFORMATION WRITTEN ON FILE\s+{}".format(self.regexs.eol)),
                                SM( re.escape("   ATOM          COORDINATES            GRADIENTS (-FORCES)"),
                                    adHoc=self.cm.ad_hoc_positions_forces("x_cpmd_geo_opt_step_positions", "x_cpmd_geo_opt_step_forces", "bohr", "hartree/bohr"),
                                ),
                                SM(" *** TOTAL STEP NR\.\s+(?P<x_cpmd_geo_opt_step_total_number_of_scf_steps>{0})\s+GEOMETRY STEP NR\.\s+(?P<x_cpmd_geo_opt_step_number>{0})  ***".replace("*", "\*").format(self.regexs.int)),
                                SM(" *** GNMAX=\s+(?P<x_cpmd_geo_opt_step_gnmax>{0})(?:\s+\[{0}\])?\s+ETOT=\s+(?P<x_cpmd_geo_opt_step_etot__hartree>{0})  ***".replace("*", "\*").format(self.regexs.float)),
                                SM(" *** GNORM=\s+(?P<x_cpmd_geo_opt_step_gnorm>{0})\s+DETOT=\s+(?P<x_cpmd_geo_opt_step_detot>{0})  ***".replace("*", "\*").format(self.regexs.float)),
                                SM(" *** CNSTR=\s+(?P<x_cpmd_geo_opt_step_cnstr>{0})\s+TCPU=\s+(?P<x_cpmd_geo_opt_step_tcpu>{0})  ***".replace("*", "\*").format(self.regexs.float)),
                            ]
                        ),
                    ]
                ),
                self.cm.footer(),
            ]
        )

    #=======================================================================
    # onClose triggers
    def onClose_x_cpmd_section_geo_opt_scf_iteration(self, backend, gIndex, section):
        # SCF step energy and energy change
        scf_id = backend.openSection("section_scf_iteration")
        energy = section.get_latest_value("x_cpmd_geo_opt_scf_etot")
        backend.addValue("energy_total_scf_iteration", energy)
        denergy = section.get_latest_value("x_cpmd_geo_opt_scf_detot")
        backend.addValue("energy_change_scf_iteration", denergy)
        backend.closeSection("section_scf_iteration", scf_id)

    def onClose_x_cpmd_section_geo_opt_step(self, backend, gIndex, section):
        total_energy = section.get_latest_value("x_cpmd_geo_opt_step_etot")
        if total_energy:
            backend.addValue("energy_total", total_energy)
            self.energies.append(total_energy)
        forces = section.get_latest_value("x_cpmd_geo_opt_step_forces")
        backend.addArrayValues("atom_forces", forces)
        positions = section.get_latest_value("x_cpmd_geo_opt_step_positions")
        backend.addArrayValues("atom_positions", positions)
        self.n_frames += 1

    def onClose_section_single_configuration_calculation(self, backend, gIndex, section):
        self.frame_refs.append(gIndex)

    def onClose_section_frame_sequence(self, backend, gIndex, section):
        backend.addValue("number_of_frames_in_sequence", self.n_frames)
        if self.sampling_method_gid is not None:
            backend.addValue("frame_sequence_to_sampling_ref", self.sampling_method_gid)
        if self.frame_refs:
            backend.addArrayValues("frame_sequence_local_frames_ref", np.array(self.frame_refs))
        if self.energies:
            backend.addArrayValues("frame_sequence_potential_energy", np.array(self.energies))

    def onClose_section_sampling_method(self, backend, gIndex, section):
        # For single point calculations there is only one method and system.
        self.sampling_method_gid = gIndex
        backend.addValue("sampling_method", "geometry_optimization")

    def onClose_section_system(self, backend, gIndex, section):
        self.cache_service.addArrayValues("atom_labels")
        self.cache_service.addArrayValues("simulation_cell", unit="bohr")
        self.cache_service.addValue("number_of_atoms")

    #=======================================================================
    # adHoc
