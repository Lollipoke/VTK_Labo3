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

# =========================== CONSTANTES ============================= #

# Fichiers
SCANNER_FILE = "data/vw_knee.slc"
BONE_FILE = "bones.vtk"

# Couleurs
RED = [1.0, 0.8, 0.8]
GREEN = [0.8, 1.0, 0.8]
BLUE = [0.8, 0.8, 1.0]
GREY = [0.8, 0.8, 0.8]
YELLOW = [1, 0.83, 0.39]
BONE = [0.90, 0.90, 0.90]
SKIN = [0.76, 0.60, 0.61]
BLACK = [0.0, 0.0, 0.0]

# Paramètres de la fenêtre
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 800
WINDOW_NAME = "Knee Scanner"

# Paramètres de la sphère du genou
SPHERE_CENTER = [70, 40, 100]
SPHERE_RADIUS = 50

# Intervalle des viewports
XMIN = [0.0, 0.5, 0.0, 0.5]
XMAX = [0.5, 1.0, 0.5, 1.0]
YMIN = [0.5, 0.5, 0.0, 0.0]
YMAX = [1.0, 1.0, 0.5, 0.5]

# Couleur de fond de gauche à droite, haut en bas
BKG = [RED, GREEN, BLUE, GREY]

# Constantes diverses
STRIP_NUM = 19
STRIP_SIZE = 2
SKIN_FILTER = 50
BONE_FILTER = 72


# =========================== METHODS ============================= #


# Retourne un filter de type contour pour une valeur donnée
def get_contour_filter(reader, filter_value):
    contourFilter = vtk.vtkContourFilter()
    contourFilter.SetInputConnection(reader.GetOutputPort())
    contourFilter.SetValue(0, filter_value)
    return contourFilter

# Création de la boîte englobante
def create_box_actor(reader):
    boxFilter = vtk.vtkOutlineFilter()
    boxFilter.SetInputConnection(reader.GetOutputPort())

    boxMapper = vtk.vtkPolyDataMapper()
    boxMapper.SetInputConnection(boxFilter.GetOutputPort())

    boxActor = vtk.vtkActor()
    boxActor.SetMapper(boxMapper)
    boxActor.GetProperty().SetColor(BLACK)

    return boxActor

# Genou avec os en gris et peau en tubes
def top_left_actors(): 
    # Plan à découper
    plane = vtk.vtkPlane()

    # Mapper de la peau
    skinMapper = vtk.vtkPolyDataMapper()
    skinMapper.SetInputConnection(skinContourFilter.GetOutputPort())
    skinMapper.ScalarVisibilityOff()

    # Cutter pour clipper le plan dans la peau
    cutter = vtk.vtkCutter()
    cutter.SetInputData(skinMapper.GetInput())
    cutter.SetCutFunction(plane)
    cutter.GenerateValues(STRIP_NUM, boxActor.GetBounds()[-2], boxActor.GetBounds()[-1])

    # Création des segments du triangle
    stripper = vtk.vtkStripper()
    stripper.SetInputConnection(cutter.GetOutputPort())
    stripper.JoinContiguousSegmentsOn()

    # Création des tubes autour des lignes du stripper
    tubeFilter = vtk.vtkTubeFilter()
    tubeFilter.SetRadius(STRIP_SIZE)
    tubeFilter.SetInputConnection(stripper.GetOutputPort())

    # Mapper des tubes
    tubesPolyDataMapper = vtk.vtkPolyDataMapper()
    tubesPolyDataMapper.ScalarVisibilityOff()
    tubesPolyDataMapper.SetInputConnection(tubeFilter.GetOutputPort())

    # Acteurs des tubes
    tubesActor = vtk.vtkActor()
    tubesActor.SetMapper(tubesPolyDataMapper)
    tubesActor.GetProperty().SetColor(SKIN)

    return [tubesActor]

def top_right_actors(): # Genou avec os en gris et peau clippé par une sphère transparente
    # Acteur de la peau transparente devant le genou et opaque derrière
    skinActor = vtk.vtkActor()
    skinActor.SetMapper(clippedSkinMapper)
    skinActor.GetProperty().SetColor(SKIN)
    skinActor.GetProperty().SetOpacity(0.4)
    skinActor.SetBackfaceProperty(skinActor.MakeProperty())
    skinActor.GetBackfaceProperty().SetColor(SKIN)

    return [skinActor]

def bottom_left_actors(): # Genou avec peau opaque et clippé par une sphère jaune
    # Acteur pour la peau
    skinActor = vtk.vtkActor()
    skinActor.SetMapper(clippedSkinMapper)
    skinActor.GetProperty().SetColor(SKIN)

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
    sphereActor.GetProperty().SetColor(YELLOW)

    return [skinActor, sphereActor]

