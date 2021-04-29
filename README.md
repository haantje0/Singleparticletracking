# Singleparticletracking
This python script can detect particles in a Tiff or ND2 movie and preform calculations on the motion of the particles.

# Manual
This manual describes how to use the Singleparticletracking package. The important functions and variables are shown with the use of an example. In this example multiple video’s of a sample of active particles are analysed in an automated manner. The example is done for the SingleparticletrackingND2 script, which uses ND2 videos. If you use the SingleparticletrackingTiff script, it is important to check the hardcoded variables in the script and change them accordingly.

## Setup & variables
Before you start, you have to import the singleparticletracking package. Other packages such as matplotlib (for plotting), numpy (for scientific computing) or pandas (for database management) might be useful for your script, but are not necessary for the basic use of Singleparticletracking.

'''
import SingleparticletrackingND2 as spt

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
'''
