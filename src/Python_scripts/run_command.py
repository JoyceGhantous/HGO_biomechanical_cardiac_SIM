import sys 
import subprocess 
import os
import numpy as np

def runCommand(comm, verbose=False, stopOnFail=True, exitCode=1):
    """
    A wrapper around subprocess.Popen.

    Parameters
    ----------
    comm : str
        Shell command to run.
    verbose : bool
        If True, do not capture stdout.
    stopOnFail : bool
        If True, stop the Python script if the command fails.
    exitCode : int
        Exit code used if stopOnFail is triggered.

    Returns
    -------
    out : str
        Standard output produced by the command.
    vals : np.ndarray
        Numerical values extracted from stdout.
    err : str
        Standard error produced by the command.
    returncode : int
        Return code of the subprocess.
    """

    my_env = os.environ.copy()  
    if verbose:
        # Run the command and only capture stderr
        subP = subprocess.Popen(
            comm,
            shell=True,
            stderr=subprocess.PIPE,
            env=my_env
        )
    else:
        # Run the command and capture both stdout and stderr
        subP = subprocess.Popen(
            comm,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=my_env
        )

    out, err = subP.communicate()  
    out = out.decode() if out else ""   # Convert stdout from bytes to string

    vals = []
    for line in out.splitlines():       # Loop over each line of the output
        s = line.strip()                # Remove leading/trailing spaces
        try:
            vals.append(float(s))       # Keep the line only if it is a valid float
        except ValueError:
            pass                        # Ignore non-numerical lines

    vals = np.array(vals)             

    if stopOnFail and subP.returncode != 0:
        print("Error while running:\n   " + comm + "\n\n")
        print("Returned code: " + str(subP.returncode) + " with the following error message:\n\n")
        print(err.decode())
        print("----- end error message -----")
        sys.exit(exitCode)

    return out, vals, err.decode(), subP.returncode  

