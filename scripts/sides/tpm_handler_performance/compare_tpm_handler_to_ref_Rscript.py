"""
This script compares the performance of tpm_handler as opposed to the provided reference Rscript by Andrej.
"""

import time
import subprocess
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from alive_progress import alive_bar

if __name__ == '__main__':

    lengths = "v22.lengths"
    file = "cropped.countTable"

    reps = 20

    times_R = np.arange( reps )
    times_tpm_handler = np.arange( reps )
    
    with alive_bar( reps * 2 ) as bar:
        
        bar.title = "Measuring performance (R)"
        # start by the Rscript
        for i,_ in enumerate(times_R):
            start = time.time()
            subprocess.run( "Rscript ref.R", shell = True )
            times_R[i] = time.time() - start
            bar()
        
        bar.title = "Measuring performance (tpm_handler)"
        # now the same for tpm_handler
        for i,_ in enumerate(times_tpm_handler):
            start = time.time()
            subprocess.run( f"tpm_handler normalise -r 5 -l {lengths} {file}", shell = True )
            times_tpm_handler[i] = time.time() - start
            bar()

    # plot the results
    times = pd.DataFrame( 
        { "ref Rscript": times_R, "tpm_handler": times_tpm_handler },
    )
    times = times.melt()
    times.columns = ["program", "time"]
    times.to_csv( "times.tsv", sep="\t", index=False )

    fig, ax = plt.subplots()
    sns.boxplot( x = "program", y = "time", data = times, ax = ax )
    sns.stripplot( x = "program", y = "time", data = times, ax = ax, color = "black", size = 5, jitter = True )
    sns.despine( trim = True )

    with open( f"{file}", "r" ) as f:
        lines = len( f.readlines() )
    ax.set( xlabel = "Program", ylabel = "Time (s)", title = f"TPM conversion performance on {lines} lines" )
    fig.savefig( "performance.jpg", dpi = 300 )