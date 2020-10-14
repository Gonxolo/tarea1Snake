"""
Este archivo generaría todos los modelos que tiene la aplicación. En programas más complicados
tendríamos una cosa así:

src/models/actor/chansey.py
src/models/actor/egg.py
src/models/factory/eggcreator.py

...
Y este archivo sería algo como
src/models/model.py --> sólo importaría los objetos que usa el resto de la aplicación, sin tocar el detalle mismo

from src.models.actor.chansey import Chansey
from src.models.actor.factory import EggCreator
...

Pero aquí, como nuestra app es sencilla, definimos todas las clases aquí mismo.
1. Chansey
2. Los huevos
"""

import transformations as tr
import basic_shapes as bs
import scene_graph as sg
import easy_shaders as es
import glfw

from OpenGL.GL import *
import random
from typing import List


class Snake(object):

    def __init__(self):
        # Figuras básicas
        gpu_head_quad = es.toGPUShape(bs.createTextureQuad("img/snake.png"), GL_REPEAT, GL_NEAREST)#es.toGPUShape(bs.createColorQuad(0.0, 1.0, 0.0))  # rojo

        head = sg.SceneGraphNode('head')
        head.transform = tr.uniformScale(1)
        head.childs += [gpu_head_quad]

        body = sg.SceneGraphNode('body')
        body.transform = tr.uniformScale(1)
        #body.childs += [gpu_body_quad]

        player = sg.SceneGraphNode('snok')
        player.transform = tr.matmul([tr.scale(1/6, 1/6, 0), tr.translate(0, 0, 0)])
        player.childs += [head]

        transform_player = sg.SceneGraphNode('snokTR')
        transform_player.childs += [player]

        self.model = transform_player
        self.pos_x = 1/12
        self.pos_y = 1/12
        self.v_x = 0
        self.v_y = 1/6
    
    def draw(self, pipeline):
        self.model.transform = tr.translate(self.pos_x, self.pos_y, 0)
        sg.drawSceneGraphNode(self.model, pipeline, "transform")

    def movement(self, dt):
        self.pos_y = self.pos_y + self.v_y*dt
        self.pos_x = self.pos_x + self.v_x*dt

    def move_left(self):
        if self.v_x != 0:
            return
        self.v_y = 0
        #self.pos_x = -1/10
        self.v_x = -1/6

    def move_right(self):
        if self.v_x != 0:
            return
        self.v_y = 0
        #self.pos_x = 1/10
        self.v_x = 1/6    

    def move_up(self):
        if self.v_y != 0:
            return
        self.v_x = 0
        #self.pos_y = -1/10
        self.v_y = 1/6

    def move_down(self):
        if self.v_y != 0:
            return
        self.v_x = 0
        #self.pos_y = -1/10
        self.v_y = -1/6

    def collide(self, apples: 'ApplePlacer'):
        deleted_apples = []
        for a in apples.apples:
            if (a.pos_y - 0.1 < self.pos_y < a.pos_y + 0.1) and (a.pos_x - 0.1 < self.pos_x < a.pos_x + 0.1):
                deleted_apples.append(a)
                print("A")
        apples.delete(deleted_apples)


class Tile(object):

    def __init__(self):
        # Figuras básicas
        gpu_tile_quad = es.toGPUShape(bs.createTextureQuad("img/background_tile.png"), GL_REPEAT, GL_NEAREST)

        tile = sg.SceneGraphNode('snok')
        tile.transform = tr.scale(2/6, 2/6, 0)
        tile.childs += [gpu_tile_quad]

        transform_tile = sg.SceneGraphNode('tileTR')
        transform_tile.childs += [tile]

        self.model = transform_tile
    
    def draw(self, pipeline, c_x=0, c_y = 0):
        self.model.transform = tr.translate(-1+(c_x+1)*2/6, 1-(c_y+1)*2/6, 0)
        sg.drawSceneGraphNode(self.model, pipeline, "transform")


class Background(object):

    tiles: List['Tile']
    def __init__(self):
        self.tiles = []
    
    def place_tile(self):
        for i in range(25):
            self.tiles.append(Tile())

    def draw(self, pipeline):
        c_x = 0
        c_y = 0
        for k in self.tiles:
            k.draw(pipeline, c_x%5, c_y)
            c_x += 1
            c_y = c_x//5


