import numpy as np
import reboundx
import pandas as pd
import rebound
import time
import matplotlib
from matplotlib import pyplot as plt
import sys

simID = sys.argv([1]) # efac factor
#efac is already correctly formatted
sa_number = sys.argv([2]) # run number
main_path = "/mnt/scratch-lustre/nhussain/data/distributions/solar_efac{0}_1e9/".format(simID)

#run this after all the runs are done, collect the times



sim = rebound.SimlationArchive(main_path+"/simulation_archives/sa{0:07d}.bin".format(sa_number))
   
last_snap = sim[-1]
rebx  = reboundx.Extras(last_snap)
gr = rebx.add("gr_potential")
gr.params["c"] = 10058.24
last_snap.collision = "direct"
yr = 2.*np.pi # one year is 2 pi in these units
last_snap.simulationarchive_filename = main_path +"/simulation_archives/sa{0:07d}.bin".format(sa_number)

try:
    last_snap.integrate(last_snap.t + 1e9*yr) # integrate for a million years   
    end = time.time()
    print("New_time", last_snap.t )
    #print(sim[-1].t)
    #sim = rebound.SimulationArchive("../../csvs/Solar_feats/solar_efac1.45_1e9/simulation_archives/sa{0:07d}.bin".format(vals))
    #print(sim[-1].t)
    #print(last_snap.t)
except Exception as e:
    print(e)
    print("Time at collision", last_snap.t)

#need to update the final conditions with the new time
last_snap.save(datapath + "/final_conditions/fc{0:07d}.bin".format(sa_number))

#break
