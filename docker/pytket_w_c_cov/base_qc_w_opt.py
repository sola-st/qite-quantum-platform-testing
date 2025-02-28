from pytket import Circuit


# from pytket.circuit import Circuit
# from pytket.passes import FullPeepholeOptimise


# def test_optimization():
#     # Create circuit
#     circ = Circuit(2)
#     circ.H(0)
#     circ.CX(0, 1)
#     circ.SWAP(0, 1)

#     # Add measurements
#     circ.measure_all()

#     # Optimize circuit
#     opt_pass = FullPeepholeOptimise()
#     opt_pass.apply(circ)

#     # Print circuit
#     print(circ.get_commands())


# if __name__ == "__main__":
#     test_optimization()
