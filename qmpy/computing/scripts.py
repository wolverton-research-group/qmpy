import logging
import time
from django.db import models
from django.core.exceptions import *
from datetime import datetime
import os

import qmpy.utils as utils
from qmpy.analysis.vasp import *
from qmpy.analysis.thermodynamics.space import PhaseSpace
from qmpy.computing.resources import *
from copy import deepcopy

logger = logging.getLogger(__name__)


def initialize(entry, **kwargs):
    """
    DEPRECATED: Run a relaxation with very low settings
    """
    entry.input.set_magnetism("ferro")
    calc = Calculation.setup(
        entry.input,
        entry=entry,
        configuration="initialize",
        path=entry.path + "/initialize",
        **kwargs,
    )

    calc.set_label("initialize")
    if not calc.converged:
        calc.write()
        return calc

    if calc.converged:
        if calc.magmom > 0.1:
            entry.keywords.append("magnetic")
    return calc


def coarse_relax(entry, **kwargs):
    """
    DEPRECATED: Run a relaxation with low cutoff energy
    """
    if entry.calculations.get("coarse_relax", Calculation()).converged:
        return entry.calculations["coarse_relax"]

    calc = initialize(entry, **kwargs)
    if not calc.converged:
        calc.write()
        return calc

    calc.set_label("coarse_relax")
    inp = entry.structures["input"]
    if not "magnetic" in entry.keywords:
        inp.set_magnetism("none")

    calc = Calculation.setup(
        inp,
        entry=entry,
        configuration="coarse_relax",
        path=entry.path + "/coarse_relax",
        **kwargs,
    )

    if calc.converged:
        calc.output.set_label("coarse_relax")
    return calc


def fine_relax(entry, **kwargs):
    """
    DEPRECATED: Run a slightly more expensive relaxation calculation
    """
    if entry.calculations.get("fine_relax", Calculation()).converged:
        return entry.calculations["fine_relax"]

    calc = coarse_relax(entry, **kwargs)
    if not calc.converged:
        calc.write()
        return calc
    inp = entry.structures["coarse_relax"]
    if "magnetic" in entry.keywords:
        inp.set_magnetism("ferro")

    calc = Calculation.setup(
        inp,
        entry=entry,
        configuration="fine_relax",
        path=entry.path + "/fine_relax",
        **kwargs,
    )
    if calc.converged:
        entry.structures["fine_relax"] = calc.output
        entry.calculations["fine_relax"] = calc
    return calc


def standard(entry, **kwargs):
    """'
    DEPRECATED: Run a final, static calculation at standard cutoff energy
    """
    if entry.calculations.get("standard", Calculation()).converged:
        return entry.calculations["standard"]

    calc = fine_relax(entry, **kwargs)
    if not calc.converged:
        calc.write()
        return calc

    inp = entry.structures["fine_relax"]
    if "magnetic" in entry.keywords:
        inp.set_magnetism("ferro")

    calc = Calculation.setup(
        inp,
        entry=entry,
        configuration="standard",
        path=entry.path + "/standard",
        **kwargs,
    )
    if calc.converged:
        f = calc.get_formation()
        f.save()
        entry.calculations["standard"] = calc
        entry.structures["standard"] = calc.output
        ps = PhaseSpace(list(calc.input.comp.keys()))
        ps.compute_stabilities(save=True)
    return calc


def check_spin(entry, xc_func="PBE"):
    """
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
    """

    # Get name of high-spin calculation
    high_name = "relaxation"
    if xc_func.lower() != "pbe":
        high_name += "_%s" % (xc_func.lower())

    # Get name of low-spin calculation
    low_name = "Co_lowspin"
    if xc_func.lower() != "pbe":
        low_name += "_%s" % (xc_func.lower())

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
            if e1 - e2 <= 0.005:
                return entry.calculations[high_name]
            else:
                return entry.calculations[low_name]

    # If both calculations are not complete
    return None


