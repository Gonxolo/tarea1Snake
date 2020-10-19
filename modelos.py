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

    def __init__(self, grid_size):
        # Figuras básicas
        gpu_head_quad = es.toGPUShape(bs.createTextureQuad("img/guy_a.png"), GL_REPEAT, GL_NEAREST)#es.toGPUShape(bs.createColorQuad(0.0, 1.0, 0.0))  # rojo
        gpu_body_quad = es.toGPUShape(bs.createTextureQuad("img/guy_b.png"), GL_REPEAT, GL_NEAREST)
        gpu_body2_quad = es.toGPUShape(bs.createTextureQuad("img/guy_c.png"), GL_REPEAT, GL_NEAREST)

        self.size = grid_size

        body = sg.SceneGraphNode('body')
        body.transform = tr.uniformScale(1)
        body.childs += [gpu_body_quad]

        player_body = sg.SceneGraphNode('snok_body')
        player_body.transform = tr.matmul([tr.scale(1/(self.size/2), 1/(self.size/2), 0), tr.translate(0, 2/(self.size/2), 0)])
        player_body.childs += [body]

        transform_player_body = sg.SceneGraphNode('snok_bodyTR')
        transform_player_body.childs += [player_body]

        self.body_model = transform_player_body

        body2 = sg.SceneGraphNode('body2')
        body2.transform = tr.uniformScale(1)
        body2.childs += [gpu_body2_quad]

        player_body2 = sg.SceneGraphNode('snok_body2')
        player_body2.transform = tr.matmul([tr.scale(1/(self.size/2), 1/(self.size/2), 0), tr.translate(0, 2/(self.size/2), 0)])
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

        self.x = [i/self.size for i in range(-1*self.size+1,self.size,2)]
        self.y = [j/self.size for j in range(-1*self.size+1,self.size,2)]
        self.ppos_x = [7,7,7]
        self.ppos_y = [7,6,5]
        self.pos_x = [7,7,7]
        self.pos_y = [7,6,5]
        self.body_size = 3

        player = sg.SceneGraphNode('snok')
        player.transform = tr.matmul([tr.scale(1/(self.size/2), 1/(self.size/2), 0), tr.translate(0, 2/(self.size/2), 0)])
        player.childs += [head]

        transform_player = sg.SceneGraphNode('snokTR')
        transform_player.childs += [player]

        self.model = transform_player
    
    def draw(self, pipeline):

        # Body
        for i in range(1,self.body_size):
            if i%2 == 0:
                self.body_model.transform = tr.translate(self.x[self.pos_x[i]], self.y[self.pos_y[i]], 0)
                sg.drawSceneGraphNode(self.body_model, pipeline, "transform")
            else:
                self.body2_model.transform = tr.translate(self.x[self.pos_x[i]], self.y[self.pos_y[i]], 0)
                sg.drawSceneGraphNode(self.body2_model, pipeline, "transform")

        # Head
        if self.alive:
            self.model.transform = tr.translate(self.x[self.pos_x[0]], self.y[self.pos_y[0]], 0)
            sg.drawSceneGraphNode(self.model, pipeline, "transform")


        if not self.alive:
            self.model.transform = tr.translate(self.x[self.pos_x[0]], self.y[self.pos_y[0]], 0)
            sg.drawSceneGraphNode(self.model, pipeline, "transform")   
        
    def movement(self):

        if not self.alive:
            return

        #Guardar las posiciones previas
        for i in range(self.body_size):
            self.ppos_x[i] = self.pos_x[i] 
            self.ppos_y[i] = self.pos_y[i] 
        
        #Actualizar posiciones
        self.pos_y[0] += self.s_y
        self.pos_x[0] += self.s_x

        # pos nueva i = pos previa i-1
        for i in range(1,self.body_size):
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

    def collide(self, apples: 'ApplePlacer'): # Colissions w/ apples , self and borders
        deleted_apples = []
        if min(self.pos_x) <= 0 or max(self.pos_x) >= self.size-1:
            self.alive = False

        if min(self.pos_y) <= 0 or max(self.pos_y)  >= self.size-1:
            self.alive = False

        for i in range(1,len(self.pos_y)):
            if self.pos_y[0] == self.pos_y[i]:
                if self.pos_x[0] == self.pos_x[i] :
                    self.alive = False
                    
        for a in apples.apples:
            if (a.pos_y/a.size + 1/a.size - 1/(2*a.size) < self.y[self.pos_y[0]] < a.pos_y/a.size + 1/a.size + 1/(2*a.size)):
                if a.pos_x/a.size + 1/a.size - 1/(2*a.size) < self.x[self.pos_x[0]] < a.pos_x/a.size + 1/a.size + 1/(2*a.size):
                    deleted_apples.append(a)
                    c = self.body_size-1
                    self.pos_x.append(self.ppos_x[c])
                    self.pos_y.append(self.ppos_y[c])
                    self.ppos_x.append(self.ppos_x[c])
                    self.ppos_y.append(self.ppos_y[c])
                    self.body_size += 1
                
            for i in range(1,len(self.pos_x)):    
                #if (a.pos_y - 0.1 < self.y[self.pos_y[i]] < a.pos_y + 0.1) and (a.pos_x - 0.1 < self.x[self.pos_x[i]] < a.pos_x + 0.1):
                if (a.pos_y/a.size + 1/a.size - 1/(2*a.size) < self.y[self.pos_y[i]] < a.pos_y/a.size + 1/a.size + 1/(2*a.size)):
                    if a.pos_x/a.size + 1/a.size - 1/(2*a.size) < self.x[self.pos_x[i]] < a.pos_x/a.size + 1/a.size + 1/(2*a.size):
                        deleted_apples.append(a)
        apples.delete(deleted_apples)


