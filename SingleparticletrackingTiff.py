# -*- coding: utf-8 -*-
"""
This script is designed for the detection an analysation of active 
(micro)particles. This is done via single particle tracking, using the 
Trackpy package*.

Main features:
    - Detecting particles from tiff movies.
    - Combining particles into trajectories.
    - Create mp4 videos of the tiff files, with and without the trajectories.
    - Plot the trajectories in a graph.
    - Calculate and plot velocity distributions.
    - Calculate and plot the mean square displacements of the particles 
        (including 3 different filters)

Created on Wed Sep 30 2020
@author: L. de Haan

*(D.  Allan,   C.  van  der  Wel,   N.  Keim,   T.  A.  Caswell,   D.  Wieker,   
 R.  Verweij,C. Reid, Thierry, L. Grueter, K. Ramos, apiszcz, zoeith, 
 R. W. Perry, F. Boulogne,P. Sinha, pfigliozzi, N. Bruot, L. Uieda, J. Katins, 
 H. Mary, and A. Ahmadia, “soft-matter/trackpy:  Trackpy v0.4.2,” Oct. 2019.)
"""

import seaborn as sns
import numpy as np
import pandas as pd
import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pims
import trackpy as tp
import os


def directory_setup(filename_startswith, get_dir, save_dir):
    '''Find the files that start the given name. Then create a dataframe for
    all the get and save folder locations.    

    Parameters
    ----------
    filename_startswith : String, the name of the files for the analysis.
    get_dir : String, directory where to get the videos from.
    save_dir : String, directory where to save the analysis data.

    Returns
    -------
    paths : Dataframe with all get and save locations   
    '''
    paths_data = []
    directory = os.fsencode(get_dir)
        
    for file in os.listdir(directory):
         filename = os.fsdecode(file)
         if filename.startswith(filename_startswith): 
             paths_data.append([get_dir + filename, save_dir + filename + "\\"])
             continue
         else:
             continue
    
    paths = pd.DataFrame(paths_data, columns=['get', 'save'])
    
    return paths


def create_folder(path):
    '''Create a folder to save the analysis data.
    
    Parameters
    ----------
    path : String, directory folder location.
    '''
    # Create target directory & all intermediate directories if don't exists
    try:
        os.makedirs(path)    
        print("Directory " , path ,  " Created ")
    except FileExistsError:
        print("Directory " , path ,  " already exists")  


def get_dpi(frames):
    '''Get the dots per inch (dpi) from the given width and height.

    Parameters
    ----------
    frames : pims.TiffStack

    Returns
    -------
    dpi : integer, dots per inch
    '''
    dpi = 0
    width = 2560        # This is hardcoded and might be changed accordingly
    height = 2160       # This is hardcoded and might be changed accordingly
    if width > dpi:
        dpi = width
    elif height > dpi:
        dpi = height
    return dpi


def locate_particles(file_path, exp_max, psize, minmass):
    '''Read Tiff file, find particles in all video frames and link the particles
    into trajectories.

    Parameters
    ----------
    file_path : Dataframe with single "save" and "get" paths.
    exp_max : Integer, expected maximum speed of a particle (nm/s). Particles 
        that are faster, will not be detected.
    psize : Integer, particle size. Has to be an odd number.
    minmass : Integer, Trackpy measure to identify particles.

    Notes
    -----
    The trajectories with a length below a certain threshold (5 frames) are 
    considered eroneous and are removed.
    
    See also
    --------
    Trackpy for more information: 
    http://soft-matter.github.io/trackpy/v0.4.2/tutorial/walkthrough.html
    '''
    # Open the frames from file location (Tiff file)
    frames = pims.TiffStack(file_path['get'])
    mpp = 0.4630        # This is hardcoded and calculated from width of capillary (fits in hight of frame)
    
    # Find the particles
    particles = tp.batch(frames, psize, minmass=minmass, invert=True)
    
    # Link particles into trajectories
    frame_rate = 1/36.4407    # This is hardcoded an can be changed accordingly
    trajectories = tp.link(particles, (exp_max/mpp)*frame_rate, memory=3)
    
    timesteps = []
    for idx, trajectory in trajectories.iterrows():
        timesteps.append(trajectory['frame']*frame_rate)
    trajectories['time'] = timesteps
    
    # Filter noise (particles with short tracks)
    filtered_trajectories = tp.filter_stubs(trajectories,5)
    print('Before:', trajectories['particle'].nunique())
    print('After:', filtered_trajectories['particle'].nunique())
    filtered_trajectories.to_csv(file_path['save'] + "t1")

    return(frames, particles, filtered_trajectories)

    
