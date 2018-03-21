"""
Finding the minimum energy for a k-local Hamiltonian with QAOA.
"""
import pyquil.api as api
from grove.pyqaoa.qaoa import QAOA
from pyquil.paulis import PauliSum, PauliTerm
from scipy.optimize import minimize
import numpy as np

conn = api.QVMConnection()


def energy_value(h, generalized_J, sol):
    """
    Obtain energy of an Ising solution for a given generalized Ising problem (h,J).

    :param h: Biases of the individual qubits [List]
    :param generalized_J: Coupling coefficients of the k-local Hamiltonian [Dictionary]
    :param sol: Solution [List]
    :returns: Energy of the solution string.
    :rtype: Integer or float.

    """

    energy = 0
    for elm in generalized_J.keys():
        if any([elm[i]==elm[i+1] for i in range(0,len(elm)-1)]):
            raise TypeError("""Interaction term must connect different variables. This one contains a duplicate!""")
        else:
            multipliers = int(sol[elm[0]]) * int(sol[elm[1]])
            # if locality > 2 then add more multipliers
            for i in range(2,len(elm)):
                multpliers = multipliers*sol[elm[i]]
            energy += generalized_J[elm] * multipliers
    for i in range(len(h)):
        energy += h[i] * int(sol[i])
    return energy

def print_fun(x):
    print(x)

def ising_trans(x):
    # Transformation to Ising notation
    if x == 1:
        return -1
    else:
        return 1

def klocal_ising(h, generalized_J, num_steps=0, verbose=True, rand_seed=None, connection=None, samples=None,
          initial_beta=None, initial_gamma=None, minimizer_kwargs=None,
          vqe_option=None):
    """
    k-local generalized Ising set up method

    :param h: Biases of the individual qubits [List]
    :param generalized_J: Coupling coefficients of the k-local Hamiltonian [Dictionary]
    :param num_steps: (Optional.Default=2 * len(h)) Trotterization order for the
                  QAOA algorithm.
    :param verbose: (Optional.Default=True) Verbosity of the code.
    :param rand_seed: (Optional. Default=None) random seed when beta and
                      gamma angles are not provided.
    :param connection: (Optional) connection to the QVM. Default is None.
    :param samples: (Optional. Default=None) VQE option. Number of samples
                    (circuit preparation and measurement) to use in operator
                    averaging.
    :param initial_beta: (Optional. Default=None) Initial guess for beta
                         parameters.
    :param initial_gamma: (Optional. Default=None) Initial guess for gamma
                          parameters.
    :param minimizer_kwargs: (Optional. Default=None). Minimizer optional
                             arguments.  If None set to
                             {'method': 'Nelder-Mead',
                             'options': {'ftol': 1.0e-2, 'xtol': 1.0e-2,
                                        'disp': False}
    :param vqe_option: (Optional. Default=None). VQE optional
                             arguments.  If None set to
                       vqe_option = {'disp': print_fun, 'return_all': True,
                       'samples': samples}
    :return: most frequent solution string, energy of the solution string, circuit used to obtain result.
    :rtype: List, Integer or float, 'pyquil.quil.Program'.

    """
    
    # default number of steps
    if num_steps == 0:
        num_steps = 2 * len(h)
    
    # number of qubits
    n_nodes = len(h)
    #qubit_list = [0,1,2,5,6,7,8]
    qubit_list = []

    cost_operators = []
    driver_operators = []
    for key in generalized_J.keys():

        # first PauliTerm is multiplied with coefficient obtained from generalized_J
        if key[0] >= 3:
            print 'current key: ', key[0]
            qubit_index = key[0]+1 # increase qubit index by 1 to avoid dead qubit 3 on the QPU
            print 'new key: ', qubit_index
        else:
            qubit_index = key[0]

        if not qubit_index in qubit_list:
            qubit_list.append(qubit_index)

        pauli_product = PauliTerm("Z", qubit_index, generalized_J[key])

        # depending on the locality we multiply with additional Z PauliTerms
        for i in range(1,len(key)):
            if key[i] >= 3:
                print 'current key: ', key[i]
                qubit_index = key[i]+1 # increase qubit index by 1 to avoid dead qubit 3 on the QPU
                print 'new key: ', qubit_index
            else:
                qubit_index = key[i]
            if not qubit_index in qubit_list:
                qubit_list.append(qubit_index)
            pauli_product = pauli_product * PauliTerm("Z", qubit_index)
        # finally we cast the pauli_product into a PauliSum object and append it to the cost_operators
        cost_operators.append(PauliSum([pauli_product]))

    # sort the list of qubit indices
    qubit_list.sort()
    print 'generated qubit_list: ', qubit_list

    #for i in range(n_nodes):
    for i in qubit_list:
        if i >= 3:
            i -= 1
        print 'i in cost_operators:', i
        cost_operators.append(PauliSum([PauliTerm("Z", i, h[i])]))

    #for i in range(n_nodes):
    for i in qubit_list:
        if i >= 3:
            i -= 1
        print 'i in driver_operators:', i
        driver_operators.append(PauliSum([PauliTerm("X", i, -1.0)]))

    if connection is None:
        connection = con

    if minimizer_kwargs is None:
        minimizer_kwargs = {'method': 'Nelder-Mead',
                            'options': {'ftol': 1.0e-2, 'xtol': 1.0e-2,
                                        'disp': False}}

    if vqe_option is None:
        vqe_option = {'disp': print_fun, 'return_all': True,
                      'samples': samples}

    if not verbose:
        vqe_option['disp'] = None

    qaoa_inst = QAOA(connection, n_nodes, qubit_list, steps=num_steps, cost_ham=cost_operators,
                     ref_hamiltonian=driver_operators,
                     store_basis=True,
                     rand_seed=rand_seed,
                     init_betas=initial_beta,
                     init_gammas=initial_gamma,
                     minimizer=minimize,
                     minimizer_kwargs=minimizer_kwargs,
                     vqe_options=vqe_option)

    betas, gammas = qaoa_inst.get_angles()
    most_freq_string, sampling_results = qaoa_inst.get_string(betas, gammas)

    most_freq_string_ising = [ising_trans(it) for it in most_freq_string]
    #energy_ising = energy_value(h, generalized_J, most_freq_string_ising)
    energy_ising = 0

    param_prog = qaoa_inst.get_parameterized_program()
    circuit = param_prog(np.hstack((betas, gammas)))

    return most_freq_string_ising, energy_ising, circuit
