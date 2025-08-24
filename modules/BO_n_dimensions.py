from bayes_opt import BayesianOptimization
from bayes_opt.logger import JSONLogger
from bayes_opt.event import Events
from bayes_opt.util import load_logs
from bayes_opt import UtilityFunction
import numpy as np
import matplotlib.pyplot as plt

import os

from sklearn.decomposition import PCA
from sklearn.cross_decomposition import PLSRegression
from scipy.spatial import Delaunay


## TO INSTALL LIBRARY
##    
## pip install bayesian-optimization==1.4.1
## pip install matplotlib


def black_box_function(x1,x2,x3,x4):
    """Function with unknown internals we wish to maximize.

    This is just serving as an example, for all intents and
    purposes think of the internals of this function, i.e.: the process
    which generates its output values, as unknown.
    """
    value=60-((x1*x2-1)**2-(x3+0.5)**2+(x4-1)**2)
    if value<0: value=0
    return value

def plot_target_estimation(pbounds, optimizer, next_point, cycle): 
    # Setup the grid to plot on
    TotalPoints=1000
    num_points=round(TotalPoints**(1/len(pbounds)))
    if num_points<2: num_points=2
    LinSpaces=[]
    for element in pbounds:
        LinSpaces.append(np.linspace(pbounds[element][0]-0.1, pbounds[element][1]+0.1, num_points))
    tmp=[]
    for data in range(num_points**len(LinSpaces)):
        line=[]
        for i,dimension in enumerate(LinSpaces):
            line.append(dimension[(data // (num_points)**i) % num_points])
        tmp.append(line)

    x_n=np.array(tmp)

    independent_variables=len(pbounds)
    calculated_points=num_points**independent_variables
    total_dimensions=independent_variables+1
    
    Z_est = optimizer._gp.predict(x_n)
 
    # Extract & unpack the optimization results
    max_ = optimizer.max
    res = optimizer.res
    x_=[]
    #below the tried positions
    for i in range(independent_variables):
        x_.append(np.array([r["params"]['x'+str(i+1)] for r in res]))
    explored_points=[]
    for i in range(len(x_[0])):
        line=[]
        for j in range(independent_variables):
            line.append(x_[j][i])
        #line=[a, x_[i],x3_[i],x4_[i]]
        Z = optimizer._gp.predict([line])
        line.append(Z[0]*1000)
        explored_points.append(line)
    

    # Prepare array for PCA
    count=0
    x_n_Z=[]
    for element in x_n:
        line=[]
        for el in element:
            line.append(el)
        line.append(Z_est[count]*1000)
        x_n_Z.append(line)
        count+=1
   
    graphtype=2

    if graphtype==0:
        print("no data reduction needed")
    elif graphtype>=1: #1=2D reduction, 2=3D reduction
        if graphtype==1:
            components_PCA=2
        else:
            components_PCA=3
        pca = PCA(n_components=components_PCA)
        reduced_data = pca.fit_transform(np.array(x_n_Z).reshape(calculated_points,total_dimensions))
        components = pca.components_
        fig = plt.figure()
        if components_PCA==3:
            ax = fig.add_subplot(111, projection='3d')
            ax.scatter(reduced_data[:,0],reduced_data[:,1],reduced_data[:,2], c=Z_est,cmap='viridis')
            if len(explored_points)>0:
                # Project the explored points into the PCA space
                projected_points = pca.transform(explored_points)
                ax.scatter(projected_points[:, 0], projected_points[:, 1], projected_points[:, 2], c='red', s=100, label='Projected Points')
        else:
            ax = fig.add_subplot(111)
            ax.scatter(reduced_data[:, 0], reduced_data[:, 1],c=Z_est,cmap='viridis')
            if len(explored_points)>0:
                # Project the explored points into the PCA space
                projected_points = pca.transform(explored_points)
                ax.scatter(projected_points[:, 0], projected_points[:, 1], c='red', s=100, label='Projected Points')

        comp_norm=[]
        for component in components:
            norm=""
            abs_sum=0
            for n,element in enumerate(component):
                if n<len(component)-1:
                    abs_sum+=abs(element)
            for n,element in enumerate(component):
                if n<len(component)-1:
                    if not(element==0):
                        element_norm=element/abs_sum*100
                    else:
                        element_norm=0
                    norm+=f"{element_norm:.1f}"+" "
            comp_norm.append(norm)
        print(comp_norm)
                
        ax.set_xlabel('PC1= '+' '.join(comp_norm[0]))
        ax.set_ylabel('PC2= '+' '.join(comp_norm[1]))
        if components_PCA==3:
            ax.set_zlabel('PC3= '+' '.join(comp_norm[2]))
        print("Composition of Principal Components:")
        np.set_printoptions(formatter={'float': lambda x: f"{x:.2e}"})
        print(components)
      

    return fig
  

utility = UtilityFunction(kind="ucb", kappa=2.5, xi=0.0)
figures=[]


# Bounded region of parameter space
start=[-2,-2,-2,-2]
stop=[8,8,8,8]
pbounds={'x'+str(i+1): (start[i],stop[i]) for i in range(len(stop))}
print(pbounds)
MaxIterations=20

optimizer = BayesianOptimization(f=None, pbounds=pbounds, verbose=2, random_state=1)

#below how to load and continue a previous optimization
file_path = './logs.log.json'

if os.path.exists(file_path): #actually it is not finding anything
    print("Log file present")
    ask=input("Do you want to load the previous log file? [y/n] ").upper()
    if ask=="Y":
        load_logs(optimizer, logs=["./logs.log.json"])
        print("New optimizer is now aware of {} points.".format(len(optimizer.space)))

logger = JSONLogger(path="./logs.log")
optimizer.subscribe(Events.OPTIMIZATION_STEP, logger)


for cycle in range(MaxIterations):
     next_point = optimizer.suggest(utility)
     print("-"*30,"Cycle ",str(cycle+1),"/",str(MaxIterations),"-"*30)
     print("Next point to probe is:", next_point)
     figure=plot_target_estimation(pbounds, optimizer, next_point, cycle)
     #figure.savefig("Cycle4D "+str(cycle+1))     
     figures.append(figure)
     #ask=input('Press ENTER to perform the measurement')
     target = black_box_function(**next_point)
     optimizer.register(params=next_point, target=target)


for figure in figures:  figure.show() #show all the figures

print('\nMAXIMUM:',optimizer.max)

