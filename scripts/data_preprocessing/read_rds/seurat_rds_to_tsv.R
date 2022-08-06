# This script allows to read an RDS file and convert it to TSV format.

library( logger )
library( argparse )
library( stringr )
library( Seurat )

get_args = function() {
    #' Setup the command line arguments parser
    #' @return args: The command line arguments
    
    descr = "Convert an RDS file to TSV format"
    parser = argparse::ArgumentParser(description = descr)
    parser$add_argument( "input", help="Input RDS file" )
    parser$add_argument( "-o", "--output", help="Output TSV file. By default the same name as the input is used.", default = NULL )
    args = parser$parse_args()
    return( args )
}

get.from.seurat = function( obj ) {
    #' Extracts counts and metadata from a Seurat object and returns a list of two tables.
    #' @param obj: The Seurat object to extract data from.
    #' @return data: A list of of counts and metadata as tables.
    #' @export

    # get the actual data
    # the SeuratObject contains both meta data and raw data attributes.
    
    counts = GetAssayData( obj, slot = "counts" )
    counts = as.matrix( counts )
    counts = as.data.frame( counts )

    metadata = obj@meta.data

    return(
        list(
                counts = counts,
                metadata = metadata
            )
        )
}

write.tsv = function( data, filename ){
    #' Write the extracted counts and metadata to TSV files.
    #' @param data: The extracted data list (containing a counts and metadata entry).
    #' @param filename: The filename to write the data to. 
    #' @export

    counts_file = paste0( filename, ".counts.tsv" )
    metadata_file = paste0( filename, ".metadata.tsv" )
    
    log_info( paste("Writing counts to:", counts_file) )
    write.table( data$counts, counts_file, sep = "\t", row.names = TRUE, col.names = TRUE )

    log_info( paste("Writing metadata to:", metadata_file) )
    write.table( data$metadata, metadata_file, sep = "\t", row.names = TRUE, col.names = TRUE )

}

main = function() {
    #' The main CLI function.
    
    args = get_args()

    log_info( paste( "Reading RDS file:", args$input ) )
    data = readRDS( args$input )

    # get the data from the Seurat object
    log_info( paste( "Extracting data from Seurat object..." ) )
    data = get.from.seurat( data )

    # write the data to a TSV file
    if (is.null( args$output )) {
        args$output = args$input
    }
    write.tsv( data, args$output )


}
# run the script if called directly
if (sys.nframe() == 0){
    main()
}
