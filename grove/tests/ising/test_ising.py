from grove.ising.ising_qaoa import ising
from grove.ising.ising_qaoa import energy_value, unembed_solution, ising_trans
import numpy as np
from mock import patch


def test_energy_value():
    J = {(0, 1): 2.3}
    h = [-2.4, 5.2]
    sol = [1, -1]
    ener_ising = energy_value(h, J, sol)

    assert(np.isclose(ener_ising, -9.9))

def test_ising_trans():
    sol = [0, 1, 1, 0]
    ising_sol = [ising_trans(bit) for bit in sol]
    assert ising_sol == [1, -1, -1, 1]

def test_unembed_solution():
    sol = [0, 1, 1, 1]
    inv_embedding = {20: 0, 13: 2, 23: 1, 15: 3}
    assert unembed_solution(sol, inv_embedding) == [1, 1, 0, 1]

    sol = [0, 1, 1, 1, 0]
    inv_embedding = {9: 0, 7: 2, 3: 1, 17: 3, 5: 4}
    assert unembed_solution(sol, inv_embedding) == [1, 0, 1, 0, 1]

def test_ising_mock():
    with patch("pyquil.api.QVMConnection") as cxn:
        # Mock the response
        cxn.run_and_measure.return_value = [[1, 1, 0, 1]]
        cxn.expectation.return_value = [-0.4893891813015294, 0.8876822987380573, -0.4893891813015292, -0.9333372094534063, -0.9859245403423198, 0.9333372094534065]

    J = {(0, 1): -2, (2, 3): 3}
    h = [1, 1, -1, 1]
    p = 1
    most_freq_string_ising, energy_ising, circuit = ising(h, J, num_steps=p, vqe_option=None, connection=cxn)

    assert most_freq_string_ising == [-1, -1, 1, -1]
    assert energy_ising == -9

    with patch("pyquil.api.QVMConnection") as cxn:
        # Mock the response
        cxn.run_and_measure.return_value = [[1, 0, 1, 0]]
        cxn.expectation.return_value = [0, 0, 0, 0] # dummy

    # checkerboard
    J = {(0, 1): 1, (0, 2): 1, (1, 3): 1, (2, 3): 1}
    h = {}
    p = 1
    most_freq_string_ising, energy_ising, circuit = ising(h, J, num_steps=p, vqe_option=None, connection=cxn)

    assert most_freq_string_ising == [-1, 1, -1, 1]
    assert energy_ising == 0

    with patch("pyquil.api.QVMConnection") as cxn:
        # Mock the response
        cxn.run_and_measure.return_value = [[1, 0, 1, 0]]
        cxn.expectation.return_value = [0, 0, 0, 0] # dummy

    # checkerboard
    J = {}
    h = {0: 1, 1: -1, 2: 1, 3: -1}
    p = 1
    most_freq_string_ising, energy_ising, circuit = ising(h, J, num_steps=p, vqe_option=None, connection=cxn)

    assert most_freq_string_ising == [-1, 1, -1, 1]
    assert energy_ising == -4

    with patch("pyquil.api.QVMConnection") as cxn:
        # Mock the response
        cxn.run_and_measure.return_value = [[1, 0, 1, 0, 1]]
        cxn.expectation.return_value = [0, 0, 0, 0, 0] # dummy

    J = {(0, 4): -1}
    h = {0: 1, 1: -1, 2: 1, 3: -1}
    p = 1
    most_freq_string_ising, energy_ising, circuit = ising(h, J, num_steps=p, vqe_option=None, connection=cxn)

    assert most_freq_string_ising == [-1, 1, -1, 1, -1]
    assert energy_ising == -5
