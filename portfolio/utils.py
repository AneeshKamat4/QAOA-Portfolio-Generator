import numpy as np
import time

# Importing Dwave Ocean SDK
import dimod
import neal
import numpy
from collections import Counter
from dwave.system import DWaveSampler, EmbeddingComposite
from dimod import BinaryQuadraticModel

# Importing standard Qiskit libraries
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit import transpile, Aer, IBMQ, execute, assemble
from qiskit.circuit import Parameter
from qiskit.visualization import *
from qiskit.providers.aer import QasmSimulator

def QAOA(M, P, budget, futSol, Pcon):

    # Loading your IBM Quantum account(s)
    provider = IBMQ.enable_account('a170cdf4d554be80145e3309747183530788ee352efd9c9527edc96219bb88efaac4a4ccbdd6bf9942018206a5be914bfee3ef38890879a2e71b903fb5336762')
    
    Cov=M
    currentprice=P
    totalcost = budget               # cost budget
    numvar=len(currentprice)         # Number of assets
    futuresoln = futSol #partial projection data: 2 -> no info available, 1 -> must pick, 0 -> must drop
    futuresolnpositions1=[index for (index, item) in enumerate(futuresoln) if item == 1]
    futuresolnpositions0=[index for (index, item) in enumerate(futuresoln) if item == 0]
    convergence=0
    Pconvergence = Pcon
    
    fieldcoeff=[1,1,0] #user-input constraint present or absent 
    delh=-0.1


    # Calculate input quadratic and linear biases for the system
    rcost=totalcost-sum([fieldcoeff[futuresoln[k]]*currentprice[k]*futuresoln[k] for k in range(numvar)]) #residual cost
    constraintmatrix=[[0 for j in range(numvar)] for i in range(numvar)] 
    for i in range(numvar):
        for j in range(numvar):
            if i==j:
                constraintmatrix[i][i]=(1-fieldcoeff[futuresoln[i]])*(currentprice[i]*currentprice[i]-2*currentprice[i]*rcost)
            else:
                constraintmatrix[i][j]=(1-fieldcoeff[futuresoln[i]])*(1-fieldcoeff[futuresoln[j]])*2*currentprice[i]*currentprice[j]

    # Calculate lagrange multiplier for adding the constraint            
    lagmultiplier=max(max(Cov))/max(max(constraintmatrix))            

    # Quadratic and linear biases and offset
    quadraticbiasmatrix=[[0 for j in range(numvar)] for i in range(numvar)]
    for i in range(numvar):
        for j in range(numvar):
            if j>i:     # input quadratic bias is upper diagonal
                quadraticbiasmatrix[i][j]=2*Cov[i][j]+lagmultiplier*constraintmatrix[i][j]


    linearbiasvector=[0 for i in range(numvar)]
    for i in range(numvar):
        linearbiasvector[i]=Cov[i][i]+lagmultiplier*constraintmatrix[i][i]

    
    #-------
    
    qbm = quadraticbiasmatrix
    nqubits = len(qbm) #size of circuit
    N = 100 #length of circuit

    maxJ = qbm[0][0]
    for m in range(len(qbm)):
        for n in range(len(qbm[0])):
            if (qbm[m][n] > maxJ):
                maxJ = qbm[m][n]
    print(maxJ)
    
    #-------
    
    iter = 1
    maxiter = 10*(nqubits**2) #to break the loop
    while convergence != 1:

        print('iteration:',iter)
        h = linearbiasvector #updating the field effect after feedback

        fieldweightingfactor=[abs(linearbiasvector[k]) for k in range(nqubits)]
        
        maxh = h[0]
        for m in range(len(h)):
            if h[m] > maxh:
                    maxh = h[m]

        maxJh = max(maxJ,maxh)

        del_t = 0.01/maxJh #choosing a discrete time-interval for tauterization
        if iter==1: print(del_t)

        q = QuantumRegister(nqubits,'q')
        
        qc_qaoa = QuantumCircuit(q)

        #initializing the qubits
        qc_0 = QuantumCircuit(nqubits)

        for i in range(nqubits):

            qc_0.h(i)

        qc_0.barrier() #visual segregation in the circuit diagram
        qc_0.barrier()

        qc_qaoa.append(qc_0, [i for i in range(nqubits)])

        for n in range(N): #for every time-step

            #problem quantum circuit
            qc_p = QuantumCircuit(nqubits)

            for i in range(nqubits):

                delta = (n*h[i]*del_t)/N
                qc_p.rz(2 * delta, i) #Z rotation by delta

                for j in range(i):

                    gamma = (n*qbm[j][i]*del_t)/N  #qbm is upper diagonal
                    qc_p.rzz(2 * gamma, j, i) #Coupled Z rotation by gamma
                    qc_p.barrier()

            #mixing quantum circuit
            qc_mix = QuantumCircuit(nqubits)

            for i in range(nqubits):

                beta = (1-(n/N))*del_t
                qc_mix.rx(2 * beta, i)

            qc_qaoa.append(qc_p, [i for i in range(nqubits)])
            qc_qaoa.append(qc_mix, [i for i in range(nqubits)])
            qc_qaoa.barrier()
            qc_qaoa.barrier()

        qc_qaoa.measure_all() #measuring every qubit onto a classical register

        qaoa_circ = qc_qaoa.decompose().decompose() #decomposing into basic gates
        # qaoa_circ.draw() 
        
        #sim = provider.get_backend('ibm_oslo') # Tell Qiskit which IBM backend to use
        sim = Aer.get_backend('aer_simulator')  # Tell Qiskit how to simulate our circuit
        #qobj = assemble(qaoa_circ)
        transpiled = transpile(qaoa_circ, backend = sim)
        job = sim.run(transpiled)
        result = job.result()
        counts = result.get_counts() #returns a dictionary of state and probabilistic weight
        
        # to return a group of the key-value pairs in the dictionary
        elements = counts.items()

        # Convert object to a list
        data = list(elements)

        # Convert list to an array
        array = np.array(data)

        # Convert string to int
        int_list = []
        for i in range(len(array[:,0])):
            int_row = [int(numeric_string) for numeric_string in array[i]]
            int_list.append(int_row[0])

        int_array = np.array(int_list)
        
        
        bit_array = np.zeros((len(array[:,0]), nqubits + 2),int)

        for i in range(len(array[:,0])):
            bit_array[i][0] = int_array[i]

            num = bit_array[i][0]
            
            # segregate bitstring into individual bits
            for j in range(1,nqubits + 1):
                bit_array[i][nqubits + 1 - j] = num % 10
                num /= 10
        
        # change data type to float for calculations
        bit_array = bit_array.astype(np.float)
        
        # calculating Hamiltonian of each solution
        for i in range(len(array[:,0])):
            for m in range(nqubits):
                bit_array[i][nqubits + 1] += h[m]*bit_array[i][-2-m]
                for n in range(m):
                    bit_array[i][nqubits + 1] += qbm[n][m]*bit_array[i][-2-m]*bit_array[i][-2-n]

        bit_array = np.concatenate([bit_array, np.zeros((len(array[:,0]),1),int)], axis=1)

        # create an array with probabilistic weights
        prob_list = []
        for i in range(len(array[:,0])):
            prob_row = [int(numeric_string) for numeric_string in array[i]]
            prob_list.append(prob_row[1])

        prob_array = np.array(prob_list)
        
        # sort in increasing order of energy
        for i in range(len(array[:,0])):
            bit_array[i][-1] = prob_array[i]

        bit_array = bit_array[bit_array[:, nqubits + 1].argsort()] #sorting by energy

        
        # count the unique solutions for the minimum energy
        degen = 0
        minEnergy = bit_array[0][-2]
        for i in range(len(array[:,0])):
            if bit_array[i][-2] == minEnergy:
                degen += 1

        uniq_sol = np.zeros((degen,nqubits+2),float)
        for i in range(degen):
            for j in range(nqubits):
                uniq_sol[i][j] = bit_array[i][-3-j]
            uniq_sol[i][-1] = bit_array[i][-1] # probabilistic weight
            uniq_sol[i][-2] = bit_array[i][-2] # energy

        # vector of probabilities in solution space
        probvector = np.zeros(4)
        for i in range(degen):
            probvector[i] = uniq_sol[i][-1]
        probvector /= sum(probvector)
        
        #array of solution bits without energy and probability 
        only_sol = np.delete(uniq_sol, [-1,-2], axis=1)

        print('Solution(s) are: ',only_sol)

        solutionlist = only_sol

        # Find marginal probability of solutions matching partial future projection vector.
        marginalprob=0
        numsolutions=len(solutionlist)
        for i in range(numsolutions):
            match=1
            for j in range(len(futuresolnpositions1)):
                if solutionlist[i][futuresolnpositions1[j]]==futuresoln[futuresolnpositions1[j]]:
                    match=match*1
                else:
                    match=match*0
            for j in range(len(futuresolnpositions0)):
                if solutionlist[i][futuresolnpositions0[j]]==futuresoln[futuresolnpositions0[j]]:
                    match=match*1
                else:
                    match=match*0        
            if match==1:
                    marginalprob=marginalprob+probvector[i]
        print('marginalprob: ', marginalprob)



        # Check for convergence or time-out
        if (marginalprob>=Pconvergence or iter==maxiter):
            convergence=1
            print('futuresoln: ',futuresoln)
        else:
            localfieldincrement=[0 for k in range(nqubits)]
            averagesol=[0 for i in range(nqubits)]
            sumsol=[0 for i in range(nqubits)]
            for i in range(degen):
                sumsol+=only_sol[i][:]
            averagesol=[(1/degen)*k for k in sumsol]

            localfieldincrement=[fieldcoeff[futuresoln[k]]*(futuresoln[k]-averagesol[k])*fieldweightingfactor[k]*delh for k in range(nqubits)]
            
            # Update local fields for the next iteration
            
            linearbiasvector += localfieldincrement
            print('field increment:',localfieldincrement)
            print("----")
            

        iter += 1
        
    # Final solution
    numfinalsolutions=0
    finalsolutionlist=list()
    finalprobvector=list()
    costlist=list()
    risklist=list()
    for i in range(numsolutions):
            match=1
            for j in range(len(futuresolnpositions1)):
                if solutionlist[i][futuresolnpositions1[j]]==futuresoln[futuresolnpositions1[j]]:
                    match=match*1
                else:
                    match=match*0
            for j in range(len(futuresolnpositions0)):
                if solutionlist[i][futuresolnpositions0[j]]==futuresoln[futuresolnpositions0[j]]:
                    match=match*1
                else:
                    match=match*0        
            if match==1:
                numfinalsolutions=numfinalsolutions+1
                finalsolutionlist.append(solutionlist[i])
                finalprobvector.append(probvector[i])
                costlist.append(sum([currentprice[j]*solutionlist[i][j] for j in range(numvar)]))
                risklist.append(solutionlist[i] @ Cov @ solutionlist[i])


    if numfinalsolutions==0:
        finalprobvector=probvector
        finalsolutionlist=solutionlist
        for i in range(len(solutionlist)):
            costlist.append(sum([currentprice[j]*solutionlist[i][j] for j in range(numvar)]))
            risklist.append(solutionlist[i] @ Cov @ solutionlist[i])

    totalfinalprob=sum(finalprobvector)
    finalprobvector=[prob/totalfinalprob for prob in finalprobvector]
    maxprob=max(finalprobvector)

    maxprobindex=[index for (index, item) in enumerate(finalprobvector) if item == maxprob]

    # chooses the most optimal solution
    optimalsolution=finalsolutionlist[maxprobindex[0]]
    optimalcost=costlist[maxprobindex[0]]
    optimalrisk=risklist[maxprobindex[0]]


    print('----FINAL SOLUTION-----')
    print('Final Probability:',maxprob)
    print('Final solution:',optimalsolution)
    print('Future solution:',futuresoln)
    print('Final Cost:',optimalcost)
    print('Final Risk:',optimalrisk)
    print('Number of Iterations:',iter)
    
    return(optimalsolution)


