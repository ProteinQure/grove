"""
This class generates a PauliSum (from Rigetti's pyquil) that
represent an XY mixer hamiltonian for QAOA.

Normal QAOA uses a pure X mixer but we can implement QAOA with
hard and soft constraints by using a mixer hamiltonian that
ensures that we stay in a feasible subspace that contains all
feasible solutions.

see the following paper:
Hadfield, S., Wang, Z., Rieffel, E. G., O'Gorman, B., Venturelli, D., & Biswas, R. (2017, November).
Quantum Approximate Optimization with Hard and Soft Constraints.
In Proceedings of the Second International Workshop on Post Moores Era Supercomputing (pp. 15-21). ACM.
"""

from pyquil.paulis import PauliSum, PauliTerm


class constrainedQAOA(object):
    """
    Class with helper functions to enable QAOA with constraints.
    """

    @staticmethod	
    def indicator_qubit_index(move, direction):
	"""
	To know if a certain move went into a certain
	direction we can call this function and get the
	index of the qubit that is 1 if TRUE or FALSE otherwise.
	"""
	# list of directions
	# (padded with a zero to get intended indices)
	directions = ['r','l','u','d']
	
	# number of qubits before this move
	prev_qubits = 4*(move-1)
	
	# add the index of the direction to the previous qubits
	return prev_qubits+directions.index(direction)

    @classmethod
    def generate_mixer(cls,num_qubits):
        """
        Method that generates the mixer Hamiltonian that keeps
        the solutions within the feasible subspace.

        This one is currently customized to the one-hot encoding of
        the directions and the mixer currently only takes care of
        'going back on itself'.

        One-Hot encoding:
            r: 1000
            l: 0100
            u: 0010
            d: 0001
        """

        mixer_operators = []
        qubit_map = cls.indicator_qubit_index

        num_moves = num_qubits/4
        turns = ['r','l','u','d']

        if num_moves%1 != 0.0:
            raise ValueError("The number of qubits suggest that you have not used the One-Hot encoding.")
        num_moves = int(num_moves)

        # we need to pair each qubit with all other direction-encoding qubits for that move
        # we can save terms due to symmetry
        for move in range(1,num_moves):
            for index, turn in enumerate(turns[:-1]):
                for alt_turn in turns[index+1:]:
                    #print("Possible move from " + str(qubit_map(move,turn)) + ' to ' + str(qubit_map(move,alt_turn)))
                    mixer_operators.append(PauliSum([PauliTerm("X", qubit_map(move,turn), 1/(2**1)) * PauliTerm("X", qubit_map(move,alt_turn))]))
                    mixer_operators.append(PauliSum([PauliTerm("Y", qubit_map(move,turn), 1/(2**1)) * PauliTerm("Y", qubit_map(move,alt_turn))]))

            # how to do the product with the Pauli Z's??
            # we could try this first and then multiply
            # Hamming weight should still be preserved

        return mixer_operators
