import pandas as pd
import numpy as np
import GPy
from scipy import stats
from scipy import optimize
import matplotlib.pyplot as plt
from sklearn import metrics
from tqdm import tqdm
from functools import partial
from scipy.io import loadmat
import scipy.io
import os
clear = lambda: os.system('cls')  # On Windows System
clear()
plt.close('all')

# filesubjectnum = open("/home/fzahedi/Fatemeh/Adaptive/AP_BO_newsetup/config/Config.txt","r")
# Subjectnum = filesubjectnum.readlines()[3][:-1]
# print(Subjectnum)
# filesubjectnum.close()
Subjectnum = 5

obj = loadmat('/home/fzahedi/Fatemeh/Adaptive/AP_BO_newsetup/DATA/Subject'+ str(Subjectnum) + '/Obfunc')
n1final = obj['Objectivefunc'].shape[1]
#print(annots.items())
#print(annots['Weight'].shape[0])
#print(annots['maxmin'].shape)
#print(annots.keys())
#print(annots.values())
# print(annots['Weight'])
# print(annots['Weight'][0][1])

def select_hyperparams_random(param_ranges, random = True, trialnum = 1, direction = 1):
    """
    Select hyperparameters at random.
    
    Parameters
    ----------
    param_ranges : dict
        Named parameter ranges.

        Example:
        
        {
            'foo': {
                'range': [1, 10],
                'type': 'float'
            }
            'bar': {
                'range': [10, 1000],
                'type': 'int'
            }
        }

    Returns
    -------
    selection : dict
        Randomly selected hyperparameters within given boundaries.
        
        Example:
        {'foo': 4.213, 'bar': 935}

    """
    selection = {}
    if direction == 2:
        j = 3
    else:
        j = 1
    if random:
        for k in param_ranges:
            val = np.random.choice(
                np.linspace(*param_ranges[k]['range'], num=100)
            )

            dtype = param_ranges[k]['type']
            if dtype is 'int':
                val = int(val)
            selection[k] = val
    else: 
        """
        This part is for those training trials that we want to be specific values
        instead of being random, number of trials and number of values will change 
        based on the function and application 

        """
        for trialcounter in range(0, n1):
            if trialnum == trialcounter:
                for k in param_ranges:
                    val = obj['Objectivefunc'][j][trialcounter]
                    j = j + 1
                    dtype = param_ranges[k]['type']
                    if dtype is 'int':
                        val = int(val)
                    selection[k] = val
        
    return selection


# param_ranges = {
#     'foo': {
#         'range': [1, 10],
#         'type': 'float'
#     },
#     'bar': {
#         'range': [10, 1000],
#         'type': 'int'
#     }
# }

#print(select_hyperparams_random(param_ranges, random = False))

#print(param_ranges.keys())



#----------------------------------------------------------------------

def expected_improvement(f, y_current, x_proposed):
    """
    Return E(max(f_proposed - f_current), 0)

    Parameters
    ----------

    f : GP predict function
    y_current : float
        Current best evaluation f(x+)
    x_proposed : np.array
        Proposal parameters. Shape: (1, 1)

    Returns
    -------
    expected_improvement : float
        E(max(f_proposed - f_current), 0)
    """
    si = 0.25
    mu, var = f(x_proposed)
    std = var ** 0.5
    delta = mu - y_current - si

    # x / inf = 0
    std[std == 0] = np.inf
    z = delta / std
    unit_norm = stats.norm()
    return delta * unit_norm.cdf(z) + std * unit_norm.pdf(z)


