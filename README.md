# Singleparticletracking
This python script can detect particles in a Tiff or ND2 movie and preform calculations on the motion of the particles.

# Manual
This manual describes how to use the Singleparticletracking package. The important functions and variables are shown with the use of an example. In this example multiple video’s of a sample of active particles are analysed in an automated manner. The example is done for the SingleparticletrackingND2 script, which uses ND2 videos. If you use the SingleparticletrackingTiff script, it is important to check the hardcoded variables in the script and change them accordingly.

### Setup & variables
Before you start, you have to import the singleparticletracking package. Other packages such as matplotlib (for plotting), numpy (for scientific computing) or pandas (for database management) might be useful for your script, but are not necessary for the basic use of Singleparticletracking.

```
import SingleparticletrackingND2 as spt

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
```

Some variables have to be defined beforehand:
- get dir A string of the path to the directory where your videos are saved.
- save dir A string of the path to the directory where you want to save the analysis results. This directory does not have to exist yet, and will be created by the create folder() function in Step 1.
- filename startswith A string of the filenames of the videos you want to analyse. Typically ND2 files are named in the same way, starting with a sample name and ending with a number. To analyse multiple videos automatically, as done in this manual, this string consists of the first part of the filenames that is the same for the sample. When only one video is analysed, you can specify the first (unique) part of the file name or the whole file name.
- exp max The expected maximum speed of you particles (in micron/s). This variable is important for the trackpy trajectory coupling. Entering a too low number, results in decoupled trajectories, while a too high number results in a drastic increase in computation time.
- psize The size of your particles (in pixels). This can be estimated or measured, but has to be an odd number. If you estimate the size, it is better to estimate it too large!
- minmass The minimum mass of your particles. This is a trackpy parameter, which indicates how bright a particle is. This variable is further explained in Step 1.

```
get_dir = "D:\\your path\\directory\\"
save_dir = "C:\\your path\\directory\\"
filename_startswith = "Filename_00"

exp_max = 100 # expected max particle speed (in micron/s)
psize = 11 # particle diameter size in pixels (has to be an odd number)
minmass = 500 # size of the particle (trackpy variable)
```

In this example, the particles have a size of roughly 11 pixels. The minmass is chosen at random and will be re-evaluated in Step 1. 
To handle (multiple) videos, a dataframe has to be created to store the different files and their locations. This can be done with the directory setup() function, using the previously defined filename and directory. The paths dataframe will consist of a ’get’ and a ’save’ column.

```
paths = spt.directory_setup(filename_startswith, get_dir, save_dir)
```

### Step 1: Particle Identification
Once everything is setup, you can start identifying you particles by first looping over the paths dataframe. With the test locations() function, you can do a fast check to see if your particles are identified correctly. If this is not the case, you can tweak your minmass or psize variables.

```
for index, path in paths.iterrows():
  spt.create_folder(path['save'])
  spt.test_locations(path, psize, minmass)
```

It is important to first create the directories where the data will be stored, with the create folder() function. This will create folders with the same names as the ND2 files. If the folder already exists, the create folder() function will not create new folders and the existing folder will be used to save the data.
In your new folders you can find the graphs that the test locations() function has created. The test frame graph shows the first frame of your video and the particles that were detected and the test hist graph shows a distribution of the mass of the detected particles. As you can see in the example test frame, not all detected particles are the particles that we are interested in. For instance the identified particle in the top right, is not really a particle. In the test hist graph you can see that there are several particles with a higher mass, and thus a higher brightness, which are probably our particles. You can change minmass in the test locations() functions to see if these are indeed the correct particles.

<img src="https://github.com/haantje0/Singleparticletracking/blob/main/docs/test_frame.png" width="400"/>
<img src="https://github.com/haantje0/Singleparticletracking/blob/main/docs/test_hist.png" width="400"/>

