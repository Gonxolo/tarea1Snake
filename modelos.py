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
        gpu_head_quad = es.toGPUShape(bs.createTextureQuad("img/guy_a.png"), GL_REPEAT, GL_NEAREST)#es.toGPUShape(bs.createColorQuad(0.0, 1.0, 0.0))  # rojo
        gpu_body_quad = es.toGPUShape(bs.createTextureQuad("img/guy_b.png"), GL_REPEAT, GL_NEAREST)
        gpu_body2_quad = es.toGPUShape(bs.createTextureQuad("img/guy_c.png"), GL_REPEAT, GL_NEAREST)

        body = sg.SceneGraphNode('body')
        body.transform = tr.uniformScale(1)
        body.childs += [gpu_body_quad]

        player_body = sg.SceneGraphNode('snok_body')
        player_body.transform = tr.matmul([tr.scale(1/6, 1/6, 0), tr.translate(0, 2/6, 0)])
        player_body.childs += [body]

        transform_player_body = sg.SceneGraphNode('snok_bodyTR')
        transform_player_body.childs += [player_body]

        self.body_model = transform_player_body

        body2 = sg.SceneGraphNode('body2')
        body2.transform = tr.uniformScale(1)
        body2.childs += [gpu_body2_quad]

        player_body2 = sg.SceneGraphNode('snok_body2')
        player_body2.transform = tr.matmul([tr.scale(1/6, 1/6, 0), tr.translate(0, 2/6, 0)])
        player_body2.childs += [body2]

        transform_player_body2 = sg.SceneGraphNode('snok_bodyTR')
        transform_player_body2.childs += [player_body2]

        self.body2_model = transform_player_body2

        head = sg.SceneGraphNode('head')
        head.transform = tr.uniformScale(1)
        head.childs += [gpu_head_quad]

        self.s_x = 0
        self.s_y = 1

        self.alive = True

        self.x = [i/12 for i in range(-11,12,2)]
        self.y = [j/12 for j in range(-11,12,2)]
        self.ppos_x = [7,7,7]
        self.ppos_y = [7,6,5]
        self.pos_x = [7,7,7]
        self.pos_y = [7,6,5]
        self.size = 3

        player = sg.SceneGraphNode('snok')
        player.transform = tr.matmul([tr.scale(1/6, 1/6, 0), tr.translate(0, 2/6, 0)])
        player.childs += [head]

        transform_player = sg.SceneGraphNode('snokTR')
        transform_player.childs += [player]

        self.model = transform_player
    
    def draw(self, pipeline):
        # Head
        self.model.transform = tr.translate(self.x[self.pos_x[0]], self.y[self.pos_y[0]], 0)
        sg.drawSceneGraphNode(self.model, pipeline, "transform")

        # Body
        for i in range(1,self.size):
            if i%2 == 0:
                self.body_model.transform = tr.translate(self.x[self.pos_x[i]], self.y[self.pos_y[i]], 0)
                sg.drawSceneGraphNode(self.body_model, pipeline, "transform")
            else:
                self.body2_model.transform = tr.translate(self.x[self.pos_x[i]], self.y[self.pos_y[i]], 0)
                sg.drawSceneGraphNode(self.body2_model, pipeline, "transform")


        if not self.alive:
            self.model.transform = tr.translate(self.x[self.pos_x[0]], self.y[self.pos_y[0]], 0)
            sg.drawSceneGraphNode(self.model, pipeline, "transform")           

    def movement(self):

        if not self.alive:
            return

        #Guardar las posiciones previas
        for i in range(self.size):
            self.ppos_x[i] = self.pos_x[i] 
            self.ppos_y[i] = self.pos_y[i] 
        
        #Actualizar posiciones
        self.pos_y[0] += self.s_y
        self.pos_x[0] += self.s_x

        # pos nueva i = pos previa i-1
        for i in range(1,self.size):
            self.pos_y[i] = self.ppos_y[i-1]
            self.pos_x[i] = self.ppos_x[i-1]
    
    def move_left(self): #LEFT
        if self.s_x != 0:
            return
        self.s_y = 0
        self.s_x = -1
    
    def move_right(self): #RIGHT
        if self.s_x != 0:
            return
        self.s_y = 0
        self.s_x = 1    

    def move_up(self): #UP
        if self.s_y != 0:
            return
        self.s_x = 0
        self.s_y = 1

    def move_down(self): #DOWN
        if self.s_y != 0:
            return
        self.s_x = 0
        self.s_y = -1

    def collide(self, apples: 'ApplePlacer'): # Colissions w/ apples
        deleted_apples = []

        if self.pos_x[0] == 0 or self.pos_x[0] == 11:
            self.alive = False

        if self.pos_y[0] == 0 or self.pos_y[0]  == 11:
            self.alive = False

        for i in range(1,len(self.pos_y)):
            if self.pos_y[0] == self.pos_y[i]:
                if self.pos_x[0] == self.pos_x[i] :
                    self.alive = False
                    
        for a in apples.apples:
            if (a.pos_y - 0.1 < self.y[self.pos_y[0]] < a.pos_y + 0.1) and (a.pos_x - 0.1 < self.x[self.pos_x[0]] < a.pos_x + 0.1):
                deleted_apples.append(a)
                c = self.size-1
                self.pos_x.append(self.ppos_x[c])
                self.pos_y.append(self.ppos_y[c])
                self.ppos_x.append(self.ppos_x[c])
                self.ppos_y.append(self.ppos_y[c])
                self.size += 1
                
            for i in range(1,len(self.pos_x)):    
                if (a.pos_y - 0.1 < self.y[self.pos_y[i]] < a.pos_y + 0.1) and (a.pos_x - 0.1 < self.x[self.pos_x[i]] < a.pos_x + 0.1):
                    deleted_apples.append(a)
        apples.delete(deleted_apples)