def relaxation(entry, xc_func="PBE", **kwargs):
    """
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
    """

    # Get the name of this configuration
    cnfg_name = "relaxation"
    if not xc_func.lower() == "pbe":
        cnfg_name = cnfg_name + "_" + xc_func.lower()

    # Use this to define the calculation path
    path = entry.path + "/" + cnfg_name

    # Check whether to use high or low spin for Co compounds
    if "Co" in entry.comp:
        spin = check_spin(entry, xc_func=xc_func)
        if not spin is None:
            return spin
    else:
        # If relaxation calculation is converged, return that calculation
        if entry.calculations.get(cnfg_name, Calculation()).converged:
            return entry.calculations[cnfg_name]

    # Check if the calculation is converged / started
    if not entry.calculations.get(cnfg_name, Calculation()).converged:
        in_struct = entry.input.copy()

        projects = entry.project_set.all()
        if "fast" in entry.keywords:
            calc = Calculation.setup(
                in_struct,
                entry=entry,
                configuration=cnfg_name,
                path=path,
                settings={"kpar": 4},
                **kwargs,
            )
        else:
            calc = Calculation.setup(
                in_struct, entry=entry, configuration=cnfg_name, path=path, **kwargs
            )

        entry.calculations[cnfg_name] = calc
        calc.Co_lowspin = False

        # If converged, write results to disk and return calculation
        if not calc.converged:
            calc.write()
            return calc

    # Special case: Co, which requires high and low spin calculations
    if "Co" in entry.comp:
        # Get name of low spin calculation
        low_name = "Co_lowspin"
        if xc_func.lower() != "pbe":
            low_name += "_%s" % (xc_func.lower())

        # Update / start the low spin calculation
        if not entry.calculations.get(low_name, Calculation()).converged:

            # Get the low_spin calculation directory
            lowspin_dir = os.path.join(entry.path, low_name)

            # Get input structure
            in_struct = entry.input.copy()

            if "fast" in entry.keywords:
                calc = Calculation.setup(
                    in_struct,
                    entry=entry,
                    configuration=cnfg_name,
                    path=lowspin_dir,
                    settings={"kpar": 4},
                    **kwargs,
                )
            else:
                calc = Calculation.setup(
                    in_struct,
                    entry=entry,
                    configuration=cnfg_name,
                    path=lowspin_dir,
                    **kwargs,
                )

            # Return atoms to the low-spin configuration
            for atom in calc.input:
                if atom.element.symbol == "Co":
                    atom.magmom = 0.01

            entry.calculations[low_name] = calc
            calc.Co_lowspin = True
            if not calc.converged:
                calc.write()
                return calc

    # Special case: Save structure to "relaxed" if this is a PBE calculation
    if xc_func.lower() == "pbe":
        if "Co" in entry.comp:
            calc = check_spin(entry, xc_func=xc_func)
            assert not calc is None
            entry.structures["relaxed"] = calc.output
        else:
            entry.structures["relaxed"] = calc.output
    return calc


def relaxation_lda(entry, **kwargs):
    """
    Start a LDA relaxation calculation

    Arguments:
        entry:
            Entry to be run

    Output:
        Calculation object containing result (if converged)
    """

    return relaxation_lda(entry, xc_func="LDA", **kwargs)


