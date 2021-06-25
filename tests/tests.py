import math

signature = "!command <searchterm>"
missing_arg = "searchterm"
op = ""
op += signature + "\n"
op += " " * signature.index(missing_arg) + " " * round(len(missing_arg) / 2) + "^\n"
op += f"The argument {missing_arg} is missing"
print(op)