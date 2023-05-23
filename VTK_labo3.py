#!/usr/bin/env python
#
# Labo 3
# Le but de ce laboratoire est de générer une visualisation d'un genou contenant 4 viewports :
# Dans la fenêtre en haut à droite, on voit l'os et la peau en couleurs réalistes. La peau est semi-transparente sur la face avant et opaque sur la face arrière. Elle est clippée par une sphère de manière à laisser voir l'articulation.
# Dans la fenêtre en bas à gauche, la peau est entièrement opaque et la sphère utilisée pour la clipper est visible en transparence.
# Dans la fenêtre en haut à gauche, la peau n'est visible que sous la forme de tubes coupant la surface de la peau horizontalement tous les centimètres.
# Enfin, dans la fenêtre en bas à droite, on ne voit que la surface de l'os, mais celle-ci est colorisée de manière à visualiser la distance entre chaque point de l'os et la peau. Comme la génération de cette donnée de distance est assez lente, je vous encourage vivement à en stocker le résultat dans un fichier .vtk et à ne pas la régénérer à chaque fois. Laissez les deux possibilités disponibles dans votre code.
#
# Auteurs: Mélissa Gehring et Tania Nunez 

import vtk
import os.path
SKIN_COLOR = [0.77, 0.61, 0.60]

SPHERE_CENTER = [70, 40, 100]
SPHERE_RADIUS = 45

SCANER_FILE_NAME = "data/vw_knee.slc"
BONE_SURFACE_SAVE_FILE_NAME = "bone_save.vtk"

LIGHT_RED = [1.0, 0.8, 0.8]
LIGHT_GREEN = [0.8, 1.0, 0.8]
LIGHT_BLUE = [0.8, 0.8, 1.0]
LIGHT_GREY = [0.8, 0.8, 0.8]
SPHERE_YELLOW = [1, 0.82, 0.37]
BONE_COLOR = [0.90, 0.90, 0.90]
BLACK = [0.0, 0.0, 0.0]

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 800
WINDOW_NAME = "Knee Scanner"

STRIP_COUNT = 19
STRIP_RADIUS = 2

DIST_MIN_SKIN = 2

# Lecture du fichier SLC
slcReader = vtk.vtkSLCReader()
slcReader.SetFileName(SCANER_FILE_NAME)

# Acteur de la boîte englobante
boxOutlineFilter = vtk.vtkOutlineFilter()
boxOutlineFilter.SetInputConnection(slcReader.GetOutputPort())

boxPolyDataMapper = vtk.vtkPolyDataMapper()
boxPolyDataMapper.SetInputConnection(boxOutlineFilter.GetOutputPort())

boxActor = vtk.vtkActor()
boxActor.SetMapper(boxPolyDataMapper)
boxActor.GetProperty().SetColor(BLACK)

# Topologie de la peau
skinContourFilter = vtk.vtkContourFilter()
skinContourFilter.SetInputConnection(slcReader.GetOutputPort())
# Valeur trouvée par tatônnement
skinContourFilter.SetValue(0, 50)

# Mapper de la peau, clippée par une sphère
sphere = vtk.vtkSphere()
sphere.SetRadius(SPHERE_RADIUS)
sphere.SetCenter(SPHERE_CENTER)

clippedSkinPolyData = vtk.vtkClipPolyData()
clippedSkinPolyData.SetClipFunction(sphere)
clippedSkinPolyData.SetInputConnection(skinContourFilter.GetOutputPort())

clippedSkinPolyDataMapper = vtk.vtkPolyDataMapper()
clippedSkinPolyDataMapper.SetInputConnection(clippedSkinPolyData.GetOutputPort())
clippedSkinPolyDataMapper.ScalarVisibilityOff()

# Acteur de l'os de couleur grise
boneContourFilter = vtk.vtkContourFilter()
boneContourFilter.SetInputConnection(slcReader.GetOutputPort())

bonePolyDataMapper = vtk.vtkPolyDataMapper()
bonePolyDataMapper.SetInputConnection(boneContourFilter.GetOutputPort())
bonePolyDataMapper.ScalarVisibilityOff()



