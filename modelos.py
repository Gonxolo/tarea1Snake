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

    def collide(self, vinyls: 'VinylPlacer'): # Colissions w/ vinyls , self and borders
        deleted_vinyls = []
        if min(self.pos_x) <= 0 or max(self.pos_x) >= self.size-1:
            self.alive = False

        if min(self.pos_y) <= 0 or max(self.pos_y)  >= self.size-1:
            self.alive = False

        for i in range(1,len(self.pos_y)):
            if self.pos_y[0] == self.pos_y[i]:
                if self.pos_x[0] == self.pos_x[i] :
                    self.alive = False
                    
        for a in vinyls.vinyls:
            if (a.pos_y/a.size + 1/a.size - 1/(2*a.size) < self.y[self.pos_y[0]] < a.pos_y/a.size + 1/a.size + 1/(2*a.size)):
                if a.pos_x/a.size + 1/a.size - 1/(2*a.size) < self.x[self.pos_x[0]] < a.pos_x/a.size + 1/a.size + 1/(2*a.size):
                    deleted_vinyls.append(a)
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
                        deleted_vinyls.append(a)
        vinyls.delete(deleted_vinyls)


class Tile(object):

    def __init__(self, grid_size):
        
        self.size = grid_size

        ######      RAINBOW A       ######
        self.gpu_r1_quad = es.toGPUShape(bs.createTextureQuad("img/rainbow1.png",(self.size-2)/10,(self.size-2)/10), GL_REPEAT, GL_NEAREST) #f1
        self.gpu_r2_quad = es.toGPUShape(bs.createTextureQuad("img/rainbow2.png",(self.size-2)/10,(self.size-2)/10), GL_REPEAT, GL_NEAREST) #f2
        self.gpu_r3_quad = es.toGPUShape(bs.createTextureQuad("img/rainbow3.png",(self.size-2)/10,(self.size-2)/10), GL_REPEAT, GL_NEAREST) #f3
        self.gpu_r4_quad = es.toGPUShape(bs.createTextureQuad("img/rainbow4.png",(self.size-2)/10,(self.size-2)/10), GL_REPEAT, GL_NEAREST) #f4
        self.gpu_r5_quad = es.toGPUShape(bs.createTextureQuad("img/rainbow5.png",(self.size-2)/10,(self.size-2)/10), GL_REPEAT, GL_NEAREST) #f5

        ######      RAINBOW B       ######
        self.gpu_rb1_quad = es.toGPUShape(bs.createTextureQuad("img/rainbowb1.png",(self.size-2)/10,(self.size-2)/10), GL_REPEAT, GL_NEAREST) #f1
        self.gpu_rb2_quad = es.toGPUShape(bs.createTextureQuad("img/rainbowb2.png",(self.size-2)/10,(self.size-2)/10), GL_REPEAT, GL_NEAREST) #f2
        self.gpu_rb3_quad = es.toGPUShape(bs.createTextureQuad("img/rainbowb3.png",(self.size-2)/10,(self.size-2)/10), GL_REPEAT, GL_NEAREST) #f3
        self.gpu_rb4_quad = es.toGPUShape(bs.createTextureQuad("img/rainbowb4.png",(self.size-2)/10,(self.size-2)/10), GL_REPEAT, GL_NEAREST) #f4
        self.gpu_rb5_quad = es.toGPUShape(bs.createTextureQuad("img/rainbowb5.png",(self.size-2)/10,(self.size-2)/10), GL_REPEAT, GL_NEAREST) #f5


        ### RAINBOW ANIMATION ###
        rainbow = sg.SceneGraphNode('rainbow')
        rainbow.transform = tr.matmul([tr.scale((self.size-2)/self.size, (self.size-2)/self.size, 1),tr.scale(2, 2, 1)])
        rainbow.childs += [self.gpu_r1_quad]

        transform_rainbow = sg.SceneGraphNode('rainbowTR')
        transform_rainbow.childs += [rainbow]

        self.rmodel = transform_rainbow
        
        
        # Figuras básicas
        ###     PATRON A      ###
        self.gpu_tile_a_quad = es.toGPUShape(bs.createTextureQuad("img/pattern_a.png",(self.size-2)/10,(self.size-2)/10), GL_REPEAT, GL_NEAREST)
        self.gpu_tile_a2_quad = es.toGPUShape(bs.createTextureQuad("img/pattern_a2.png",(self.size-2)/10,(self.size-2)/10), GL_REPEAT, GL_NEAREST)
        
        tile_a = sg.SceneGraphNode('tile_a')
        tile_a.transform = tr.matmul([tr.scale((self.size-2)/self.size, (self.size-2)/self.size, 1),tr.scale(2, 2, 1)])
        tile_a.childs += [self.gpu_tile_a_quad]

        transform_tile_a = sg.SceneGraphNode('tile_aTR')
        transform_tile_a.childs += [tile_a]

        self.amodel = transform_tile_a

        
        ###     PATRON B      ###
        self.gpu_tile_b_quad = es.toGPUShape(bs.createTextureQuad("img/pattern_b.png",(self.size-2)/10,(self.size-2)/10), GL_REPEAT, GL_NEAREST)
        self.gpu_tile_b2_quad = es.toGPUShape(bs.createTextureQuad("img/pattern_b2.png",(self.size-2)/10,(self.size-2)/10), GL_REPEAT, GL_NEAREST)

        tile_b = sg.SceneGraphNode('tile_b')
        tile_b.transform = tr.matmul([tr.scale((self.size-2)/self.size, (self.size-2)/self.size, 1),tr.scale(2, 2, 1)])
        tile_b.childs += [self.gpu_tile_b_quad]

        transform_tile_b = sg.SceneGraphNode('tile_bTR')
        transform_tile_b.childs += [tile_b]

        self.bmodel = transform_tile_b

        self.anim_counter = 0
        self.color_counter = 3

        #### FRONT BUILDING ####
        gpuFront = es.toGPUShape(bs.createTextureQuad("img/front.png",(self.size-2),1), GL_REPEAT, GL_NEAREST)

        front = sg.SceneGraphNode('front')
        front.transform = tr.matmul([tr.translate(0,-1*(self.size-1)/self.size,0), tr.scale((self.size-2)/self.size, 1/self.size, 1),tr.scale(2, 2, 1)])
        front.childs += [gpuFront]

        transform_front = sg.SceneGraphNode('frontTR')
        transform_front.childs += [front]

        self.fmodel = transform_front

    
    def draw(self, pipeline):
        sg.drawSceneGraphNode(self.fmodel, pipeline, "transform")

        if self.color_counter%15 == 0:
            sg.findNode(self.rmodel, 'rainbow').childs = []
            if self.anim_counter%10 <= 1:
                sg.findNode(self.rmodel, 'rainbow').childs += [self.gpu_r1_quad]
            elif self.anim_counter%10 <= 3:
                sg.findNode(self.rmodel, 'rainbow').childs += [self.gpu_r2_quad]
            elif self.anim_counter%10 <= 5:
                sg.findNode(self.rmodel, 'rainbow').childs += [self.gpu_r3_quad]
            elif self.anim_counter%10 <= 7:
                sg.findNode(self.rmodel, 'rainbow').childs += [self.gpu_r4_quad]
            elif self.anim_counter%10 <= 9:
                sg.findNode(self.rmodel, 'rainbow').childs += [self.gpu_r5_quad]
            sg.drawSceneGraphNode(self.rmodel, pipeline, "transform")

        elif self.color_counter%7 == 0:
            sg.findNode(self.rmodel, 'rainbow').childs = []
            if self.anim_counter%10 <= 1:
                sg.findNode(self.rmodel, 'rainbow').childs += [self.gpu_rb1_quad]
            elif self.anim_counter%10 <= 3:
                sg.findNode(self.rmodel, 'rainbow').childs += [self.gpu_rb2_quad]
            elif self.anim_counter%10 <= 5:
                sg.findNode(self.rmodel, 'rainbow').childs += [self.gpu_rb3_quad]
            elif self.anim_counter%10 <= 7:
                sg.findNode(self.rmodel, 'rainbow').childs += [self.gpu_rb4_quad]
            elif self.anim_counter%10 <= 9:
                sg.findNode(self.rmodel, 'rainbow').childs += [self.gpu_rb5_quad]
            sg.drawSceneGraphNode(self.rmodel, pipeline, "transform")

        elif self.color_counter%2 == 0:
            sg.findNode(self.amodel, 'tile_a').childs = []
            if self.anim_counter%10 >= 5:
                sg.findNode(self.amodel, 'tile_a').childs += [self.gpu_tile_a_quad]
            else:
                sg.findNode(self.amodel, 'tile_a').childs += [self.gpu_tile_a2_quad]
            sg.drawSceneGraphNode(self.amodel, pipeline, "transform")

        elif self.color_counter%2 == 1:
            sg.findNode(self.bmodel, 'tile_b').childs = []
            if self.anim_counter%10 >= 5:
                sg.findNode(self.bmodel, 'tile_b').childs += [self.gpu_tile_b_quad]
            else:
                sg.findNode(self.bmodel, 'tile_b').childs += [self.gpu_tile_b2_quad]
            sg.drawSceneGraphNode(self.bmodel, pipeline, "transform")



