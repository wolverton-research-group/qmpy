import os
import logging

from qmpy.analysis.vasp import *
from qmpy.analysis.thermodynamics.space import PhaseSpace
from qmpy.computing.resources import *
from qmpy.analysis.symmetry import routines

logger = logging.getLogger(__name__)


def initialize(entry, **kwargs):
    '''
    DEPRECATED: Run a relaxation with very low settings
    '''
    entry.input.set_magnetism('ferro')
    calc = Calculation.setup(
        entry.input,
        entry=entry,
        configuration='initialize',
        path=os.path.join(entry.path, 'initialize'),
        **kwargs
    )

    calc.set_label('initialize')
    if not calc.converged:
        calc.write()
        return calc

    if calc.converged:
        if calc.magmom > 0.1:
            entry.keywords.append('magnetic')
    return calc


def coarse_relax(entry, **kwargs):
    '''
    DEPRECATED: Run a relaxation with low cutoff energy
    '''
    if entry.calculations.get('coarse_relax', Calculation()).converged:
        return entry.calculations['coarse_relax']

    calc = initialize(entry, **kwargs)
    if not calc.converged:
        calc.write()
        return calc

    calc.set_label('coarse_relax')
    input_structure = entry.structures['input']
    if 'magnetic' not in entry.keywords:
        input_structure.set_magnetism('none')

    calc = Calculation.setup(
        input_structure,
        entry=entry,
        configuration='coarse_relax',
        path=os.path.join(entry.path, 'coarse_relax'),
        **kwargs
    )

    if calc.converged:
        calc.output.set_label('coarse_relax')
    return calc


def fine_relax(entry, **kwargs):
    '''
    DEPRECATED: Run a slightly more expensive relaxation calculation
    '''
    if entry.calculations.get('fine_relax', Calculation()).converged:
        return entry.calculations['fine_relax']

    calc = coarse_relax(entry, **kwargs)
    if not calc.converged:
        calc.write()
        return calc
    input_structure = entry.structures['coarse_relax']
    if 'magnetic' in entry.keywords:
        input_structure.set_magnetism('ferro')

    calc = Calculation.setup(
        input_structure,
        entry=entry,
        configuration='fine_relax',
        path=os.path.join(entry.path, 'fine_relax'),
        **kwargs
    )

    if calc.converged:
        entry.structures['fine_relax'] = calc.output
        entry.calculations['fine_relax'] = calc
    return calc


def standard(entry, **kwargs):
    ''''
    DEPRECATED: Run a final, static calculation at standard cutoff energy
    '''
    if entry.calculations.get('standard', Calculation()).converged:
        return entry.calculations['standard']

    calc = fine_relax(entry, **kwargs)
    if not calc.converged:
        calc.write()
        return calc

    input_structure = entry.structures['fine_relax']
    if 'magnetic' in entry.keywords:
        input_structure.set_magnetism('ferro')

    calc = Calculation.setup(
        input_structure,
        entry=entry,
        configuration='standard',
        path=os.path.join(entry.path, 'standard'),
        **kwargs
    )

    if calc.converged:
        f = calc.get_formation()
        f.save()
        entry.calculations['standard'] = calc
        entry.structures['standard'] = calc.output
        ps = PhaseSpace(calc.input.comp.keys())
        ps.compute_stabilities(save=True)
    return calc


def check_spin(entry, xc_func='PBE'):
    '''
    Special case for Co-containing materials. Run calculation 
    at with Co in low and high spin state

    Arguments:
        entry
            Entry, Entry to be run
        xc_func
            string, Desired XC functional
    Output:
        Calculation, Relaxation with high spin if low spin
        energy calculation is more than 5 meV/atom lower in energy
        None if calculations are not complete
    '''

    # Get name of high-spin calculation
    high_name = 'relaxation'
    if xc_func.lower() != 'pbe':
        high_name += "_{}".format(xc_func.lower())

    # Get name of low-spin calculation
    low_name = 'Co_lowspin'
    if xc_func.lower() != 'pbe':
        low_name += "_{}".format(xc_func.lower())
    
    # Check if the high-spin has converged
    if entry.calculations.get(high_name, Calculation()).converged:

        # If so, get the high-spin energy
        e1 = entry.calculations[high_name].energy

        # Mark that this calculation is high-spin
        entry.calculations[high_name].Co_lowspin = False

        # Check if the low-spin has converged
        if entry.calculations.get(low_name, Calculation()).converged:

            # If so, check whether it is lower by more than 5 meV/atom
            e2 = entry.calculations[low_name].energy

            # Mark that this calculation is low spin
            entry.calculations[low_name].Co_lowspin = True
            if e1-e2 <= 0.005:
                return entry.calculations[high_name]
            else:
                return entry.calculations[low_name]

    # If both calculations are not complete
    return None


