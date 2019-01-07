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

import re
import logging
import datetime
import calendar
import numpy as np
from nomadcore.baseclasses import CommonParser
from nomadcore.simple_parser import SimpleMatcher as SM
from nomadcore.unit_conversion.unit_conversion import convert_unit
from .inputparser import CPMDInputParser
logger = logging.getLogger("nomad")


class CPMDCommonParser(CommonParser):
    """
    This class is used to store and instantiate common parts of the
    hierarchical SimpleMatcher structure used in the parsing of a CPMD
    calculation.
    """
    def __init__(self, parser_context):
        super(CPMDCommonParser, self).__init__(parser_context)

        #=======================================================================
        # Globally cached values
        self.cache_service.add("initial_positions", single=False, update=False)
        self.cache_service.add("atom_labels", single=False, update=False)
        self.cache_service.add("number_of_atoms", single=False, update=False)
        self.cache_service.add("simulation_cell", single=False, update=False)
        self.cache_service.add("n_steps")
        self.cache_service.add("ensemble_type")
        self.cache_service.add("time_step_ions")

        self.cache_service.add("trajectory_range", False)
        self.cache_service.add("trajectory_sample", False)
        self.cache_service.add("print_freq", 1)
        self.cache_service.add("configuration_periodic_dimensions", single=False, update=False)

        self.cache_service.add("single_configuration_calculation_to_system_ref", single=False, update=True)
        self.cache_service.add("single_configuration_to_calculation_method_ref", single=False, update=False)

    #===========================================================================
    # Common SimpleMatchers
    def header(self):
        """Returns the simplematcher that parser the CPMD header containng the
        starting information. Common to all run types.
        """
        return SM( " PROGRAM CPMD STARTED AT",
            forwardMatch=True,
            sections=["x_cpmd_section_start_information"],
            subMatchers=[
                SM( " PROGRAM CPMD STARTED AT: (?P<x_cpmd_start_datetime>{})".format(self.regexs.eol)),
                SM( "\s+VERSION (?P<program_version>\d+\.\d+)"),
                SM( r"\s+\*\*\*  (?P<x_cpmd_compilation_date>[\s\w\-:\d]+)  \*\*\*$"),
                SM( " THE INPUT FILE IS:\s+(?P<x_cpmd_input_filename>{})".format(self.regexs.eol)),
                SM( " THIS JOB RUNS ON:\s+(?P<x_cpmd_run_host_name>{})".format(self.regexs.eol)),
                SM( " THE PROCESS ID IS:\s+(?P<x_cpmd_process_id>{})".format(self.regexs.int)),
                SM( " THE JOB WAS SUBMITTED BY:\s+(?P<x_cpmd_run_user_name>{})".format(self.regexs.eol)),
            ]
        )

    def method(self):
        """Returns the simplematcher that parses informatio about the method
        used. Common to all run types.
        """
        return SM( "(?: SINGLE POINT DENSITY OPTIMIZATION)|(?: OPTIMIZATION OF IONIC POSITIONS)|(?: CAR-PARRINELLO MOLECULAR DYNAMICS)|(?: BORN-OPPENHEIMER MOLECULAR DYNAMICS)",
            subMatchers=[
                SM( " USING SEED",
                    forwardMatch=True,
                    sections=["x_cpmd_section_run_type_information"],
                    subMatchers=[
                        SM( " USING SEED\s+{}\s+TO INIT. PSEUDO RANDOM NUMBER GEN.".format(self.regexs.int)),
                        SM( " PATH TO THE RESTART FILES:\s+{}".format(self.regexs.eol)),
                        SM( " GRAM-SCHMIDT ORTHOGONALIZATION"),
                        SM( " ITERATIVE ORTHOGONALIZATION",
                            subMatchers={
                                SM("    MAXIT:\s+{}".format(self.regexs.int)),
                                SM("    EPS:\s+{}".format(self.regexs.float)),
                            }
                        ),
                        SM( " MAXIMUM NUMBER OF STEPS:\s+(?P<x_cpmd_max_steps>{}) STEPS".format(self.regexs.int)),
                        SM( " MAXIMUM NUMBER OF ITERATIONS FOR SC:\s+(?P<scf_max_iteration>{}) STEPS".format(self.regexs.int)),
                        SM( " PRINT INTERMEDIATE RESULTS EVERY\s+{} STEPS".format(self.regexs.int)),
                        SM( " STORE INTERMEDIATE RESULTS EVERY\s+{} STEPS".format(self.regexs.int)),
                        SM( " STORE INTERMEDIATE RESULTS EVERY\s+{} SELF-CONSISTENT STEPS".format(self.regexs.int)),
                        SM( " NUMBER OF DISTINCT RESTART FILES:\s+{}".format(self.regexs.int)),
                        SM( " TEMPERATURE IS CALCULATED ASSUMING EXTENDED BULK BEHAVIOR"),
                        SM( " FICTITIOUS ELECTRON MASS:\s+{}".format(self.regexs.float)),
                        SM( " TIME STEP FOR ELECTRONS:\s+(?P<x_cpmd_time_step_electrons__hbar_hartree_1>{})".format(self.regexs.float)),
                        SM( " TIME STEP FOR IONS:\s+(?P<x_cpmd_time_step_ions__hbar_hartree_1>{})".format(self.regexs.float)),

                        SM( " TRAJECTORIES ARE SAVED ON FILE"),
                        SM( " TRAJEC\.xyz IS SAVED ON FILE"),
                        SM( " ELECTRON DYNAMICS:"),
                        SM( " ION DYNAMICS:(?P<x_cpmd_ion_temperature_control>{})".format(self.regexs.eol)),

                        SM( " CONVERGENCE CRITERIA FOR WAVEFUNCTION OPTIMIZATION:\s+(?P<scf_threshold_energy_change__hartree>{})".format(self.regexs.float)),
                        SM( " WAVEFUNCTION OPTIMIZATION BY PRECONDITIONED DIIS"),
                        SM( " THRESHOLD FOR THE WF-HESSIAN IS\s+{}".format(self.regexs.float)),
                        SM( " MAXIMUM NUMBER OF VECTORS RETAINED FOR DIIS:\s+{}".format(self.regexs.int)),
                        SM( " STEPS UNTIL DIIS RESET ON POOR PROGRESS:\s+{}".format(self.regexs.int)),
                        SM( " FULL ELECTRONIC GRADIENT IS USED".format(self.regexs.int)),

                        SM( " CONVERGENCE CRITERIA FOR GEOMETRY OPTIMIZATION:\s+(?P<geometry_optimization_threshold_force__hartree_bohr_1>{})".format(self.regexs.float)),
                        SM( " GEOMETRY OPTIMIZATION BY (?P<x_cpmd_geo_opt_method>(?:GDIIS/BFGS)|(?:LOW-MEMORY BFGS)|(?:CONJUGATE GRADIENT)|(?:STEEPEST DESCENT))"),
                        SM( "   SIZE OF GDIIS MATRIX:\s+{}".format(self.regexs.int)),
                        SM( "GEOMETRY OPTIMIZATION IS SAVED ON FILE {}".format(self.regexs.eol)),
                        SM( " EMPIRICAL INITIAL HESSIAN (DISCO PARAMETRISATION)"),

                        SM( " SPLINE INTERPOLATION IN G-SPACE FOR PSEUDOPOTENTIAL FUNCTIONS",
                            subMatchers=[
                                SM( "    NUMBER OF SPLINE POINTS:\s+{}".format(self.regexs.int)),
                            ]
                        ),
                    ]
                ),
                SM( " EXCHANGE CORRELATION FUNCTIONALS",
                    sections=["x_cpmd_section_xc_information"],
                    subMatchers=[
                        # SM( " PROGRAM CPMD STARTED AT: (?P<x_cpmd_start_datetime>{})".format(self.regexs.eol)),
                    ]
                ),
            ]
        )

    def atoms(self):
        """Returns the simplematcher that parses system information including
        the atom labels, positions, and pseudopotentials. Common to all run
        types.
        """
        return SM( re.escape(" ***************************** ATOMS ****************************"),
            forwardMatch=True,
            subMatchers=[
                SM( re.escape(" ***************************** ATOMS ****************************"),
                    sections=["x_cpmd_section_system_information"],
                    subMatchers=[
                        SM( "   NR   TYPE        X(BOHR)        Y(BOHR)        Z(BOHR)     MBL".replace("(", "\(").replace(")", "\)"),
                            adHoc=self.ad_hoc_atom_information()
                        ),
                        SM( " CHARGE:\s+(?P<total_charge>{})".format(self.regexs.int)),
                    ]
                ),
                SM( re.escape("    |    Pseudopotential Report"),
                    sections=["x_cpmd_section_pseudopotential_information"],
                ),
                SM( re.escape(" *   ATOM       MASS   RAGGIO NLCC              PSEUDOPOTENTIAL *"),
                    sections=["x_cpmd_section_atom_kinds"],
                    subMatchers=[
                        SM( " \*\s+(?P<x_cpmd_atom_kind_label>{0})\s+(?P<x_cpmd_atom_kind_mass>{1})\s+(?P<x_cpmd_atom_kind_raggio>{1})\s+(?P<x_cpmd_atom_kind_nlcc>{0})\s+(?P<x_cpmd_atom_kind_pseudopotential_l>{0})\s+(?P<x_cpmd_atom_kind_pseudopotential_type>{0})\s+\*".format(self.regexs.word, self.regexs.float),
                            sections=["x_cpmd_section_atom_kind"],
                            repeats=True,
                        ),
                    ]
                ),
            ]
        )

    def cell(self):
        """Returns the simplematcher that parser the cell information. Common to all run types.
        """
        return SM( re.escape(" ************************** SUPERCELL ***************************"),
            sections=["x_cpmd_section_supercell"],
            subMatchers=[
                SM( " SYMMETRY:\s+(?P<x_cpmd_cell_symmetry>{})".format(self.regexs.eol)),
                SM( " LATTICE CONSTANT\(a\.u\.\):\s+(?P<x_cpmd_cell_lattice_constant>{})".format(self.regexs.float)),
                SM( " CELL DIMENSION:\s+(?P<x_cpmd_cell_dimension>{})".format(self.regexs.eol)),
                SM( " VOLUME\(OMEGA IN BOHR\^3\):\s+(?P<x_cpmd_cell_volume>{})".format(self.regexs.float)),
                SM( " LATTICE VECTOR A1\(BOHR\):\s+(?P<x_cpmd_lattice_vector_A1>{})".format(self.regexs.eol)),
                SM( " LATTICE VECTOR A2\(BOHR\):\s+(?P<x_cpmd_lattice_vector_A2>{})".format(self.regexs.eol)),
                SM( " LATTICE VECTOR A3\(BOHR\):\s+(?P<x_cpmd_lattice_vector_A3>{})".format(self.regexs.eol)),
                SM( " RECIP\. LAT\. VEC\. B1\(2Pi/BOHR\):\s+(?P<x_cpmd_reciprocal_lattice_vector_B1>{})".format(self.regexs.eol)),
                SM( " RECIP\. LAT\. VEC\. B2\(2Pi/BOHR\):\s+(?P<x_cpmd_reciprocal_lattice_vector_B2>{})".format(self.regexs.eol)),
                SM( " RECIP\. LAT\. VEC\. B3\(2Pi/BOHR\):\s+(?P<x_cpmd_reciprocal_lattice_vector_B3>{})".format(self.regexs.eol)),
                SM( " RECIP\. LAT\. VEC\. B3\(2Pi/BOHR\):\s+(?P<x_cpmd_reciprocal_lattice_vector_B3>{})".format(self.regexs.eol)),
                SM( " REAL SPACE MESH:\s+(?P<x_cpmd_real_space_mesh>{})".format(self.regexs.eol)),
                SM( " WAVEFUNCTION CUTOFF\(RYDBERG\):\s+(?P<x_cpmd_wave_function_cutoff>{})".format(self.regexs.float)),
                SM( " DENSITY CUTOFF\(RYDBERG\):          \(DUAL= 4\.00\)\s+(?P<x_cpmd_density_cutoff>{})".format(self.regexs.float)),
                SM( " NUMBER OF PLANE WAVES FOR WAVEFUNCTION CUTOFF:\s+(?P<x_cpmd_number_of_planewaves_wave_function>{})".format(self.regexs.int)),
                SM( " NUMBER OF PLANE WAVES FOR DENSITY CUTOFF:\s+(?P<x_cpmd_number_of_planewaves_density>{})".format(self.regexs.int)),
            ]
        )

    def initialization(self):
        """Returns the simplematcher that parser the atom initialization
        information. Common to all run types.
        """
        return SM(" GENERATE ATOMIC BASIS SET",
            forwardMatch=True,
            sections=["x_cpmd_section_wave_function_initialization"],
            subMatchers=[
            ]
        )

    def footer(self):
        """Returns the simplematcher that parser the CPMD footer containng the
        ending information. Common to all run types.
        """
        return SM( re.escape(" *                            TIMING                            *"),
            forwardMatch=True,
            subMatchers=[
                SM( re.escape(" *                            TIMING                            *"),
                    sections=["x_cpmd_section_timing"],
                    subMatchers=[
                    ]
                ),
                SM( "       CPU TIME :",
                    forwardMatch=True,
                    sections=["x_cpmd_section_end_information"],
                    subMatchers=[
                        # SM( " PROGRAM CPMD STARTED AT: (?P<x_cpmd_start_datetime>{})".format(self.regexs.eol)),
                    ]
                )
            ]
        )

    #===========================================================================
    # onOpen triggers
    def onOpen_section_method(self, backend, gIndex, section):
        self.cache_service["single_configuration_to_calculation_method_ref"] = gIndex

    def onOpen_section_system(self, backend, gIndex, section):
        self.cache_service["single_configuration_calculation_to_system_ref"] = gIndex

    #===========================================================================
    # onClose triggers
    def onClose_section_run(self, backend, gIndex, section):
        backend.addValue("program_name", "CPMD")
        backend.addValue("program_basis_set_type", "plane waves")

    def onClose_section_single_configuration_calculation(self, backend, gIndex, section):
        self.cache_service.addValue("single_configuration_calculation_to_system_ref")
        self.cache_service.addValue("single_configuration_to_calculation_method_ref")

    def onClose_section_system(self, backend, gIndex, section):
        self.cache_service.addArrayValues("configuration_periodic_dimensions")

    def onClose_section_method(self, backend, gIndex, section):
        backend.addValue("electronic_structure_method", "DFT")
        basis_id = backend.openSection("section_method_basis_set")
        backend.addValue("method_basis_set_kind", "wavefunction")
        backend.addValue("mapping_section_method_basis_set_cell_associated", 0)
        backend.closeSection("section_method_basis_set", basis_id)

    def onClose_x_cpmd_section_atom_kind(self, backend, gIndex, section):
        # Atomic kinds
        label = section.get_latest_value("x_cpmd_atom_kind_label")
        number = self.get_atom_number(label)
        id_kind = backend.openSection("section_method_atom_kind")
        backend.addValue("method_atom_kind_atom_number", number)
        backend.addValue("method_atom_kind_label", label)
        backend.closeSection("section_method_atom_kind", id_kind)

    def onClose_x_cpmd_section_start_information(self, backend, gIndex, section):
        # Starting date and time
        start_datetime = section.get_latest_value("x_cpmd_start_datetime")
        timestamp = self.timestamp_from_string(start_datetime)
        if timestamp:
            start_date_stamp, start_wall_time = timestamp
            backend.addValue("time_run_date_start", start_date_stamp)
            backend.addValue("time_run_wall_start", start_wall_time)

        # Input file
        input_filename = section.get_latest_value("x_cpmd_input_filename")
        input_filepath = self.file_service.set_file_id(input_filename, "input")
        if input_filepath is not None:
            input_parser = CPMDInputParser(self.parser_context)
            input_parser.parse(input_filepath)
        else:
            logger.warning("The input file for the calculation could not be found.")

        # Compilation date
        # date = section.get_latest_value("x_cpmd_compilation_date")

    def onClose_x_cpmd_section_supercell(self, backend, gIndex, section):
        # Simulation cell
        A1 = section.get_latest_value("x_cpmd_lattice_vector_A1")
        A2 = section.get_latest_value("x_cpmd_lattice_vector_A2")
        A3 = section.get_latest_value("x_cpmd_lattice_vector_A3")
        A1_array = self.vector_from_string(A1)
        A2_array = self.vector_from_string(A2)
        A3_array = self.vector_from_string(A3)
        cell = np.vstack((A1_array, A2_array, A3_array))
        self.cache_service["simulation_cell"] = cell

        # Plane wave basis
        cutoff = section.get_latest_value("x_cpmd_wave_function_cutoff")
        si_cutoff = convert_unit(cutoff, "rydberg")
        basis_id = backend.openSection("section_basis_set_cell_dependent")
        backend.addValue("basis_set_cell_dependent_kind", "plane_waves")
        backend.addValue("basis_set_cell_dependent_name", "PW_{}".format(cutoff))
        backend.addValue("basis_set_planewave_cutoff", si_cutoff)
        backend.closeSection("section_basis_set_cell_dependent", basis_id)

    def onClose_x_cpmd_section_run_type_information(self, backend, gIndex, section):
        geo_opt_method = section.get_latest_value("x_cpmd_geo_opt_method")
        geo_opt_method_mapping = {
            "GDIIS/BFGS": "bfgs",
            "LOW-MEMORY BFGS": "bfgs",
            "CONJUGATE GRADIENT": "conjugate_gradient",
            "STEEPEST DESCENT": "steepest_descent",
        }
        geo_opt_method = geo_opt_method_mapping.get(geo_opt_method)
        if geo_opt_method is not None:
            backend.addValue("geometry_optimization_method", geo_opt_method)

        # Number of steps
        n_steps = section.get_latest_value("x_cpmd_max_steps")
        self.cache_service["n_steps"] = n_steps

        # Temperature control for ions
        temp_control = section.get_latest_value("x_cpmd_ion_temperature_control")
        if temp_control is not None:
            if temp_control.strip() == "THE TEMPERATURE IS NOT CONTROLLED":
                self.cache_service["ensemble_type"] = "NVE"

        # Ions time step
        time_step_ions = section.get_latest_value("x_cpmd_time_step_ions")
        self.cache_service["time_step_ions"] = time_step_ions

    #===========================================================================
    # adHoc functions
    def ad_hoc_atom_information(self):
        """Parses the atom labels and coordinates.
        """
        def wrapper(parser):
            # Define the regex that extracts the information
            regex_string = r"\s+({0})\s+({1})\s+({2})\s+({2})\s+({2})\s+({0})".format(self.regexs.int, self.regexs.word, self.regexs.float)
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
                self.cache_service["initial_positions"] = coordinates
                self.cache_service["atom_labels"] = labels
                self.cache_service["number_of_atoms"] = coordinates.shape[0]

        return wrapper

    def ad_hoc_positions_forces(self, coord_metaname, force_metaname, coord_unit, force_unit):
        """Parses multiple lines with atom coordinates and forces.
        """
        def wrapper(parser):
            # Define the regex that extracts the information
            regex_string = r"\s+({0})\s+({1})\s+({2})\s+({2})\s+({2})\s+({2})\s+({2})\s+({2})".format(self.regexs.int, self.regexs.word, self.regexs.float)
            regex_compiled = re.compile(regex_string)

            match = True
            coordinates = []
            forces = []

            while match:
                line = parser.fIn.readline()
                result = regex_compiled.match(line)

                if result:
                    match = True
                    coordinate = [float(x) for x in result.groups()[2:5]]
                    force = [float(x) for x in result.groups()[5:8]]
                    coordinates.append(coordinate)
                    forces.append(force)
                else:
                    match = False

            coordinates = np.array(coordinates)
            forces = -np.array(forces)

            # If anything found, push the results to the correct section
            if len(coordinates) == len(forces) and len(coordinates) != 0:
                parser.backend.addArrayValues(coord_metaname, coordinates, unit=coord_unit)
                parser.backend.addArrayValues(force_metaname, forces, unit=force_unit)

        return wrapper

    def debug(self):
        def wrapper(parser):
            print("DEBUG")
        return wrapper

    #===========================================================================
    # Misc. functions
    def timestamp_from_string(self, timestring):

        class UTCtzinfo(datetime.tzinfo):
            """Class that represents the UTC timezone.
            """
            ZERO = datetime.timedelta(0)

            def utcoffset(self, dt):
                return UTCtzinfo.ZERO

            def tzname(self, dt):
                return "UTC"

            def dst(self, dt):
                return UTCtzinfo.ZERO

        """Returns the seconds since epoch for the given date and the wall
        clock seconds for the given wall clock time. Assumes UTC timezone.
        """
        # The start datetime can be formatted in different ways. First we try
        # to determine which way is used.
        try:
            timestring = timestring.strip()
            splitted = timestring.split()
            n_split = len(splitted)
            if n_split == 2:
                date, clock_time = timestring.split()
                year, month, day = [int(x) for x in date.split("-")]
                hour, minute, second, msec = [float(x) for x in re.split("[:.]", clock_time)]

                date_obj = datetime.datetime(year, month, day, tzinfo=UTCtzinfo())
                date_timestamp = (date_obj - datetime.datetime(1970, 1, 1, tzinfo=UTCtzinfo())).total_seconds()

                wall_time = hour*3600+minute*60+second+0.001*msec
            elif n_split == 5:
                weekday, month, day, clock_time, year = timestring.split()
                year = int(year)
                day = int(day)
                hour, minute, second = [float(x) for x in re.split("[:]", clock_time)]
                month_name_to_number = dict((v, k) for k, v in enumerate(calendar.month_abbr))
                month = month_name_to_number[month]

                date_obj = datetime.datetime(year, month, day, tzinfo=UTCtzinfo())
                date_timestamp = (date_obj - datetime.datetime(1970, 1, 1, tzinfo=UTCtzinfo())).total_seconds()
                wall_time = hour*3600+minute*60+second
        # If any sxception is encountered here, just return None as the
        # datetime is not very crucial
        except Exception:
            return None
        else:
            return date_timestamp, wall_time

    def get_atom_number(self, symbol):
        """ Returns the atomic number when given the atomic symbol.

        Args:
            symbol: atomic symbol as string

        Returns:
            The atomic number (number of protons) for the given symbol.
        """
        chemical_symbols = [
            'X',  'H',  'He', 'Li', 'Be',
            'B',  'C',  'N',  'O',  'F',
            'Ne', 'Na', 'Mg', 'Al', 'Si',
            'P',  'S',  'Cl', 'Ar', 'K',
            'Ca', 'Sc', 'Ti', 'V',  'Cr',
            'Mn', 'Fe', 'Co', 'Ni', 'Cu',
            'Zn', 'Ga', 'Ge', 'As', 'Se',
            'Br', 'Kr', 'Rb', 'Sr', 'Y',
            'Zr', 'Nb', 'Mo', 'Tc', 'Ru',
            'Rh', 'Pd', 'Ag', 'Cd', 'In',
            'Sn', 'Sb', 'Te', 'I',  'Xe',
            'Cs', 'Ba', 'La', 'Ce', 'Pr',
            'Nd', 'Pm', 'Sm', 'Eu', 'Gd',
            'Tb', 'Dy', 'Ho', 'Er', 'Tm',
            'Yb', 'Lu', 'Hf', 'Ta', 'W',
            'Re', 'Os', 'Ir', 'Pt', 'Au',
            'Hg', 'Tl', 'Pb', 'Bi', 'Po',
            'At', 'Rn', 'Fr', 'Ra', 'Ac',
            'Th', 'Pa', 'U',  'Np', 'Pu',
            'Am', 'Cm', 'Bk', 'Cf', 'Es',
            'Fm', 'Md', 'No', 'Lr'
        ]

        atom_numbers = {}
        for Z, name in enumerate(chemical_symbols):
            atom_numbers[name] = Z

        return atom_numbers[symbol]

    def vector_from_string(self, vectorstr):
        """Returns a numpy array from a string comprising of floating
        point numbers.
        """
        vectorstr = vectorstr.strip().split()
        vec_array = np.array([float(x) for x in vectorstr])
        return vec_array
