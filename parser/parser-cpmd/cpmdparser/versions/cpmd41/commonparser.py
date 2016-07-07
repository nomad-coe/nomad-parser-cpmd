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

    def onClose_section_method(self, backend, gIndex, section):
        backend.addValue("electronic_structure_method", "DFT")
        basis_id = backend.openSection("section_method_basis_set")
        backend.addValue("method_basis_set_kind", "wavefunction")
        backend.addValue("mapping_section_method_basis_set_cell_associated", 0)
        backend.closeSection("section_method_basis_set", basis_id)
