from builtins import next
from builtins import range
import os
import re
import logging
import importlib
from nomadcore.baseclasses import ParserInterface
logger = logging.getLogger("nomad")


#===============================================================================
class CPMDRunType(object):
    def __init__(self, module_name, class_name):
        self.module_name = module_name
        self.class_name = class_name


#===============================================================================
class CPMDParser(ParserInterface):
    """This class handles the initial setup before any parsing can happen. It
    determines which version of CPMD was used to generate the output and then
    sets up a correct main parser.

    After the implementation has been setup, you can parse the files with
    parse().
    """
    def __init__(self, main_file, metainfo_to_keep=None, backend=None, default_units=None, metainfo_units=None, debug=True, log_level=logging.ERROR, store=True):
        super(CPMDParser, self).__init__(main_file, metainfo_to_keep, backend, default_units, metainfo_units, debug, log_level, store)

    def setup_version(self):
        """Setups the version by looking at the output file and the version
        specified in it.
        """
        # Search for the CPMD version specification and the run type for the
        # calculation. The correct and optimized parser is initialized based on
        # this information.
        regex_version = re.compile("\s+VERSION ([\d\.]+)")
        regex_single_point = re.compile(r" SINGLE POINT DENSITY OPTIMIZATION")
        regex_geo_opt = re.compile(r" OPTIMIZATION OF IONIC POSITIONS")
        regex_md = re.compile(r" CAR-PARRINELLO MOLECULAR DYNAMICS")
        run_type = None
        n_lines = 1000
        version_id = None
        with open(self.parser_context.main_file, 'r') as outputfile:
            for i_line in range(n_lines):
                try:
                    line = next(outputfile)
                except StopIteration:
                    break

                # Look for version
                result_version = regex_version.match(line)
                if result_version:
                    version_id = result_version.group(1).replace('.', '')

                # Look for geometry optimization
                result_geo_opt = regex_geo_opt.match(line)
                if result_geo_opt:
                    run_type = CPMDRunType(module_name="geooptparser", class_name="CPMDGeoOptParser")

                # Look for single point calculation
                result_single_point = regex_single_point.match(line)
                if result_single_point:
                    run_type = CPMDRunType(module_name="singlepointparser", class_name="CPMDSinglePointParser")

                # Look for MD calculation
                result_md = regex_md.match(line)
                if result_md:
                    run_type = CPMDRunType(module_name="mdparser", class_name="CPMDMDParser")

        if version_id is None:
            msg = "Could not find a version specification from the given main file."
            logger.exception(msg)
            raise RuntimeError(msg)

        if run_type is None:
            msg = "Could not find a run type specification from the given main file."
            logger.exception(msg)
            raise RuntimeError(msg)

        # Setup the root folder to the fileservice that is used to access files
        dirpath, filename = os.path.split(self.parser_context.main_file)
        dirpath = os.path.abspath(dirpath)
        self.parser_context.file_service.setup_root_folder(dirpath)
        self.parser_context.file_service.set_file_id(filename, "output")

        # Setup the correct main parser based on the version id. If no match
        # for the version is found, use the main parser for CPMD 4.1
        self.setup_main_parser(version_id, run_type)

    def get_metainfo_filename(self):
        return "cpmd.nomadmetainfo.json"

    def get_parser_info(self):
        return {'name': 'cpmd-parser', 'version': '1.0'}

    def setup_main_parser(self, version_id, run_type):
        # Currently the version id is a pure integer, so it can directly be mapped
        # into a package name.
        base = "cpmdparser.versions.cpmd{}.{}".format(version_id, run_type.module_name)
        parser_module = None
        parser_class = None
        try:
            parser_module = importlib.import_module(base)
        except ImportError:
            logger.warning("Could not find a parser for version '{}'. Trying to default to the base implementation for CPMD 4.1".format(version_id))
            base = "cpmdparser.versions.cp2k41.{}".format(run_type.module_name)
            try:
                parser_module = importlib.import_module(base)
            except ImportError:
                logger.exception("Tried to default to the CPMD 4.1 implementation but could not find the correct module.")
                raise
        try:
            parser_class = getattr(parser_module, "{}".format(run_type.class_name))
        except AttributeError:
            logger.exception("A parser class '{}' could not be found in the module '[]'.".format(run_type.class_name, parser_module))
            raise
        self.main_parser = parser_class(self.parser_context.main_file, self.parser_context)
