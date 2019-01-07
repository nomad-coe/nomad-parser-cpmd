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
from .commonparser import CPMDCommonParser
import re
import logging
import numpy as np
LOGGER = logging.getLogger("nomad")


class CPMDSinglePointParser(MainHierarchicalParser):
    """The main parser class that is called for all run types. Parses the CPMD
    output file.
    """
    def __init__(self, parser_context):
        """
        """
        super(CPMDSinglePointParser, self).__init__(parser_context)
        self.setup_common_matcher(CPMDCommonParser(parser_context))
        self.n_scf_iterations = 0

        #=======================================================================
        # Cache levels
        # self.caching_levels.update({
            # 'section_run': CachingLevel.ForwardAndCache,
        # })

        #=======================================================================
        # SimpleMatchers
        self.root_matcher = SM("",
            forwardMatch=True,
            sections=['section_run', "section_single_configuration_calculation", "section_system", "section_method"],
            subMatchers=[
                self.cm.header(),
                self.cm.method(),
                self.cm.atoms(),
                self.cm.cell(),
                self.cm.initialization(),
                SM( " NFI      GEMAX       CNORM           ETOT        DETOT      TCPU",
                    sections=["x_cpmd_section_scf"],
                    subMatchers=[
                        SM( "\s+(?P<x_cpmd_scf_nfi>{0})\s+(?P<x_cpmd_scf_gemax>{1})\s+(?P<x_cpmd_scf_cnorm>{1})\s+(?P<x_cpmd_scf_etot__hartree>{1})\s+(?P<x_cpmd_scf_detot__hartree>{1})\s+(?P<x_cpmd_scf_tcpu__s>{1})".format(self.regexs.int, self.regexs.float),
                            sections=["x_cpmd_section_scf_iteration"],
                            repeats=True,
                        ),
                    ]
                ),
                SM( re.escape(" *                        FINAL RESULTS                         *"),
                    sections=["x_cpmd_section_final_results"],
                    subMatchers=[
                        SM( "   ATOM          COORDINATES            GRADIENTS \(-FORCES\)",
                            adHoc=self.ad_hoc_atom_forces(),
                        ),
                        SM( " \(K\+E1\+L\+N\+X\)           TOTAL ENERGY =\s+(?P<energy_total__hartree>{}) A\.U\.".format(self.regexs.float)),
                        SM( " \(E1=A-S\+R\)     ELECTROSTATIC ENERGY =\s+(?P<energy_electrostatic__hartree>{}) A\.U\.".format(self.regexs.float)),
                        SM( " \(X\)     EXCHANGE-CORRELATION ENERGY =\s+(?P<energy_XC_potential__hartree>{}) A\.U\.".format(self.regexs.float)),
                    ]
                ),
                self.cm.footer(),
            ]
        )

    #=======================================================================
    # onClose triggers
    def onClose_x_cpmd_section_scf_iteration(self, backend, gIndex, section):
        # SCF step energy and energy change
        scf_id = backend.openSection("section_scf_iteration")
        energy = section.get_latest_value("x_cpmd_scf_etot")
        backend.addValue("energy_total_scf_iteration", energy)
        denergy = section.get_latest_value("x_cpmd_scf_detot")
        backend.addValue("energy_change_scf_iteration", denergy)
        backend.closeSection("section_scf_iteration", scf_id)
        self.n_scf_iterations += 1

    def onClose_x_cpmd_section_scf(self, backend, gIndex, section):
        backend.addValue("number_of_scf_iterations", self.n_scf_iterations)

    def onClose_section_system(self, backend, gIndex, section):
        self.cache_service.addArrayValues("atom_positions", "initial_positions", unit="bohr")
        self.cache_service.addArrayValues("atom_labels")
        self.cache_service.addArrayValues("simulation_cell", unit="bohr")
        self.cache_service.addValue("number_of_atoms")

    #=======================================================================
    # adHoc

    def ad_hoc_atom_forces(self):
        """Parses the atomic forces from the final results.
        """
        def wrapper(parser):
            # Define the regex that extracts the information
            regex_string = r"\s+({0})\s+({1})\s+({2})\s+({2})\s+({2})\s+({2})\s+({2})\s+({2})".format(self.regexs.int, self.regexs.word, self.regexs.float)
            regex_compiled = re.compile(regex_string)

            match = True
            forces = []

            while match:
                line = parser.fIn.readline()
                result = regex_compiled.match(line)

                if result:
                    match = True
                    force = [float(x) for x in result.groups()[5:8]]
                    forces.append(force)
                else:
                    match = False

            forces = -np.array(forces)

            # If anything found, push the results to the correct section
            if len(forces) != 0:
                parser.backend.addArrayValues("atom_forces", forces, unit="hartree/bohr")

        return wrapper

    #=======================================================================
    # Misc. functions
