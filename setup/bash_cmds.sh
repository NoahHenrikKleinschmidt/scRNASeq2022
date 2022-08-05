# this script sets up the working environment for working with EcoTyper
# this assumes the conda environment is also called EcoTyper

env_name="EcoTyper"
function ecotyper {
    # go to the directory
    cd /data/users/${USER}/EcoTyper

    # activate the conda environment
    conda activate ${env_name}

    echo "--------------------------------"
    echo "            EcoTyper"
    echo "--------------------------------"
}