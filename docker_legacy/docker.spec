I want to generate a dockerfile that uses python image (the slimmest possible) (3.10) and instals the qiskit version qiskit 0.46.2 via pip.
it then has a folder working dir where the user can mount volumes, then the folder will have a single python file called to_execute.py and the image runs it automatically.
Give me the dockerfile.