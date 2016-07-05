from __future__ import absolute_import
from nomadcore.simple_parser import SimpleMatcher as SM
from nomadcore.baseclasses import MainHierarchicalParser
from nomadcore.caching_backend import CachingLevel
from .commonmatcher import CPMDCommonMatcher
import re
import logging
import datetime
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
        self.setup_common_matcher(CPMDCommonMatcher(parser_context))

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
                SM( " PROGRAM CPMD STARTED AT: (?P<x_cpmd_start_datetime>{})".format(self.regexs.regex_eol)),
                SM( "\s+VERSION (?P<program_version>\d+\.\d+)"),
                SM( " THE INPUT FILE IS:\s+(?P<x_cpmd_input_file>{})".format(self.regexs.regex_eol)),
                SM( " THIS JOB RUNS ON:\s+(?P<x_cpmd_run_host_name>{})".format(self.regexs.regex_eol)),
                SM( " THE JOB WAS SUBMITTED BY:\s+(?P<x_cpmd_run_user_name>{})".format(self.regexs.regex_eol)),
            ]
        )

    #=======================================================================
    # onClose triggers
    def onClose_section_run(self, backend, gIndex, section):
        start_datetime = section.get_latest_value("x_cpmd_start_datetime")
        start_date_stamp, start_wall_time = self.timestamp_from_string(start_datetime)
        backend.addValue("time_run_date_start", start_date_stamp)
        backend.addValue("time_run_wall_start", start_wall_time)

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

    #=======================================================================
    # adHoc
    def debug(self):
        def wrapper(parser):
            print("DEBUG")
        return wrapper
