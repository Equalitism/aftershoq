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

from structure.classes import Structure, MaterialPar as mp
from structure.sgenerator import Sgenerator
from utils.qclutil import MaterialUtil as mu
from numerics.runplatf import Local
from utils.systemutil import SystemUtil as su
from utils.debug import Debugger as dbg
from interface.isewself import Isewself
from numerics.paraopt import Paraopt
from matplotlib import pyplot as pl


if __name__ == '__main__':
    
    # the working directory:
    path = "../../demo"
    path = os.getcwd()+"/"+path
    su.mkdir(path)
    
    # Setup debugger:
    dbg.open(dbg.verb_modes['verbose'],path+"/debug.log")
    dbg.debug("Debug file \n\n")
    dbg.flush()
    
    sep = '\n----------------------------------------------\n'
    
    print '--- Welcome to the "sewself" demonstration of ---\n'
    print '               "AFTERSHOQ" \n\n'
    print '       Written by Martin Franckie 2018.'
    print '       Please give credit where credit'
    print '                   is due\n'
    print sep
    print 'Creating semiconductor materials and alloys:\n'
    print '       ( All CBO relative to GaAs )\n'
    
    # create materials GaAs, AlAs, InAs:
    
    GaAs = mu.createGaAs()
    AlAs = mu.createAlAs()
    InAs = mu.createInAs()
    
    # create InGaAs/InAlAs lattice matched to InP:
    
    x = 0.47
    lmname = "In" + str(x) + "Ga" + str(1-x) + "As"
    InGaAsLM = mu.createGaInAs(x,lmname)
    print str(InGaAsLM) + ":\n"
    for val in mp.valdict:
        print val + " = " + str(InGaAsLM.params[mp.valdict[val]])
    
    x = 0.48
    lmname = "In" + str(x) + "Al" + str(1-x) + "As"
    InAlAs = mu.createAlInAs(x,lmname)
    print "\n" + str(InAlAs) + ":\n"
    for val in mp.valdict:
        print val + " = " + str(InAlAs.params[mp.valdict[val]])
    
    # create Al_0.15Ga_0.85As 
    x = 0.20
    AlGaAs = mu.createAlGaAs(x)
    print "\n" + str(AlGaAs) + ":\n"
    for val in mp.valdict:
        print val + " = " + str(AlGaAs.params[mp.valdict[val]])
    
    print sep
    print 'Creating a structure from generated materials:\n'
    print '[width, material, eta, lambda]'
    
    # creating a two quantum-well structure
    s = Structure()
    
    # set interface roughness parameters for all interfaces:
    eta = 0.1
    lam = 2.0
    s.setIFR(eta, lam)
    
    # Add layers:
    # Add layers:
    s.addLayerMW(3.0, AlGaAs)
    s.addLayerMW(20.0, AlGaAs)
    s.addLayerMW(4.0,GaAs)
    s.addLayerMW(2.0,AlGaAs) # <-- doped layer 3
    s.addLayerMW(6.0,GaAs)
    s.addLayerMW(20,AlGaAs)
    
    # define doping layer
    zstart = 0; zend = 2.0; dopdens = 2e18; layer = 3
    
    # add a doping layer
    s.addDoping(zstart, zend, dopdens, layer)
    
    print "Structure created : "
    print s
    
    print sep
    print 'Generating N random structures:\n'
    N = input('N = ?\n')
    
    # define variations in composition, layer widths,
    # and doping location/density:
    dx = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    dw = [0,0,2,0,2,0]
    ddop = [0,0,0]
    
    # create a structure generator instance, based on our structure s above:
    sg = Sgenerator(s,dw,dx,ddop)
    
    # generate N random structures with the distribution in parameters defined above:
    #sg.genRanStructs(N)
    
    # generate N random structures, along the Hilbert curve with p = 5
    coords = sg.genRanHilbertStructs(N, 7)
    
    for st in sg.structures:
        print str(st.sid) + ' ' + str(st)
        
    print sep
    
    proceed = input("Proceed to create directory tree?\nYes = 1\nExit = 0")
    if proceed == 0:
        print sep + "User exit. Good bye!"
        dbg.close()
        exit()
    
    # set numerical parameters:
    
    # the binaries (change to your bin folder):
    binpath = "/Users/martin/git/Sewself_JF/bin/"
    
    print 'Creating directory tree in: ' + path + '.\n'
    print 'Please change variable "binpath" to match your binaries!\n'
    
    # make the directory:
    su.mkdir(path)
    
    # Define the platform, local or cluster (e. g. Euler cluster at ETH Zuerich)
    pltfm = Local()
    #pltfm = Euler(1,"1:00")
    
    # sewself interface:
    material_list = [GaAs,AlGaAs]
    model = Isewself(binpath,pltfm,material_list)
    
    
    # to change parameters, change the dictionaries in isewself:
    model.sewselfpar["emin"] = -0.0001
    model.numpar["efield"] = 0.00
    # (material parameters are atuo-generated from materials in material_list)
    
    
    # to create input files with default parameters:
    model.writeStructFile(s, path)
    model.writeParameterFile(path)
    model.writeSewselfPar(path)
    
    # define the merit function as max gain/current density, from a dictionary of merit funcs.:
    model.merit = model.merits.get("DeltaE_12")
    model.target = 0.030
    
    print sep + 'Starting simulations in directory tree? This will overwrite any previous results.'
    proceed = input("Yes = 1\nExit = 0")
    if proceed == 0:
        print sep + "User exit. Good bye!"
        dbg.close()
        exit()
    
    # execute the model for simulating the structures:
    model.runStructures(sg.structures, path)
    
    model.waitforproc(1, "sewself is running....")
    
    print sep + 'Gathering results to: ' + path + '/results.log'
    
    # gather the results from the simulation of all structures:
    model.gatherResults(sg.structures, path)
    
    print sep + 'First results acheived. Proceed with optimization?'
    proceed = input("Yes = 1\nExit = 0")
    if proceed == 0:
        print sep + "User exit. Good bye!"
        dbg.close()
        exit()
    
    # collect results from trial points
    x0 = []
    [x0.append( sg.hutil.interp_dist_from_coords( c ) ) for c in coords]
    x0 = numpy.array(x0)
    x0.sort()
    x0 = x0.tolist()
    print x0
    y0 = []
    xi = 0
    for i in range(0,len(x0)):
        try:
            y0.append( -float(model.getMerit(sg.structures[i],path)) )
        except( ValueError ):
            del x0[xi]
            xi-=1
        xi +=1
    
    print 'Array of trial results:\n' + str(y0)

    # create optimization object
    print "imax = " + str(sg.hutil.imax)
    tol, r, itmax, procmax = 0.001*sg.hutil.imax, 1.5, 100, 20
    
    opt = Paraopt(tol,r,itmax,procmax,x0,y0)
    
    conv = opt.minimize(model, sg, path)
    
    print "Optimization distances: \n" + str(opt.x)
    print "Optimization values: \n"    + str(opt.y)
    
    pl.plot(opt.x,opt.y)
    pl.show()
    
    print sep + 'Program completed! Good bye!'
    dbg.close()
    