import sys
import numpy as np
from pypower.runpf import runpf,ppoption

#
# Executes power flow of full one line network
# for validation of the co-simulation
#
def full_powerflow(r,x,ratio):
    # Define system base MVA
    baseMVA = 1.0
    Zbase = 4761

    # Define buses
    # Bus format:
    #   [bus_i, type, Pd, Qd, Gs, Bs, area, Vm, Va, baseKV, zone, Vmax, Vmin]
    buses = np.array([
        [1, 3,        0,        0, 0, 0, 1, 1.0, 0, 69, 1, 1.05, 0.85],  # Slack Bus (69 kV, 0 deg)
        [2, 1,        0,        0, 0, 0, 1, 1.0, 0, 69, 1, 1.05, 0.85],  # Center Bus
        [3, 1, 20.0, 15.0, 0, 0, 1, 1.0, 0, 69, 1, 1.05, 0.85],  # Load Bus
    ])

    # Define generator (only the slack bus has a generator)
    # Generator format: [bus, Pg, Qg, Qmax, Qmin, Vg, mBase, status, Pmax, Pmin]
    generators = np.array([
        [1, 0, 0, 999, -999, 1.0, baseMVA, 1, 999, -999],  # Slack Bus Generator
    ])

    # Define branches (transmission line)
    # Branch format: [fbus, tbus, r, x, b, rateA, rateB, rateC, ratio, angle, status, angmin, angmax]
    branches = np.array([
        [1, 2, r*ratio/Zbase, x*ratio/Zbase, 0, 999, 999, 999, 0, 0, 1, -360, 360],  # Impedance of 0.1 + j0.2 Ohms
        [2, 3, r*(1.0-ratio)/Zbase, x*(1.0-ratio)/Zbase, 0, 999, 999, 999, 0, 0, 1, -360, 360],  # Impedance of 0.1 + j0.2 Ohms
    ])

    print(branches)

    # Define cost data (not used in power flow)
    gencost = np.array([
        [2, 0, 0, 3, 0, 0, 0],  # Dummy cost function
    ])

    # Construct PYPOWER case dictionary
    ppc = {
        "version": '2',
        "baseMVA": baseMVA,
        "bus": buses,
        "gen": generators,
        "branch": branches,
        "gencost": gencost
    }

    # Run power flow
    ppopt = ppoption(VERBOSE=0, OUT_ALL=0)  # This disables the console output
    results, success = runpf(ppc, ppopt)

    if success:
        print("Full Network Power Flow Converged!\n")
        print(f"Center Bus Voltage: {results["bus"][1][7]} pu , {results["bus"][1][8]} deg ")
        print(f"P & Q Flowing from Center Bus: {results["branch"][0][13]} MW , {results["branch"][0][14]} MVAR ")
    else:
        print("Power Flow did not converge.")


    return [results["bus"][1][7],
            results["bus"][1][8],
            results["branch"][1][13],
            results["branch"][1][14]
            ]

def left_powerflow(p_right,q_right,r,x):
    # Define system base MVA
    baseMVA = 1.0
    Zbase = 4761

    # Define buses
    # Bus format:
    #   [bus_i, type, Pd, Qd, Gs, Bs, area, Vm, Va, baseKV, zone, Vmax, Vmin]
    buses = np.array([
        [1, 3,        0,        0, 0, 0, 1, 1.0, 0, 69, 1, 1.05, 0.85],  # Slack Bus (69 kV, 0 deg)
        [2, 1,  p_right,  q_right, 0, 0, 1, 1.0, 0, 69, 1, 1.05, 0.85],  # Load Bus
    ])

    # Define generator (only the slack bus has a generator)
    # Generator format: [bus, Pg, Qg, Qmax, Qmin, Vg, mBase, status, Pmax, Pmin]
    generators = np.array([
        [1, 0, 0, 999, -999, 1.0, baseMVA, 1, 999, -999],  # Slack Bus Generator
    ])

    # Define branches (transmission line)
    # Branch format: [fbus, tbus, r, x, b, rateA, rateB, rateC, ratio, angle, status, angmin, angmax]
    branches = np.array([
        [1, 2, r/Zbase, x/Zbase, 0, 999, 999, 999, 0, 0, 1, -360, 360],  # Impedance of 0.1 + j0.2 Ohms
    ])

    # Define cost data (not used in power flow)
    gencost = np.array([
        [2, 0, 0, 3, 0, 0, 0],  # Dummy cost function
    ])

    # Construct PYPOWER case dictionary
    ppc = {
        "version": '2',
        "baseMVA": baseMVA,
        "bus": buses,
        "gen": generators,
        "branch": branches,
        "gencost": gencost
    }

    # Run power flow
    ppopt = ppoption(VERBOSE=0, OUT_ALL=0)  # This disables the console output
    results, success = runpf(ppc,ppopt)

    return [results["bus"][1][7],results["bus"][1][8]]

