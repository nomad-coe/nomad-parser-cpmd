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
import re
import logging
import numpy as np
from .commonparser import CPMDCommonParser
from nomadcore.simple_parser import SimpleMatcher as SM
from nomadcore.baseclasses import MainHierarchicalParser
import nomadcore.csvparsing
import nomadcore.configurationreading
LOGGER = logging.getLogger("nomad")


class CPMDMDParser(MainHierarchicalParser):
    """The main parser class that is called for all run types. Parses the CPMD
    output file.
    """
    def __init__(self, parser_context):
        """
        """
        super(CPMDMDParser, self).__init__(parser_context)
        self.setup_common_matcher(CPMDCommonParser(parser_context))
        self.sampling_method_gid = None
        self.frame_refs = []
        self.energies = []

        # Detect what files are available in the same folder where the main
        # file is located.
        self.dcd_filepath = self.file_service.get_absolute_path_to_file("TRAJEC.dcd")
        self.xyz_filepath = self.file_service.get_absolute_path_to_file("TRAJEC.xyz")
        self.trajectory_filepath = self.file_service.get_absolute_path_to_file("TRAJECTORY")
        self.ftrajectory_filepath = self.file_service.get_absolute_path_to_file("FTRAJECTORY")
        self.energies_filepath = self.file_service.get_absolute_path_to_file("ENERGIES")

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
                SM( " DEGREES OF FREEDOM FOR SYSTEM:",
                    sections=["x_cpmd_section_md_initialization"],
                    forwardMatch=True,
                    subMatchers=[
                        SM( " DEGREES OF FREEDOM FOR SYSTEM:"),
                        SM( " RVSCAL| RESCALING IONIC TEMP FROM\s+{0} TO\s+{0}".format(self.regexs.float)),
                        SM( re.escape(" ==                     FORCES INITIALIZATION                  ==")),
                        SM( " EWALD\| SUM IN REAL SPACE OVER\s+{0}\*\s+{0}\*\s+{0} CELLS".format(self.regexs.int)),
                        SM( re.escape(" ==                END OF FORCES INITIALIZATION                ==")),
                        SM( " TIME FOR INITIALIZATION:\s+{} SECONDS".format(self.regexs.float)),
                    ]
                ),
                SM( "       NFI    EKINC   TEMPP           EKS      ECLASSIC          EHAM         DIS    TCPU"),
                SM( re.escape(" *                      AVERAGED QUANTITIES                     *"),
                    sections=["x_cpmd_section_md_averaged_quantities"],
                    subMatchers=[
                        SM( re.escape("                              MEAN VALUE       +/-  RMS DEVIATION")),
                        SM( re.escape("                                     <x>     [<x^2>-<x>^2]**(1/2)")),
                        SM( " ELECTRON KINETIC ENERGY\s+(?P<x_cpmd_electron_kinetic_energy_mean>{0})\s+(?P<x_cpmd_electron_kinetic_energy_std>{0})".format(self.regexs.float)),
                        SM( " IONIC TEMPERATURE\s+(?P<x_cpmd_ionic_temperature_mean>{0})\s+(?P<x_cpmd_ionic_temperature_std>{0})".format(self.regexs.float)),
                        SM( " DENSITY FUNCTIONAL ENERGY\s+(?P<x_cpmd_density_functional_energy_mean>{0})\s+(?P<x_cpmd_density_functional_energy_std>{0})".format(self.regexs.float)),
                        SM( " CLASSICAL ENERGY\s+(?P<x_cpmd_classical_energy_mean>{0})\s+(?P<x_cpmd_classical_energy_std>{0})".format(self.regexs.float)),
                        SM( " CONSERVED ENERGY\s+(?P<x_cpmd_conserved_energy_mean>{0})\s+(?P<x_cpmd_conserved_energy_std>{0})".format(self.regexs.float)),
                        SM( " NOSE ENERGY ELECTRONS\s+(?P<x_cpmd_nose_energy_electrons_mean>{0})\s+(?P<x_cpmd_nose_energy_electrons_std>{0})".format(self.regexs.float)),
                        SM( " NOSE ENERGY IONS\s+(?P<x_cpmd_nose_energy_ions_mean>{0})\s+(?P<x_cpmd_nose_energy_ions_std>{0})              0.000000              0.00000    ".format(self.regexs.float)),
                        SM( " CONSTRAINTS ENERGY\s+(?P<x_cpmd_constraints_energy_mean>{0})\s+(?P<x_cpmd_constraints_energy_std>{0})".format(self.regexs.float)),
                        SM( " RESTRAINTS ENERGY\s+(?P<x_cpmd_restraints_energy_mean>{0})\s+(?P<x_cpmd_restraints_energy_std>{0})".format(self.regexs.float)),
                        SM( " ION DISPLACEMENT\s+(?P<x_cpmd_ion_displacement_mean>{0})\s+(?P<x_cpmd_ion_displacement_std>{0})".format(self.regexs.float)),
                        SM( " CPU TIME\s+(?P<x_cpmd_cpu_time_mean>{0})".format(self.regexs.float)),
                    ]
                ),
                self.cm.footer(),
            ]
        )

    #===========================================================================
    # onClose triggers
    def onClose_section_sampling_method(self, backend, gIndex, section):
        self.sampling_method_gid = gIndex
        backend.addValue("sampling_method", "molecular_dynamics")
        self.cache_service.addValue("ensemble_type")

    def onClose_x_cpmd_section_md_averaged_quantities(self, backend, gIndex, section):
        cons_mean = section.get_latest_value("x_cpmd_conserved_energy_mean")
        cons_std = section.get_latest_value("x_cpmd_conserved_energy_std")
        temp_mean = section.get_latest_value("x_cpmd_ionic_temperature_mean")
        temp_std = section.get_latest_value("x_cpmd_ionic_temperature_std")
        pot_mean = section.get_latest_value("x_cpmd_density_functional_energy_mean")
        pot_std = section.get_latest_value("x_cpmd_density_functional_energy_std")

        self.parse_md()

        if temp_mean is not None and temp_std is not None:
            backend.addArrayValues("frame_sequence_temperature_stats", np.array([temp_mean, temp_std]), unit="K")
        if cons_mean is not None and cons_std is not None:
            backend.addArrayValues("frame_sequence_conserved_quantity_stats", np.array([cons_mean, cons_std]), unit="hartree")
        if pot_mean is not None and pot_std is not None:
            backend.addArrayValues("frame_sequence_potential_energy_stats", np.array([pot_mean, pot_std]), unit="hartree")

    #===========================================================================
    # adHoc
    def parse_md(self):
        """Parses all the md step information.
        """
        # Decide from which file trajectory is read
        n_atoms = self.cache_service["number_of_atoms"]
        trajectory_range = self.cache_service["trajectory_range"]
        trajectory_sample = self.cache_service["trajectory_sample"]
        print_freq = self.cache_service["print_freq"]
        read_trajectory = True
        traj_file = None
        traj_step = 1
        trajec_file_iterator = None
        if self.dcd_filepath is not None:
            traj_file = self.dcd_filepath
        elif self.xyz_filepath is not None:
            traj_file = self.xyz_filepath

        # Initialize the TRAJEC file iterator
        if traj_file is not None:
            try:
                trajec_file_iterator = nomadcore.configurationreading.iread(traj_file)
            except ValueError:
                pass

        # If RANGE is not specified, initialize the TRAJECTORY and FTRAJECTORY
        # iterators if files available
        ftrajectory_file_iterator = None
        trajectory_file_iterator = None
        if not trajectory_range:
            if self.ftrajectory_filepath is not None:
                ftrajectory_file_iterator = nomadcore.csvparsing.iread(self.ftrajectory_filepath, columns=range(10), n_conf=n_atoms)
            if self.trajectory_filepath is not None:
                trajectory_file_iterator = nomadcore.csvparsing.iread(self.trajectory_filepath, columns=range(7), n_conf=n_atoms)

        # Initialize the ENERGIES file iterator
        energies_iterator = None
        if self.energies_filepath is not None:
            energies_iterator = nomadcore.csvparsing.iread(self.energies_filepath, columns=range(8))

        # Start reading the frames
        i_frame = 0
        n_frames = self.cache_service["n_steps"]
        time_step = self.cache_service["time_step_ions"]
        self.backend.addArrayValues("frame_sequence_time", np.array([(x+1)*time_step for x in range(n_frames)]))
        self.backend.addValue("number_of_frames_in_sequence", n_frames)

        temperatures = []
        potential_energies = []
        kinetic_energies = []
        conserved_quantities = []

        for i_frame in range(n_frames):

            # Open sections
            scc_id = self.backend.openSection("section_single_configuration_calculation")
            sys_id = self.backend.openSection("section_system")

            # System
            self.cache_service.addArrayValues("atom_labels")
            self.cache_service.addArrayValues("simulation_cell", unit="bohr")
            self.cache_service.addValue("number_of_atoms")

            if print_freq is not None:
                if i_frame % print_freq == 0:

                    # TRAJEC file
                    if trajec_file_iterator is not None:
                        try:
                            pos = next(trajec_file_iterator)
                        except StopIteration:
                            LOGGER.error("Could not get the next geometries from a TRAJEC file.")
                        else:
                            self.backend.addArrayValues("atom_positions", pos, unit="angstrom")

                    # FTRAJECTORY file
                    if ftrajectory_file_iterator is not None:
                        try:
                            values = next(ftrajectory_file_iterator)
                        except StopIteration:
                            LOGGER.error("Could not get the next configuration from a FTRAJECTORY file.")
                        else:
                            velocities = values[:, 4:7]
                            self.backend.addArrayValues("atom_velocities", velocities, unit="bohr/(hbar/hartree)")

                            forces = values[:, 7:10]
                            self.backend.addArrayValues("atom_forces", forces, unit="hartree / bohr")

                            if trajec_file_iterator is None:
                                pos = values[:, 1:4]
                                self.backend.addArrayValues("atom_positions", pos, unit="bohr")

                    # TRAJECTORY file
                    if ftrajectory_file_iterator is None:
                        if trajectory_file_iterator is not None:
                            try:
                                values = next(trajectory_file_iterator)
                            except StopIteration:
                                LOGGER.error("Could not get the next configuration from a TRAJECTORY file.")
                            else:
                                velocities = values[:, 4:]
                                self.backend.addArrayValues("atom_velocities", velocities, unit="bohr/(hbar/hartree)")

                                if trajec_file_iterator is None:
                                    pos = values[:, 1:4]
                                    self.backend.addArrayValues("atom_positions", pos, unit="bohr")

            # Energies file
            if energies_iterator is not None:
                try:
                    values = next(energies_iterator)
                except StopIteration:
                    LOGGER.error("Could not get the next configuration from an ENERGIES file.")
                else:
                    potential_energy = values[3]
                    conserved_quantity = values[5]
                    ion_total_energy = values[4]
                    kinetic_energy = ion_total_energy - potential_energy
                    temperature = values[2]
                    # electronic_kinetic_energy = values[1]
                    # msd = values[6]
                    # i_step = values[0]
                    tcpu = values[7]
                    conserved_quantities.append(conserved_quantity)
                    potential_energies.append(potential_energy)
                    kinetic_energies.append(kinetic_energy)
                    temperatures.append(temperature)
                    self.backend.addRealValue("energy_total", potential_energy, unit="hartree")
                    self.backend.addValue("time_calculation", tcpu)

            # Close sections
            self.backend.closeSection("section_single_configuration_calculation", scc_id)
            self.backend.closeSection("section_system", sys_id)

        # Push the summaries
        if potential_energies:
            potential_energies = np.array(potential_energies)
            self.backend.addArrayValues("frame_sequence_potential_energy", potential_energies, unit="hartree")
        if kinetic_energies:
            kinetic_energies = np.array(kinetic_energies)
            self.backend.addArrayValues("frame_sequence_kinetic_energy", kinetic_energies, unit="hartree")

            # Push the statistics. CPMD prints some statistics at the end, but the
            # mean and std of kinetic energy are missing
            kin_mean = kinetic_energies.mean()
            kin_temp = (kinetic_energies - kin_mean)
            kin_std = np.sqrt(np.dot(kin_temp, kin_temp)/kinetic_energies.size)
            kin_temp = None
            self.backend.addArrayValues("frame_sequence_kinetic_energy_stats", np.array([kin_mean, kin_std]), unit="hartree")

        if conserved_quantities:
            conserved_quantities = np.array(conserved_quantities)
            self.backend.addArrayValues("frame_sequence_conserved_quantity", conserved_quantities, unit="hartree")
        if temperatures:
            temperatures = np.array(temperatures)
            self.backend.addArrayValues("frame_sequence_temperature", temperatures, unit="K")