def relaxation(entry, xc_func='PBE', **kwargs):
    '''
    Start a calculation to relax atom positions and lattice parameters

    Arguments:
        entry:
            Entry, structure to be relaxed

    Keyword Arguments:
        xc_func:
            String, name of XC function to use (Default='PBE'). Is used to
            determine the name of the configuration settings file to use
        kwargs:
            Settings passed to calculation object

    Output:
        Calculation:
            results of calculation object
    '''

    # Get the name of this configuration
    cnfg_name = 'relaxation'
    if not xc_func.lower() == 'pbe':
        cnfg_name = cnfg_name + '_' + xc_func.lower()

    # Use this to define the calculation path
    path = os.path.join(entry.path, cnfg_name)

    # Check whether to use high or low spin for Co compounds
    if 'Co' in entry.comp:
        spin = check_spin(entry, xc_func=xc_func)
        if spin is not None:
            return spin
    else:
        # If relaxation calculation is converged, return that calculation
        if entry.calculations.get(cnfg_name, Calculation()).converged:
            return entry.calculations[cnfg_name]

    # Check if the calculation is converged / started
    if not entry.calculations.get(cnfg_name, Calculation()).converged:
        input_structure = entry.input.copy()

        calc = Calculation.setup(
            input_structure,
            entry=entry,
            configuration=cnfg_name,
            path=path,
            **kwargs
        )

        entry.calculations[cnfg_name] = calc
        entry.Co_lowspin = False

        # If converged, write results to disk and return calculation
        if not calc.converged:
            calc.write()
            return calc

    # Special case: Co, which requires high and low spin calculations
    if 'Co' in entry.comp:
        # Get name of low spin calculation
        low_name = 'Co_lowspin'
        if xc_func.lower() != 'pbe':
            low_name += "_{}".format(xc_func.lower())

        # Update / start the low spin calculation
        if not entry.calculations.get(low_name, Calculation()).converged:

            # Get the low_spin calculation directory
            lowspin_dir = os.path.join(entry.path, low_name)

            # Get input structure
            input_structure = entry.input.copy()

            calc = Calculation.setup(
                input_structure,
                entry=entry,
                configuration=cnfg_name,
                path=lowspin_dir,
                **kwargs
            )
            # Return atoms to the low-spin configuration
            for atom in calc.input:
                if atom.element.symbol == 'Co':
                    atom.magmom = 0.01

            entry.calculations[low_name] = calc
            entry.Co_lowspin = True
            if not calc.converged:
                calc.write()
                return calc

    # Special case: Save structure to "relaxed" if this is a PBE calculation
    if xc_func.lower() == 'pbe':
        if 'Co' in entry.comp:
            calc = check_spin(entry, xc_func=xc_func)
            assert calc is not None
            entry.structures['relaxed'] = calc.output
        else:
            entry.structures['relaxed'] = calc.output
    return calc


def relaxation_lda(entry, **kwargs):
    '''
    Start a LDA relaxation calculation

    Arguments:
        entry:
            Entry to be run

    Output:
        Calculation object containing result (if converged)
    '''

    return relaxation_lda(entry, xc_func='LDA', **kwargs)


def static(entry, xc_func='PBE', **kwargs):
    '''
    Start a final, accurate static calculation

    Arguments:
        entry:
            Entry, structure to be relaxed

    Keyword Arguments:
        xc_func:
            String, name of XC function to use (Default='PBE'). Is used to
            determine the name of the configuration settings file to use
        kwargs:
            Settings passed to calculation object

    Output:
        Calculation:
            results of calculation object
    '''

    # Get name of static run
    cnfg_name = 'static'
    if xc_func.lower() != 'pbe':
        cnfg_name += "_{}".format(xc_func.lower())

    # Get the calculation directory
    calc_dir = os.path.join(entry.path, cnfg_name)

    # Check if this calculation has converged
    if entry.calculations.get(cnfg_name, Calculation()).converged:
        return entry.calculations[cnfg_name]

    # Get the relaxation calculation
    calc = relaxation(entry, xc_func=xc_func, **kwargs)

    # Special Case: Check whether relaxation is low-spin
    if hasattr(calc, 'Co_lowspin'):
        use_lowspin = (calc.Co_lowspin is True)
    else:
        use_lowspin = False

    if not calc.converged:
        return calc

    # Input structure = output structure from relaxation
    input_structure = calc.output

    # Get path to CHGCAR
    chgcar_path = calc.path

    # Set up calculation
    calc = Calculation.setup(
        input_structure,
        entry=entry,
        configuration=cnfg_name,
        path=calc_dir,
        chgcar=chgcar_path,
        **kwargs
    )

    # Special Case: Set Co to low-spin configuration
    if use_lowspin:
        for atom in calc.input:
            if atom.element.symbol == 'Co':
                atom.magmom = 0.01

    # Store calculation in Entry list
    entry.calculations[cnfg_name] = calc
    entry.save()

    if not calc.converged:
        calc.write()

    # Save calculation [ LW 20Jan16: Only for PBE for now ]
    # Uncomment after the chemical potentials runs are done
    # [vh]