boneActor = vtk.vtkActor()
boneActor.SetMapper(bonePolyDataMapper)
boneActor.GetProperty().SetColor(BONE_COLOR)

def upper_left_viewport_actors(): # Genou avec os en gris et peau en tubes
    # Plan à découper
    plane = vtk.vtkPlane()

    # Mapper de la peau
    skinPolyDataMapper = vtk.vtkPolyDataMapper()
    skinPolyDataMapper.SetInputConnection(skinContourFilter.GetOutputPort())
    skinPolyDataMapper.ScalarVisibilityOff()

    # Cutter pour clipper la sphère dans la peau
    cutter = vtk.vtkCutter()
    cutter.SetInputData(skinPolyDataMapper.GetInput())
    cutter.SetCutFunction(plane)
    cutter.GenerateValues(STRIP_COUNT, boxActor.GetBounds()[-2], boxActor.GetBounds()[-1])

    # Création des segments du triangle
    stripper = vtk.vtkStripper()
    stripper.SetInputConnection(cutter.GetOutputPort())
    stripper.JoinContiguousSegmentsOn()

    # Création des tubes autour des lignes du stripper
    tubeFilter = vtk.vtkTubeFilter()
    tubeFilter.SetRadius(STRIP_RADIUS)
    tubeFilter.SetInputConnection(stripper.GetOutputPort())

    # Mapper des tubes
    tubesPolyDataMapper = vtk.vtkPolyDataMapper()
    tubesPolyDataMapper.ScalarVisibilityOff()
    tubesPolyDataMapper.SetInputConnection(tubeFilter.GetOutputPort())

    # Acteurs des tubes
    tubesActor = vtk.vtkActor()
    tubesActor.SetMapper(tubesPolyDataMapper)
    tubesActor.GetProperty().SetColor(SKIN_COLOR)

    return [boxActor, boneActor, tubesActor]

def top_right_viewport_actors(): # Genou avec os en gris et peau clippé par une sphère transparente
    # Acteur de la peau transparente devant le genou et opaque derrière
    skinActor = vtk.vtkActor()
    skinActor.SetMapper(clippedSkinPolyDataMapper)
    skinActor.GetProperty().SetColor(SKIN_COLOR)
    skinActor.GetProperty().SetOpacity(0.4)
    skinActor.SetBackfaceProperty(skinActor.MakeProperty())
    skinActor.GetBackfaceProperty().SetColor(SKIN_COLOR)

    return [boxActor, boneActor, skinActor]

def bottom_lef_viewport_actors(): # Genou avec peau opaque et clippé par une sphère jaune
    # Acteur pour la peau
    skinActor = vtk.vtkActor()
    skinActor.SetMapper(clippedSkinPolyDataMapper)
    skinActor.GetProperty().SetColor(SKIN_COLOR)

    # https://python.hotexamples.com/fr/examples/vtk/-/vtkSampleFunction/python-vtksamplefunction-function-examples.html
    # Conversion de fonction implicite à polydata et utilisation d'une fonction explicite en choisissant les contours
    sphereSampleFunction = vtk.vtkSampleFunction()
    sphereSampleFunction.SetImplicitFunction(sphere)

    sphereBounds = []

    for c in SPHERE_CENTER:
        sphereBounds.append(c - SPHERE_RADIUS)
        sphereBounds.append(c + SPHERE_RADIUS)

    sphereSampleFunction.SetModelBounds(sphereBounds)

    # Création d'un filtre pour définir les contours de la sphère
    contourFilter = vtk.vtkContourFilter()
    contourFilter.SetInputConnection(sphereSampleFunction.GetOutputPort())

    # PolyDataMapper
    spherePolyDataMapper = vtk.vtkPolyDataMapper()
    spherePolyDataMapper.SetInputConnection(contourFilter.GetOutputPort())
    spherePolyDataMapper.ScalarVisibilityOff()

    # Création de l'acteur qui utilise ce mapper
    sphereActor = vtk.vtkActor()
    sphereActor.SetMapper(spherePolyDataMapper)
    sphereActor.GetProperty().SetOpacity(0.3)
    sphereActor.GetProperty().SetColor(SPHERE_YELLOW)

    return [boxActor, boneActor, skinActor, sphereActor]

