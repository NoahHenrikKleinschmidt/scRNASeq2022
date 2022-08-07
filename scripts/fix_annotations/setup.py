import setuptools

setuptools.setup(
    name="fix_annotations", 
    version="0.0.1",
    author="Noah H. Kleinschmidt",
    author_email="noah.kleinschmidt@students.unibe.ch",
    description="A small script to ensure that columns within expression matrix and annotation tables conform with EcoTyper requirements.",
    long_description="A small script to ensure that columns within expression matrix and annotation tables conform with EcoTyper requirements.",
    long_description_content_type="text/markdown",
    url="https://github.com/NoahHenrikKleinschmidt/scRNASeq2022",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
    entry_points={
        "console_scripts": [ 
            "fix_annotations=fix_annotations.main:main",
        ]
    },
    python_requires='>=3.6',
)