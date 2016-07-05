from builtins import next
from builtins import range
import os
import re
import logging
import importlib
from nomadcore.baseclasses import ParserInterface
logger = logging.getLogger("nomad")


#===============================================================================
class CPMDParser(ParserInterface):
    """This class handles the initial setup before any parsing can happen. It
    determines which version of CP2K was used to generate the output and then
    sets up a correct main parser.

    After the implementation has been setup, you can parse the files with
    parse().
    """
    def __init__(self, main_file, metainfo_to_keep=None, backend=None, default_units=None, metainfo_units=None, debug=True, store=True):
        super(CPMDParser, self).__init__(main_file, metainfo_to_keep, backend, default_units, metainfo_units, debug, store)

    def setup_version(self):
        """Setups the version by looking at the output file and the version
        specified in it.
        """
        # Search for the CP2K version specification and the RUN_TYPE for the
        # calculation. The correct and optimized parser is initialized based on
        # this information.
        regex_version = re.compile("\s+VERSION ([\d\.]+)")
        n_lines = 50
        version_id = None
        with open(self.parser_context.main_file, 'r') as outputfile:
            for i_line in range(n_lines):
                line = next(outputfile)
                result_version = regex_version.match(line)
                if result_version:
                    version_id = result_version.group(1).replace('.', '')
        if version_id is None:
            msg = "Could not find a version specification from the given main file."
            logger.exception(msg)
            raise RuntimeError(msg)

        # Setup the root folder to the fileservice that is used to access files
        dirpath, filename = os.path.split(self.parser_context.main_file)
        dirpath = os.path.abspath(dirpath)
        self.parser_context.file_service.setup_root_folder(dirpath)
        self.parser_context.file_service.set_file_id(filename, "output")

        # Setup the correct main parser based on the version id. If no match
        # for the version is found, use the main parser for CP2K 2.6.2
        self.setup_main_parser(version_id)

    def get_metainfo_filename(self):
        return "cpmd.nomadmetainfo.json"

    def get_parser_info(self):
        return {'name': 'cpmd-parser', 'version': '1.0'}

    def setup_main_parser(self, version_id):
        # Currently the version id is a pure integer, so it can directly be mapped
        # into a package name.
        base = "cpmdparser.versions.cpmd{}.mainparser".format(version_id)
        parser_module = None
        parser_class = None
        try:
            parser_module = importlib.import_module(base)
        except ImportError:
            logger.warning("Could not find a parser for version '{}'. Trying to default to the base implementation for CPMD 4.1".format(version_id))
            base = "cpmdparser.versions.cp2k41.mainparser"
            try:
                parser_module = importlib.import_module(base)
            except ImportError:
                logger.exception("Tried to default to the CPMD 4.1 implementation but could not find the correct module.")
                raise
        try:
            parser_class = getattr(parser_module, "CPMDMainParser")
        except AttributeError:
            logger.exception("A parser class 'CPMDMainParser' could not be found in the module '[]'.".format(parser_module))
            raise
        self.main_parser = parser_class(self.parser_context.main_file, self.parser_context)