def test_locations(file_path, psize, minmass, frame = 0):
    '''Find particles in the first video frame. 
    
    Parameters
    ----------
    file_path : Dataframe with single "save" and "get" paths.
    psize : Integer, particle size. Has to be an odd number.
    minmass : Integer, Trackpy measure to identify particles.
    frame : Integer, which frame to use as testframe.

    Returns
    -------
    None. Images of the located particles are in the specified directories.
    
    Notes
    -----
    This function is meant to see how the trackpy locate() behaves. By using 
    this function you can easily see which particles are located and tune the
    variables accordingly.
    
    See also
    --------
    get_dpi()
    Trackpy for more information:
    http://soft-matter.github.io/trackpy/v0.4.2/tutorial/walkthrough.html
    '''
    frames = pims.TiffStack(file_path['get'])
    dpi = get_dpi(frames)
    f = tp.locate(frames.get_frame(frame), psize, minmass=minmass, invert=True)
    fig, ax = plt.subplots()
    ax = tp.annotate(f, frames.get_frame(frame))
    for frame, particle in f.iterrows():
        ax.scatter(particle.x, particle.y, color = "#0000FF", s=(72./dpi)**2)
    plt.savefig(file_path['save'] + 'test_frame.png', dpi=dpi)
    
    fig, ax = plt.subplots()
    ax.hist(f['mass'], bins=20)
    ax.set(xlabel='mass', ylabel='count');
    plt.savefig(file_path['save'] + 'test_hist.png')
    
    plt.close('all')


def save_video(fig, ims, name, path, writer):
    ani = animation.ArtistAnimation(fig, ims, interval=50)
    ani.save(path + name, writer=writer)
    plt.close("all")    
    return


def make_videos(frames, particles, save_path):
    '''Make and save mp4 videos of the movie and the developing trajectories.

    Parameters
    ----------
    frames : TiffStack.
    particles : Dataframe containing each particle location.
    save_path : String, save directory location.

    Returns
    -------
    None. Two videos are saved in the specified directory:
        - An mp4 file of the TiffStack movie.
        - An mp4 file of the movie with developing trajectories.
        
    See also
    --------
    save_video()
    '''
    print("Making first video")
    fps = 36.4407       # This is hardcoded and can be changed accordingly
    writer = animation.FFMpegWriter(fps=fps)   # Framerate as indicated by andor software
    fig = plt.figure()
    
    ims = []
    count = 0
    width = 2
    dots = []
    
    for i in frames:
        new_dots = particles[particles['frame'] == count].loc[:, ['x', 'y', 'frame']].to_numpy()
    
        for new_dot in new_dots:
            dots.append(new_dot)
        
        for dot in dots:
            ymin = int(dot[0]) - width
            ymax = int(dot[0]) + width
            xmin = int(dot[1]) - width
            xmax = int(dot[1]) + width
            i[xmin:xmax, ymin:ymax] = 0
    
        im = plt.imshow(i)
        ims.append([im])
        count += 1
    
    print("Saving first video")
    save_video(fig, ims, 'trajectories.mp4', save_path, writer)
    print("First video saved!")
    
    print("Making second video")
    fig = plt.figure()
    ims2 = []
    for i in frames:
        im = plt.imshow(i)
        ims2.append([im])
        count += 1
    
    print("Saving second video")
    save_video(fig, ims2, 'animation.mp4', save_path, writer)
    print("Second video saved!")       
        
        
def save_velocity_distribution(speed, exp_max, title, path):
    df = pd.DataFrame({'nb' : speed})
    df.sort_values('nb')
    mean = sum(speed) / len(speed)
    
    fig, ax = plt.subplots()
    ax = sns.distplot(df['nb'])
    kdeline = ax.lines[0]
    xs = kdeline.get_xdata()
    ys = kdeline.get_ydata()
    height = np.interp(mean, xs, ys)
    ax.set(xlabel='speed [um/s]', ylabel='probability density', title=title);
    if max(speed) < exp_max:
        ax.set(xlim= (0,exp_max))
    else:
        ax.set(xlim= (0,max(speed)))
    ax.vlines(mean, 0, height, color='steelblue', ls=':')
    ax.annotate("mean="+str("{:.2f}".format(mean)), (mean,0))
    plt.savefig(path + '.png')
    plt.close("all")
        
    
