import numpy as np
import sys
from subprocess import call
import time
import pandas as pd
import os
import rebound
import reboundx

#use to read the sims to get the inst times
def get_times(row):
    #print(fcpath+row["runstring"])
    try:
        sim = rebound.Simulation.from_file(fcpath+row["runstring"])
        columns = ['t']
        features = [ sim.t ]
        #print ('{0:.16f}'.format(sim.t))
    except Exception as e:
        #print(e)
        columns= ['t']
        features = [ np.nan ]
    return pd.Series(features, index=columns)


simID = float(sys.argv[1]) #efac label for the desireds csv file
#Nruns = int(sys.argv[2])

if (simID%1 ==0):
    simID == int(simID)

#create the csv files here, assume the entire batch is already done running

path = "/mnt/scratch-lustre/nhussain/data/distributions/solar_efac{0}_1e9/".format(simID)
file_name = "solar_efac{0}_1e9".format(simID)
fcpath = path + "/final_conditions/fc"
df= pd.read_csv(path+"/times_{0}.csv".format(simID))
df = pd.concat([df, df.apply(get_times, axis = 1)], axis = 1)
df.to_csv("/mnt/raid-cita/nhussain/stability_stuff/stabilitydataset/Analysis/solar_{0}_1e9_1000.csv".format(simID, index_col = False ))
print("saving {0}".format(file_name.split("_")[1]) )
print(df.head(15))
print("Processed data")

try:
    inst_times = pd.read_csv("/mnt/raid-cita/nhussain/stability_stuff/stabilitydataset/Analysis/solar_{0}_1e9_1000.csv".format(simID), index_col=0)
    print(inst_times.head())
    times = inst_times["t"].astype("float64").values
    #print(times)
    redo_sims = np.where(np.isnan(times)==True)[0]
    print(redo_sims) 
    #'''
    for vals in redo_sims:
        runstring = "{0:0=7d}.bin".format(vals)
        with open("sunnyvale_rerun.sh", "w") as of:
            of.write("#!/bin/bash -l\n")
            of.write("#PBS -l nodes=1:ppn=1\n")
            of.write("#PBS -q workq\n")
            of.write("#PBS -r n\n")
            of.write("#PBS -l walltime=48:00:00\n")
            of.write("#PBS -N rerun_e{0}sa_{1}\n".format(simID, vals))
            of.write("# EVERYTHING ABOVE THIS COMMENT IS NECESSARY, SHOULD ONLY CHANGE nodes,ppn,walltime and my_job_name VALUES\n")
            of.write("cd $PBS_O_WORKDIR\n")
            of.write("module load gcc/5.4.0\n")
            of.write("source /mnt/raid-cita/nhussain/venv-3.4.3/bin/activate\n")
            #of.write("source /mnt/raid-cita/dtamayo/stability/bin/activate\n")
            of.write("python ~/mnt/stability_stuff/stabilitydataset/generate_data/rerunsolar.py {0} {1}\n".format(simID, vals))
            #parameter passes will be the sa ID number file to load
        
        try:
            call("chmod u=rwx sunnyvale_rerun.sh", shell=True) # chmod u =rwx sun...i
            call("qsub sunnyvale_rerun.sh", shell=True)
            print("Submit  Script Again for Efac:{} , Simulation Number:{}".format(simID, vals))
        except Exception as e:
            print(e)
            print("Could not create sunnyvale_rerun file")
        #'''
        #print("Done submitting first script")
except Exception as e:
    print(e)