def static(entry, xc_func="PBE", **kwargs):
    """
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
    """

    # Get name of static run and relaxation runs for Co
    cnfg_name = "static"
    if xc_func.lower() != "pbe":
        cnfg_name += "_%s" % (xc_func.lower())

    # Get the calculation directory
    calc_dir = os.path.join(entry.path, cnfg_name)

    # If static calculation has converged, return that calculation
    if entry.calculations.get(cnfg_name, Calculation()).converged:
        return entry.calculations[cnfg_name]

    # Get the relaxation calculation
    calc = relaxation(entry, xc_func=xc_func, **kwargs)

    # Special Case: Check whether relaxation is low-spin
    if hasattr(calc, "Co_lowspin"):
        use_lowspin = calc.Co_lowspin is True
    else:
        use_lowspin = False

    if not calc.converged:
        return calc

    # Special case: also perform the static for the higher energy spin configuration
    if "Co" in entry.comp:

        # If the lower energy relaxation was low spin, perform now the high spin static
        if use_lowspin:
            
            cnfg_name_spin = "static_highspin"
            if xc_func.lower() != "pbe":
                cnfg_name_spin += "_%s" % (xc_func.lower())

            # Update / start the high spin calculation
            if not entry.calculations.get(cnfg_name_spin, Calculation()).converged:

                # Get the high spin calculation directory
                calc_dir_spin = os.path.join(entry.path, cnfg_name_spin)

                # Get input structure
                in_struct_spin = entry.calculations["relaxation"].output

                # Get input path
                chgcar_path_spin = entry.calculations["relaxation"].path
                
                # Setup calculation
                calc_spin = Calculation.setup(
                    in_struct_spin,
                    entry=entry,
                    configuration=cnfg_name,
                    path=calc_dir_spin,
                    chgcar=chgcar_path_spin,
                    **kwargs,
                )
                
                # Return atoms to the high spin configuration
                for atom in calc_spin.input:
                    if atom.element.symbol == "Co":
                        atom.magmom = 5

                entry.calculations[cnfg_name_spin] = calc_spin

                if not calc_spin.converged:
                    calc_spin.write()
                    return calc_spin

        else:

            cnfg_name_spin = "static_lowspin"
            if xc_func.lower() != "pbe":
                cnfg_name_spin += "_%s" % (xc_func.lower())

            # Update / start the low spin calculation
            if not entry.calculations.get(cnfg_name_spin, Calculation()).converged:

                # Get the low spin calculation directory
                calc_dir_spin = os.path.join(entry.path, cnfg_name_spin)

                # Get input structure
                in_struct_spin = entry.calculations["Co_lowspin"].output

                # Get input path
                chgcar_path_spin = entry.calculations["Co_lowspin"].path

                # Setup calculation
                calc_spin = Calculation.setup(
                    in_struct_spin,
                    entry=entry,
                    configuration=cnfg_name,
                    path=calc_dir_spin,
                    chgcar=chgcar_path_spin,
                    **kwargs,
                )

                # Return atoms to the low spin configuration
                for atom in calc_spin.input:
                    if atom.element.symbol == "Co":
                        atom.magmom = 0.01

                entry.calculations[cnfg_name_spin] = calc_spin

                if not calc_spin.converged:
                    calc_spin.write()
                    return calc_spin

    # Input structure == output structure from relaxation
    in_struct = calc.output

    # Get path to CHGCAR
    chgcar_path = calc.path

    # Set up calculation
    if "fast" in entry.keywords:
        calc = Calculation.setup(
            in_struct,
            entry=entry,
            configuration=cnfg_name,
            path=calc_dir,
            chgcar=chgcar_path,
            settings={"kpar": 4},
            **kwargs,
        )
    else:
        calc = Calculation.setup(
            in_struct,
            entry=entry,
            configuration=cnfg_name,
            path=calc_dir,
            chgcar=chgcar_path,
            **kwargs,
        )

    # Special Case: Set Co to low-spin configuration
    if use_lowspin:
        for atom in calc.input:
            if atom.element.symbol == "Co":
                atom.magmom = 0.01

    # Store calculation in Entry list
    entry.calculations[cnfg_name] = calc

    # Save calculation [ LW 20Jan16: Only for PBE for now ]
    if calc.converged and xc_func.lower() == "pbe":
        calc.save()
        f = calc.get_formation()  # LW 16 Jan 2016: Need to rewrite this to have
        # separate hulls for LDA / PBE / ...
        f.save()
        ps = PhaseSpace(list(calc.input.comp.keys()))
        ps.compute_stabilities(reevaluate=True, save=True)
    else:
        calc.write()
    return calc


def static_lda(entry, **kwargs):
    """
    Run a static calculation with LDA XC functionals

    Input:
        entry - Entry, OQMD entry to be computed

    Output:
        Calculation, result
    """

    return static(entry, xc_func="LDA", **kwargs)


def wavefunction(entry, **kwargs):
    if entry.calculations.get("wavefunction", Calculation()).converged:
        return entry.calculations["wavefunction"]

    calc = static(entry, **kwargs)
    if not calc.converged:
        return calc

    in_struct = calc.input
    calc = Calculation.setup(
        in_struct,
        entry=entry,
        configuration="static",
        path=entry.path + "/hybrids/wavefunction",
        chgcar=entry.path + "/static",
        settings={"lwave": True},
        **kwargs,
    )
    entry.calculations["wavefunction"] = calc
    if not calc.converged:
        calc.write()
    return calc


def hybrid(entry, **kwargs):
    # first, get a wavecar
    wave = wavefunction(entry, **kwargs)
    if not wave.converged:
        return wave

    calcs = []
    default = ["b3lyp", "hse06", "pbe0", "vdw"]
    for hybrid in kwargs.get("forms", default):
        calc = Calculation.setup(
            input,
            entry=entry,
            configuration=hybrid,
            path=entry.path + "/hybrids/" + hybrid,
            wavecar=wave,
            settings={"lwave": True},
            **kwargs,
        )
        calcs.append(calc)
    return calcs
