#!/usr/bin/Rscript

# This script allows to convert a mtx file to a tsv file.

library( argparse )
library( Matrix )
library( stringr )

# --------------------------------------------------------------------------------
# Define the necessary functions
# --------------------------------------------------------------------------------

# Special characters that need to be replaced with something else in 
# order to be able to use the names for the tsv file.
formatters = list(
    "-" = "_",
    " " = "."
)

# setup the CLI
setup_cli = function(){

    parser = argparse::ArgumentParser( description = "Convert a mtx file to a tsv file" )
    parser$add_argument( "input", help = "The mtx file to convert." )
    parser$add_argument( "-o", "--output", help = "The output file. By default this will be the same as the input file.", default = NULL )
    parser$add_argument( "-n", "--names", help = "Add column and row names from `mtx_cols` and `mtx_rows` files of the same name as the input file and in the same directory.", action = "store_true", default = FALSE )
    
    return( parser )
}

# Load the mtx file to a matrix.
#' param file: The mtx file to load
#' @export
read_mtx = function( file ){
    mtx = readMM( file )
    mtx = as.matrix( mtx )
    return( mtx )
}

# Write the matrix to a tsv file.
#' param data: The matrix to write
#' param args: The command-line arguments
#' @export
write_tsv = function( data, args ){

    outfile = args$output
    if( is.null( outfile ) ){
        outfile = file.path( file = args$input )
        outfile = str_replace( outfile, ".mtx", ".tsv" )
    }

    names = args$names
    write.table( 
                    data, 
                    file = outfile, 
                    sep = "\t", quote = FALSE, 
                    row.names = names, col.names = names 
                )
}

# add column and row names. This requires that mtx_cols and mtx_rows have the same
# name and are in the same directory as the input file. 
#' param data: The matrix to add names to
#' param file: The mtx filename from which the data was loaded.
#' @export
add_names = function( data, file ){

    cols = paste0( file, "_cols" )
    rows = paste0( file, "_rows" )

    cols = read.table( cols, sep = "\t" )
    rows = read.table( rows, sep = "\t" )

    cols = cols[,1] # there is only one column in the mtx_cols file
    rows = rows[,2] # there are two columns, the second one of which are "unique" identifiers

    # now ensure that the names are in the proper format so EcoTyper won't cry around...
    for ( i in formatters ){
        
        cols = str_replace( cols, i, formatters[i] )
        rows = str_replace( rows, i, formatters[i] )
    }
    
    rownames( data ) = rows
    colnames( data ) = cols
    
    return( data )
}

# --------------------------------------------------------------------------------
# Main script
# --------------------------------------------------------------------------------

if ( sys.nframe() == 0 ){

    parser = setup_cli()
    args = parser$parse_args()

    print( "Loading mtx file..." )
    data = read_mtx( args$input )

    if ( args$names == TRUE ){

        print( "Adding column and row names..." )
        data = add_names( data, args$input )

    }

    print( "Writing matrix to tsv file..." )
    write_tsv( data, args ) 
    print( "Done" )

}