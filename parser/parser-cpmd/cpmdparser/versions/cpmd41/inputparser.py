import os
import pickle
import logging
from nomadcore.baseclasses import BasicParser
from cpmdparser.generic.inputparsing import metainfo_data_prefix, metainfo_section_prefix
logger = logging.getLogger("nomad")


#===============================================================================
class CPMDInputParser(BasicParser):
    """Parses the CPMD input file.
    """
    def __init__(self, file_path, parser_context):
        """
        """
        super(CPMDInputParser, self).__init__(file_path, parser_context)
        self.input_tree = None
        self.cache_service.add("trajectory_range", False)
        self.cache_service.add("trajectory_sample", False)
        self.cache_service.add("print_freq", 1)

    def parse(self):
        self.setup_input_tree(self.parser_context.version_id)
        self.collect_input()
        self.analyze_input()
        self.fill_metadata()

    def collect_input(self):
        """This function will first go through the input file and gather the
        information to the input tree.

        The data is not directly pushed to the backend inside this function
        because it is safer to first validate the whole structure and only then
        push it.
        """
        # The input file should be relatively small so we are better off
        # loading it into memory all at once.
        lines = None
        with open(self.file_path, "r") as fin:
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
                    if parameters:
                        old_keyword_object.parameters = "\n".join(parameters)
                        parameters = []
                    options = splitted[i_match+1:]
                    options = " ".join(options)
                    keyword_object.options = options
                    keyword_object.accessed = True
                    old_keyword_object = keyword_object

                # If no keyword was found, the line is a parameter line
                if keyword_object is None:
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
