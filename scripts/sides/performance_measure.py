"""
This is a performance measurement tool to compare multiple functions.
"""

from time import perf_counter
import numpy as np
from alive_progress import alive_bar
import matplotlib.pyplot as plt
import seaborn as sns

class PerformanceMeasure:
    """
    Measure repeated function call's execution times, and summarize the results.

    Parameters
    ----------
    executions : int
        The number of times the functions shall be executed.
    """
    def __init__( self, executions : int = 3, ):
        self.executions = executions

        self.times = None
        self.functions = {}
        self._lambda_counter = 0

    def add_function( self, f, *args, **kwargs ):
        """
        Add a function to the performance test.

        Parameters
        ----------
        f : function
            A function to be added to the performance test.
        *args
            Any unnamed arguments to be passed to the function during execution.
        **kwargs
            Any named arguments to be passed to the function during execution.
        """
        name = f.__name__
        if name == "<lambda>":
            name += str(self._lambda_counter)
            self._lambda_counter += 1
        self.functions[ name ] = [ f, args, kwargs ]

    def add_function_with_name( self, name, f, *args, **kwargs ):
        """
        Add a function to the performance test and specify a name for the function that differs from the normal function name.
        This can be useful for comparing the performance of the same function when given different parameter sets.

        Parameters
        ----------
        name : str
            The name of the function to be added to the performance test.
        f : function
            A function to be added to the performance test.
        *args
            Any unnamed arguments to be passed to the function during execution.
        **kwargs
            Any named arguments to be passed to the function during execution.
        """
        self.functions[ name ] = [ f, args, kwargs ]

    def run( self ) -> np.ndarray:
        """
        Run performance tests.

        Returns
        -------
        times : np.ndarray
            The performance results as a 2D numpy array.
        """
        times = np.zeros( shape = ( len(self.functions), self.executions ) )
        repeats = np.arange( self.executions )

        with alive_bar( len(self.functions) ) as bar:

            for i,f in enumerate( self.functions.keys() ):

                bar.title = f"Testing {f}"
                func, args, kwargs = self.functions[f]

                for j in repeats:
                    start = perf_counter()
                    _ = func( *args, **kwargs )
                    stop = perf_counter()
                    times[i,j] = stop - start

                bar()

        times = times.transpose()
        self.times = times
        return times

    def save( self, filename ):
        """
        Save the performance results to a text file.

        Parameters
        ----------
        filename : str
            The filename to save the results to.
        """
        np.savetxt( filename, self.times, delimiter = "\t", header = self.functions.keys() )

    def boxplot( self, filename : str = None, **kwargs ):
        """
        Summarize the performance results in a boxplot.

        Parameters
        ----------
        filename : str
            A filename to save the figure to.
        """
        fig, ax = plt.subplots( figsize = kwargs.pop("figsize", None), dpi = kwargs.pop("dpi", None) )

        sns.set_style( kwargs.pop("style", "ticks") )
        if kwargs.pop( "despine", True ):
            sns.despine()

        kwargs.pop( "labels", None )
        patch_artist = kwargs.pop( "patch_artist", True )

        edgecolor = kwargs.pop( "edgecolor", "black" )

        flierprops = kwargs.pop( "flierprops", None )
        if not flierprops:
            flierprops = dict( markerfacecolor = kwargs.pop("fliercolor", "gray"), alpha = 0.5, marker = kwargs.pop( "fliermarker", "o") )
            kwargs["flierprops"] = flierprops
        medianprops = kwargs.pop( "medianprops", None )
        if not medianprops:
            medianprops = dict( color = kwargs.pop("medianlinecolor", edgecolor) )
            kwargs["medianprops"] = medianprops

        colors = kwargs.pop( "colors", "husl" )
        if not isinstance( colors, list ):
            colors = sns.color_palette( colors, self.times.shape[1] )

        ax.set( title = kwargs.pop("title", "Performance Results"),
                xlabel = kwargs.pop("xlabel", "Functions"),
                ylabel = kwargs.pop("ylabel", "Time (s)")  )

        boxplot = ax.boxplot( self.times, labels = self.functions.keys(), patch_artist = patch_artist, **kwargs )

        for patch, color  in zip( boxplot["boxes"], colors ):
            patch.set_facecolor( color )
            patch.set_edgecolor( edgecolor )

        if filename:
            plt.savefig( filename )
        plt.show()

if __name__ == "__main__":

    func1 = lambda x, y : np.exp( x + y ) * x / y

    def func2( x, y ):
        return np.exp( x + y ) * x / y

    def func3( x, y ):
        if not isinstance( x, np.ndarray ):
            x = np.asarray( x )
        if not isinstance( y, np.ndarray ):
            y = np.asarray( y )
        a = x / y
        b = np.exp( x + y )
        result = a * b
        return result

    def func4( x, y ):
        """Function with docstring"""
        return func3( x, y )

    def func5( x, y ):
        """Function with docstring"""
        # let's add a lot of comments and stuff in here...
        # which does nothing but help us understand a bit better
        # what the code is supposed to be doing...
        return np.exp( x + y ) * x / y

    x = np.random.random( 100000 )
    y = np.random.random( 100000 )

    perf = PerformanceMeasure( 800 )
    perf.add_function( func1, x = x, y = y )
    perf.add_function( func2, x = x, y = y )
    perf.add_function( func3, x = x, y = y )
    perf.add_function( func4, x = x, y = y )
    perf.add_function( func5, x = x, y = y )

    perf.run()
    perf.boxplot()
