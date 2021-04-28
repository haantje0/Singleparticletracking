# -*- coding: utf-8 -*-
"""
Created on Wed Sep 30 2020
@author: L. de Haan
"""

import singleparticletracking as spt


filename_startswith = "2017_cubes3_Au_sput_UV"
get_dir = "D:\\Thesis old data\\CSMR DATA 2017\\"
save_dir = "C:\\Users\\ldhaa\\Documents\\Chemical Enigneering\\Thesis\\Data Analysis\\CSMR DATA 2017\\"

exp_max = 100     # expected max particle speed (in micron/s)
psize = 5         # particle diameter size in pixels (has to be an odd number)
minmass = 200     # size of the particle (for trackpy)

paths = spt.directory_setup(filename_startswith, get_dir, save_dir)
for index, path in paths.iterrows():
    spt.create_folder(path['save'])
    spt.test_locations(path, psize, minmass)

    frames, particles, trajectories = spt.locate_particles(path, exp_max, psize, minmass)
    
    # remove = []
    # trajectories = spt.remove_trajectories(trajectories, remove, path)
        
    spt.get_velocity_distribution(trajectories, frames.metadata['calibration_um'], exp_max, path['save'])
    
    spt.get_msd(trajectories, frames, path['save'])

    spt.plot_trajectories(trajectories, frames, particles, path['save'])

spt.combine(paths, save_dir, filename_startswith, exp_max)
