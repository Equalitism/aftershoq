'''
Created on 2 Feb 2018

@author: martin
'''

from systemutil import SystemUtil as su
import time

class Platform(object):
    '''
    classdocs
    '''


    def __init__(self, name=None):
        '''
        Constructor
        '''
        
    def submitjob(self,prog,args,dirpath,Nproc=None,wtime=None):
        pass
    
    def jobstatus(self,proc):
        pass
    
class Euler(Platform):
    
    def __init__(self,Nproc,wtime):
        '''
        Constructor
        '''
        super(Euler,self).__init__("Euler")
        self.Nproc = Nproc
        self.wtime = wtime
        self.subcommand = "bsub"
        self.procinfo = []
    
    def submitjob(self, prog, args,dirpath,Nproc=None,wtime=None):
        if Nproc is None:
            Nproc = self.Nproc
        if wtime is None:
            wtime = self.wtime
        
        progargs = []
        jobname = str(dirpath)
        
        progargs.append("-n")
        progargs.append(str(Nproc))
        progargs.append("-W")
        progargs.append(str(wtime))
        progargs.append("-J")
        progargs.append(jobname)
        if Nproc>1:
            progargs.append("mpirun")
        progargs.append(prog)
        [progargs.append(a) for a in args]
        proc = su.dispatch(self.subcommand, progargs, dirpath)
        self.procinfo.append([proc.pid,jobname])
        return proc
    
    def jobstatus(self, proc):
        for info in self.procinfo:
            if info[0]==proc.pid:
                jobname = info[1]
        p = su.runprogram("bjobs",["-J",jobname])
        out = p.communicate()
        
        if ("not found" in out[1]) and (proc.poll()!=None):
            print "process ended!"
            return False
        else:
            return True
        
class Local(Platform):
    
    def __init__(self):
        super(Local,self).__init__("Local")
        
    def submitjob(self, prog, args, dirpath, Nproc = None, wtime = None):
        proc = su.dispatch(prog, args, dirpath)
        return proc
    
    def submitandwait(self, prog,  args, dirpath):
        proc = su.runprogram(prog, args, dirpath)
        while proc.poll() == None:
            print proc.poll()
            time.sleep(0.1)
            print proc.poll()
        return proc
    
    def jobstatus(self, proc):
        if proc.poll()==None:
            return True
        else:
            return False
        
