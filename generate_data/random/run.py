# Run script with python run.py sim_id, where sim_id is an integer to use for the sim_id (and the RNG seed). Runs a base system and a shadow system
import numpy as np
import rebound
from random import random, uniform, seed
import time
import sys

def collision(reb_sim, col):
    reb_sim.contents._status = 5 # causes simulation to stop running and have flag for whether sim stopped due to collision
    return 0

def run_system(sim_id, shadow):
    maxorbs = 1.e9
    datapath = '../../data/random/'

    a1 = 1. # All distances in units of the innermost semimajor axis (always at 1)
    Mstar = 1. # All masses in units of stellar mass

    logMmin = np.log10(1.e-7) # 1/3 Mars around Sun
    logMmax = np.log10(1.e-4) # 2 Nep around Sun
    logemin = np.log10(1.e-3)
    logincmin = np.log10(1.e-3)
    logincmax = np.log10(1.e-1) # max mutual inclination of 11.4 degrees. Absolute of 5.7 deg
    betamin = 1. # min separation in Hill radii
    betamax = 5.

    seed(sim_id)

    M1 = 10.**uniform(logMmin, logMmax)
    M2 = 10.**uniform(logMmin, logMmax)
    M3 = 10.**uniform(logMmin, logMmax)

    hill12 = a1*((M1+M2)/3.)**(1./3.)
    beta1 = uniform(betamin, betamax)
    a2 = a1 + beta1*hill12
    ecrit12 = (a2-a1)/a2

    hill23 = a2*((M2+M3)/3.)**(1./3.)
    beta2 = uniform(betamin, betamax)
    a3 = a2 + beta2*hill23
    ecrit23 = (a3-a2)/a3

    minhill = min(hill12, hill23)

    logemax1 = np.log10(ecrit12)
    logemax2 = np.log10(min(ecrit12, ecrit23))
    logemax3 = np.log10(ecrit23)

    #print("beta1 = {0}, beta2 = {1}".format(beta1, beta2))
    #print("emax1 = {0}, emax2 = {1}, emax3 = {2}".format(10**logemax1, 10**logemax2, 10**logemax3))

    e1 = min(10.**uniform(logemin, logemax1), 1.) # make sure ecc < 1
    e2 = min(10.**uniform(logemin, logemax2), 1.)
    e3 = min(10.**uniform(logemin, logemax3), 1.)

    i1 = 10.**uniform(logincmin, logincmax)
    i2 = 10.**uniform(logincmin, logincmax)
    i3 = 10.**uniform(logincmin, logincmax)

    sim = rebound.Simulation()
    sim.integrator="whfast"
    sim.ri_whfast.safe_mode = 0
    sim.G = 4*np.pi**2

    sim.add(m=1.)
    sim.add(m=M1, a=a1, e=e1, pomega=random()*2.*np.pi, inc=i1, Omega=random()*2.*np.pi, f=random()*2.*np.pi, r=minhill)
    sim.add(m=M2, a=a2, e=e2, pomega=random()*2.*np.pi, inc=i2, Omega=random()*2.*np.pi, f=random()*2.*np.pi, r=minhill)
    sim.add(m=M3, a=a3, e=e3, pomega=random()*2.*np.pi, inc=i3, Omega=random()*2.*np.pi, f=random()*2.*np.pi, r=minhill)
    sim.move_to_com()
    ps = sim.particles

    if shadow:
        kicksize=1.e-11
        ps[2].x += kicksize

    sim.dt = 0.09 # 0.09 of inner orbital period
    sim.collision = "direct"
    sim.collision_resolve = collision
        
    runstr = "{0:0=7d}.bin".format(sim_id)
    if shadow:
        shadowstr = 'shadow'
        print(shadowstr)
    else:
        shadowstr = ''

    sim.save(datapath+'initial_conditions/'+shadowstr+'runs/ic'+runstr)
    sim.initSimulationArchive(datapath+'simulation_archives/'+shadowstr+'runs/sa'+runstr, interval=maxorbs/1000.)
    sim.integrate(maxorbs) # will stop if collision occurs
    sim.save(datapath+'final_conditions/'+shadowstr+'runs/fc'+runstr)

sim_id = int(sys.argv[1])
run_system(sim_id, 0) # run base system
run_system(sim_id, 1) # run shadow system
