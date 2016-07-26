from __future__ import absolute_import
import re
import logging
import numpy as np
from .commonparser import CPMDCommonParser
from nomadcore.simple_parser import SimpleMatcher as SM
from nomadcore.baseclasses import MainHierarchicalParser
import nomadcore.csvparsing
import nomadcore.configurationreading
LOGGER = logging.getLogger("nomad")


#===============================================================================
class CPMDMDParser(MainHierarchicalParser):
    """The main parser class that is called for all run types. Parses the CPMD
    output file.
    """
    def __init__(self, file_path, parser_context):
        """
        """
        super(CPMDMDParser, self).__init__(file_path, parser_context)
        self.setup_common_matcher(CPMDCommonParser(parser_context))
        self.sampling_method_gid = None
        self.frame_refs = []
        self.energies = []

        # Detect what files are available in the same folder where the main
        # file is located.
        self.dcd_filepath = self.file_service.get_absolute_path_to_file("TRAJEC.dcd")
        self.xyz_filepath = self.file_service.get_absolute_path_to_file("TRAJEC.xyz")
        self.trajectory_filepath = self.file_service.get_absolute_path_to_file("TRAJECTORY")
        self.ftrajectory_filepath = self.file_service.get_absolute_path_to_file("FTRAJECTORY")

        #=======================================================================
        # Cache levels
        # self.caching_levels.update({
            # 'section_run': CachingLevel.ForwardAndCache,
        # })

        #=======================================================================
        # Main structure
        self.root_matcher = SM("",
            forwardMatch=True,
            sections=['section_run', "section_frame_sequence", "section_sampling_method",  "section_method"],
            subMatchers=[
                self.cm.header(),
                self.cm.method(),
                self.cm.atoms(),
                self.cm.cell(),
                self.cm.initialization(),
                SM( " DEGREES OF FREEDOM FOR SYSTEM:",
                    sections=["x_cpmd_section_md_initialization"],
                    forwardMatch=True,
                    subMatchers=[
                        SM( " DEGREES OF FREEDOM FOR SYSTEM:"),
                        SM( " RVSCAL| RESCALING IONIC TEMP FROM\s+{0} TO\s+{0}".format(self.regexs.float)),
                        SM( re.escape(" ==                     FORCES INITIALIZATION                  ==")),
                        SM( " EWALD\| SUM IN REAL SPACE OVER\s+{0}\*\s+{0}\*\s+{0} CELLS".format(self.regexs.int)),
                        SM( re.escape(" ==                END OF FORCES INITIALIZATION                ==")),
                        SM( " TIME FOR INITIALIZATION:\s+{} SECONDS".format(self.regexs.float)),
                    ]
                ),
                SM( "       NFI    EKINC   TEMPP           EKS      ECLASSIC          EHAM         DIS    TCPU",
                    adHoc=self.ad_hoc_parse_md(),
                ),
                self.cm.footer(),
            ]
        )

    #=======================================================================
    # onClose triggers
    # def onClose_section_single_configuration_calculation(self, backend, gIndex, section):
        # # For single point calculations there is only one method and system.
        # backend.addValue("single_configuration_calculation_to_system_ref", 0)
        # backend.addValue("single_configuration_to_calculation_method_ref", 0)
        # self.frame_refs.append(gIndex)

    # def onClose_section_frame_sequence(self, backend, gIndex, section):
        # backend.addValue("number_of_frames_in_sequence", self.n_frames)
        # if self.sampling_method_gid is not None:
            # backend.addValue("frame_sequence_to_sampling_ref", self.sampling_method_gid)
        # if self.frame_refs:
            # backend.addArrayValues("frame_sequence_local_frames_ref", np.array(self.frame_refs))
        # if self.energies:
            # backend.addArrayValues("frame_sequence_potential_energy", np.array(self.energies))

    def onClose_section_sampling_method(self, backend, gIndex, section):
        self.sampling_method_gid = gIndex
        backend.addValue("sampling_method", "molecular_dynamics")
        self.cache_service.addValue("ensemble_type")

    # def onClose_section_system(self, backend, gIndex, section):
        # self.cache_service.addArrayValues("atom_labels")
        # self.cache_service.addArrayValues("simulation_cell", unit="bohr")
        # self.cache_service.addValue("number_of_atoms")

    #=======================================================================
    # adHoc
    def ad_hoc_parse_md(self):
        """Parses all the md step information.
        """
        def wrapper(parser):

            # Decide from which file trajectory is read
            traj_file = None
            traj_format = None
            traj_step = 1
            traj_iterator = None
            traj_unit = None
            if self.dcd_filepath:
                traj_file = self.dcd_filepath
                traj_format = "dcd"
                traj_unit = "angstrom"
            elif self.xyz_filepath:
                traj_file = self.xyz_filepath
                traj_format = "xyz"
                traj_unit = "angstrom"
            elif self.trajectory_filepath:
                traj_file = self.trajectory_filepath
                traj_format = "custom"
                traj_unit = "bohr"

            # Initialize the trajectory iterator
            if traj_format == "custom":
                n_atoms = self.cache_service["number_of_atoms"]
                traj_iterator = nomadcore.csvparsing.iread(traj_file, columns=[1, 2, 3], n_conf=n_atoms)
            else:
                try:
                    traj_iterator = nomadcore.configurationreading.iread(traj_file)
                except ValueError:
                    pass

            # Start reading the frames
            i_frame = 0
            n_frames = self.cache_service["n_steps"]
            parser.backend.addValue("number_of_frames_in_sequence", n_frames)

            for i_frame in range(n_frames):
                scc_id = parser.backend.openSection("section_single_configuration_calculation")
                sys_id = parser.backend.openSection("section_system")

                # System
                self.cache_service.addArrayValues("atom_labels")
                self.cache_service.addArrayValues("simulation_cell", unit="bohr")
                self.cache_service.addValue("number_of_atoms")

                # Coordinates
                if i_frame % traj_step == 0:
                    try:
                        pos = next(traj_iterator)
                    except StopIteration:
                        LOGGER.error("Could not get the next geometries from an external file. It seems that the number of MD steps in the CPMD outputfile doesn't match the number of steps found in the external trajectory file.")
                    else:
                        parser.backend.addArrayValues("atom_positions", pos, unit=traj_unit)

                parser.backend.closeSection("section_single_configuration_calculation", scc_id)
                parser.backend.closeSection("section_system", sys_id)

        return wrapper
