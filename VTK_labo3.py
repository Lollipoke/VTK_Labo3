#!/usr/bin/env python
#
# Labo 3
# Le but de ce laboratoire est de générer une visualisation d'un genou
#
# Auteurs: Mélissa Gehring et Tania Nunez 

import vtk

LIGHT_RED = [1.0, 0.8, 0.8]
LIGHT_GREEN = [0.8, 1.0, 0.8]
LIGHT_BLUE = [0.8, 0.8, 1.0]
LIGHT_GREY = [0.8, 0.8, 0.8]
UGLY_YELLOW = [1, 0.82, 0.37]
BONE_COLOR = [0.90, 0.90, 0.90]
BLACK = [0.0, 0.0, 0.0]

# Define viewport ranges.
xmins = [0.0, 0.5, 0.0, 0.5]
xmaxs = [0.5, 1.0, 0.5, 1.0]
ymins = [0.5, 0.5, 0.0, 0.0]
ymaxs = [1.0, 1.0, 0.5, 0.5]

# 0: top left, 1: top right, 2: bottom left, 3: bottom right
renBkg = [LIGHT_RED, LIGHT_GREEN, LIGHT_BLUE, LIGHT_GREY]

renderWindow = vtk.vtkRenderWindow()
interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(renderWindow)
interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())

# Interactor
intWin= vtk.vtkRenderWindowInteractor()
intWin.SetRenderWindow(renderWindow)
style = vtk.vtkInteractorStyleTrackballCamera()
intWin.SetInteractorStyle(style)

camera = vtk.vtkCamera()

# Creating each viewport, top left, top right, bottom left, bottom right
for i in range(4):

    renderer = vtk.vtkRenderer()

    renderWindow.AddRenderer(renderer)
    renderer.SetViewport(xmins[i], ymins[i], xmaxs[i], ymaxs[i])

    # Share the camera between viewports.
    if i == 0:
        camera = renderer.GetActiveCamera()
        camera.SetPosition(0.0, -1.0, 0.0)
        camera.SetViewUp(0.0, 0.0, -1.0)
    else:
        renderer.SetActiveCamera(camera)

    #for actor in renActors[i]:
    #    renderer.AddActor(actor)

    renderer.SetBackground(renBkg[i])
    renderer.ResetCamera()

# Initialisation et démarrage de l'interactor
intWin.Initialize()
intWin.Start()