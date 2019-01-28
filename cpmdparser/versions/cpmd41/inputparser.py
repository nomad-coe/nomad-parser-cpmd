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

import os
import pickle
import numpy as np
from nomadcore.baseclasses import AbstractBaseParser
from cpmdparser.generic.inputparsing import metainfo_data_prefix, metainfo_section_prefix


class CPMDInputParser(AbstractBaseParser):
    """Parses the CPMD input file.
    """
    def __init__(self, parser_context):
        """
        """
        super(CPMDInputParser, self).__init__(parser_context)
        self.input_tree = None

    def parse(self, filepath):
        self.setup_input_tree(self.parser_context.version_id)
        self.collect_input(filepath)
        self.analyze_input()
        self.fill_metadata()

    def collect_input(self, filepath):
        """This function will first go through the input file and gather the
        information to the input tree.

        The data is not directly pushed to the backend inside this function
        because it is safer to first validate the whole structure and only then
        push it.
        """
        # The input file should be relatively small so we are better off
        # loading it into memory all at once.
        lines = None
        with open(filepath, "r") as fin:
            lines = fin.readlines()

        # Read the input line by line
        section_stack = []
        section_name = None
        section_object = None
        old_keyword_object = None
        parameters = []
        input_tree = self.input_tree
        input_tree.accessed = True

        for line in lines:
            line = line.strip()
            keyword_object = None

            # Skip empty lines
            if len(line) == 0:
                continue
            # Section ends
            if line.upper().startswith('&END'):
                if parameters:
                    if old_keyword_object is not None:
                        old_keyword_object.parameters = "\n".join(parameters)
                    else:
                        section_object.default_keyword = "\n".join(parameters)
                    parameters = []
                old_keyword_object = None
                section_stack.pop()
            # Section starts
            elif line[0] == '&':
                section_name = line[1:]
                section_stack.append(section_name)
                section_object = input_tree.get_section(section_name)
                section_object.accessed = True
            # Keywords, parameters
            else:
                # Try to find a keyword object
                splitted = line.split()
                current_keyword_name = []
                i_match = None
                for i_part, part in enumerate(splitted):
                    current_keyword_name.append(part)
                    current_keyword_object = section_object.get_keyword(" ".join(current_keyword_name))
                    if current_keyword_object is not None:
                        keyword_object = current_keyword_object
                        i_match = i_part

                # If multiple keywords with this name exist, choose the correct
                # one based on switch
                if isinstance(keyword_object, list):
                    switch = splitted[i_match]
                    correct_keyword_object = None
                    for keyword in keyword_object:
                        if switch in keyword.available_options:
                            correct_keyword_object = keyword
                            break
                    if correct_keyword_object is None:
                        raise LookupError("Could not find the correct keyword for '{}' in the input structure.".format(line))
                    keyword_object = correct_keyword_object

                # If keyword object found, place the options and save any
                # parameters that were found before
                if keyword_object is not None:
                    # print(keyword_object.name)
                    if parameters:
                        if old_keyword_object is not None:
                            old_keyword_object.parameters = "\n".join(parameters)
                            parameters = []
                    options = splitted[i_match+1:]
                    if options:
                        options = " ".join(options)
                    else:
                        options = None
                    keyword_object.options = options
                    keyword_object.accessed = True
                    old_keyword_object = keyword_object

                # If no keyword was found, and a section is open, the line is a
                # parameter line
                if keyword_object is None and len(section_stack) != 0:
                    parameters.append(line)

    def analyze_input(self):

        # Get the trajectory print settings
        root = self.input_tree
        cpmd = root.get_section("CPMD")
        trajectory = cpmd.get_keyword("TRAJECTORY")
        if trajectory:
            options = trajectory.options
            if options:
                if "RANGE" in options:
                    self.cache_service["trajectory_range"] = True
                if "SAMPLE" in options:
                    self.cache_service["trajectory_sample"] = True
                    parameters = trajectory.parameters
                    try:
                        lines = parameters.split("\n")
                        print_freq = int(lines[-1])
                    except (IndexError, ValueError):
                        self.cache_service["print_freq"] = None
                    else:
                        self.cache_service["print_freq"] = print_freq

        # Get the periodicity settings
        system = root.get_section("SYSTEM")
        symmetry = system.get_keyword("SYMMETRY")
        symmetry_parameters = symmetry.parameters.strip()
        cluster = system.get_keyword("CLUSTER")
        surface = system.get_keyword("SURFACE")
        polymer = system.get_keyword("POLYMER")

        # Bulk
        if symmetry_parameters != "0" and symmetry_parameters != "ISOLATED" and cluster.accessed is False:
            periodicity = [True, True, True]

        # Surface
        elif surface.accessed:
            options = surface.options
            if options is None:
                options = "XY"
            else:
                options = options.strip()
            if options == "XY":
                periodicity = [True, True, False]
            elif options == "XZ":
                periodicity = [True, False, True]
            elif options == "YZ":
                periodicity = [False, True, True]

        # Polymer
        elif polymer.accessed:
            periodicity = [True, False, False]

        # Isolated
        elif cluster.accessed or symmetry_parameters == "ISOLATED" or symmetry_parameters == "0":
            periodicity = [False, False, False]

        self.cache_service["configuration_periodic_dimensions"] = np.array(periodicity)

        # Get the XC functional
        class XCFunctional(object):
            def __init__(self, name, weight=1, parameters=None):
                self.name = name
                self.weight = weight
                self.parameters = parameters

        xc_list = []
        dft = root.get_section("DFT")
        if dft is not None:
            functional = dft.get_keyword("FUNCTIONAL")
            if functional is not None:
                xc = functional.options
                if xc is not None:
                    xc = xc.strip()

                    if xc == "LDA":
                        xc_list.append(XCFunctional("LDA_XC_TETER93"))

                    elif xc == "BLYP":
                        xc_list.append(XCFunctional("GGA_X_B88"))
                        xc_list.append(XCFunctional("GGA_C_LYP"))

                    elif xc == "B3LYP":
                        xc_list.append(XCFunctional("HYB_GGA_XC_B3LYP"))

                    elif xc == "PBE":
                        xc_list.append(XCFunctional("GGA_X_PBE"))
                        xc_list.append(XCFunctional("GGA_C_PBE"))

                    elif xc == "OLYP":
                        xc_list.append(XCFunctional("GGA_X_OPTX"))
                        xc_list.append(XCFunctional("GGA_C_LYP"))

                    elif xc == "HCTH":
                        xc_list.append(XCFunctional("GGA_XC_HCTH_120"))

                    elif xc == "PBE0":
                        xc_list.append(XCFunctional("HYB_GGA_XC_PBEH"))

                    elif xc == "BP":
                        xc_list.append(XCFunctional("GGA_X_B88"))
                        xc_list.append(XCFunctional("GGA_C_P86"))

                    elif xc == "XLYP":
                        xc_list.append(XCFunctional("GGA_XC_XLYP"))

                    elif xc == "PBES":
                        xc_list.append(XCFunctional("GGA_C_PBE_SOL"))
                        xc_list.append(XCFunctional("GGA_X_PBE_SOL"))

                    elif xc == "REVPBE":
                        xc_list.append(XCFunctional("GGA_C_PBE"))
                        xc_list.append(XCFunctional("GGA_X_PBE_R"))

                    elif xc == "TPSS":
                        xc_list.append(XCFunctional("MGGA_C_TPSS"))
                        xc_list.append(XCFunctional("MGGA_X_TPSS"))

                    # This version of OPTX is not yet found on the official list
                    # elif xc == "OPTX":

                    elif xc == "B1LYP":
                        xc_list.append(XCFunctional("HYB_GGA_XC_B1LYP"))

                    elif xc == "X3LYP":
                        xc_list.append(XCFunctional("HYB_GGA_XC_X3LYP"))

                    elif xc == "HSE06":
                        xc_list.append(XCFunctional("HYB_GGA_XC_HSE06"))

        # Sort the functionals alphabetically by name
        xc_list.sort(key=lambda x: x.name)
        xc_summary = ""

        # For every defined functional, stream the information to the
        # backend and construct the summary string
        for i, functional in enumerate(xc_list):

            gId = self.backend.openSection("section_XC_functionals")
            self.backend.addValue("XC_functional_name", functional.name)
            self.backend.addValue("XC_functional_weight", functional.weight)
            if functional.parameters is not None:
                pass
            self.backend.closeSection("section_XC_functionals", gId)

            if i != 0:
                xc_summary += "+"
            xc_summary += "{}*{}".format(functional.weight, functional.name)
            if functional.parameters is not None:
                xc_summary += ":{}".format()

        # Stream summary
        if xc_summary is not "":
            self.backend.addValue("XC_functional", xc_summary)

    def fill_metadata(self):
        """Goes through the input data and pushes everything to the
        backend.
        """
        def fill_metadata_recursively(section):
            """Recursively goes through the input sections and pushes everything to the
            backend.
            """
            if not section.accessed:
                return

            if section.name != "":
                section_name = metainfo_section_prefix + "{}".format(section.name)
            else:
                section_name = metainfo_section_prefix[:-1]
            gid = self.backend.openSection(section_name)

            # Keywords
            for keyword_list in section.keywords.values():
                for keyword in keyword_list:
                    if keyword.accessed:
                        # Open keyword section
                        keyword_name = metainfo_section_prefix + "{}.{}".format(section.name, keyword.unique_name.replace(" ", "_"))
                        key_id = self.backend.openSection(keyword_name)

                        # Add options
                        if keyword.options:
                            option_name = metainfo_data_prefix + "{}.{}_options".format(section.name, keyword.unique_name.replace(" ", "_"))
                            self.backend.addValue(option_name, keyword.options)

                        # Add parameters
                        if keyword.parameters:
                            parameter_name = metainfo_data_prefix + "{}.{}_parameters".format(section.name, keyword.unique_name.replace(" ", "_"))
                            self.backend.addValue(parameter_name, keyword.parameters)

                        # Close keyword section
                        self.backend.closeSection(keyword_name, key_id)

            # # Default keyword
            default_keyword = section.default_keyword
            if default_keyword is not None:
                name = metainfo_data_prefix + "{}_default_keyword".format(section.name)
                self.backend.addValue(name, default_keyword)

            # Subsections
            for subsection in section.subsections.values():
                fill_metadata_recursively(subsection)

            self.backend.closeSection(section_name, gid)

        fill_metadata_recursively(self.input_tree)

    def setup_input_tree(self, version_number):
        """Loads the version specific pickle file which contains pregenerated
        input structure.
        """
        pickle_path = os.path.dirname(__file__) + "/input_data/cpmd_input_tree.pickle"
        input_tree_pickle_file = open(pickle_path, 'rb')
        self.input_tree = pickle.load(input_tree_pickle_file)
