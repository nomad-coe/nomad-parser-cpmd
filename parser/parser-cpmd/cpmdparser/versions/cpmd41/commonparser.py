from nomadcore.baseclasses import CommonParser


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
    # onClose triggers
    def onClose_section_run(self, backend, gIndex, section):
        backend.addValue("program_name", "CPMD")
        backend.addValue("program_basis_set_type", "plane waves")