###    if calc.converged and xc_func.lower() == 'pbe':
###        f = calc.get_formation() # LW 16 Jan 2016: Need to rewrite this to have
###        # separate hulls for LDA / PBE / ...
###        f.save()
###        ps = PhaseSpace(calc.input.comp.keys())
###        ps.compute_stabilities(reevaluate=True, save=True)
###    else:
###        calc.write()
    return calc


def static_lda(entry, **kwargs):
    '''
    Run a static calculation with LDA XC functionals

    Input:
        entry - Entry, OQMD entry to be computed
    Output:
        Calculation, result
    '''

    return static(entry, xc_func='LDA', **kwargs)


def wavefunction(entry, **kwargs):
    '''
    Run a DFT calcualtion that produces a WAVECAR file.

    Useful as a step before running a hybrid functional calculation

    Input:
        entry - Entry, OQMD entry to be computed

    Output:
        Calculation, result
    '''
    if entry.calculations.get('wavefunction', Calculation()).converged:
        return entry.calculations['wavefunction']

    # Get the static calculation result
    static_run = static(entry, **kwargs)
    # parallelization for PBE and HSE are different
    if not static_run.converged:
        raise NotImplementedError

    # Use the same input structure as input into our calculation
    input_structure = static_run.input
    ispin = int(static_run.setting_from_incar('ISPIN'))

    calc = Calculation.setup(
        input_structure,
        entry=entry,
        configuration='wavefunction',
        path=os.path.join(entry.path, 'wavefunction'),
        settings={'lwave': True,
                  'ispin': ispin},
        chgcar=os.path.join(entry.path, 'static'),
        **kwargs
    )

    # Save the calculation and exit
    entry.calculations['wavefunction'] = calc
    if not calc.converged:
        calc.write()
    return calc


def hybrid(entry, **kwargs):
    '''
    Perform one (or more) hybrid functional calculations

    Input:
        entry - Entry, OQMD entry to be computed

    Keyword arguments:
        forms - list of strings denoting the kind of hybrid calculation to run
        (e.g., ['hse06'])

        NOTE: Only HSE06 implemented so far.

    Output:
        dict of Calculation, results
    '''
    calcs = {}

    # first, get a wavecar
    wave = wavefunction(entry, **kwargs)
    if not wave.converged:
        calcs['wavefunction'] = wave
        return calcs

    # Run all the requested calculations
    default = ['b3lyp', 'hse06', 'pbe0', 'vdw']

    input_structure = wave.input
    ispin = int(wave.setting_from_incar('ISPIN'))

    for form in kwargs.get('forms', default):
        if not form == 'hse06':
            continue
        if wave.band_gap > 0:
            algo_flag = 'All'
        else:
            algo_flag = 'Damped'

        # special instructions for HSE calculations
        calc = Calculation.setup(
            input_structure,
            entry=entry,
            configuration=form,
            path=os.path.join(entry.path, form),
            settings={'lwave': True,
                      'ispin': ispin,
                      'algo': algo_flag},
            chgcar=os.path.join(entry.path, 'wavefunction'),
            wavecar=os.path.join(entry.path, 'wavefunction'),
            **kwargs
        )

        entry.calculations[form] = calc
        if not calc.converged:
            calc.write()

        calcs[form] = calc
    return calcs


def hse06(entry, **kwargs):
    '''
    Run an HSE06 static calculation

    Input:
        entry - Entry, OQMD entry to be computed

    Output:
        Calculation, results
    '''
    calcs = hybrid(entry, forms=['hse06'], **kwargs)

    if 'wavefunction' in calcs:
        return calcs['wavefunction']
    else:
        return calcs['hse06']