def get_velocity_distribution(trajectories, mpp, exp_max, save_path):
    '''Calculate and save the instantaneous velocity distributions.

    Parameters
    ----------
    trajectories : Dataframe with all trajectories.
    mpp : Float, micron per pixel.
    exp_max : Integer, expected max speed.
    save_path : String, path to file save location.
    
    Returns
    -------
    None. Multiple graphs are saved in the specified directory:
        - One graph of the ensamble velocity distribution.
        - A graph for each particle with its velocity distribution.
    
    See also
    --------
    save_velocity_distribution()
    '''
    total_speed = []
    df = pd.DataFrame()
    
    for particle in trajectories.particle.unique():
        locations = trajectories[trajectories["particle"] == particle].loc[:, ['frame', 'x', 'y', 'time']]
        
        speed = []
        prev_frame, prev_x, prev_y, prev_t = locations.iloc[0]
        for frame, loc in locations.iloc[1:].iterrows():
            new_speed_f = math.sqrt((prev_x - loc['x'])**2 + (prev_y - loc['y'])**2) * mpp
            new_speed_s = new_speed_f / ((loc['time'] - prev_t))
            speed.append(new_speed_s) 
            total_speed.append(new_speed_s)
            
            prev_x = loc['x']
            prev_y = loc['y']
            prev_t = loc['time']
            
        df = pd.concat([df,pd.DataFrame({particle:speed})], axis=1)
        save_velocity_distribution(speed, exp_max, 'speed distribution, particle ' + str(particle), save_path + 'vd' + str(particle))
    
    df.to_csv(save_path + 'speed')
    save_velocity_distribution(total_speed, exp_max, 'total speed distribution', save_path + 'vd_all')
    return
        
        
def plot_trajectories(trajectories, frames, particles, save_path, video=True):
    '''Plot the trajectories.

    Parameters
    ----------
    trajectories : Dataframe containing all trajectories.
    save_path : String, save directory location.

    Returns
    -------
    None. Saves two graphs with all trajectories, in one of them the 
    trajectories are numbered. Also saves two videos, an mp4 file of the Tiff 
    movie and an mp4 file of the movie with developing trajectories.
    
    See also
    --------
    make_videos()
    '''
    fig = plt.figure()
    fig = tp.plot_traj(trajectories)
    fig.set_xlim([0, 2560])     # Hardcoded width of video, can be changed accordingly
    fig.set_ylim([2160, 0])     # Hardcoded height of video, can be changed accordingly
    plt.savefig(save_path + 'trajectories.png')
    
    for particle in trajectories.particle.unique():
        first_loc = trajectories[trajectories["particle"] == particle].head(1).loc[:, ['x', 'y']]
        plt.text(first_loc.x, first_loc.y, particle)
        
    plt.savefig(save_path + 'trajectories_numbered.png')
    
    if video:
        make_videos(frames, particles, save_path)
    
    
def filter_frame(trajectories, frames):
    '''Filter only the trajectories that start in the middle of the video 
    frame'''
    width = 2560        # This is hardcoded and can be changed accordingly
    height = 2160       # This is hardcoded and can be changed accordingly
    
    middle_particles = []
    for index, particle in trajectories[trajectories["frame"] == 0].iterrows():
        if (0.25*width < particle.x < 0.75*width) and (0.25*height < particle.y < 0.75*height):
            middle_particles.append(int(particle.particle))
    
    t = trajectories.loc[trajectories["particle"].isin(middle_particles)]
    
    counts = t.frame.value_counts()
    
    max_frame = counts[counts == len(middle_particles)].index.max()
    
    trajectories_filt = t[t.index <= max_frame]
    
    return(trajectories_filt)

     
def filter_ft(trajectories):
    '''Full trajectories. Filter only the particles that start and end in 
    the frame.'''
    frame_numbers = trajectories['frame'].unique()
    
    first_frame = frame_numbers[0]
    last_frame = frame_numbers[-1]
    
    first_frame_particles = trajectories[trajectories["frame"] == first_frame]['particle']
    last_frame_particles = trajectories[trajectories["frame"] == last_frame]['particle']
    
    same = set(first_frame_particles).intersection(last_frame_particles)
    
    trajectories_filt = trajectories.loc[trajectories['particle'].isin(same)]    
    
    return(trajectories_filt)


def save_msd(im, save_path):
    ''' Save the msd graph at the save_path location.''' 
    fig, ax = plt.subplots()
    ax.plot(im.index, im, 'k-', alpha=0.1)  # black lines, semitransparent
    ax.set(ylabel=r'$\langle \Delta r^2 \rangle$ [$um^2$]',
           xlabel='lag time $t$ [$s$]')
    im.to_csv(save_path)
    plt.savefig(save_path + '.png')
    
    