def optimal_allocation_anneal(Cov,currentprice,totalcost,futuresoln,Pconvergence):
    # Initialize local variables
    sampler = neal.sampler.SimulatedAnnealingSampler()
    numvar=len(currentprice)          # Number of assets
    futuresolnpositions1=[index for (index, item) in enumerate(futuresoln) if item == 1]
    futuresolnpositions0=[index for (index, item) in enumerate(futuresoln) if item == 0]
    convergence=0
    fieldcoeff=[1,1,0]
    delh=-0.1


    # Calculate input quadratic and linear biases for the BQM
    rcost=totalcost-sum([fieldcoeff[futuresoln[k]]*currentprice[k]*futuresoln[k] for k in range(numvar)]) #residual cost
    constraintmatrix=[[0 for j in range(numvar)] for i in range(numvar)] #symmetrix matrix
    for i in range(numvar):
        for j in range(numvar):
            if i==j:
                constraintmatrix[i][i]=(1-fieldcoeff[futuresoln[i]])*(currentprice[i]*currentprice[i]-2*currentprice[i]*rcost)
            else:
                constraintmatrix[i][j]=(1-fieldcoeff[futuresoln[i]])*(1-fieldcoeff[futuresoln[j]])*2*currentprice[i]*currentprice[j]

    # Calculate lagrange multiplier for adding the constraint            
    lagmultiplier=max(max(Cov))/max(max(constraintmatrix))            

    # Quadratic and linear biases and offset
    quadraticbiasmatrix=[[0 for j in range(numvar)] for i in range(numvar)]
    for i in range(numvar):
        for j in range(numvar):
            if j>i:                                               # input quadratic bias is upper diagonal
                quadraticbiasmatrix[i][j]=2*Cov[i][j]+lagmultiplier*constraintmatrix[i][j]

    linearbiasvector=[0 for i in range(numvar)]
    for i in range(numvar):
        linearbiasvector[i]=Cov[i][i]+lagmultiplier*constraintmatrix[i][i]

    costoffset=lagmultiplier*rcost*rcost
    print('Initial field:',linearbiasvector)

    # create BQM Object
    bqm1=dimod.BinaryQuadraticModel('BINARY')
    bqm1.add_quadratic_from_dense(quadraticbiasmatrix)
    bqm1.add_linear_from_array(linearbiasvector)
    bqm1.offset+=costoffset
    fieldweightingfactor=[abs(bqm1.get_linear(k)) for k in range(numvar)]

    maxiter=10*numvar**2    # Maximum iterations of the feedback loop based on problem size.
    iter=1
    while convergence!=1:

        # Sample from BQM
        sampleset1=sampler.sample(bqm1, seed=1234, num_reads=100, num_sweeps=1000, beta_schedule_type='geometric',sorted_by='energy')



        x=sampleset1.record.sample
        y=sampleset1.record.energy
        miny=min(y)
        sortedy=sorted(y)
        z=list(range(y.size))#creates a list of indices.
        energyindexpair=[k for _, k in sorted(list(zip(y, z)))]# sorts (energy, index) pair based on energies and outputs ordered indices
        sortedsample=[x[k] for k in energyindexpair] # creates a list of bitstrings sorted in increasing order of energy.

        # Find the number of lowest energy bitstrings
        lowestenlistsize=0
        for i in range(y.size):
            if sortedy[i]==miny:
                lowestenlistsize=i

        # Store the solutions (only the lowest energy bitstrings)
        lowestenergysortedsample=sortedsample[0:lowestenlistsize+1]

        # Extract unique solutions and their frequency or probability
        strsample=map(str,lowestenergysortedsample)
        strsamplelist=list(map(str,lowestenergysortedsample))
        struniqsols=list(set(strsample)) # creates a unique set from the list of lowest energy bitstrings
        count=Counter(strsamplelist)
        totalcount=sum(count.values())
        solutionlist=list()
        for i in range(len(struniqsols)):
            solutionlist.append(numpy.frombuffer(struniqsols[i].replace('[','').replace(']','').replace(" ",'').encode(), numpy.int8) - 48)
        probvector=[frequency/totalcount for frequency in count.values()]
        print('iteration:',iter)
        print(probvector)
        print(solutionlist)

        # Find marginal probability of solutions matching partial future projection vector.
        marginalprob=0
        numsolutions=len(solutionlist)           # number of unique lowest energy solutions.
        for i in range(numsolutions):
            match=1
            for j in range(len(futuresolnpositions1)):
                if solutionlist[i][futuresolnpositions1[j]]==futuresoln[futuresolnpositions1[j]]:
                    match=match*1
                else:
                    match=match*0
            for j in range(len(futuresolnpositions0)):
                if solutionlist[i][futuresolnpositions0[j]]==futuresoln[futuresolnpositions0[j]]:
                    match=match*1
                else:
                    match=match*0        
            if match==1:
                marginalprob=marginalprob+probvector[i]

        # Check for convergence
        if (marginalprob>=Pconvergence or iter==maxiter):
            convergence=1
        else:
            localfieldincrement=[0 for k in range(numvar)]
            averagesol=[0 for i in range(numvar)]
            sumsol=[0 for i in range(numvar)]
            for i in range(numsolutions):
                #sumsol=[sum(k) for k in zip(sumsol,solutionlist[i])]
                sumsol+=solutionlist[i]
            averagesol=[(1/numsolutions)*k for k in sumsol]
            localfieldincrement=[fieldcoeff[futuresoln[k]]*(futuresoln[k]-averagesol[k])*fieldweightingfactor[k]*delh for k in range(numvar)]
            # Update local fields in the BQM for the next iteration
            bqm1.add_linear_from_array(localfieldincrement)
            print('field increment:',localfieldincrement)
            print("----")
        iter=iter+1

    # Final solution
    numfinalsolutions=0         # Number of unique solutions that satisfy partial future projection
    finalsolutionlist=list()
    finalprobvector=list()
    costlist=list()
    risklist=list()
    for i in range(numsolutions):
            match=1
            for j in range(len(futuresolnpositions1)):
                if solutionlist[i][futuresolnpositions1[j]]==futuresoln[futuresolnpositions1[j]]:
                    match=match*1
                else:
                    match=match*0
            for j in range(len(futuresolnpositions0)):
                if solutionlist[i][futuresolnpositions0[j]]==futuresoln[futuresolnpositions0[j]]:
                    match=match*1
                else:
                    match=match*0        
            if match==1:
                numfinalsolutions+=1     # Count unique solutions that satisfy partial future prediction
                finalsolutionlist.append(solutionlist[i])
                finalprobvector.append(probvector[i])
                costlist.append(sum([currentprice[j]*solutionlist[i][j] for j in range(numvar)]))
                risklist.append(solutionlist[i] @ Cov @ solutionlist[i])


    if numfinalsolutions==0:          # If no solutions satisfy partial future prediction return best current solution
        finalprobvector=probvector
        finalsolutionlist=solutionlist
        for i in range(len(solutionlist)):
            costlist.append(sum([currentprice[j]*solutionlist[i][j] for j in range(numvar)]))
            risklist.append(solutionlist[i] @ Cov @ solutionlist[i])

    totalfinalprob=sum(finalprobvector)
    finalprobvector=[prob/totalfinalprob for prob in finalprobvector]
    maxprob=max(finalprobvector)
    maxprobindex=[index for (index, item) in enumerate(finalprobvector) if item == maxprob]
    optimalsolution=finalsolutionlist[maxprobindex[0]]
    optimalcost=costlist[maxprobindex[0]]
    optimalrisk=risklist[maxprobindex[0]]

    return(optimalsolution)