class Tile(object):

    def __init__(self):
        # Figuras básicas
        gpu_tile_a_quad = es.toGPUShape(bs.createTextureQuad("img/dancefloor_a.png"), GL_REPEAT, GL_NEAREST)
        gpu_tile_b_quad = es.toGPUShape(bs.createTextureQuad("img/dancefloor_b.png"), GL_REPEAT, GL_NEAREST)
        gpu_tile_c_quad = es.toGPUShape(bs.createTextureQuad("img/dancefloor_c.png"), GL_REPEAT, GL_NEAREST)
        gpu_tile_d_quad = es.toGPUShape(bs.createTextureQuad("img/dancefloor_d.png"), GL_REPEAT, GL_NEAREST)

        tile_a = sg.SceneGraphNode('tile_a')
        tile_a.transform = tr.scale(2/6, 2/6, 0)
        tile_a.childs += [gpu_tile_a_quad]

        tile_b = sg.SceneGraphNode('tile_b')
        tile_b.transform = tr.scale(2/6, 2/6, 0)
        tile_b.childs += [gpu_tile_b_quad]

        tile_c = sg.SceneGraphNode('tile_c')
        tile_c.transform = tr.scale(2/6, 2/6, 0)
        tile_c.childs += [gpu_tile_c_quad]

        tile_d = sg.SceneGraphNode('tile_d')
        tile_d.transform = tr.scale(2/6, 2/6, 0)
        tile_d.childs += [gpu_tile_d_quad]

        transform_tile_a = sg.SceneGraphNode('tile_aTR')
        transform_tile_a.childs += [tile_a]

        transform_tile_b = sg.SceneGraphNode('tile_bTR')
        transform_tile_b.childs += [tile_b]

        transform_tile_c = sg.SceneGraphNode('tile_cTR')
        transform_tile_c.childs += [tile_c]

        transform_tile_d = sg.SceneGraphNode('tile_dTR')
        transform_tile_d.childs += [tile_d]

        self.selector = random.choice([0, 1, 2, 3])
        
        if self.selector == 0:
            self.model = transform_tile_a

        if self.selector == 1:
            self.model = transform_tile_b

        if self.selector == 2:
            self.model = transform_tile_c

        if self.selector == 3:
            self.model = transform_tile_d
    
    def draw(self, pipeline, c_x=0, c_y = 0):
        self.model.transform = tr.translate(-1+(c_x+1)*2/6, 1-(c_y+1)*2/6, 0)
        sg.drawSceneGraphNode(self.model, pipeline, "transform")


class Background(object):

    tiles: List['Tile']
    def __init__(self):
        self.tiles = []
        self.count = 0

    def Counter(self):
        self.count += 1

    def update(self):
        k = self.tiles[0]
        for j in range(len(self.tiles)-1):
            self.tiles[j] = self.tiles[j+1]
            self.tiles[len(self.tiles)-1] = k
        self.count = 0
    
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

        self.pos_y = random.choice([j * 1/6 for j in range(-5,5)]) + 1/12
        self.pos_x = random.choice([i * 1/6 for i in range(-5,5)]) + 1/12     
        #self.pos_y = random.randint(-5,4) * 1/6 + 1/12
        #self.pos_x = random.randint(-5,4) * 1/6 + 1/12
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
            k.draw(pipeline)
    
    def create_apple(self):
        if len(self.apples) >= 1:
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
