# This script will download the docker images of CIBERSORTx and convert them signularity images. 
# Depending on the system this script may need to be executed on a different computer where 
# super-user privileges are available to the user to run docker. 
#
# Note
# ----------------------------------------------------------------
# This script was executed locallay and the resultant singularity
# images were uploaded to the cluster. For some reason singularity 
# would not directly work on the IBU cluster (need to check with 
# Berthier...)
#
# Requirements:
# - Docker 4.11.0
# - Singularity-vagrant (MacOS) 3.0.3-1
# ----------------------------------------------------------------

# get cibersortx HiRes and Fractions
# and convert to singularity images
sudo singularity build cibersortx_fractions.sif docker://cibersortx/fractions
sudo singularity build cibersortx_hires.sif docker://cibersortx/hires

# to transfer the built sif files to the cluster (takes quite a while)
# user="noahkleinschmidt"
# dir="EcoTyper/cibersortx/"
# scp *sif ${user}@binfservms01.unibe.ch:/data/users/${user}/${dir}