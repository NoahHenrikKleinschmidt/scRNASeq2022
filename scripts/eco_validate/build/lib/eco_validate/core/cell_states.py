"""
This class handles Cell State assignments for different EcoTyper runs. 
"""

import logging
import eco_validate.core.find as find
import eco_validate.core.cell_types as cell_types
import eco_validate.core.gene_sets as gene_sets
import eco_validate.core.settings as settings

import pandas as pd
import os

class CellStateCollection( cell_types.CellTypeCollection ):
    """
    This class handles the state assignments between runs.

    Parameters
    ----------
    directories : list
        List of EcoTyper results (output) directories to get state assignments from.
    """
    def __init__( self, directories : list ):
        super().__init__( directories )
        self.state_assignments = {}
        self.genes = {}
        # we drop the expression stuff until further notice
        # self.expressions = {}

        for cell_type, dirs in self.cell_types.items() :
            self._find_state_assignments( cell_type, dirs ) 
    
    def save( self, directory : str ):
        """
        Save the state assignments of each cell type to a directory (one file per cell type).
        
        Note
        ----
        The `export_to_gseapy` method allows streamlined export of gene 
        sets destined for subsequent analysis with `gseapy` prerank or enrichr.

        Parameters
        ----------
        directory : str
            The directory to save the state assignments to.
        """
        for cell_type, df in self.state_assignments.items():
            df.to_csv( os.path.join( directory, cell_type + settings.state_assignments_suffix ), sep = "\t" )

        if len( self.genes ) != 0:
            self.genes.save( directory )

    def export_to_gseapy( self, directory : str, prerank : bool = False, enrichr : bool = True ):
        """
        Export the gene sets for each cell type and state into separate files in a directory.
        If `get_genes()` has not been called yet, this method will call it automatically.
        
        Note
        ----
        If both prerank and enrichr are set to true, then the ouput 
        files will be placed in separate subdirectories.

        Parameters
        ----------
        directory : str
            The directory to export the gene sets to.
        prerank : bool
            Export both the gene names alongside the max. Fold change for `gseapy prerank` (default False).
        enrichr : bool
            Export only the gene names as a simple text file for `gseapy enrichr` (default True).
        
        """
        if len( self.genes ) == 0:
            self.get_genes()

        if prerank and settings:
            enrichr_dir = os.path.join( directory, settings.enrichr_outdir )
            prerank_dir = os.path.join( directory, settings.prerank_outdir )
            os.mkdir( enrichr_dir )
            os.mkdir( prerank_dir )
        else:
            enrichr_dir = directory
            prerank_dir = directory
        
        if enrichr: 
            for subset, cell_type in zip( self.genes.subsets(), self.genes.cell_types ):
                for state, df in subset:
                    filename = f"{ cell_type }_{ state }.txt" 
                    filename = os.path.join( enrichr_dir, filename )

                    df[ settings.gene_col ] = df.index 
                    df = df[ settings.gene_col ]
                    df.to_csv( filename, sep = "\t", header = False, index = False )

        if prerank:
            for subset, cell_type in zip( self.genes.subsets(), self.genes.cell_types ):
                for state, df in subset:
                    filename = f"{ cell_type }_{ state }.txt" 
                    filename = os.path.join( prerank_dir, filename )

                    df[ settings.gene_col ] = df.index 
                    df = df[ [ settings.gene_col, settings.rel_expr_col ] ]
                    df.to_csv( filename, sep = "\t", header = False, index = False )

      
    def get_genes( self ):
        """
        Get the gene info with the fold-change data for each cell type and the assigned cell state.

        Returns
        -------
        genes : GeneSetCollection
            A GeneSetCollection with the gene info with the fold-change data for each cell type and the assigned cell state.
        """
        self.genes = self._get_genes_to_states()
        return self.genes

    # def get_genes( self, full_expression : bool = False ):
    #     """
    #     Get the gene info with the fold-change data for each cell type and the assigned cell state.

    #     Parameters
    #     ----------
    #     full_expression : bool
    #         If True the full expression matrices will be extracted in addition to the fold-change and assignments.
        
    #     Returns
    #     -------
    #     genes : dict or tuple
    #         Either only the genes dictionary or both the genes and expressions dictionaries.
    #     """
    #     self.genes = self._get_genes_to_states()
    #     if full_expression:
    #         self.expressions = self._get_expressions()
    #         return self.genes, self.expressions
    #     return self.genes

    def compare_gene_overlaps( self, percent : bool = False ) -> pd.DataFrame:
        """
        Compares the gene set overlaps between differen EcoTyper runs over per cell type for all cell states.

        Note
        ----
        A per-state comparison makes no sense because the state labelling is arbitrary for each clustering and therefore 
        S01 from two different runs need not correspond to the same state.

        Parameters
        ----------
        percent : bool
            If True, compute the overlap as a percentage of the total set of genes per state.
        
        Returns
        -------
        df : pd.DataFrame
            Dataframe with the gene set overlaps for each cell type between different runs.
        """
        gene_sets = []
        for overlap in self._get_gene_overlaps().values():

            overlap = overlap.compute_overlap( percent = percent ) 
            gene_sets += [overlap]
        
        gene_sets = pd.concat( gene_sets, axis = 0 )
        return gene_sets

    def _get_genes_to_states(self):
        """
        Get the gene info with the fold-change data for each cell type and the assigned cell state.
        """
        genes = {}
        for cell_type, dirs in self.cell_types.items():
            files = ( find.find_files( i, settings.gene_info_file ) for i in dirs )

            df = pd.DataFrame()
            for file in files:
                # get the run name 
                name = os.path.basename( os.path.dirname( os.path.dirname( file[0] ) ) )
                
                new = pd.read_csv( file[0], sep = "\t", index_col = 0 )
                new["run"] = name
                new = new[ [settings.state_col, settings.rel_expr_col, settings.ecotyper_experiment_col] ]
                
                if df.empty:
                    df = new
                else:
                    df = pd.concat( [df, new], axis = 0 )
            
            genes[ cell_type ] = df

        genes = gene_sets.GeneSetCollection( genes )
        return genes

    # we drop that one for the moment until we are sure what to do with that...
    # def _get_expressions( self ):
    #     """
    #     Get the full expression matrices for each cell type.
    #     """
    #     expressions = {}
    #     for cell_type, dirs in self.cell_types.items():
            
    #         tmp = {}
    #         files = ( find.find_files( i, "heatmap_data.txt") for i in dirs )
    #         for file in files:

    #             # get the run name 
    #             name = os.path.basename( os.path.dirname( os.path.dirname( file[0] ) ) )
                
    #             new = pd.read_csv( file[0], sep = "\t", index_col = 0 )
                
    #             tmp[ name ] = new 
    #         expressions[ cell_type ] = tmp

    #     return expressions

    def _find_state_assignments( self, cell_type : str, dirs : list ):
        """
        Find the state assignments from a single cell type from multiple EcoTyper results directories.
        
        Parameters
        ----------
        cell_type : str
            The cell type to find state assignments for.
        dirs : list
            The EcoTyper results directories to get state assignments from.
        """
        state_assignments = pd.DataFrame()

        for dir in dirs:
            
            name = find.find_files( dir, settings.gene_info_file )
            if not name:
                logging.warning( f"No state assignment file found in {dir}" )
                continue
            
            df = pd.read_csv( name[0], sep = "\t", index_col = 1 )

            name = os.path.basename( os.path.dirname( dir ) )
            state_assignments[ name ] = df[ settings.state_col ]
       
        self.state_assignments[ cell_type ] = state_assignments

    def _get_gene_overlaps( self ):
        """
        Generate GeneSetOverlaps for each cell type.
        """
        _gene_sets = { 
                        cell_type : gene_sets.GeneSetOverlap( cell_type, df ) 
                        for cell_type,df in self.genes.items() 
                    }
        return _gene_sets

    def __iter__( self ):
        """
        Iterate over the cell type state_assignments.
        """
        return iter( self.state_assignments )

    def __getitem__( self, key ):
        """
        Get the cell type state_assignments.
        """
        return self.state_assignments[key]

    def __len__( self ):
        """
        Get the number of cell types.
        """
        return len( self.state_assignments )
