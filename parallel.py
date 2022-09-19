from multiprocessing import Process, cpu_count
import subprocess

totalEvents  = int(1e6)
eventsPerJob = 125000
N = 8 #number of parallel jobs


#multiprocessing.cpu_count()
#   i: job number
def MC(i):
    command = "g4bl G4V7M_piE5.g4bl profileFile=./profiles/CMBL2021_05_Collimator_profile_p%d.dat  DOprofile=1 currentsFile=CurrentsCMBL2021.txt histoFile=./scores/CMBL2021_05_Collimator_p%d first=%d last=%d divertOUT=1 outFile=out/CMBL2021_05_Collimator_p%d.out "  %(i, i, i*eventsPerJob + 1, (i+1)*eventsPerJob, i)
        
    subprocess.call(command, shell =True)

# Create node-local processes
shared_processes = []
#for i in range(cpu_count()):
subprocess.call("(rm duration.txt && date >> duration.txt) || date >> duration.txt", shell=True)

for j in range(int(totalEvents/eventsPerJob/N)): # job group
    for i in range(N): #job index
        p = Process(target= MC, args = (i + j*N,))
        shared_processes.append(p)

    # Start processes
    for sp in shared_processes:
        sp.start()

    # Wait for all processes to finish
    for sp in shared_processes:
        sp.join()
    
    shared_processes=[]

subprocess.call("date >> duration.txt", shell=True)

