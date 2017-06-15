import numpy as np
import sys
from subprocess import call
import time
import pandas as pd

simID = int(sys.argv[1])
Nruns = int(sys.argv[2])

try:
    df = pd.read_csv("../data/distributions/{0}.csv".format(simID), index_col=0)
except:
    columns=['runstring']
    df = pd.DataFrame(columns=columns)

lastseed = df.shape[0]

for i in range(lastseed, lastseed+Nruns):
    runstring = "{0:0=7d}.bin".format(i)
    df.loc[i] = [runstring]
    with open("sunnyvale.sh", "w") as of:
        of.write("#!/bin/bash -l\n")
        of.write("#PBS -l nodes=1:ppn=1\n")
        of.write("#PBS -q workq\n")
        of.write("#PBS -r n\n")
        of.write("#PBS -l walltime=48:00:00\n")
        of.write("#PBS -N stab{0}\n".format(i))
        of.write("# EVERYTHING ABOVE THIS COMMENT IS NECESSARY, SHOULD ONLY CHANGE nodes,ppn,walltime and my_job_name VALUES\n")
        of.write("cd $PBS_O_WORKDIR\n")
        of.write("module load gcc/5.4.0\n")
        of.write("source /mnt/raid-cita/dtamayo/stability/bin/activate\n")
        of.write("python rundistribution.py {0} {1} {2}\n".format(simID, runstring, i))

    call("chmod u=rwx sunnyvale.sh", shell=True)
    call("qsub sunnyvale.sh", shell=True)
        
df.to_csv("../data/distributions/{0}.csv".format(simID), encoding='ascii')