class BayesOpt:
    def __init__(
        self, param_ranges, f, random_trials=5, optimization_trials=20, kernel=None, train_type=None, direction=1
    ):
        """
        Parameters
        ----------

        param_ranges : dict
        f : function
            black box function to evaluate
        random_trials : int
            Number of random trials to run before optimization starts
        optimization_trials : int
            Number of optimization trials to run.
            Together with the random_trials this is the total budget
        kernel: GPy.kern.src.kern.Kern
            GPy kernel for the Gaussian Process.
            If None given, RBF kernel is used
        """
        self.param_ranges = param_ranges
        self.f = f
        self.random_trials = random_trials
        self.optimization_trials = optimization_trials
        self.n_trials = random_trials + optimization_trials
        self.direction = direction
        self.x = np.zeros((self.n_trials, len(param_ranges)))
        self.y = np.zeros((self.n_trials, 1))

        if train_type is None:
            self.train_type = True
        else:
            self.train_type = train_type

        if kernel is None:
            self.kernel = GPy.kern.RBF(
                #input_dim=self.x.shape[1], ARD=True
                input_dim=self.x.shape[1], variance=1, lengthscale=2.5
            ) 
        else:
            self.kernel = kernel
        self.gp = None
        self.bounds = np.array([pr["range"] for pr in param_ranges.values()])

    @property
    def best_params(self):
        """
        Select best parameters.

        Returns
        -------
        best_parameters : dict
        """
        
        return self._prepare_kwargs(self.x[self.y.argmax()])

    def fit(self):
        self._random_search()
        self._bayesian_search()

    def _random_search(self):
        """
        Run the random trials budget
        """
        print(f"Starting {self.random_trials} random trials...")
        for i in tqdm(range(self.random_trials)):
            if self.train_type is True:
                hp = select_hyperparams_random(self.param_ranges)
            else:
                hp = select_hyperparams_random(self.param_ranges, False, i, self.direction) # For having specific training data
            self.x[i] = np.array(list(hp.values()))
            self.y[i] = self.f(hp)

    def _bayesian_search(self):
        """
        Run the Bayesian Optimization budget
        """
        print(f"Starting {self.optimization_trials} optimization trials...")
        for i in tqdm(
            range(self.random_trials, self.random_trials + self.optimization_trials)
        ):
            self.x[i], self.y[i] = self._single_iter()

    def _single_iter(self, x=None):
        """
        Fit a GP and retrieve and evaluate a new
        parameter proposal.

        Returns
        -------
        out : tuple[np.array[flt], np.array[flt]]
            (x, f(x))

        """
        self._fit_gp()
        if x is None:
            x = self._new_proposal()
        y = self.f(self._prepare_kwargs(x))
        return x, y

    def _fit_gp(self, noise_var=0.001):
        """
        Fit a GP on the currently observed data points.

        Parameters
        ----------
        noise_var : flt
            GPY argmument noise_var
        """
        mask = self.x.sum(axis=1) != 0
        self.gp = GPy.models.GPRegression(
            self.x[mask],
            self.y[mask],
            normalizer=True,
            kernel=self.kernel,
            noise_var=noise_var,
        )
        #self.gp.Gaussian_noise.variance.constrain_fixed()
        self.gp.optimize()
        # print(self.gp.log_likelihood())
        print(self.gp)

    def _new_proposal(self, n=50):
        """
        Get a new parameter proposal by maximizing
        the acquisition function.

        Parameters
        ----------
        n : int
            Number of retries.
            Each new retry the optimization is
            started in another parameter location.
            This improves the chance of finding a global optimum.

        Returns
        -------
        proposal : dict
            Example:
           {'foo': 4.213, 'bar': 935}
        """

        def f(x):
            return -expected_improvement(
                f=self.gp.predict, y_current=self.y.max(), x_proposed=x[None, :]
            )

        x0 = np.random.uniform(
            low=self.bounds[:, 0], high=self.bounds[:, 1], size=(n, self.x.shape[1])
        )
        proposal = None
        best_ei = np.inf
        for x0_ in x0:
            res = optimize.minimize(f, x0_, bounds=self.bounds)
            if res.success and res.fun < best_ei:
                best_ei = res.fun
                proposal = res.x
            if np.isnan(res.fun):
                raise ValueError("NaN within bounds")
        #print(proposal)
        return proposal

    def _prepare_kwargs(self, x):
        """
        Create a dictionary with named parameters
        and the proper python types.

        Parameters
        ----------
        x : np.array
            Example:
            [4.213, 935.03]

        Returns
        -------
        hyperparameters : dict

            Example:
            {'foo': 4.213, 'bar': 935}
        """
        # create hyper parameter dict
        hp = dict(zip(self.param_ranges.keys(), x))
        # cast values
        for k in self.param_ranges:
            if self.param_ranges[k]["type"] == "int":
                hp[k] = int(hp[k])
            elif self.param_ranges[k]["type"] == "float":
                hp[k] = float(hp[k])
            else:
                raise ValueError("Parameter type not known")
        return hp

#-----------------------------------------------------------------------------

# AP lowerbound study

#x = np.linspace(-50, -5)
#x = np.arange(-50, -5, 0.01).reshape(-1, 1)
blbap = np.arange(-55, -1, 1)#.reshape(-1, 1)
bubap = np.arange(5, 105, 1)#.reshape(-1, 1)
gx, gy = np.meshgrid(blbap, bubap)

X_2D = np.c_[gx.ravel(), gy.ravel()]
#print(obj['Objectivefunc'][1])