def bottom_right_actors():
    # Lit le fichier contenant les distances à la peau si il existe, sinon le crée
    inputConnection = None
    if os.path.exists(BONE_FILE):
        # Lecture des données
        boneReader = vtk.vtkPolyDataReader()
        boneReader.SetFileName(BONE_FILE)
        boneReader.ReadAllScalarsOn()
        boneReader.Update()

        inputConnection = boneReader
    else:
        # Calcule la distance entre la peau et l'os
        # https://kitware.github.io/vtk-examples/site/Cxx/PolyData/DistancePolyDataFilter/
        distancePolyDataFilter = vtk.vtkDistancePolyDataFilter()
        distancePolyDataFilter.SignedDistanceOff()
        distancePolyDataFilter.SetInputConnection(0, boneContourFilter.GetOutputPort())
        distancePolyDataFilter.SetInputConnection(1, skinContourFilter.GetOutputPort())
        distancePolyDataFilter.Update()

        # Sauve les données dans un fichier pour ne pas avoir à les recalculer
        bonePolyDataWriter = vtk.vtkPolyDataWriter()
        bonePolyDataWriter.SetFileName(BONE_FILE)
        bonePolyDataWriter.SetFileTypeToBinary()
        bonePolyDataWriter.SetInputConnection(distancePolyDataFilter.GetOutputPort())
        bonePolyDataWriter.Write()

        inputConnection = distancePolyDataFilter

    # Mapper de la distance
    distanceMapper = vtk.vtkPolyDataMapper()
    distanceMapper.SetInputConnection(inputConnection.GetOutputPort())
    distanceMapper.SetScalarRange(inputConnection.GetOutput().GetScalarRange())

    # Acteur de l'os coloré
    coloredBoneActor = vtk.vtkActor()
    coloredBoneActor.SetMapper(distanceMapper)

    return [coloredBoneActor]

# ======================== MAIN ============================ #

# Lecture du fichier SLC
reader = vtk.vtkSLCReader()
reader.SetFileName(SCANNER_FILE)
reader.Update()


# Topologie de la peau
skinContourFilter = get_contour_filter(reader, SKIN_FILTER)


# Sphere pour le clipping de la peau
sphere = vtk.vtkSphere()
sphere.SetRadius(SPHERE_RADIUS)
sphere.SetCenter(SPHERE_CENTER)

# Mapper de la peau
clippedSkinPolyData = vtk.vtkClipPolyData()
clippedSkinPolyData.SetClipFunction(sphere)
clippedSkinPolyData.SetInputConnection(skinContourFilter.GetOutputPort())

clippedSkinMapper = vtk.vtkPolyDataMapper()
clippedSkinMapper.SetInputConnection(clippedSkinPolyData.GetOutputPort())
clippedSkinMapper.ScalarVisibilityOff()


# Topologie de l'os
boneContourFilter = get_contour_filter(reader, BONE_FILTER)

# Mapper de l'os
boneMapper = vtk.vtkPolyDataMapper()
boneMapper.SetInputConnection(boneContourFilter.GetOutputPort())
boneMapper.ScalarVisibilityOff()

# Acteur de l'os gris
boneActor = vtk.vtkActor()
boneActor.SetMapper(boneMapper)
boneActor.GetProperty().SetColor(BONE)

# Acteur de la boîte englobante
boxActor = create_box_actor(reader)

# Génération de la fenêtre d'affichage
window = vtk.vtkRenderWindow()
interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(window)
interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())

# Création de la caméra
camera = vtk.vtkCamera()

# Génération des actors pour chaque viewport
renActors = [top_left_actors(),
             top_right_actors(),
             bottom_left_actors(),
             bottom_right_actors()]

# Création de la grille 2x2 de viewports selon l'exemple
# https://kitware.github.io/vtk-examples/site/Cxx/Visualization/MultipleViewports/
# Création des viewports
for i in range(4):
    renderer = vtk.vtkRenderer()

    window.AddRenderer(renderer)
    renderer.SetViewport(XMIN[i], YMIN[i], XMAX[i], YMAX[i])

    if i == 0: # Même caméra pour tous les viewports
        camera = renderer.GetActiveCamera()
        camera.SetPosition(0.0, -1.0, 0.0)
        camera.SetViewUp(0.0, 0.0, -1.0)
    else:
        renderer.SetActiveCamera(camera)

    # Ajout des actors
    for actor in renActors[i]:
        renderer.AddActor(actor)
    renderer.AddActor(boxActor)
    if i != 3: # Pas d'os gris pour le viewport du bas à droite
        renderer.AddActor(boneActor)

    renderer.SetBackground(BKG[i])
    renderer.ResetCamera()

# Affichage
window.SetWindowName(WINDOW_NAME)
window.SetSize(WINDOW_WIDTH, WINDOW_HEIGHT)

interactor.Initialize()
window.Render()
interactor.Start()
