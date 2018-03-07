import numpy as np
import sys
from subprocess import call
import time
import pandas as pd
import os


simID = sys.argv[1] #efac param
Nruns = int(sys.argv[2])

try:
    change_omega = eval(sys.argv[3])
    change_omega = True
except:
    change_omega = False

print (change_omega)
#'''

if change_omega ==False:
    file_path = "/mnt/scratch-lustre/nhussain/data/distributions/solar_efac{0}_1e9/".format(simID)
else:
    file_path = "/mnt/scratch-lustre/nhussain/data/distributions/solar_efac{0}_1e9_omega/".format(simID)

directory = os.path.dirname(file_path)
#print("Directory")
print("Run script")


try:
    os.stat(directory)
except:
    print(directory)
    os.mkdir(directory)

try:
    os.stat(directory+'/initial_conditions/')
except:
    os.mkdir(directory+'/initial_conditions/')

try:
    os.stat(directory+'/simulation_archives/')
except:
    os.mkdir(directory+'/simulation_archives/')


try:    
    os.stat(directory+'/final_conditions/')
except:
    os.mkdir(directory+'/final_conditions/')


try:
    df = pd.read_csv(directory +"/times_{1}.csv".format(simID, simID), index_col=0)

except:
    columns=['runstring']
    df = pd.DataFrame(columns=columns)

print("Create all the directories")
lastseed = df.shape[0]
#print(lastseed)

for i in range(lastseed, lastseed+Nruns):
    runstring = "{0:0=7d}.bin".format(i)
    df.loc[i] = [runstring]
    with open("sunnyvale_sol.sh", "w") as of:
        of.write("#!/bin/bash -l\n")
        of.write("#PBS -l nodes=1:ppn=1\n")
        of.write("#PBS -q workq\n")
        of.write("#PBS -r n\n")
        of.write("#PBS -l walltime=48:00:00\n")
        of.write("#PBS -N stab_{0}_efac_{1}\n".format(i, simID))
        of.write("# EVERYTHING ABOVE THIS COMMENT IS NECESSARY, SHOULD ONLY CHANGE nodes,ppn,walltime and my_job_name VALUES\n")
        of.write("cd $PBS_O_WORKDIR\n")
        of.write("module load gcc/5.4.0\n")
        of.write("source /mnt/raid-cita/nhussain/venv-3.4.3/bin/activate\n")
        #of.write("source /mnt/raid-cita/dtamayo/stability/bin/activate\n")
        of.write("python ~/mnt/stability_stuff/stabilitydataset/generate_data/solarsystem.py {0} {1} {2} {3}\n".format(simID, runstring, i, change_omega))

    try:
        call("chmod u=rwx sunnyvale_sol.sh", shell=True) # chmod u =rwx sun...i
        call("qsub sunnyvale_sol.sh", shell=True)
        print("Submit Resonance Script", i)
    except Exception as e:
        print(e)
        print("Could not create sunnyvale_sol file")

#   
try:
    df.to_csv(directory +"/times_{1}.csv".format(simID, simID), encoding='ascii')
except Exception as e:
    print(e)
    print("Can't save file")
   
#print("Done submitting first script")
#'''