blbml = np.arange(-33, -1, 1)
bubml = np.arange(5, 105, 1)
gxml, gyml = np.meshgrid(blbml,bubml)

X_2Dml = np.c_[gxml.ravel(), gyml.ravel()]


def func(blbap, bubap):
    #new objective function
    index = np.argwhere((np.abs(obj['Objectivefunc'][1] -blbap)<=2.5) & (np.abs(obj['Objectivefunc'][2] -bubap)<=0.5))
    print(index)
    if not len(index):
        #lastindex = 
        out = -10
    else:
        if len(index)>1:
            #indindex = np.argmin(np.abs(obj['Objectivefunc'][1][index] -x))
            indindex = np.argmin(np.sqrt((obj['Objectivefunc'][1][index] -blbap)**2 + (obj['Objectivefunc'][2][index] -bubap)**2))
            lastindex = index[indindex]
        else:
            lastindex = index[-1]
        out = obj['Objectivefunc'][0][lastindex]
    print(out)
    return out

# second function
def func2(blbml, bubml):
    #new objective function
    index2 = np.argwhere((np.abs(obj['Objectivefunc'][3] -blbml)<=0.5)& (np.abs(obj['Objectivefunc'][4] -bubml)<=0.5))
    print(index2)
    if not len(index2):
        #lastindex = 
        out2 = -10
    else:
        if len(index2)>1:
            #indindex = np.argmin(np.abs(obj['Objectivefunc'][1][index] -x))
            indindex2 = np.argmin(np.sqrt((obj['Objectivefunc'][3][index2] -blbml)**2+ obj['Objectivefunc'][4][index2] -bubml)**2)
            lastindex2 = index2[indindex2]
        else:
            lastindex2 = index2[-1]
        out2 = obj['Objectivefunc'][9][lastindex2]
    print(out2)
    return out2


def evaluate_params(hyperparams):
    return func(**hyperparams)

def evaluate_params2(hyperparams):
    return func2(**hyperparams)

param_ranges = {
    'blbap': {
        'range': [-50, -5],
        'type': 'float'
    },
    'bubap': {
        'range': [10, 100],
        'type': 'float'
    }
}
param_ranges2 = {
    'blbml': {
        'range': [-30, -5],
        'type': 'float'
    },
    'bubml': {
        'range': [10, 100],
        'type': 'float'
    }
}
#----------------------------------------------------------------------------------------------------------
#n1 = 5

n2 = 1
bigmu = np.zeros(shape=(n1final,gx.shape[0],gx.shape[1]))
bigquants = np.zeros(shape=(n1final,gx.shape[0],gx.shape[1]))
bigei = np.zeros(shape=(n1final,gx.shape[0],gx.shape[1]))

bigmuml = np.zeros(shape=(n1final,gxml.shape[0],gxml.shape[1]))
bigquantsml = np.zeros(shape=(n1final,gxml.shape[0],gxml.shape[1]))
bigeiml = np.zeros(shape=(n1final,gxml.shape[0],gxml.shape[1]))
print(bigmu.shape)
for n1 in range(13,n1final+1):


    ## AP
    bo = BayesOpt(param_ranges, evaluate_params, random_trials=n1, optimization_trials=n2, train_type=False)

    bo.fit()
    new_proposal = bo._new_proposal()

    mu, var = bo.gp.predict(X_2D)
    quants = bo.gp.predict_quantiles(X_2D, quantiles=(10, 90))

    ei = expected_improvement(
            f=bo.gp.predict, y_current=bo.y.max(), x_proposed=X_2D
        )

    ei_max = ei.max()
    ei_min = ei.min()

    plt.figure()
    plt.contourf(gx, gy, mu.reshape(gx.shape), cmap='coolwarm')
    plt.xlabel('$b_{lb}$')
    plt.ylabel('$b_{ub}$')
    plt.title(f"Iteration {n1}")
    plt.scatter(bo.x[:-1,0],bo.x[:-1,1], c='k', marker='.')
    plt.scatter(bo.best_params['blbap'],bo.best_params['bubap'], c='yellow', marker='*')

    bigmu[:][:][n1-1] = mu.reshape(gx.shape)
    bigquants[:][:][n1-1] = quants[0].reshape(gx.shape)
    bigei[:][:][n1-1] = ei.reshape(gx.shape)

    ## ML
    bo2 = BayesOpt(param_ranges2, evaluate_params2, random_trials=n1, optimization_trials=n2, train_type=False, direction=2)

    bo2.fit()
    new_proposal2 = bo2._new_proposal()

    mu2, var2 = bo2.gp.predict(X_2Dml)
    quants2 = bo2.gp.predict_quantiles(X_2Dml, quantiles=(10, 90))

    ei2 = expected_improvement(
            f=bo2.gp.predict, y_current=bo2.y.max(), x_proposed=X_2Dml
        )

    ei_max2 = ei2.max()
    ei_min2 = ei2.min()

    plt.figure()
    plt.contourf(gxml, gyml, mu2.reshape(gxml.shape), cmap='coolwarm')
    plt.xlabel('$b_{lb}$')
    plt.ylabel('$b_{ub}$')
    plt.title(f"Iteration {n1}")
    plt.scatter(bo2.x[:-1,0],bo2.x[:-1,1], c='k', marker='.')
    plt.scatter(bo2.best_params['blbml'],bo2.best_params['bubml'], c='yellow', marker='*')

    bigmuml[:][:][n1-1] = mu2.reshape(gxml.shape)
    bigquantsml[:][:][n1-1] = quants2[0].reshape(gxml.shape)
    bigeiml[:][:][n1-1] = ei2.reshape(gxml.shape)