class Apple(object):

    def __init__(self):
        #gpu_apple = es.toGPUShape(bs.createColorQuad(0.7, .7, .7))
        gpuBoo = es.toGPUShape(bs.createTextureQuad("img/boo.png"), GL_REPEAT, GL_NEAREST)

        apple = sg.SceneGraphNode('apple')
        apple.transform = tr.scale(1/6, 1/6, 1)
        apple.childs += [gpuBoo]

        apple_tr = sg.SceneGraphNode('appleTR')
        apple_tr.childs += [apple]

        self.pos_y = random.randint(-5,4) * 1/6 + 1/12
        self.pos_x = random.randint(-5,4) * 1/6 + 1/12 # LOGICA
        self.model = apple_tr

    def draw(self, pipeline):
        self.model.transform = tr.translate(self.pos_x, self.pos_y, 0)
        sg.drawSceneGraphNode(self.model, pipeline, "transform")


class ApplePlacer(object):
    apples: List['Apple']

    def __init__(self):
        self.apples = []

    def draw(self, pipeline):
        for k in self.apples:
            #k.eaten()
            k.draw(pipeline)
    
    def create_apple(self):
        if len(self.apples) >= 1:  # No puede haber un máximo de 10 huevos en pantalla
            return
        else:
            self.apples.append(Apple())

    def delete(self, d):
        if len(d) == 0:
            return
        remain_apples = []
        for k in self.apples:  # Recorro todos los huevos
            if k not in d:  # Si no se elimina, lo añado a la lista de huevos que quedan
                remain_apples.append(k)
        self.apples = remain_apples  # Actualizo la lista

class StrongTile(object):
    def __init__(self):
        #Tiles
        gpu_strong_tile = es.toGPUShape(bs.createColorQuad(0, 0.2, 0.8)) #strong

        strong_tile = sg.SceneGraphNode('strong_tile')
        strong_tile.transform = tr.scale(1/10, 1/10, 0)
        strong_tile.childs += [gpu_strong_tile]

        self.model = strong_tile

    def draw(self, pipeline):
        sg.drawSceneGraphNode(self.model, pipeline, 'transform')


class WeakTile(object):
    def __init__(self):
        #Tiles
        gpu_weak_tile = es.toGPUShape(bs.createColorQuad(0, 0.1, 0.4)) #weak

        weak_tile = sg.SceneGraphNode('weak_tile')
        weak_tile.transform = tr.scale(1/10, 1/10, 0)
        weak_tile.childs += [gpu_weak_tile]
        
        self.model = weak_tile

    def draw(self, pipeline):
        sg.drawSceneGraphNode(self.model, pipeline, 'transform')


class BorderTile(object):
    def __init__(self):
        #Tiles
        gpu_border_tile = es.toGPUShape(bs.createColorQuad(0, 0.8, 0)) #border

        border_tile = sg.SceneGraphNode('border_tile')
        border_tile.transform = tr.scale(1/10, 1/10, 0)
        border_tile.childs += [gpu_border_tile]
        
        self.model = border_tile

        self.pos_y = 1 - 1/10
        self.pos_x = -1 + 1/10 


    def draw(self, pipeline):
        sg.drawSceneGraphNode(self.model, pipeline, 'transform')


class Tiler(object):
    tiles: List['Tiles']

    def __init__(self):
        self.tiles = []
        self.grid_size = 10
        self.on = True
        self.i = 0
        self.N = 10                  

    def draw(self, pipeline):
        if self.on:
            for k in self.tiles:
                self.i += 1
                k.draw(pipeline)