def bottom_right_viewport_actors():

    bonePolyDataMapper = vtk.vtkPolyDataMapper()


    if os.path.exists(BONE_SURFACE_SAVE_FILE_NAME):

        # Lecture des polydata de l'os
        bonePolyDataReader = vtk.vtkPolyDataReader()
        bonePolyDataReader.SetFileName(BONE_SURFACE_SAVE_FILE_NAME)
        bonePolyDataReader.ReadAllScalarsOn()
        bonePolyDataReader.Update()

        # Création du mapper de l'os
        bonePolyDataMapper.SetInputConnection(bonePolyDataReader.GetOutputPort())
        bonePolyDataMapper.SetScalarRange(bonePolyDataReader.GetOutput().GetScalarRange())

    else:

        # Calcul the la plus courte distance de chaque segment de l'os à la peau
        # https://kitware.github.io/vtk-examples/site/Cxx/PolyData/DistancePolyDataFilter/
        distancePolyDataFilter = vtk.vtkDistancePolyDataFilter()
        distancePolyDataFilter.SignedDistanceOff()
        distancePolyDataFilter.SetInputConnection(0, boneContourFilter.GetOutputPort())
        distancePolyDataFilter.SetInputConnection(1, skinContourFilter.GetOutputPort())
        distancePolyDataFilter.Update()

        # Sauvegarde du fichier au format vtk pour ne pas avoir à recalculer toutes les distances
        # Le calcul ci-dessus prend quelques minutes
        bonePolyDataWriter = vtk.vtkPolyDataWriter()
        bonePolyDataWriter.SetFileName(BONE_SURFACE_SAVE_FILE_NAME)
        bonePolyDataWriter.SetFileTypeToBinary()
        bonePolyDataWriter.SetInputConnection(distancePolyDataFilter.GetOutputPort())
        bonePolyDataWriter.Write()

        # Création du mapper de l'os
        bonePolyDataMapper.SetInputConnection(distancePolyDataFilter.GetOutputPort())
        bonePolyDataMapper.SetScalarRange(distancePolyDataFilter.GetOutput().GetScalarRange())

    # Making bone actor
    boneActor = vtk.vtkActor()
    boneActor.SetMapper(bonePolyDataMapper)

    return [boxActor, boneActor]

# Création de la grille 2x2 de viewports selon l'exemple
# https://kitware.github.io/vtk-examples/site/Cxx/Visualization/MultipleViewports/

# Intervalle des viewports
xmins = [0.0, 0.5, 0.0, 0.5]
xmaxs = [0.5, 1.0, 0.5, 1.0]
ymins = [0.5, 0.5, 0.0, 0.0]
ymaxs = [1.0, 1.0, 0.5, 0.5]

# Viewports de gauche à droite, haut en bas
renBkg = [LIGHT_RED, LIGHT_GREEN, LIGHT_BLUE, LIGHT_GREY]

# Génération des actors pour chaque viewport
renActors = [upper_left_viewport_actors(),
             top_right_viewport_actors(),
             bottom_lef_viewport_actors(),
             bottom_right_viewport_actors()]

# Génération de la fenêtre d'affichage
window = vtk.vtkRenderWindow()
interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(window)
interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())

camera = vtk.vtkCamera()

# Création des viewports
for i in range(4):

    renderer = vtk.vtkRenderer()

    window.AddRenderer(renderer)
    renderer.SetViewport(xmins[i], ymins[i], xmaxs[i], ymaxs[i])

    if i == 0: # Même caméra pour tous les viewports
        camera = renderer.GetActiveCamera()
        camera.SetPosition(0.0, -1.0, 0.0)
        camera.SetViewUp(0.0, 0.0, -1.0)
    else:
        renderer.SetActiveCamera(camera)

    for actor in renActors[i]:
        renderer.AddActor(actor)

    renderer.SetBackground(renBkg[i])
    renderer.ResetCamera()

# Affichage
window.SetWindowName(WINDOW_NAME)
window.SetSize(WINDOW_WIDTH, WINDOW_HEIGHT)

interactor.Initialize()
window.Render()
interactor.Start()
