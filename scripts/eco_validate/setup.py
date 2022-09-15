import setuptools

setuptools.setup(
    name="eco_validate", 
    version="0.0.1",
    author="Noah H. Kleinschmidt",
    author_email="noah.kleinschmidt@students.unibe.ch",
    description="A small package to summarize and test multiple re-runs of the EcoTyper framework.",
    long_description="A small package to summarize and test multiple re-runs of the EcoTyper framework.",
    long_description_content_type="text/markdown",
    url="https://github.com/NoahHenrikKleinschmidt/scRNASeq2022",
    packages=setuptools.find_packages(),

    install_requires = [
                            "matplotlib",
                            "pandas",
                            "PyYAML",
                            "seaborn",
                        ],

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
    entry_points={
        "console_scripts": [ 
            "ecovalidate=eco_validate.cli:main",
            "eco_validate=eco_validate.cli:main",
        ]
    },
    python_requires='>=3.6',
)