class Tile(object):

    def __init__(self, grid_size):
        # Figuras básicas
        gpu_tile_a_quad = es.toGPUShape(bs.createTextureQuad("img/pattern_a.png",1,1), GL_REPEAT, GL_NEAREST)

        self.size = grid_size

        tile_a = sg.SceneGraphNode('tile_a')
        tile_a.transform = tr.matmul([tr.scale((self.size-2)/self.size, (self.size-2)/self.size, 1),tr.scale(2, 2, 1)])
        tile_a.childs += [gpu_tile_a_quad]

        transform_tile_a = sg.SceneGraphNode('tile_aTR')
        transform_tile_a.childs += [tile_a]

        self.amodel = transform_tile_a

        self.counter = 0
        self.ran_sec1 = [random.randint(0,69) for i in range(self.size-2)]
        self.ran_sec2 = [random.randint(0,69) for i in range(self.size-2)]

    def update(self):
        self.ran_sec1 = [random.randint(0,69) for i in range(self.size-2)]
        self.ran_sec2 = [random.randint(0,69) for i in range(self.size-2)]
    
    def draw(self, pipeline):
        sg.drawSceneGraphNode(self.amodel, pipeline, "transform")


class Apple(object):

    def __init__(self, grid_size):
        gpu_apple = es.toGPUShape(bs.createColorQuad(1.0, 0.0, 0.0))
        #gpuBoo = es.toGPUShape(bs.createTextureQuad("img/boo.png"), GL_REPEAT, GL_NEAREST)
        gpu_cup = es.toGPUShape(bs.Shape([#   positions        colors
                                            -0.85, 1.0, 0.0, 153/255, 217/255, 234/255, 
                                            0.85, 1.0, 0.0, 153/255, 217/255, 234/255,
                                            0.0, 4/12, 0.0, 153/255, 217/255, 234/255], [0, 1, 2]))
        gpu_drink = es.toGPUShape(bs.Shape([#   positions        colors
                                            -0.55, 0.8, 0.0, 205/255, 238/255, 106/255, 
                                            0.55, 0.8, 0.0, 205/255, 238/255, 106/255,
                                            0.0, 5/12, 0.0, 205/255, 238/255, 106/255], [0, 1, 2]))
        gpu_neck = es.toGPUShape(bs.createColorQuad(153/255, 217/255, 234/255))
        gpu_base = es.toGPUShape(bs.Shape([#   positions        colors
                                            -0.6, -0.7, 0.0, 153/255, 217/255, 234/255, 
                                            0.6, -0.7, 0.0, 153/255, 217/255, 234/255,
                                            0.0, -1/2, 0.0, 153/255, 217/255, 234/255], [0, 1, 2]))

        cup = sg.SceneGraphNode('cup')
        cup.transform = tr.uniformScale(1)
        cup.childs += [gpu_cup]

        drink = sg.SceneGraphNode('drink')
        drink.transform = tr.uniformScale(1)
        drink.childs += [gpu_drink]

        neck = sg.SceneGraphNode('neck')
        neck.transform = tr.scale(0.1,1.2,1)
        neck.childs += [gpu_neck]

        base = sg.SceneGraphNode('base')
        base.transform = tr.uniformScale(1)
        base.childs += [gpu_base]

        self.size = grid_size
        self.sizef = grid_size/2

        apple = sg.SceneGraphNode('apple')
        apple.transform = tr.matmul([tr.scale(0.5,0.5,0.0),tr.scale(1/self.sizef, 1/self.sizef, 1)])
        apple.childs += [cup, neck, base, drink]

        # apple = sg.SceneGraphNode('apple')
        # apple.transform = tr.scale(1/self.sizef, 1/self.sizef, 1)
        # apple.childs += [gpu_drink]

        apple_tr = sg.SceneGraphNode('appleTR')
        apple_tr.childs += [apple]

        self.pos_y = random.randrange(-1*self.size + 2, self.size - 2, 2)
        self.pos_x = random.randrange(-1*self.size + 2, self.size - 2, 2)   
        self.model = apple_tr

    def draw(self, pipeline):
        self.model.transform = tr.translate(self.pos_x/self.size + 1/self.size, self.pos_y/self.size + 1/self.size, 0)
        sg.drawSceneGraphNode(self.model, pipeline, "transform")


