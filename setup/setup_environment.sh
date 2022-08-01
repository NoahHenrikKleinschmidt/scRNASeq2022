# This script will setup a new anaconda environment named EcoTyper (by default)
# for running EcoTyper with the required packages.

name=$1
if [ "$name" == "" ]; then 
    name="EcoTyper"
fi

# create the new environment
conda create --name ${name} r=4.1.0
conda activate ${name}

# now install the necessary packages
Rscript install_requirements.R
