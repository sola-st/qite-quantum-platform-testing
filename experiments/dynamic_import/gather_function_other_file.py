import experiments.dynamic_import.gather_functions as my_module
import inspect
import sys

functions = inspect.getmembers(my_module, inspect.isfunction)

# Filter functions that start with the given prefix
filtered_functions = [func for name, func in functions
                      if name.startswith("export_")]

for func in filtered_functions:
    func()
    print(str(func.__name__))
