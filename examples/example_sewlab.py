'''
Created on 15 Feb 2018

@author: martin
'''
import sys
import os
import numpy
# change path as apropriate
path_to_aftershoq = os.getcwd()
sys.path.append(path_to_aftershoq)
sys.path.append(path_to_aftershoq + '/hilbert_curve/')

from structure.classes import Structure
import structure.matpar as mp
from structure.sgenerator import Sgenerator
from structure.materials import GaAs, AlGaAs
from numerics.runplatf import Local
import utils.systemutil as su
import utils.debug as dbg
from utils.qcls import *
from interface.isewlab import Isewlab
from numerics.paraopt import Paraopt
from matplotlib import pyplot as pl
import numpy as np


if __name__ == '__main__':
    
    # the binaries (change to your bin folder):
    binpath = "sewlab"
    
    # the working directory:
    path = "demo"
    path = os.getcwd()+"/"+path
    su.mkdir(path)
    
    # Setup debugger:
    dbg.open(dbg.verb_modes['verbose'],path+"/debug.log")
    dbg.debug("Debug file \n\n")
    dbg.flush()
    
    sep = '\n----------------------------------------------\n'
    
    print('--- Welcome to the "sewlab" demonstration of ---\n')
    print('               "AFTERSHOQ" \n\n')
    print('       Written by Martin Franckie 2018.')
    print('       Please give credit where credit')
    print('                   is due\n')
    print(sep)
    print('Creating semiconductor materials and alloys:\n')
    print('       ( All CBO relative to GaAs )\n')
    
    # create materials:
    # create GaAs:
    gaas = GaAs()
    
    
    # create Al_0.15Ga_0.85As 
    algaas = AlGaAs(x = 0.15)
    print("\n" + str(algaas) + ":\n")
    for val in mp.valdict:
        print(val + " = " + str(algaas.params[mp.valdict[val]]))
    
    print(sep)
    print('Creating a structure from generated materials:\n')
    print('[width, material, eta, lambda]')
    
    # creating a structure:
    
    mystruct = EV2017()
    
    print("Structure created : ")
    print(mystruct)
    
    print(sep)
    
    print('Creating directory tree in: ' + path + '.\n')
    print('Please change variable "binpath" to match your binaries!\n')
    
    # Define the platform, local or cluster (e. g. Euler cluster at ETH Zuerich)
    pltfm = Local()
    #pltfm = Euler(1,"1:00")
    
    # sewlab interface: (add parameter version '4.6.X' if you are not running the default 4.6.4
    model = Isewlab(binpath, pltfm, gaas)
    
    # to change parameters, change the dictionaries in Isewlab:
    
    # determines the ammount of output produced (also: "Verbose")
    model.numpar["verbosity"] = "Silent"
    
    # The electric field in the simulation
    efield0 = -1
    defield = -0.5
    Nefield = 1
    model.numpar["efield0"] = -0.100
    model.numpar["defield"] = -0.020
    model.numpar["Nefield"] = 5
    
    # Set the elecron and lattice temperatures
    Te = 100 # Kelvin
    Tl = 77  # Kelvin
    model.setTe(Te)         # electron temperature (set to 1500 K if kinetic balance is used)
    model.setTlattice(Tl)   # lattice tempreature (~cryostat temperature)
    
    model.useKinBal(False) # Use of kinetic balance?
    model.useSuperself(False) # Use of superself?
    model.computeLight(False) # Use of light computations (power, photon-driven current)
    
    # to create input files with default parameters (automatically done via runStructures() below):
    model.writeSampleFile(mystruct, path)
    model.writeScriptFile(path)
    
    print(sep + 'Starting simulations in directory tree (sewlab version ' + model.version + ' ). This will overwrite any previous results.')
    
    model.runStructures([mystruct], path)
    model.waitforproc(5, "sewlab is running...")
    
    print(sep + 'Gathering results to: ' + path + '/results.log')
    
    # gather the results from the simulation of all structures:
    model.gatherResults( [mystruct], path )
    
    print(sep + 'Results acheived!')
    
    # now, the results for each bias are stored in mystruct.results, .dipoles, .energies, .populations, and .rates
    results = np.array( mystruct.results )
    descr = ['E (kV/cm)', 'j (A/cm^2)', 'Max gain (1/cm)', 'Peak energy. (meV)']
    print(descr)
    print(results)
    # plots the I-V:
    pl.plot(-results[:,0], results[:,1],'-*')
    pl.xlabel("Electric field (kV/cm)")
    pl.ylabel("Current density (A/cm^2)")
    
    pl.figure(2)
    pl.plot(-results[:,0], results[:,2],'-*')
    pl.xlabel("Electric field (kV/cm)")
    pl.ylabel("Max gain (cm^{-1})")
    
    pl.figure(3)
    pl.plot(-results[:,0], results[:,3]*1000.,'-*')
    pl.xlabel("Electric field (kV/cm)")
    pl.ylabel("Peak position (meV)")
    
    pl.show()
    
    
    print(sep + 'Program completed! Good bye!')
    dbg.close()
    