def get_msd(trajectories, frames, save_path, max_lagtime=10, EMSD="mean"):
    ''' Compute and save the MSD of all particles and the average MSD of the
    ensamble.

    Parameters
    ----------
    trajectories : Dataframe with all trajectories
    frames : TiffStack.
    save_path : string, the path to file save location
    max_lagtime : integer, maximum lag time in seconds. The default is 10.
    EMSD : {"mean", "emsd", "ft", "filt"}. The default is "mean". You can 
        chose which filter to use. 
        "mean": Calculate mean MSD only for particles which reach the max 
            lag time.
        "emsd": Use the emsd() function from trackpy. Calculate mean MSD for 
            all particles.
        "ft": Full trajectories. Calculate the mean MSD only for particles that
            stay in view.
        "frame": Calculate the mean MSD only for particles that start in the 
            middle of the video frame.
    
    Notes
    -----
    The individual MSDs are always calculated, the average MSD is calculated 
    in different ways. The graphs are saved at the save_path location.
    
    See also
    --------
    save_msd(), filter_ft() and filter_frame()
    '''
    fps = 36.4407        # frames/second. This is hardcoded and can be changed accordingly
    mpp = 0.4630         # micron/pixel. This is hardcoded and can be changed accordingly
    
    im1 = tp.imsd(trajectories, mpp, fps, max_lagtime=int(max_lagtime*fps)).dropna(axis=1)  
    save_msd(im1, save_path + "MSD")
    
    if EMSD=="mean":
        save_msd(im1.dropna(axis=1).mean(axis=1), save_path + "MSD_mean")
        
    elif EMSD=="emsd":
        im2 = tp.emsd(trajectories, mpp, fps)
        save_msd(im2, save_path + "MSD_ensamble")    
        
    elif EMSD=="ft":
        try:
            t_filt = filter_ft(trajectories)
            im3 = tp.imsd(t_filt, mpp, fps).dropna(axis=1)  
            save_msd(im3, save_path + "MSD_full_traj")
        except ValueError:
            print("No unbroken trajectories")
            
    elif EMSD=="frame":
        try:
            t_filt = filter_frame(trajectories, frames)
            im4 = tp.emsd(t_filt, mpp, fps)
            save_msd(im4, save_path + "MSD_Frame")
        except ValueError:
            print("No particles near the center")
            
    else:
        print("Mean square displacement filter not correctly defined.")
        
        
def remove_trajectories(trajectories, remove, file_path):
    '''Remove trajectories that should not be taken into account in the analysis.

    Parameters
    ----------
    trajectories : Dataframe containing all trajectories.
    remove : List containing all particle numbers that should be removed.
    file_path : string, the path to the save directory

    Returns
    -------
    Trajectories, the new dataframe without the removed trajectories.
    '''
    remove.sort()
    pd.DataFrame(remove).to_csv(file_path['save'] + "removed")
    
    for p in remove:
        trajectories = trajectories[trajectories.particle != p]    
    return(trajectories)


def combine_csv(get_paths, file):
    '''Combine dataframes for the combine() function.'''
    df = pd.DataFrame()
    for path in get_paths:
        df = pd.concat([df,pd.read_csv(path + file, index_col=0)], axis=1) 
    return df


def combine(paths, save_dir, filenames, exp_max):
    ''' Combine the MSD and velocity distributions of multple samples.

    Parameters
    ----------
    paths : Dataframe with all sample data directories
    save_dir : string, the path to file save location
    filenames : string, filename_startswith
    exp_max : integer, expected maximum velocity
    
    See also
    --------
    create_folder(), combine_csv(), save_velocity_distribution() 
    and save_msd()
    '''
    total_path = save_dir + filenames + '_Total'
    create_folder(total_path)    
    
    # total speed distribution
    all_speed_df = combine_csv(paths['save'].tolist(), "speed")
    all_speed_df.to_csv(total_path + '\\speed')
    all_speed = []
    for x in all_speed_df.values.tolist():
        for y in x:
            if str(y) != 'nan':
                all_speed.append(y)
    save_velocity_distribution(all_speed, exp_max, 'total speed distribution', total_path + '\\vd_all')
    
    # total msd
    all_msd =  combine_csv(paths['save'].tolist(), "msd")
    all_msd.to_csv(total_path + '\\msd')
    save_msd(all_msd, total_path + '\\msd')
    save_msd(all_msd.dropna(axis=1).mean(axis=1), total_path + "\\MSD_mean")
