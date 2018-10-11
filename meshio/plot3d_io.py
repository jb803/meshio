# -*- coding: utf-8 -*-
#
"""
I/O for the PLOT3D format
<https://www.grc.nasa.gov/www/wind/valid/plot3d.html>.
"""

import gzip
import logging
import numpy

from .mesh import Mesh

def read(filename):
    """Reads a Plot3d  mesh file.
    """

    opener = gzip.open if filename.endswith(".gz") else open

    with opener(filename, "rb") as f:
        out = read_buffer(f)
    return out

def read_buffer(f):
    """We read the (assumed) ASCII, plot3d file. We detect the number
    of elements in the first two lines to determine whether it is a
    multiblock mesh and the dimension"""

    #We assume we have a multiblock file that is 2d.
    #TODO: try and work out what the format of the file is

    tokens = f.read().split()

    format_hint = sum([1  for tok in tokens[0:4] if tok.isdigit()]) #We try and guess the format based on the number of integer tokens at the file start

    if format_hint == 0:
        raise Exception('Badly formatted plot3d file')
    elif format_hint == 1:
        #The only sensible interpretation is a 1D mesh
        n_blocks = 1
        mesh_dim = 1
        grid_dim = [int(tokens[0])]

        raise Exception('Cannot do 1D meshes at the moment')

    elif format_hint == 2:
        #A multiblock 1d mesh doesn't make sense so this must be a single block 2D mesh
        n_blocks = 1
        mesh_dim = 2 
        grid_dim = [int(tokens[0]), int(tokens[1])]
    elif format_hint == 3:
        #This is the tricky case. We assume that all 3D meshes are going to be multiblock. So this is a multiblock 2d mesh
        n_blocks = int(tokens[0])
        mesh_dim = 2
        grid_dim = [int(tokens[1]), int(tokens[2])]
    elif format_hint == 4:
        #has to be a mutliblock 3d mesh
        n_blocks = int(tokens[0])
        mesh_dim = 3
        grid_dim = [int(tok) for tok in tokens[1:4]]

        raise Exception('Cannot do 3d meshes at the moment')
    else:
        raise Exception('Badly formatted plot3d file')

    offset = format_hint

    assert n_blocks == 1 #Currently we only do 1 block plot3d meshes

    #We now load the point data
    n_points = numpy.prod(grid_dim)

    points = numpy.zeros([n_points,mesh_dim])
    for point_index in range(n_points):
        x_index     = offset + point_index
        y_index     = offset + n_points + point_index

        points[point_index,:] = [float(tokens[x_index]), float(tokens[y_index])]

    n_cells = (grid_dim[0]-1)*(grid_dim[1]-1)*2 #we split into triangles

    cells = numpy.zeros([n_cells,3],dtype=int) #4 as they're quads

    for cell_index in range(n_cells//2):
        row         = cell_index//(grid_dim[0]-1)
        row_offset  = cell_index% (grid_dim[0]-1)


        bottom_left_index = row_offset + row*grid_dim[0]
        top_left_index    = row_offset + (row+1)*grid_dim[0]

        print(bottom_left_index)

        cells[2*cell_index  ,:]  = [bottom_left_index, bottom_left_index+1, top_left_index]
        cells[2*cell_index+1,:]  = [bottom_left_index+1,top_left_index+1,top_left_index]

    cellDict = {'triangle':cells}

    return Mesh(points,cellDict)


        