class Vinyl(object):

    def __init__(self, grid_size):
        #gpu_apple = es.toGPUShape(bs.createColorQuad(1.0, 0.0, 0.0))
        #gpuBoo = es.toGPUShape(bs.createTextureQuad("img/boo.png"), GL_REPEAT, GL_NEAREST)
        # gpu_cup = es.toGPUShape(bs.Shape([#   positions        colors
        #                                     -0.85, 1.0, 0.0, 153/255, 217/255, 234/255, 
        #                                     0.85, 1.0, 0.0, 153/255, 217/255, 234/255,
        #                                     0.0, 4/12, 0.0, 153/255, 217/255, 234/255], [0, 1, 2]))
        # gpu_drink = es.toGPUShape(bs.Shape([#   positions        colors
        #                                     -0.55, 0.8, 0.0, 205/255, 238/255, 106/255, 
        #                                     0.55, 0.8, 0.0, 205/255, 238/255, 106/255,
        #                                     0.0, 5/12, 0.0, 205/255, 238/255, 106/255], [0, 1, 2]))
        # gpu_neck = es.toGPUShape(bs.createColorQuad(153/255, 217/255, 234/255))
        # gpu_base = es.toGPUShape(bs.Shape([#   positions        colors
        #                                     -0.6, -0.7, 0.0, 153/255, 217/255, 234/255, 
        #                                     0.6, -0.7, 0.0, 153/255, 217/255, 234/255,
        #                                     0.0, -1/2, 0.0, 153/255, 217/255, 234/255], [0, 1, 2]))

        gpu_vert_rect = es.toGPUShape(bs.createColorQuad(0.0, 0.0, 0.0))
        gpu_horz_rect = es.toGPUShape(bs.createColorQuad(0.0, 0.0, 0.0))
        gpu_cuad = es.toGPUShape(bs.createColorQuad(0.0, 0.0, 0.0))
        gpu_cuad2 = es.toGPUShape(bs.createColorQuad(0.2, 0.2, 0.2))
        gpu_cuad3 = es.toGPUShape(bs.createColorQuad(0.0, 0.0, 0.0))
        gpu_cuad4 = es.toGPUShape(bs.createColorQuad(0.2, 0.2, 0.2))
        gpu_cuad5 = es.toGPUShape(bs.createColorQuad(0.0, 0.0, 0.0))
        gpu_cuad6 = es.toGPUShape(bs.createColorQuad(0.2, 0.2, 0.2))
        gpu_cuad7 = es.toGPUShape(bs.createColorQuad(0.0, 0.0, 0.0))
        gpu_vert_rect2 = es.toGPUShape(bs.createColorQuad(0.0, 0.0, 0.0))
        gpu_horz_rect2 = es.toGPUShape(bs.createColorQuad(0.0, 0.0, 0.0))
        gpu_label = es.toGPUShape(bs.createColorQuad(0.85, 0.0, 0.0))
        gpu_hole = es.toGPUShape(bs.createColorQuad(0.1, 0.0, 0.0))

        vert_rect = sg.SceneGraphNode('vert_rect')
        vert_rect.transform = tr.scale(1.1,1.6,1)
        vert_rect.childs += [gpu_vert_rect]

        horz_rect = sg.SceneGraphNode('horz_rect')
        horz_rect.transform = tr.scale(1.6,1.1,1)
        horz_rect.childs += [gpu_horz_rect]

        cuad = sg.SceneGraphNode('cuad')
        cuad.transform = tr.scale(1.4, 1.4, 1)
        cuad.childs += [gpu_cuad]

        cuad2 = sg.SceneGraphNode('cuad2')
        cuad2.transform = tr.matmul([tr.scale(0.83,0.83,1),tr.scale(1.4, 1.4, 1)])
        cuad2.childs += [gpu_cuad2]

        cuad3 = sg.SceneGraphNode('cuad3')
        cuad3.transform = tr.matmul([tr.scale(0.9,0.9,1),tr.scale(0.83,0.83,1),tr.scale(1.4, 1.4, 1)])
        cuad3.childs += [gpu_cuad3]

        cuad4 = sg.SceneGraphNode('cuad4')
        cuad4.transform = tr.matmul([tr.scale(0.8,0.8,1),tr.scale(0.9,0.9,1),tr.scale(0.83,0.83,1),tr.scale(1.4, 1.4, 1)])
        cuad4.childs += [gpu_cuad4]

        cuad5 = sg.SceneGraphNode('cuad5')
        cuad5.transform = tr.matmul([tr.scale(0.9,0.9,1),tr.scale(0.8,0.8,1),tr.scale(0.9,0.9,1),tr.scale(0.83,0.83,1),tr.scale(1.4, 1.4, 1)])
        cuad5.childs += [gpu_cuad5]
        
        cuad6 = sg.SceneGraphNode('cuad6')
        cuad6.transform = tr.matmul([tr.scale(0.7,0.7,1),tr.scale(0.9,0.9,1),tr.scale(0.8,0.8,1),tr.scale(0.9,0.9,1),tr.scale(0.83,0.83,1),tr.scale(1.4, 1.4, 1)])
        cuad6.childs += [gpu_cuad6]

        cuad7 = sg.SceneGraphNode('cuad7')
        cuad7.transform = tr.matmul([tr.scale(0.9,0.9,1),tr.scale(0.7,0.7,1),tr.scale(0.9,0.9,1),tr.scale(0.8,0.8,1),tr.scale(0.9,0.9,1),tr.scale(0.83,0.83,1),tr.scale(1.4, 1.4, 1)])
        cuad7.childs += [gpu_cuad7]

        vert_rect2 = sg.SceneGraphNode('vert_rect2')
        vert_rect2.transform = tr.scale(1.2,0.5,1)
        vert_rect2.childs += [gpu_vert_rect2]

        horz_rect2 = sg.SceneGraphNode('horz_rect2')
        horz_rect2.transform = tr.scale(0.5,1.2,1)
        horz_rect2.childs += [gpu_horz_rect2]

        label = sg.SceneGraphNode('label')
        label.transform = tr.scale(0.35,0.35,1)
        label.childs += [gpu_label]

        hole = sg.SceneGraphNode('hole')
        hole.transform = tr.scale(0.15,0.15,1)
        hole.childs += [gpu_hole]

        self.size = grid_size
        self.sizef = grid_size/2

        vinyl = sg.SceneGraphNode('vinyl')
        vinyl.transform = tr.matmul([tr.scale(0.5,0.5,1),tr.scale(1/self.sizef, 1/self.sizef, 1)])
        vinyl.childs += [vert_rect, horz_rect, cuad, cuad2, cuad3, cuad4, cuad5, cuad6, cuad7, vert_rect2, horz_rect2, label, hole]

        # apple = sg.SceneGraphNode('apple')
        # apple.transform = tr.scale(1/self.sizef, 1/self.sizef, 1)
        # apple.childs += [gpu_drink]

        vinyl_tr = sg.SceneGraphNode('vinylTR')
        vinyl_tr.childs += [vinyl]

        vinyl_tr2 = sg.SceneGraphNode('vinylTR2')
        vinyl_tr2.childs += [vinyl_tr]

        self.pos_y = random.randrange(-1*self.size + 2, self.size - 2, 2)
        self.pos_x = random.randrange(-1*self.size + 2, self.size - 2, 2)   
        self.model = vinyl_tr
        self.model2 = vinyl_tr2
        self.counter = 0
        self.pulse = True

    def update(self):
        if self.pulse:
            self.counter += 0.001
            if self.counter >= 0.4:
                self.pulse = False
        else:
            self.counter -= 0.001
            if self.counter <= -0.15:
                self.pulse = True
        self.model.transform = tr.scale(1 - self.counter,1 - self.counter,1)
        

    def draw(self, pipeline):
        self.model2.transform = tr.translate(self.pos_x/self.size + 1/self.size, self.pos_y/self.size + 1/self.size, 0)
        sg.drawSceneGraphNode(self.model2, pipeline, "transform")


class VinylPlacer(object):
    vinyls: List['Vinyl']

    def __init__(self, grid_size):
        self.vinyls = []
        self.vinyl_size = grid_size

    def draw(self, pipeline):
        for k in self.vinyls:
            k.draw(pipeline)
    
    def create_vinyl(self):
        if len(self.vinyls) >= 1:
            return
        else:
            self.vinyls.append(Vinyl(self.vinyl_size))

    def update(self):
        for k in self.vinyls:
            k.update()

    def delete(self, d):
        if len(d) == 0:
            return
        remain_vinyls = []
        for k in self.vinyls:  # Recorro todos los huevos
            if k not in d:  # Si no se elimina, lo añado a la lista de huevos que quedan
                remain_vinyls.append(k)
        self.vinyls = remain_vinyls  # Actualizo la lista


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