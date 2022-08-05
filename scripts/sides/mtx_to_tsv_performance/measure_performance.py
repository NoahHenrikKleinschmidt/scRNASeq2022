
import subprocess
import time
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from alive_progress import alive_bar

reps = 10
file = "counts"

times_R = np.arange( reps )
times_Py = np.arange( reps )

with alive_bar( reps*2, title = "Measuring performance" ) as bar:

    bar.title = "Measuring performance (R)"
    # start with R
    for i in range( reps ):
        start = time.time()
        subprocess.run( f"mtx_to_tsv -r True -n {file}.mtx", shell = True )
        times_R[i] = time.time() - start
        bar()

    bar.title = "Measuring performance (Py)"
    # now with python
    for i in range( reps ):
        start = time.time()
        subprocess.run( f"mtx_to_tsv -r False -n {file}.mtx", shell = True )
        times_Py[i] = time.time() - start
        bar()

# plot the result
times = pd.DataFrame( 
    { "R": times_R, "Python": times_Py },
)
times = times.melt()
times.columns = ["implementation", "time"]
times.to_csv( "times.tsv", sep="\t", index=False )

fig, ax = plt.subplots()
sns.boxplot( x = "implementation", y = "time", data = times, ax = ax )
sns.stripplot( x = "implementation", y = "time", data = times, ax = ax, color = "black", size = 5, jitter = True )
sns.despine( trim = True )

with open( f"{file}.tsv", "r" ) as f:
    lines = len( f.readlines() )
ax.set( xlabel = "implementation", ylabel = "Time (s)", title = f"MTX -> TSV conversion performance on {lines} lines" )
fig.savefig( "performance.jpg", dpi = 300 )