import re
import logging
import datetime
from nomadcore.baseclasses import CommonParser
from nomadcore.simple_parser import SimpleMatcher as SM
from .inputparser import CPMDInputParser
logger = logging.getLogger("nomad")


#===============================================================================
class CPMDCommonParser(CommonParser):
    """
    This class is used to store and instantiate common parts of the
    hierarchical SimpleMatcher structure used in the parsing of a CPMD
    calculation.
    """
    def __init__(self, parser_context):
        super(CPMDCommonParser, self).__init__(parser_context)

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
                SM( " PROGRAM CPMD STARTED AT: (?P<x_cpmd_start_datetime>{})".format(self.regexs.regex_eol)),
                SM( "\s+VERSION (?P<program_version>\d+\.\d+)"),
                SM( r"\s+\*\*\*  (?P<x_cpmd_compilation_date>[\s\w\-:\d]+)  \*\*\*$"),
                SM( " THE INPUT FILE IS:\s+(?P<x_cpmd_input_filename>{})".format(self.regexs.regex_eol)),
                SM( " THIS JOB RUNS ON:\s+(?P<x_cpmd_run_host_name>{})".format(self.regexs.regex_eol)),
                SM( " THE PROCESS ID IS:\s+(?P<x_cpmd_process_id>{})".format(self.regexs.regex_i)),
                SM( " THE JOB WAS SUBMITTED BY:\s+(?P<x_cpmd_run_user_name>{})".format(self.regexs.regex_eol)),
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
                        # SM( " PROGRAM CPMD STARTED AT: (?P<x_cpmd_start_datetime>{})".format(self.regexs.regex_eol)),
                    ]
                )
            ]
        )

    #===========================================================================
    # onClose triggers
    def onClose_section_run(self, backend, gIndex, section):
        backend.addValue("program_name", "CPMD")
        backend.addValue("program_basis_set_type", "plane waves")

    def onClose_section_method(self, backend, gIndex, section):
        backend.addValue("electronic_structure_method", "DFT")
        basis_id = backend.openSection("section_method_basis_set")
        backend.addValue("method_basis_set_kind", "wavefunction")
        backend.addValue("mapping_section_method_basis_set_cell_associated", 0)
        backend.closeSection("section_method_basis_set", basis_id)

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

        # Compilation date
        date = section.get_latest_value("x_cpmd_compilation_date")

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
        timestring = timestring.strip()
        date, clock_time = timestring.split()
        year, month, day = [int(x) for x in date.split("-")]
        hour, minute, second, msec = [float(x) for x in re.split("[:.]", clock_time)]

        date_obj = datetime.datetime(year, month, day, tzinfo=UTCtzinfo())
        date_timestamp = (date_obj - datetime.datetime(1970, 1, 1, tzinfo=UTCtzinfo())).total_seconds()

        wall_time = hour*3600+minute*60+second+0.001*msec
        return date_timestamp, wall_time
