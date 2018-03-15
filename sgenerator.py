from classes import Structure

import random
from hilbert import HilbertCurve
from hilbertutil import HilbertUtil
import numpy as np

class Sgenerator():
    def __init__(self,origstruct,dw,dx,ddop=None):
        self.dx = dx
        self.dw = dw
        self.orig = origstruct
        self.structures = []
        if ddop is None:
            ddop = [0,0,0]
        self.ddop = ddop
        for l in origstruct.layers:
            if l.width-dw[origstruct.layers.index(l)] <= 0:
                dw[origstruct.layers.index(l)] = l.width-0.01
    
    def genRanStructs(self,N):
        """
        Generate N structures with random variations in layer widths
        """
        for _ in range(0,N):
            news = Structure(self.orig)
            
            for il in range(0,len(self.dw)):
                w0 = self.orig.layers[il].width
                width = w0 + 2*(random.random()-0.5)*self.dw[il]
                news.layers[il].width = width
                
            news.dopings = []
            for dl in self.orig.dopings:
                
                # find out offset from layer start for original structure
                zc = (dl[0]+dl[1])/2
                layerindex = self.orig.layerIndex(zc)
                dzc = zc - self.orig.layerPos(layerindex)
                               
                # define new offset from layer start
                dzc = dzc + 2*(random.random()-0.5)*self.ddop[0]
                dopw = (dl[1]-dl[0]) + 2*(random.random()-0.5)*self.ddop[1]
                dopdens = dl[2] + 2*(random.random()-0.5)*self.ddop[2]
                
                # add new doping layer
                zi = dzc - dopw/2
                zf = dzc + dopw/2
                news.addDoping(zi, zf, dopdens, layerindex)
                
            self.structures.append(news)
            del news
           
    def genRanHilbertStructs(self,N,p):
        """
        Generate N structures on the Hilbert curve defined by p
        Number of dimensions is determined by # parameters to 
        change. Includes the end-points of the Hilbert curve.
        Returns the parameters scaled to the hyper cube space.
        """
        
        # Number of dimensions in Euclidian space
        ND = 0
        
        # Define list of changeable parameters
        params = []
        dparams = []
        windex = []
        xindex = []
        dopindex = []
        
        # 1) Layer widths:
        for i in range(0,len(self.orig.layers)):
            if self.dw[i]>0:
                params.append(self.orig.layers[i].width)
                dparams.append(self.dw[i])
                windex.append(i)
                ND += 1
                
        # 2) Doping layers:
        # TODO: extend to multiple doping layers
        for i in range(0,len(self.orig.dopings[0])):
            if self.ddop[i] > 0:
                params.append(self.orig.dopoings[0][i])
                dparams.append(self.ddop[i])
                dopindex.append(i)
                ND +=1
                
        # 3) Alloy composition x:
        for i in range(0,len(self.dx)):
            if self.dx[i] > 0:
                params.append(self.orig.layers[i].material.x)
                dparams.append(self.dx[i])
                xindex.append(i)
                ND += 1
  
        # 4) Add further parameters at this point...
        
        # define the Hilbert curve:
        hilbert_curve = HilbertCurve(p, ND)
        
        # imax = length of hilbert curve (# nodes)
        imax = 2**(ND*p)-1
        
        # pmax = side of hyper cube
        pmax = 2**p-1
        
        print 'Dim = {0}, p = {1}, imax = {2}, pmax = {3}'.format(ND,p,imax,pmax)
        
        self.hutil = HilbertUtil(hilbert_curve)
        self.params = params
        self.dparams = dparams
        self.windex = windex
        self.dopindex = dopindex
        self.xindex = xindex
        
        d = []
        
        for i in range(0,N):
            
            # pick a random point along the hilbert curve, and include
            # end points:
            if i == 0:
                d.append(i)
            elif i == N-1:
                d.append(imax)
            else:
                d.append(random.random()*imax)
            
        coordinates = self.gen_struct_from_hilbert_curve(d)
        
        return coordinates
    
    def gen_struct_from_hilbert_curve(self,newd):
        '''
        Generates new structures at the points along the
        Hilbert curve given in newd, and returns their
        scaled coordinates.
        '''
        
        
        dpar = np.array(self.dparams)
        parmin = np.array(self.params) - dpar
        coordinates = []
        for i in range(0,len(newd)):
            
            # interpolate to get the coordingates:            
            p_ipl = self.hutil.interp_coords_from_dist(newd[i])
            
            # un-scale it and create structure
            parnew = np.array(p_ipl)
            
            par_unscaled = parnew*2*dpar/self.hutil.pmax + parmin
            # generate strucure:
            news = Structure(self.orig)
            pindex = 0
            
            # Layer widths:
            for i in range(0,len(self.windex)):
                news.layers[self.windex[i]].width = par_unscaled[pindex]
                pindex+=1
                
            # Doping layers:
            for i in range(0,len(self.dopindex)):
                news.dopings[self.dopindex[i]] = par_unscaled[pindex]
                pindex +=1
                
            # Alloy composition:
            for i in range(0,len(self.xindex)):
                news.layers[self.xindex[i]].material.updateAlloy(par_unscaled[pindex])
                pindex +=1
                
            self.structures.append(news)
            
            coordinates.append(parnew)
            
        return coordinates