#
# Copyright The NOMAD Authors.
#
# This file is part of NOMAD.
# See https://nomad-lab.eu for further info.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import numpy as np            # pylint: disable=unused-import
import typing                 # pylint: disable=unused-import
from nomad.metainfo import (  # pylint: disable=unused-import
    MSection, MCategory, Category, Package, Quantity, Section, SubSection, SectionProxy,
    Reference
)
from nomad.metainfo.legacy import LegacyDefinition

from nomad.datamodel.metainfo import public

m_package = Package(
    name='cpmd_general_nomadmetainfo_json',
    description='None',
    a_legacy=LegacyDefinition(name='cpmd.general.nomadmetainfo.json'))


class x_cpmd_section_start_information(MSection):
    '''
    Contains information about the starting conditions for this run
    '''

    m_def = Section(validate=False, a_legacy=LegacyDefinition(name='x_cpmd_section_start_information'))

    x_cpmd_start_datetime = Quantity(
        type=str,
        shape=[],
        description='''
        CPMD run start time and date
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_start_datetime'))

    x_cpmd_input_filename = Quantity(
        type=str,
        shape=[],
        description='''
        CPMD input file name.
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_input_filename'))

    x_cpmd_compilation_date = Quantity(
        type=str,
        shape=[],
        description='''
        CPMD compilation date.
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_compilation_date'))

    x_cpmd_process_id = Quantity(
        type=np.dtype(np.int32),
        shape=[],
        description='''
        The process id for this calculation.
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_process_id'))

    x_cpmd_run_user_name = Quantity(
        type=str,
        shape=[],
        description='''
        The user who launched this calculation.
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_run_user_name'))

    x_cpmd_run_host_name = Quantity(
        type=str,
        shape=[],
        description='''
        The host on which this calculation was made on.
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_run_host_name'))


class x_cpmd_section_run_type_information(MSection):
    '''
    Contains information about the run type.
    '''

    m_def = Section(validate=False, a_legacy=LegacyDefinition(name='x_cpmd_section_run_type_information'))

    x_cpmd_time_step_ions = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        The time step for ions.
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_time_step_ions'))

    x_cpmd_time_step_electrons = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        The time step for electrons.
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_time_step_electrons'))

    x_cpmd_geo_opt_method = Quantity(
        type=str,
        shape=[],
        description='''
        The geometry optimization method.
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_geo_opt_method'))

    x_cpmd_max_steps = Quantity(
        type=np.dtype(np.int32),
        shape=[],
        description='''
        The maximum number of steps requested. In MD, this is the number of MD steps, in
        single point calculations this is the number of scf cycles, in geometry
        optimization this is the number of optimization steps.
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_max_steps'))

    x_cpmd_ion_temperature_control = Quantity(
        type=str,
        shape=[],
        description='''
        The temperature control method for ion dynamics.
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_ion_temperature_control'))


class x_cpmd_section_xc_information(MSection):
    '''
    Contains information about the exchange-correlation functional.
    '''

    m_def = Section(validate=False, a_legacy=LegacyDefinition(name='x_cpmd_section_xc_information'))


class x_cpmd_section_system_information(MSection):
    '''
    Contains information about the system.
    '''

    m_def = Section(validate=False, a_legacy=LegacyDefinition(name='x_cpmd_section_system_information'))


class x_cpmd_section_pseudopotential_information(MSection):
    '''
    Contains information about the pseudopotentials.
    '''

    m_def = Section(validate=False, a_legacy=LegacyDefinition(name='x_cpmd_section_pseudopotential_information'))


class x_cpmd_section_atom_kinds(MSection):
    '''
    Contains information about the atomic kinds present in the calculation.
    '''

    m_def = Section(validate=False, a_legacy=LegacyDefinition(name='x_cpmd_section_atom_kinds'))

    x_cpmd_section_atom_kind = SubSection(
        sub_section=SectionProxy('x_cpmd_section_atom_kind'),
        repeats=True,
        a_legacy=LegacyDefinition(name='x_cpmd_section_atom_kind'))


class x_cpmd_section_atom_kind(MSection):
    '''
    Contains information about one atomic kind.
    '''

    m_def = Section(validate=False, a_legacy=LegacyDefinition(name='x_cpmd_section_atom_kind'))

    x_cpmd_atom_kind_label = Quantity(
        type=str,
        shape=[],
        description='''
        The label of the atomic kind.
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_atom_kind_label'))

    x_cpmd_atom_kind_mass = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        The mass of the atomic kind.
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_atom_kind_mass'))

    x_cpmd_atom_kind_raggio = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        The width of the ionic charge distribution (RAGGIO) of the atomic kind.
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_atom_kind_raggio'))

    x_cpmd_atom_kind_nlcc = Quantity(
        type=str,
        shape=[],
        description='''
        The nonlinear core correction (NLCC) of the atomic kind.
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_atom_kind_nlcc'))

    x_cpmd_atom_kind_pseudopotential_l = Quantity(
        type=str,
        shape=[],
        description='''
        The angular part of the pseudopotential for the atomic kind.
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_atom_kind_pseudopotential_l'))

    x_cpmd_atom_kind_pseudopotential_type = Quantity(
        type=str,
        shape=[],
        description='''
        The type of the pseudopotential for the atomic kind.
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_atom_kind_pseudopotential_type'))


class x_cpmd_section_supercell(MSection):
    '''
    Contains information about the supercell.
    '''

    m_def = Section(validate=False, a_legacy=LegacyDefinition(name='x_cpmd_section_supercell'))

    x_cpmd_cell_symmetry = Quantity(
        type=str,
        shape=[],
        description='''
        The symmetry of the cell.
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_cell_symmetry'))

    x_cpmd_cell_lattice_constant = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        The cell lattice constant.
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_cell_lattice_constant'))

    x_cpmd_cell_volume = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        The cell volume.
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_cell_volume'))

    x_cpmd_cell_dimension = Quantity(
        type=str,
        shape=[],
        description='''
        The cell dimension.
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_cell_dimension'))

    x_cpmd_lattice_vector_A1 = Quantity(
        type=str,
        shape=[],
        description='''
        Lattice vector A1
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_lattice_vector_A1'))

    x_cpmd_lattice_vector_A2 = Quantity(
        type=str,
        shape=[],
        description='''
        Lattice vector A2
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_lattice_vector_A2'))

    x_cpmd_lattice_vector_A3 = Quantity(
        type=str,
        shape=[],
        description='''
        Lattice vector A3
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_lattice_vector_A3'))

    x_cpmd_reciprocal_lattice_vector_B1 = Quantity(
        type=str,
        shape=[],
        description='''
        Reciprocal lattice vector B1
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_reciprocal_lattice_vector_B1'))

    x_cpmd_reciprocal_lattice_vector_B2 = Quantity(
        type=str,
        shape=[],
        description='''
        Reciprocal lattice vector B2
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_reciprocal_lattice_vector_B2'))

    x_cpmd_reciprocal_lattice_vector_B3 = Quantity(
        type=str,
        shape=[],
        description='''
        Reciprocal lattice vector B3
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_reciprocal_lattice_vector_B3'))

    x_cpmd_real_space_mesh = Quantity(
        type=str,
        shape=[],
        description='''
        Number of points in the real space mesh.
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_real_space_mesh'))

    x_cpmd_wave_function_cutoff = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        Place wave cutoff energy for wave function.
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_wave_function_cutoff'))

    x_cpmd_density_cutoff = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        Place wave cutoff energy for density.
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_density_cutoff'))

    x_cpmd_number_of_planewaves_density = Quantity(
        type=np.dtype(np.int32),
        shape=[],
        description='''
        Number of plane waves for density cutoff.
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_number_of_planewaves_density'))

    x_cpmd_number_of_planewaves_wave_function = Quantity(
        type=np.dtype(np.int32),
        shape=[],
        description='''
        Number of plane waves for wave_function cutoff.
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_number_of_planewaves_wave_function'))


class x_cpmd_section_wave_function_initialization(MSection):
    '''
    Contains information about the wave function initialization
    '''

    m_def = Section(validate=False, a_legacy=LegacyDefinition(name='x_cpmd_section_wave_function_initialization'))


class x_cpmd_section_scf(MSection):
    '''
    Contains information about self-consistent field calculation
    '''

    m_def = Section(validate=False, a_legacy=LegacyDefinition(name='x_cpmd_section_scf'))

    x_cpmd_section_scf_iteration = SubSection(
        sub_section=SectionProxy('x_cpmd_section_scf_iteration'),
        repeats=True,
        a_legacy=LegacyDefinition(name='x_cpmd_section_scf_iteration'))


class x_cpmd_section_scf_iteration(MSection):
    '''
    Contains information about the self-consistent field iteration within a wavefunction
    optimization.
    '''

    m_def = Section(validate=False, a_legacy=LegacyDefinition(name='x_cpmd_section_scf_iteration'))

    x_cpmd_scf_nfi = Quantity(
        type=np.dtype(np.int32),
        shape=[],
        description='''
        The scf step number (NFI).
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_scf_nfi'))

    x_cpmd_scf_gemax = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        Largest off-diagonal component (GEMAX) during SCF step.
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_scf_gemax'))

    x_cpmd_scf_cnorm = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        Average of the off-diagonal components (CNORM) during SCF step.
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_scf_cnorm'))

    x_cpmd_scf_etot = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        The total energy (ETOT) during SCF step.
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_scf_etot'))

    x_cpmd_scf_detot = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        The difference in total energy to the previous SCF energy (DETOT).
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_scf_detot'))

    x_cpmd_scf_tcpu = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        The CPU time used during SCF step (TCPU).
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_scf_tcpu'))


class x_cpmd_section_final_results(MSection):
    '''
    The final results after a single point calculation.
    '''

    m_def = Section(validate=False, a_legacy=LegacyDefinition(name='x_cpmd_section_final_results'))


class x_cpmd_section_geo_opt_initialization(MSection):
    '''
    Geometry optimization initialization information.
    '''

    m_def = Section(validate=False, a_legacy=LegacyDefinition(name='x_cpmd_section_geo_opt_initialization'))

    x_cpmd_total_number_of_molecular_structures = Quantity(
        type=np.dtype(np.int32),
        shape=[],
        description='''
        Total number of molecular structures.
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_total_number_of_molecular_structures'))

    x_cpmd_initialized_positions = Quantity(
        type=np.dtype(np.float64),
        shape=['number_of_atoms', 3],
        description='''
        The initialized positions for geometry optimization. The ith row corresponds to
        the position for atom number i.
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_initialized_positions'))

    x_cpmd_initialized_forces = Quantity(
        type=np.dtype(np.float64),
        shape=['number_of_atoms', 3],
        description='''
        The initialized forces for geometry optimization. The ith row corresponds to the
        force for atom number i.
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_initialized_forces'))

    x_cpmd_geo_opt_initialization_time = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        Time for initialization.
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_geo_opt_initialization_time'))


class x_cpmd_section_geo_opt_step(MSection):
    '''
    Contains information for a single geometry optimization step.
    '''

    m_def = Section(validate=False, a_legacy=LegacyDefinition(name='x_cpmd_section_geo_opt_step'))

    x_cpmd_geo_opt_step_positions = Quantity(
        type=np.dtype(np.float64),
        shape=['number_of_atoms', 3],
        description='''
        The positions from a geometry optimization step. The ith row corresponds to the
        position for atom number i.
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_geo_opt_step_positions'))

    x_cpmd_geo_opt_step_forces = Quantity(
        type=np.dtype(np.float64),
        shape=['number_of_atoms', 3],
        description='''
        The forces from a geometry optimization step. The ith row corresponds to the force
        for atom number i.
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_geo_opt_step_forces'))

    x_cpmd_geo_opt_step_total_number_of_scf_steps = Quantity(
        type=np.dtype(np.int32),
        shape=[],
        description='''
        Total number of SCF steps at the end of this geometry optimization step.
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_geo_opt_step_total_number_of_scf_steps'))

    x_cpmd_geo_opt_step_number = Quantity(
        type=np.dtype(np.int32),
        shape=[],
        description='''
        Geometry optimization step number.
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_geo_opt_step_number'))

    x_cpmd_geo_opt_step_gnmax = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        The largest absolute component of the force on any atom (GNMAX).
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_geo_opt_step_gnmax'))

    x_cpmd_geo_opt_step_gnorm = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        Average force on the atoms (GNORM).
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_geo_opt_step_gnorm'))

    x_cpmd_geo_opt_step_cnstr = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        The largest absolute component of a constraint force on the atoms (CNSTR).
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_geo_opt_step_cnstr'))

    x_cpmd_geo_opt_step_etot = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        The total energy at the end of a geometry optimization step (ETOT).
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_geo_opt_step_etot'))

    x_cpmd_geo_opt_step_detot = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        The difference in total energy to the previous geometry optimization step (DETOT).
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_geo_opt_step_detot'))

    x_cpmd_geo_opt_step_tcpu = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        The CPU time used during geometry optimization step (TCPU).
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_geo_opt_step_tcpu'))

    x_cpmd_section_geo_opt_scf_iteration = SubSection(
        sub_section=SectionProxy('x_cpmd_section_geo_opt_scf_iteration'),
        repeats=True,
        a_legacy=LegacyDefinition(name='x_cpmd_section_geo_opt_scf_iteration'))


class x_cpmd_section_geo_opt_scf_iteration(MSection):
    '''
    Contains information about the self-consistent field iteration within a geometry
    optimization step.
    '''

    m_def = Section(validate=False, a_legacy=LegacyDefinition(name='x_cpmd_section_geo_opt_scf_iteration'))

    x_cpmd_geo_opt_scf_nfi = Quantity(
        type=np.dtype(np.int32),
        shape=[],
        description='''
        The scf step number (NFI) within geometry optimization step.
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_geo_opt_scf_nfi'))

    x_cpmd_geo_opt_scf_gemax = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        Largest off-diagonal component (GEMAX) during SCF step within geometry
        optimization step.
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_geo_opt_scf_gemax'))

    x_cpmd_geo_opt_scf_cnorm = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        Average of the off-diagonal components (CNORM) during SCF step within geometry
        optimization step.
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_geo_opt_scf_cnorm'))

    x_cpmd_geo_opt_scf_etot = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        The total energy (ETOT) during SCF step within geometry optimization step.
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_geo_opt_scf_etot'))

    x_cpmd_geo_opt_scf_detot = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        The difference in total energy to the previous SCF energy (DETOT) within geometry
        optimization step.
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_geo_opt_scf_detot'))

    x_cpmd_geo_opt_scf_tcpu = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        The CPU time used during SCF step (TCPU) within geometry optimization step.
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_geo_opt_scf_tcpu'))


class x_cpmd_section_md_initialization(MSection):
    '''
    Molecular dynamics initialization information.
    '''

    m_def = Section(validate=False, a_legacy=LegacyDefinition(name='x_cpmd_section_md_initialization'))


class x_cpmd_section_md_averaged_quantities(MSection):
    '''
    Averaged quantities from a MD calculation.
    '''

    m_def = Section(validate=False, a_legacy=LegacyDefinition(name='x_cpmd_section_md_averaged_quantities'))

    x_cpmd_electron_kinetic_energy_mean = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        The mean electron kinetic energy.
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_electron_kinetic_energy_mean'))

    x_cpmd_electron_kinetic_energy_std = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        The standard deviation of electron kinetic energy.
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_electron_kinetic_energy_std'))

    x_cpmd_ionic_temperature_mean = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        The mean ionic temperature.
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_ionic_temperature_mean'))

    x_cpmd_ionic_temperature_std = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        The standard deviation of ionic temperature.
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_ionic_temperature_std'))

    x_cpmd_density_functional_energy_mean = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        The mean density functional energy.
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_density_functional_energy_mean'))

    x_cpmd_density_functional_energy_std = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        The standard deviation of density functional energy.
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_density_functional_energy_std'))

    x_cpmd_classical_energy_mean = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        The mean classical energy.
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_classical_energy_mean'))

    x_cpmd_classical_energy_std = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        The standard deviation of classical energy.
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_classical_energy_std'))

    x_cpmd_conserved_energy_mean = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        The mean conserved energy.
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_conserved_energy_mean'))

    x_cpmd_conserved_energy_std = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        The standard deviation of conserved energy.
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_conserved_energy_std'))

    x_cpmd_nose_energy_electrons_mean = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        The mean Nosé energy for electrons.
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_nose_energy_electrons_mean'))

    x_cpmd_nose_energy_electrons_std = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        The standard deviation of Nosé energy for elctrons.
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_nose_energy_electrons_std'))

    x_cpmd_nose_energy_ions_mean = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        The mean Nosé energy for ions.
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_nose_energy_ions_mean'))

    x_cpmd_nose_energy_ions_std = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        The standard deviation of Nosé energy for ions.
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_nose_energy_ions_std'))

    x_cpmd_constraints_energy_mean = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        The mean constrains energy.
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_constraints_energy_mean'))

    x_cpmd_constraints_energy_std = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        The standard deviation of constraints energy.
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_constraints_energy_std'))

    x_cpmd_restraints_energy_mean = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        The mean restraints energy.
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_restraints_energy_mean'))

    x_cpmd_restraints_energy_std = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        The standard deviation of restraints energy.
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_restraints_energy_std'))

    x_cpmd_ion_displacement_mean = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        The mean ion displacement.
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_ion_displacement_mean'))

    x_cpmd_ion_displacement_std = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        The standard deviation of ion displacement.
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_ion_displacement_std'))

    x_cpmd_cpu_time_mean = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        The mean cpu time.
        ''',
        a_legacy=LegacyDefinition(name='x_cpmd_cpu_time_mean'))


class x_cpmd_section_timing(MSection):
    '''
    Contains information about the timings.
    '''

    m_def = Section(validate=False, a_legacy=LegacyDefinition(name='x_cpmd_section_timing'))


class x_cpmd_section_end_information(MSection):
    '''
    Contains information printed at the end of a calculation.
    '''

    m_def = Section(validate=False, a_legacy=LegacyDefinition(name='x_cpmd_section_end_information'))


class section_run(public.section_run):

    m_def = Section(validate=False, extends_base_section=True, a_legacy=LegacyDefinition(name='section_run'))

    x_cpmd_section_start_information = SubSection(
        sub_section=SectionProxy('x_cpmd_section_start_information'),
        repeats=True,
        a_legacy=LegacyDefinition(name='x_cpmd_section_start_information'))

    x_cpmd_section_run_type_information = SubSection(
        sub_section=SectionProxy('x_cpmd_section_run_type_information'),
        repeats=True,
        a_legacy=LegacyDefinition(name='x_cpmd_section_run_type_information'))

    x_cpmd_section_system_information = SubSection(
        sub_section=SectionProxy('x_cpmd_section_system_information'),
        repeats=True,
        a_legacy=LegacyDefinition(name='x_cpmd_section_system_information'))

    x_cpmd_section_supercell = SubSection(
        sub_section=SectionProxy('x_cpmd_section_supercell'),
        repeats=True,
        a_legacy=LegacyDefinition(name='x_cpmd_section_supercell'))

    x_cpmd_section_wave_function_initialization = SubSection(
        sub_section=SectionProxy('x_cpmd_section_wave_function_initialization'),
        repeats=True,
        a_legacy=LegacyDefinition(name='x_cpmd_section_wave_function_initialization'))

    x_cpmd_section_md_initialization = SubSection(
        sub_section=SectionProxy('x_cpmd_section_md_initialization'),
        repeats=True,
        a_legacy=LegacyDefinition(name='x_cpmd_section_md_initialization'))

    x_cpmd_section_md_averaged_quantities = SubSection(
        sub_section=SectionProxy('x_cpmd_section_md_averaged_quantities'),
        repeats=True,
        a_legacy=LegacyDefinition(name='x_cpmd_section_md_averaged_quantities'))

    x_cpmd_section_timing = SubSection(
        sub_section=SectionProxy('x_cpmd_section_timing'),
        repeats=True,
        a_legacy=LegacyDefinition(name='x_cpmd_section_timing'))

    x_cpmd_section_end_information = SubSection(
        sub_section=SectionProxy('x_cpmd_section_end_information'),
        repeats=True,
        a_legacy=LegacyDefinition(name='x_cpmd_section_end_information'))


class section_method(public.section_method):

    m_def = Section(validate=False, extends_base_section=True, a_legacy=LegacyDefinition(name='section_method'))

    x_cpmd_section_xc_information = SubSection(
        sub_section=SectionProxy('x_cpmd_section_xc_information'),
        repeats=True,
        a_legacy=LegacyDefinition(name='x_cpmd_section_xc_information'))

    x_cpmd_section_pseudopotential_information = SubSection(
        sub_section=SectionProxy('x_cpmd_section_pseudopotential_information'),
        repeats=True,
        a_legacy=LegacyDefinition(name='x_cpmd_section_pseudopotential_information'))

    x_cpmd_section_atom_kinds = SubSection(
        sub_section=SectionProxy('x_cpmd_section_atom_kinds'),
        repeats=True,
        a_legacy=LegacyDefinition(name='x_cpmd_section_atom_kinds'))


class section_single_configuration_calculation(public.section_single_configuration_calculation):

    m_def = Section(validate=False, extends_base_section=True, a_legacy=LegacyDefinition(name='section_single_configuration_calculation'))

    x_cpmd_section_scf = SubSection(
        sub_section=SectionProxy('x_cpmd_section_scf'),
        repeats=True,
        a_legacy=LegacyDefinition(name='x_cpmd_section_scf'))

    x_cpmd_section_final_results = SubSection(
        sub_section=SectionProxy('x_cpmd_section_final_results'),
        repeats=True,
        a_legacy=LegacyDefinition(name='x_cpmd_section_final_results'))


class section_frame_sequence(public.section_frame_sequence):

    m_def = Section(validate=False, extends_base_section=True, a_legacy=LegacyDefinition(name='section_frame_sequence'))

    x_cpmd_section_geo_opt_initialization = SubSection(
        sub_section=SectionProxy('x_cpmd_section_geo_opt_initialization'),
        repeats=True,
        a_legacy=LegacyDefinition(name='x_cpmd_section_geo_opt_initialization'))

    x_cpmd_section_geo_opt_step = SubSection(
        sub_section=SectionProxy('x_cpmd_section_geo_opt_step'),
        repeats=True,
        a_legacy=LegacyDefinition(name='x_cpmd_section_geo_opt_step'))


m_package.__init_metainfo__()
