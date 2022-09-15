# This script will setup a new anaconda environment named EcoTyper (by default)
# for running EcoTyper with the required packages.
#
# 
# This script accepts two optional arguments:
#
# 1. name of the environment to be created (default: EcoTyper)
# 2. path to the directory where the environment will be created (default: {../..}/ecotyper)
# 
#

name=$1
if [ "$name" == "" ]; then 
    name="EcoTyper"
fi

echo "Creating environment $name"

# create the new environment
conda create --name ${name} r=4.1.0
conda activate ${name}

# install netcdf4 because they are needed by some of the R packages
conda install -y -c conda-forge netcdf4 

# for working with seurat
conda install -y -c conda-forge r-rgeos 


# now install the necessary packages
Rscript install_requirements.R

# now clone EcoTyper from git in a specified directory
dest=$2
if [ "$dest" == "" ]; then 
    dest="../.."
fi
git clone https://github.com/digitalcytometry/ecotyper ${dest}/ecotyper

# now install some python packages 
conda install -y pip
pip install -r python_requirements.txt

# now install supplementary packages for making data handling easier
pip install git+https://github.com/NoahHenrikKleinschmidt/eco_helper
pip install git+https://github.com/NoahHenrikKleinschmidt/filerecords

echo "Finished creation of $name"