# parameterfile = open("/home/fzahedi/Fatemeh/Adaptive/AP_BO_newsetup/Underwork"+"/parameters.txt","w")
# #parameterfile.write(str(round(new_proposal[0],2)))
# param = [str(round(new_proposal[0],2))+"\n", str(round(new_proposal[1],2))+"\n"]
# parameterfile.writelines(param)
# parameterfile.close()

#Base_dir = os.path.dirname(os.path.realpath(__file__))
# parameterlocation = open(str(Base_dir) + '/DATA/parameterlocation.txt', "w")
# parameterlocation.write('/home/fzahedi/Fatemeh/Adaptive/AP_BO_newsetup/DATA/Subject'+ str(Subjectnum))
# parameterlocation.close()

# parameterfile = open("/home/fzahedi/Fatemeh/Adaptive/AP_BO_newsetup/DATA/Subject"+ str(Subjectnum)+"/parameters.txt","w")
# param = [str(round(new_proposal[0],2))+"\n", str(round(new_proposal[1],2))+"\n"]
# parameterfile.writelines(param)
# parameterfile.close()


#print(gx.shape)
## AP
scipy.io.savemat('/home/fzahedi/Fatemeh/Adaptive/AP_BO_newsetup/DATA/Subject'+ str(Subjectnum) +'/plots/bigmu.mat', {'bigmu':bigmu})
scipy.io.savemat('/home/fzahedi/Fatemeh/Adaptive/AP_BO_newsetup/DATA/Subject'+ str(Subjectnum) +'/plots/bigquants.mat', {'bigquants':bigquants})
scipy.io.savemat('/home/fzahedi/Fatemeh/Adaptive/AP_BO_newsetup/DATA/Subject'+ str(Subjectnum) +'/plots/bigei.mat', {'bigei':bigei})
scipy.io.savemat('/home/fzahedi/Fatemeh/Adaptive/AP_BO_newsetup/DATA/Subject'+ str(Subjectnum) +'/plots/gx.mat', {'gx':gx})
scipy.io.savemat('/home/fzahedi/Fatemeh/Adaptive/AP_BO_newsetup/DATA/Subject'+ str(Subjectnum) +'/plots/gy.mat', {'gy':gy})

## ML
scipy.io.savemat('/home/fzahedi/Fatemeh/Adaptive/AP_BO_newsetup/DATA/Subject'+ str(Subjectnum) +'/plots/bigmuml.mat', {'bigmuml':bigmuml})
scipy.io.savemat('/home/fzahedi/Fatemeh/Adaptive/AP_BO_newsetup/DATA/Subject'+ str(Subjectnum) +'/plots/bigquantsml.mat', {'bigquantsml':bigquantsml})
scipy.io.savemat('/home/fzahedi/Fatemeh/Adaptive/AP_BO_newsetup/DATA/Subject'+ str(Subjectnum) +'/plots/bigeiml.mat', {'bigeiml':bigeiml})
scipy.io.savemat('/home/fzahedi/Fatemeh/Adaptive/AP_BO_newsetup/DATA/Subject'+ str(Subjectnum) +'/plots/gxml.mat', {'gxml':gxml})
scipy.io.savemat('/home/fzahedi/Fatemeh/Adaptive/AP_BO_newsetup/DATA/Subject'+ str(Subjectnum) +'/plots/gyml.mat', {'gyml':gyml})



#plt.show()