def right_powerflow(v_mag,v_angle,r,x ):
    # Define system base MVA
    baseMVA = 1.0
    Zbase = 4761

    # Define buses
    # Bus format:
    #   [bus_i, type, Pd, Qd, Gs, Bs, area, Vm, Va, baseKV, zone, Vmax, Vmin]
    buses = np.array([
        [1, 3,        0,        0, 0, 0, 1, v_mag, v_angle, 69, 1, 1.05, 0.85],  # Slack Bus
        [2, 1,  20.0,  15.0, 0, 0, 1, 1.0, 0, 69, 1, 1.05, 0.85],  # Load Bus
    ])

    # Define generator (only the slack bus has a generator)
    # Generator format: [bus, Pg, Qg, Qmax, Qmin, Vg, mBase, status, Pmax, Pmin]
    generators = np.array([
        [1, 0, 0, 999, -999, v_mag, baseMVA, 1, 999, -999],  # Slack Bus Generator
    ])

    # Define branches (transmission line)
    # Branch format: [fbus, tbus, r, x, b, rateA, rateB, rateC, ratio, angle, status, angmin, angmax]
    branches = np.array([
        [1, 2, r/Zbase, x/Zbase, 0, 999, 999, 999, 0, 0, 1, -360, 360],  # Impedance of 0.1 + j0.2 Ohms
    ])

    # Define cost data (not used in power flow)
    gencost = np.array([
        [2, 0, 0, 3, 0, 0, 0],  # Dummy cost function
    ])

    # Construct PYPOWER case dictionary
    ppc = {
        "version": '2',
        "baseMVA": baseMVA,
        "bus": buses,
        "gen": generators,
        "branch": branches,
        "gencost": gencost
    }

    # Run power flow
    ppopt = ppoption(VERBOSE=0, OUT_ALL=0)  # This disables the console output
    results, success = runpf(ppc,ppopt)

    return [results["branch"][0][13],results["branch"][0][14]]
    

if __name__ == "__main__":

    r=0.5
    x=2.0
    ratio=float(sys.argv[1])

    # Run power flow on full network
    [vm_full,va_full,p_full,q_full]=full_powerflow(r,x,ratio)

    # Test iterative process between two PF solvers
    # initialization
    
    #print("\nSplit Network Power Flow Co-simulation Iteration Test")
    [vc_mag,vc_angle] = left_powerflow(0,0,r*ratio,x*ratio)
    
    for i in range(int(sys.argv[2])):
        [pc,qc] = right_powerflow(vc_mag,vc_angle,r*(1.0-ratio),x*(1.0-ratio))

        print(f"\n\tIteration: {i+1}")
        print(f"\t\tCenter Bus Voltage: {vc_mag} ({vm_full}) pu, {vc_angle} ({va_full}) deg")
        print(f"\t\tCenter Bus P & Q flow: {pc} ({p_full}) MW , {qc} ({q_full}) MVAR")
        print(f"\n\t\t\tVoltage Magnitude Error%: {(vc_mag-vm_full)/vm_full*100}%")
        print(f"\t\t\tVoltage Phase Error%: {(vc_angle-va_full)/va_full*100}%")
        print(f"\t\t\tP flow Error% {(pc-p_full)/p_full*100}%")
        print(f"\t\t\tQ flow Error% {(qc-q_full)/q_full*100}%")

        [vc_mag,vc_angle] = left_powerflow(pc,qc,r*ratio,x*ratio)
        
