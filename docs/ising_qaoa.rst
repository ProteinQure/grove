Ising wrapper for the Quantum Approximate Optimization Algorithm (QAOA)
=================================================

Overview
--------

Ising QAOA is a wrapper for the Quantum Approximate Optimization
Algorithm that makes it easy to work within the framework of
Ising-type Hamiltonians.

This wrapper will be particulary useful for people that have been
dealing with quantum annealers. However, in comparison to current quantum
annealers the Ising QAOA wrapper supports not only 2-local but also k-local
interaction terms and the driver (mixer) Hamiltonian is not dictated by the
hardware but can be defined by the user.

For each Ising instance the user specifies the bias vector $$h$$, the
interaction matrix $$J$$ and the approximation order of the algorithm.
``ising_qaoa.py`` contains routines for approximating the ground state of
the specified Ising-type Hamiltonian through the use of QAOA which itself
finds the optimal rotation angles via Grove's
`variational-quantum-eigensolver method <http://grove-docs.readthedocs.io/en/latest/vqe.html>`_.