class ApplePlacer(object):
    apples: List['Apple']

    def __init__(self, grid_size):
        self.apples = []
        self.apple_size = grid_size

    def draw(self, pipeline):
        for k in self.apples:
            k.draw(pipeline)
    
    def create_apple(self):
        if len(self.apples) >= 1:
            return
        else:
            self.apples.append(Apple(self.apple_size))

    def delete(self, d):
        if len(d) == 0:
            return
        remain_apples = []
        for k in self.apples:  # Recorro todos los huevos
            if k not in d:  # Si no se elimina, lo añado a la lista de huevos que quedan
                remain_apples.append(k)
        self.apples = remain_apples  # Actualizo la lista


class Message(object):
    def __init__(self):
        black_background = es.toGPUShape(bs.createTextureQuad("img/original.png"),GL_REPEAT, GL_NEAREST)
        gpu_game_over = es.toGPUShape(bs.createTextureQuad("img/game_over.png"), GL_REPEAT, GL_NEAREST)

        background = sg.SceneGraphNode('background')
        background.transform = tr.scale(2,2,1)
        background.childs += [black_background]
        
        game_over = sg.SceneGraphNode('game_over')
        game_over.transform = tr.scale(1.5,0.85,1)
        game_over.childs += [gpu_game_over]

        game_over_tr = sg.SceneGraphNode('game_overTR')
        game_over_tr.childs += [game_over]

        background_tr = sg.SceneGraphNode('backgroundTR')
        background_tr.childs += [background]

        self.background = background_tr
        self.game_over_model = game_over_tr

    def draw(self, pipeline,timer):
        self.game_over_model.transform = tr.rotationY(timer)
        sg.drawSceneGraphNode(self.game_over_model, pipeline, "transform")

    def draw_background(self, pipeline):
        sg.drawSceneGraphNode(self.background, pipeline, "transform")


# pipeline_no_texture = es.SimpleTransformShaderProgram()
# pipeline_texture = es.SimpleTextureTransformShaderProgram()
# ...
# ...
# ...
# glUseProgram(pipeline_texture.shaderProgram)
# snake.draw(pipeline_texture)
# glUseProgram(pipeline_no_texture.shaderProgram)
# apple.draw(pipeline_no_texture)