def hse_relaxation(entry, **kwargs):
    '''
    Run an HSE06 relaxation calculation

    Input:
        entry - Entry, OQMD entry to be computed

    Output:
        Calculation, results
    '''
    if entry.calculations.get('hse_relaxation', Calculation()).converged:
        return entry.calculations['hse_relaxation']

    # Get the static calculation result
    static_run = static(entry, **kwargs)
    if not static_run.converged:
        raise NotImplementedError

    # Use the same input structure as input into our calculation
    input_structure = static_run.input
    ispin = int(static_run.setting_from_incar('ISPIN'))

    if static_run.band_gap > 0:
        algo_flag = 'All'
    else:
        algo_flag = 'Damped'

    calc = Calculation.setup(
        input_structure,
        entry=entry,
        configuration='hse_relaxation',
        path=os.path.join(entry.path, 'hse_relaxation'),
        settings={'lwave': True,
                  'ispin': ispin,
                  'algo': algo_flag},
        **kwargs
    )

    # Save the calculation and exit
    entry.calculations['hse_relaxation'] = calc
    if not calc.converged:
        calc.write()
    return calc


def acc_std_relax(entry, xc_func='PBE', **kwargs):
    """
    Performs a very accurate relaxation of the standardized primitive cell.

    If a converged `static` calculation is not found, it is set up.
    If a converged `static` calculation is found, its output structure is
    converted into a standardized primitive cell (by default; alternate
    options can be specified via `kwargs`) using `spglib`, and an
    accurate relaxation is set up for it.
    Some parameters for the relaxation are set based on whether the converged
    `static` calculation finds the compound to have a zero/nonzero band gap,
    has zero/nonzero magnetization, etc.

    Args:
        entry:
            :class:`qmpy.Entry` object with the entry to be calculated.

    Keyword Args:
        xc_func:
            String with the xc functional to use. The corresponding PAW
            potentials are automatically used.
            Looks for calculation configuration and settings under a key named
            "acc_std_relax_[xc_func]" in the `qmpy.VASP_SETTINGS` dictionary.
            If xc functional is PBE, the key in the dictionary is named
            "acc_std_relax", without a suffix.
            Defaults to 'PBE'.

        **kwargs:
            Miscellaneous keyword arguments passed onto the
            :class:`qmpy.Calculation` object that is queried for/set up.

            The ones used in this function are:
            to_primitive:
                Boolean with whether to calculate the primitive unit cell.
                Defaults to True.

            symprec:
                Float with the tolerance used in standardizing the unit cell
                (passed on to `spglib`).
                Defaults to 1e-3.

    Returns:
        :class:`qmpy.Calculation` object with the suitable calculation in the
        workflow.

    """
    # Name of the configuration
    configuration = 'acc_std_relax'
    if xc_func.lower() != 'pbe':
        configuration += "_{}".format(xc_func.lower())

    # If the calculation has already been successfully performed for this
    # entry, return it
    if entry.calculations.get(configuration, Calculation()).converged:
        return entry.calculations[configuration]

    # Get the `static` calculation for this entry
    static_calc = static(entry, xc_func=xc_func, **kwargs)

    # If the `static` calculation has not successfully completed, return it
    if not static_calc.converged:
        return static_calc

    # Input structure = output from the converged `static` calculation
    input_structure = static_calc.output.copy()

    # Convert it into a standardized (primitive) cell
    to_primitive = kwargs.get('to_primitive', True)
    symprec = kwargs.get('symprec', 1e-3)
    routines.standardize_cell(input_structure,
                              to_primitive=to_primitive,
                              symprec=symprec)

    # Override some parameters based on the results of the `static` calculation
    settings_override = {}

    # Use Gaussian smearing (ISMEAR = 0) for semiconductors/insulators,
    # Methfessel-Paxton of order 1 (ISMEAR = 1) for metals.
    ismear = 1 if static_calc.band_gap == 0 else 0
    settings_override['ismear'] = ismear

    # Don't do spin-polarized calculation if previous OQMD calculation found
    # the compound to be non-magnetic.
    # Especially relevant for 4d/5d transition metal containing compounds
    # that are not magnetic.
    magmom_pa = static_calc.magmom_pa
    if magmom_pa is not None:
        if abs(magmom_pa) <= 1e-3:
            settings_override['ispin'] = 1

    # Folder in which to run the calculation
    path = os.path.join(entry.path, configuration)

    # Setup the calculation; get `qmpy.Calculation` object if already exists
    calc = Calculation.setup(
            input_structure,
            entry=entry,
            configuration=configuration,
            path=path,
            settings_override=settings_override,
            **kwargs
    )

    # Add calculation to the entry's calculations dictionary
    entry.calculations[configuration] = calc
    # Add the final structure to the entry's structure dictionary
    entry.structures['acc_std_relaxed'] = calc.output
    # Save the entry
    entry.save()

    # If calculation has not converged (new/fixed calculation), write all the
    # VASP input files
    if not calc.converged:
        calc.write()

    return calc


