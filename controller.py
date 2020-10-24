"""
Clase controlador, obtiene el input, lo procesa, y manda los mensajes
a los modelos.
"""

from modelos import Snake
import glfw
import sys
from typing import Union


class Controller(object):
    model: Union['Snake', None]  # Con esto queremos decir que el tipo de modelo es 'Snake' (nuestra clase) ó None

    def __init__(self):
        self.model = None
        self.menu = None

    def set_model(self, m):
        self.model = m

    def set_menu(self,menu):
        self.menu = menu


    def on_key(self, window, key, scancode, action, mods):
        if not (action == glfw.PRESS or action == glfw.RELEASE):
            return

        if key == glfw.KEY_ESCAPE:
            sys.exit()

        # Controlador modifica al modelo
        elif key == glfw.KEY_LEFT and action == glfw.PRESS:
            self.model.move_left()

        elif key == glfw.KEY_RIGHT and action == glfw.PRESS:
            self.model.move_right()

        elif key == glfw.KEY_UP and action == glfw.PRESS:
            self.model.move_up()

        elif key == glfw.KEY_DOWN and action == glfw.PRESS:
            self.model.move_down()

        elif key == glfw.KEY_E and action == glfw.PRESS:
            self.menu.start = False        

        else:
            print('Unknown key')
