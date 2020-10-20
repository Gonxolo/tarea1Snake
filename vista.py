"""
Esta sería la clase vista. Contiene el ciclo de la aplicación y ensambla
las llamadas para obtener el dibujo de la escena.
"""

import glfw
from OpenGL.GL import *
import sys
import basic_shapes as bs
import easy_shaders as es


from modelos import *
from controller import Controller

if __name__ == '__main__':

    if len(sys.argv) == 2:
        grid_size = int(sys.argv[1])+2

    else:
        grid_size = 14

    # Initialize glfw
    if not glfw.init():
        sys.exit()

    width = 800
    height = 800

    window = glfw.create_window(width, height, 'AAAAAAAAAA', None, None)

    if not window:
        glfw.terminate()
        sys.exit()

    glfw.make_context_current(window)

    controlador = Controller()

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, controlador.on_key)

    # Assembling the shader program (pipeline) with both shaders
    pipeline = es.SimpleTransformShaderProgram()
    pipeline2 = es.SimpleTextureTransformShaderProgram()

    # Telling OpenGL to use our shader program
    #glUseProgram(pipeline.shaderProgram)
    glUseProgram(pipeline2.shaderProgram)

    # Setting up the clear screen color
    glClearColor(0.0, 0.0, 0.0, 1.0)

    # Enabling transparencies
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)    

    # Our shapes here are always fully painted
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    gpuOhnoTop = es.toGPUShape(bs.createTextureQuad("img/ohno.png"), GL_REPEAT, GL_NEAREST)
    gpuOhnoBottom = es.toGPUShape(bs.createTextureQuad("img/ohno.png"), GL_REPEAT, GL_NEAREST)
    gpuOhnoLeft = es.toGPUShape(bs.createTextureQuad("img/ohno.png"), GL_REPEAT, GL_NEAREST)
    gpuOhnoRight = es.toGPUShape(bs.createTextureQuad("img/ohno.png"), GL_REPEAT, GL_NEAREST)

    # HACEMOS LOS OBJETOS
    snok = Snake(grid_size)
    #background = Background()
    apples = ApplePlacer(grid_size)
    #background = Tiler()
    background = Tile(grid_size)
    message = Message()

    #background = createTextureQuad("background_grid.png")

    controlador.set_model(snok)

    limitFPS = 1.0 / 3.0

    lastTime = glfw.get_time()
    timer = lastTime

    deltaTime = 0
    nowTime = 0
    
    frames = 0
    updates = 0

    death_time = 0
    Ida = True

    #background.place_tile()

    while not glfw.window_should_close(window):  # Dibujando --> 1. obtener el input

        # Calculamos el dt
        nowTime = glfw.get_time()
        deltaTime += (nowTime - lastTime) / limitFPS
        lastTime = nowTime

        # Using GLFW to check for input events
        glfw.poll_events()  # OBTIENE EL INPUT --> CONTROLADOR --> MODELOS

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT)

        apples.create_apple()

        if not snok.alive:
            if Ida:    
                death_time += 0.001
                if death_time >= 1.5:
                    #death_time = 1.5
                    Ida = False
            else:
                death_time -= 0.001
                if death_time <= -1.5:
                    #death_time = 0
                    Ida = True
            
        while deltaTime >= 1.0:
            snok.movement()
            background.anim_counter += 1
            background.color_counter =  snok.body_size
            updates += 1
            deltaTime -= 1
        
        snok.collide(apples)


        # DIBUJAR LOS MODELOS
        if snok.alive:
            background.draw(pipeline2)
            glUseProgram(pipeline.shaderProgram)
            apples.draw(pipeline)

        #glUniformMatrix4fv(glGetUniformLocation(pipeline2.shaderProgram, "transform"), 1, GL_TRUE,
        #                   tr.matmul([
        #                       tr.translate(0, 1-1/12, 0),
        #                       tr.scale(2, 1/6, 1),
        #                       tr.identity()]))
        #pipeline2.drawShape(gpuOhnoTop)

        #glUniformMatrix4fv(glGetUniformLocation(pipeline2.shaderProgram, "transform"), 1, GL_TRUE,
        #                   tr.matmul([
        #                       tr.translate(0, -1+1/12, 0),
        #                       tr.scale(2, 1/6, 1),
        #                       tr.identity()]))
        #pipeline2.drawShape(gpuOhnoBottom)

        #glUniformMatrix4fv(glGetUniformLocation(pipeline2.shaderProgram, "transform"), 1, GL_TRUE,
        #                   tr.matmul([
        #                       tr.translate(-1+1/12, 0, 0),
        #                       tr.scale(1/6, 2, 1),
        #                       tr.identity()]))
        #pipeline2.drawShape(gpuOhnoLeft)

        #glUniformMatrix4fv(glGetUniformLocation(pipeline2.shaderProgram, "transform"), 1, GL_TRUE,
        #                   tr.matmul([
        #                       tr.translate(1-1/12, 0, 0),
        #                       tr.scale(1/6, 2, 1),
        #                       tr.identity()]))
        #pipeline2.drawShape(gpuOhnoRight)
        if snok.alive:
            glUseProgram(pipeline2.shaderProgram)
            snok.draw(pipeline2)

        if not snok.alive:
            message.draw_background(pipeline2)
            message.draw(pipeline2,death_time)
                

        frames += 1

        # Once the render is done, buffers are swapped, showing only the complete scene.
        glfw.swap_buffers(window)

        if glfw.get_time() - timer > 1.0:
            timer += 1
            print("FPS: ",frames," Updates: ",updates)
            updates = 0
            frames = 0

    glfw.terminate()
