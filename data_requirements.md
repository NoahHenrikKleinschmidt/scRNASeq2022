## Notes on the types of data we need.

The default settings are tailored toward two pre-set states
"Carcinoma" and "Lymphoma" but we could define our own custom ones if we liked.

### Discovery / Recovery from bulk RNA-seq data
1. Expression Matrix - A TSV of format

    | target | sample1 | sample2 | ... |
    | :----- | :------ | :------ | :-- |
    | geneA  | 123.1   | 123.8   | ... |
    | ...    | ...     | ...     | ... |
    | ...    | ...     | ...     | ... |

2. Annotation File - A TSV of format
   
    | sample  | grouping | other data | ... |
    | :------ | :------- | :--------- | :-- |
    | sample1 | group1   | ...        | ... |
    | sample2 | group1   | ...        | ... |
    | ...     | ...      | ...        | ... |


### Recovery from scRNA-seq data
1. Expression Matrix - A TSV of format

    | target | sample1 | sample2 | ... |
    | :----- | :------ | :------ | :-- |
    | geneA  | 123.1   | 123.8   | ... |
    | ...    | ...     | ...     | ... |
    | ...    | ...     | ...     | ... |

2. Annotation File - A TSV of format
   
    | sample  | grouping | other data | ... |
    | :------ | :------- | :--------- | :-- |
    | sample1 | group1   | ...        | ... |
    | sample2 | group1   | ...        | ... |
    | ...     | ...      | ...        | ... |
    However, the grouping here is more restricted. 
    Since we are working with Carcinomas the "grouping" column is `Celltype` which supports the following subtypes:
    - 'B.cells'
    - 'CD4.T.cells'
    - 'CD8.T.cells',
    - 'Dendritic.cells'
    - 'Endothelial.cells',
    - 'Epithelial.cells'
    - 'Fibroblasts'
    - 'Mast.cells
    - 'Monocytes.and.Macrophages'
    - 'NK.cells'
    - 'PCs'
    - 'PMNs'