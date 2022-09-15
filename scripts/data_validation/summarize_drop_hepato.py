"""
This script summarizes all drop_hepato runs from EcoTyper
"""

import glob
import os
import subprocess 

pattern = "drop_hepato*"

parent = "/data/users/noahkleinschmidt/EcoTyper"
scripts = f"{parent}/scripts"
results = f"{parent}/results"
summaries = f"{parent}/summaries"

config = f"{scripts}/experiments/our_data/drop_hepato.yml"

os.chdir( results )

dirs = glob.glob( pattern )
dirs = [ i for i in dirs if os.path.isdir( i ) ]
dirs = [ f"'{i}'" for i in dirs if " " not in i ]
dirs = " ".join( dirs )

cmd = f"eco_validate summarize -c {config} -o {summaries} -s -r {dirs}"
subprocess.run( cmd, shell = True )