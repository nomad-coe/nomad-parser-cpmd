from __future__ import absolute_import
from nomadcore.simple_parser import SimpleMatcher as SM
from nomadcore.baseclasses import MainHierarchicalParser
from nomadcore.unit_conversion.unit_conversion import convert_unit
from nomadcore.caching_backend import CachingLevel
from .commonparser import CPMDCommonParser
from .inputparser import CPMDInputParser
import re
import logging
import datetime
import numpy as np
logger = logging.getLogger("nomad")


#===============================================================================
class CPMDMainParser(MainHierarchicalParser):
    """The main parser class that is called for all run types. Parses the CPMD
    output file.
    """
    def __init__(self, file_path, parser_context):
        """
        """
        super(CPMDMainParser, self).__init__(file_path, parser_context)
        self.setup_common_matcher(CPMDCommonParser(parser_context))

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
                SM( " PROGRAM CPMD STARTED AT",
                    forwardMatch=True,
                    sections=["x_cpmd_section_start_information"],
                    subMatchers=[
                        SM( " PROGRAM CPMD STARTED AT: (?P<x_cpmd_start_datetime>{})".format(self.regexs.regex_eol)),
                        SM( "\s+VERSION (?P<program_version>\d+\.\d+)"),
                        SM( " THE INPUT FILE IS:\s+(?P<x_cpmd_input_filename>{})".format(self.regexs.regex_eol)),
                        SM( " THIS JOB RUNS ON:\s+(?P<x_cpmd_run_host_name>{})".format(self.regexs.regex_eol)),
                        SM( " THE PROCESS ID IS:\s+(?P<x_cpmd_process_id>{})".format(self.regexs.regex_i)),
                        SM( " THE JOB WAS SUBMITTED BY:\s+(?P<x_cpmd_run_user_name>{})".format(self.regexs.regex_eol)),
                    ]
                ),
                SM( " SINGLE POINT DENSITY OPTIMIZATION",
                    sections=["x_cpmd_section_run_type_information"],
                    subMatchers=[
                        SM( " USING SEED\s+{}\s+TO INIT. PSEUDO RANDOM NUMBER GEN.".format(self.regexs.regex_i)),
                        SM( " PATH TO THE RESTART FILES:\s+{}".format(self.regexs.regex_eol)),
                        SM( " GRAM-SCHMIDT ORTHOGONALIZATION"),
                        SM( " MAXIMUM NUMBER OF STEPS:\s+{} STEPS".format(self.regexs.regex_i)),
                        SM( " MAXIMUM NUMBER OF ITERATIONS FOR SC:\s+{} STEPS".format(self.regexs.regex_i)),
                        SM( " PRINT INTERMEDIATE RESULTS EVERY\s+{} STEPS".format(self.regexs.regex_i)),
                        SM( " STORE INTERMEDIATE RESULTS EVERY\s+{} STEPS".format(self.regexs.regex_i)),
                        SM( " NUMBER OF DISTINCT RESTART FILES:\s+{}".format(self.regexs.regex_i)),
                        SM( " TEMPERATURE IS CALCULATED ASSUMING EXTENDED BULK BEHAVIOR"),
                        SM( " FICTITIOUS ELECTRON MASS:\s+{}".format(self.regexs.regex_f)),
                        SM( " TIME STEP FOR ELECTRONS:\s+{}".format(self.regexs.regex_f)),
                        SM( " TIME STEP FOR IONS:\s+{}".format(self.regexs.regex_f)),
                        SM( " CONVERGENCE CRITERIA FOR WAVEFUNCTION OPTIMIZATION:\s+{}".format(self.regexs.regex_f)),
                        SM( " WAVEFUNCTION OPTIMIZATION BY PRECONDITIONED DIIS"),
                        SM( " THRESHOLD FOR THE WF-HESSIAN IS\s+{}".format(self.regexs.regex_f)),
                        SM( " MAXIMUM NUMBER OF VECTORS RETAINED FOR DIIS:\s+{}".format(self.regexs.regex_i)),
                        SM( " STEPS UNTIL DIIS RESET ON POOR PROGRESS:\s+{}".format(self.regexs.regex_i)),
                        SM( " FULL ELECTRONIC GRADIENT IS USED".format(self.regexs.regex_i)),
                        SM( " SPLINE INTERPOLATION IN G-SPACE FOR PSEUDOPOTENTIAL FUNCTIONS",
                            subMatchers=[
                                SM( "    NUMBER OF SPLINE POINTS:\s+{}".format(self.regexs.regex_i)),
                            ]
                        ),
                    ]
                ),
                SM( " EXCHANGE CORRELATION FUNCTIONALS",
                    sections=["x_cpmd_section_xc_information"],
                    subMatchers=[
                        # SM( " PROGRAM CPMD STARTED AT: (?P<x_cpmd_start_datetime>{})".format(self.regexs.regex_eol)),
                    ]
                ),
                SM( " ***************************** ATOMS ****************************".replace("*", "\*"),
                    sections=["x_cpmd_section_system_information"],
                    subMatchers=[
                        SM( "   NR   TYPE        X(BOHR)        Y(BOHR)        Z(BOHR)     MBL".replace("(", "\(").replace(")", "\)"),
                            adHoc=self.ad_hoc_atom_information()
                        ),
                        SM( " CHARGE:\s+(?P<total_charge>{})".format(self.regexs.regex_i)),
                    ]
                ),
                SM( "    \|    Pseudopotential Report",
                    sections=["x_cpmd_section_pseudopotential_information"],
                    subMatchers=[
                        # SM( " PROGRAM CPMD STARTED AT: (?P<x_cpmd_start_datetime>{})".format(self.regexs.regex_eol)),
                    ]
                ),
                SM( " ************************** SUPERCELL ***************************".replace("*", "\*"),
                    sections=["x_cpmd_section_supercell"],
                    subMatchers=[
                        SM( " SYMMETRY:\s+(?P<x_cpmd_cell_symmetry>{})".format(self.regexs.regex_eol)),
                        SM( " LATTICE CONSTANT\(a\.u\.\):\s+(?P<x_cpmd_cell_lattice_constant>{})".format(self.regexs.regex_f)),
                        SM( " CELL DIMENSION:\s+(?P<x_cpmd_cell_dimension>{})".format(self.regexs.regex_eol)),
                        SM( " VOLUME\(OMEGA IN BOHR\^3\):\s+(?P<x_cpmd_cell_volume>{})".format(self.regexs.regex_f)),
                        SM( " LATTICE VECTOR A1\(BOHR\):\s+(?P<x_cpmd_lattice_vector_A1>{})".format(self.regexs.regex_eol)),
                        SM( " LATTICE VECTOR A2\(BOHR\):\s+(?P<x_cpmd_lattice_vector_A2>{})".format(self.regexs.regex_eol)),
                        SM( " LATTICE VECTOR A3\(BOHR\):\s+(?P<x_cpmd_lattice_vector_A3>{})".format(self.regexs.regex_eol)),
                        SM( " RECIP\. LAT\. VEC\. B1\(2Pi/BOHR\):\s+(?P<x_cpmd_reciprocal_lattice_vector_B1>{})".format(self.regexs.regex_eol)),
                        SM( " RECIP\. LAT\. VEC\. B2\(2Pi/BOHR\):\s+(?P<x_cpmd_reciprocal_lattice_vector_B2>{})".format(self.regexs.regex_eol)),
                        SM( " RECIP\. LAT\. VEC\. B3\(2Pi/BOHR\):\s+(?P<x_cpmd_reciprocal_lattice_vector_B3>{})".format(self.regexs.regex_eol)),
                        SM( " RECIP\. LAT\. VEC\. B3\(2Pi/BOHR\):\s+(?P<x_cpmd_reciprocal_lattice_vector_B3>{})".format(self.regexs.regex_eol)),
                        SM( " REAL SPACE MESH:\s+(?P<x_cpmd_real_space_mesh>{})".format(self.regexs.regex_eol)),
                        SM( " WAVEFUNCTION CUTOFF\(RYDBERG\):\s+(?P<x_cpmd_wave_function_cutoff>{})".format(self.regexs.regex_f)),
                        SM( " DENSITY CUTOFF\(RYDBERG\):          \(DUAL= 4\.00\)\s+(?P<x_cpmd_density_cutoff>{})".format(self.regexs.regex_f)),
                        SM( " NUMBER OF PLANE WAVES FOR WAVEFUNCTION CUTOFF:\s+(?P<x_cpmd_number_of_planewaves_wave_function>{})".format(self.regexs.regex_i)),
                        SM( " NUMBER OF PLANE WAVES FOR DENSITY CUTOFF:\s+(?P<x_cpmd_number_of_planewaves_density>{})".format(self.regexs.regex_i)),
                    ]
                ),
                SM( " GENERATE ATOMIC BASIS SET",
                    sections=["x_cpmd_section_wave_function_initialization"],
                    subMatchers=[
                        # SM( " PROGRAM CPMD STARTED AT: (?P<x_cpmd_start_datetime>{})".format(self.regexs.regex_eol)),
                    ]
                ),
                SM( " NFI      GEMAX       CNORM           ETOT        DETOT      TCPU",
                    sections=["x_cpmd_section_scf"],
                    subMatchers=[
                        SM( "\s+{0}\s+{1}\s+{1}\s+{1}\s+{1}\s+{1}".format(self.regexs.regex_i, self.regexs.regex_f),
                            sections=["section_scf_iteration"],
                            repeats=True,
                        ),
                    ]
                ),
                SM( " *                        FINAL RESULTS                         *".replace("*", "\*"),
                    sections=["x_cpmd_section_final_results"],
                    subMatchers=[
                        SM( "   ATOM          COORDINATES            GRADIENTS \(-FORCES\)",
                            adHoc=self.ad_hoc_atom_forces(),
                        ),
                        SM( " \(K\+E1\+L\+N\+X\)           TOTAL ENERGY =\s+(?P<energy_total__hartree>{}) A\.U\.".format(self.regexs.regex_f)),
                        SM( " \(E1=A-S\+R\)     ELECTROSTATIC ENERGY =\s+(?P<energy_electrostatic__hartree>{}) A\.U\.".format(self.regexs.regex_f)),
                        SM( " \(X\)     EXCHANGE-CORRELATION ENERGY =\s+(?P<energy_XC_potential__hartree>{}) A\.U\.".format(self.regexs.regex_f)),
                    ]
                ),
                SM( " *                            TIMING                            *".replace("*", "\*"),
                    sections=["x_cpmd_section_timing"],
                    subMatchers=[
                    ]
                ),
                SM( "       CPU TIME :",
                    forwardMatch=True,
                    sections=["x_cpmd_section_end_information"],
                    subMatchers=[
                        # SM( " PROGRAM CPMD STARTED AT: (?P<x_cpmd_start_datetime>{})".format(self.regexs.regex_eol)),
                    ]
                )
            ]
        )

    #=======================================================================
    # onClose triggers
    def onClose_x_cpmd_section_start_information(self, backend, gIndex, section):
        # Starting date and time
        start_datetime = section.get_latest_value("x_cpmd_start_datetime")
        start_date_stamp, start_wall_time = self.timestamp_from_string(start_datetime)
        backend.addValue("time_run_date_start", start_date_stamp)
        backend.addValue("time_run_wall_start", start_wall_time)

        # Input file
        input_filename = section.get_latest_value("x_cpmd_input_filename")
        input_filepath = self.file_service.set_file_id(input_filename, "input")
        if input_filepath is not None:
            input_parser = CPMDInputParser(input_filepath, self.parser_context)
            input_parser.parse()
        else:
            logger.warning("The input file for the calculation could not be found.")

    def onClose_x_cpmd_section_supercell(self, backend, gIndex, section):
        # Simulation cell
        A1 = section.get_latest_value("x_cpmd_lattice_vector_A1")
        A2 = section.get_latest_value("x_cpmd_lattice_vector_A2")
        A3 = section.get_latest_value("x_cpmd_lattice_vector_A3")
        A1_array = self.vector_from_string(A1)
        A2_array = self.vector_from_string(A2)
        A3_array = self.vector_from_string(A3)
        cell = np.vstack((A1_array, A2_array, A3_array))
        backend.addArrayValues("simulation_cell", cell, unit="bohr")

        # Plane wave basis
        cutoff = section.get_latest_value("x_cpmd_wave_function_cutoff")
        si_cutoff = convert_unit(cutoff, "rydberg")
        basis_id = backend.openSection("section_basis_set_cell_dependent")
        backend.addValue("basis_set_cell_dependent_kind", "plane_waves")
        backend.addValue("basis_set_cell_dependent_name", "PW_{}".format(cutoff))
        backend.addValue("basis_set_planewave_cutoff", si_cutoff)
        backend.closeSection("section_basis_set_cell_dependent", basis_id)

    #=======================================================================
    # adHoc
    def debug(self):
        def wrapper(parser):
            print("DEBUG")
        return wrapper

    def ad_hoc_atom_information(self):
        """Parses the atom labels and coordinates.
        """
        def wrapper(parser):
            # Define the regex that extracts the information
            regex_string = r"\s+({0})\s+({1})\s+({2})\s+({2})\s+({2})\s+({0})".format(self.regexs.regex_i, self.regexs.regex_word, self.regexs.regex_f)
            regex_compiled = re.compile(regex_string)

            match = True
            coordinates = []
            labels = []

            while match:
                line = parser.fIn.readline()
                result = regex_compiled.match(line)

                if result:
                    match = True
                    label = result.groups()[1]
                    labels.append(label)
                    coordinate = [float(x) for x in result.groups()[2:5]]
                    coordinates.append(coordinate)
                else:
                    match = False

            coordinates = np.array(coordinates)
            labels = np.array(labels)

            # If anything found, push the results to the correct section
            if len(coordinates) != 0:
                parser.backend.addArrayValues("atom_positions", coordinates, unit="bohr")
                parser.backend.addArrayValues("atom_labels", labels)
                parser.backend.addValue("number_of_atoms", coordinates.shape[0])

        return wrapper

    def ad_hoc_atom_forces(self):
        """Parses the atomic forces from the final results.
        """
        def wrapper(parser):
            # Define the regex that extracts the information
            regex_string = r"\s+({0})\s+({1})\s+({2})\s+({2})\s+({2})\s+({2})\s+({2})\s+({2})".format(self.regexs.regex_i, self.regexs.regex_word, self.regexs.regex_f)
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
    # misc. functions
    def timestamp_from_string(self, timestring):
        timestring = timestring.strip()
        date, time = timestring.split()
        year, month, day = [int(x) for x in date.split("-")]
        hour, minute, second, msec = [float(x) for x in re.split("[:.]", time)]
        date_stamp = datetime.datetime(year, month, day).timestamp()
        wall_time = hour*3600+minute*60+second+0.001*msec
        return date_stamp, wall_time

    def vector_from_string(self, vectorstr):
        """Returns a numpy array from a string comprising of floating
        point numbers.
        """
        vectorstr = vectorstr.strip().split()
        vec_array = np.array([float(x) for x in vectorstr])
        return vec_array