class Chansey(object):

    def __init__(self):
        # Figuras básicas
        gpu_body_quad = es.toGPUShape(bs.createColorQuad(1, 0.8, 0.8))  # rosado
        gpu_leg_quad = es.toGPUShape(bs.createColorQuad(1, 0.5, 1))  # rosado fuerte
        gpu_eye_quad = es.toGPUShape(bs.createColorQuad(1, 1, 1))  # blanco
        # ... triangulos

        body = sg.SceneGraphNode('body')
        body.transform = tr.uniformScale(1)
        body.childs += [gpu_body_quad]

        # Creamos las piernas
        leg = sg.SceneGraphNode('leg')  # pierna generica
        leg.transform = tr.scale(0.25, 0.25, 1)
        leg.childs += [gpu_leg_quad]

        # Izquierda
        leg_izq = sg.SceneGraphNode('legLeft')
        leg_izq.transform = tr.translate(-0.5, -0.5, 0)  # tr.matmul([])..
        leg_izq.childs += [leg]

        leg_der = sg.SceneGraphNode('legRight')
        leg_der.transform = tr.translate(0.5, -.5, 0)
        leg_der.childs += [leg]

        # Ojitos
        eye = sg.SceneGraphNode('eye')
        eye.transform = tr.scale(0.25, 0.25, 1)
        eye.childs += [gpu_eye_quad]

        eye_izq = sg.SceneGraphNode('eyeLeft')
        eye_izq.transform = tr.translate(-0.3, 0.5, 0)
        eye_izq.childs += [eye]

        eye_der = sg.SceneGraphNode('eyeRight')
        eye_der.transform = tr.translate(0.3, 0.5, 0)
        eye_der.childs += [eye]

        # Ensamblamos el mono
        mono = sg.SceneGraphNode('chansey')
        mono.transform = tr.matmul([tr.scale(0.4, 0.4, 0), tr.translate(0, -1.25, 0)])
        mono.childs += [body, leg_izq, leg_der, eye_izq, eye_der]

        transform_mono = sg.SceneGraphNode('chanseyTR')
        transform_mono.childs += [mono]

        self.model = transform_mono
        self.pos = 0

    def draw(self, pipeline):
        sg.drawSceneGraphNode(self.model, pipeline, 'transform')

    def move_left(self):
        self.model.transform = tr.translate(-0.7, 0, 0)
        self.pos = -1

    def move_right(self):
        self.model.transform = tr.translate(0.7, 0, 0)
        self.pos = 1

    def move_center(self):
        self.model.transform = tr.translate(0, 0, 0)
        self.pos = 0

    def collide(self, eggs: 'EggCreator'):
        if not eggs.on:  # Si el jugador perdió, no detecta colisiones
            return

        deleted_eggs = []
        for e in eggs.eggs:
            if e.pos_y < -0.7 and e.pos_x != self.pos:
                print('MUERE, GIT GUD')  # YOU D   I   E   D, GIT GUD
                """
                En este caso, podríamos hacer alguna pestaña de alerta al usuario,
                cambiar el fondo por alguna textura, o algo así, en este caso lo que hicimos fue
                cambiar el color del fondo de la app por uno rojo.
                """
                eggs.die()  # Básicamente cambia el color del fondo, pero podría ser algo más elaborado, obviamente
                deleted_eggs.append(e)
            elif -0.25 >= e.pos_y >= -0.7 and self.pos == e.pos_x:
                # print('COLISIONA CON EL HUEVO')
                deleted_eggs.append(e)
        eggs.delete(deleted_eggs)


class Egg(object):

    def __init__(self):
        gpu_egg = es.toGPUShape(bs.createColorQuad(0.7, .7, .7))

        egg = sg.SceneGraphNode('egg')
        egg.transform = tr.scale(random.randrange(10, 21)/100, random.randrange(10, 21)/100, 1)
        egg.childs += [gpu_egg]

        egg_tr = sg.SceneGraphNode('eggTR')
        egg_tr.childs += [egg]

        self.pos_y = 1
        self.pos_x = random.choice([-1, 0, 1])  # LOGICA
        self.model = egg_tr
        self.v_y = -0.005
        self.a = -0.75

    def draw(self, pipeline):
        self.model.transform = tr.translate(0.7 * self.pos_x, self.pos_y, 0)
        sg.drawSceneGraphNode(self.model, pipeline, "transform")

    def update(self, dt):
        self.v_y = self.v_y + self.a*dt
        self.pos_y = self.pos_y + self.v_y*dt


class EggCreator(object):
    eggs: List['Egg']

    def __init__(self):
        self.eggs = []
        self.lives = 0
        self.on = True

    def die(self):  # DARK SOULS
        self.lives += 1
        if self.lives == 3:
            glClearColor(1, 0, 0, 1.0)  # Cambiamos a rojo
            self.on = False  # Dejamos de generar huevos, si es True es porque el jugador ya perdió

    def create_egg(self):
        if len(self.eggs) >= 10:  # No puede haber un máximo de 10 huevos en pantalla
            return
        if random.random() < 0.001:
            self.eggs.append(Egg())

    def draw(self, pipeline):
        if self.on:
            for k in self.eggs:
                k.draw(pipeline)

    def update(self, dt):
        for k in self.eggs:
            k.update(dt)

    def delete(self, d):
        if len(d) == 0:
            return
        remain_eggs = []
        for k in self.eggs:  # Recorro todos los huevos
            if k not in d:  # Si no se elimina, lo añado a la lista de huevos que quedan
                remain_eggs.append(k)
        self.eggs = remain_eggs  # Actualizo la lista
