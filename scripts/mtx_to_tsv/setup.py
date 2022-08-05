import setuptools

setuptools.setup(
    name="mtx_to_tsv", 
    version="0.0.1",
    author="Noah H. Kleinschmidt",
    author_email="noah.kleinschmidt@students.unibe.ch",
    description="A small script to convert MTX files to TSV format.",
    long_description="A small script to convert MTX files to TSV format.",
    long_description_content_type="text/markdown",
    url="https://github.com/NoahHenrikKleinschmidt/scRNASeq2022",
    
    packages=setuptools.find_packages(),
    package_data={'': ['*.r', '*.R']},
    include_package_data=True,

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
    entry_points={
        "console_scripts": [ 
            "mtx_to_tsv=mtx_to_tsv.main:main",
        ]
    },
    python_requires='>=3.6',
)