import glfw
from OpenGL.GL import *
import sys
import basic_shapes as bs
import easy_shaders as es
from playsound import *
import asyncio


from modelos import *
from controller import Controller

if __name__ == '__main__':

    if len(sys.argv) == 2:
        grid_size = int(sys.argv[1])+2
    else:
        grid_size = 12

    # Initialize glfw
    if not glfw.init():
        sys.exit()

    width = 950
    height = 950

    window = glfw.create_window(width, height, 'DISCO SNOK!', None, None)

    if not window:
        glfw.terminate()
        sys.exit()


    glfw.make_context_current(window)

    controlador = Controller()

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, controlador.on_key)

    # Assembling the shader program (pipeline) with both shaders
    pipeline = es.SimpleTransformShaderProgram()
    pipeline_texture = es.SimpleTextureTransformShaderProgram()

    # Telling OpenGL to use our shader program
    glUseProgram(pipeline_texture.shaderProgram)

    # Setting up the clear screen color
    glClearColor(0.0, 0.0, 0.0, 1.0)

    # Enabling transparencies
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)    

    # Our shapes here are always fully painted
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    gpuSky = es.toGPUShape(bs.createTextureQuad("img/clouds.png"), GL_REPEAT, GL_NEAREST)

    # HACEMOS LOS OBJETOS
    snok = Snake(grid_size)
    vinyls = VinylPlacer(grid_size)
    floor = Tile(grid_size)
    message = Message()

    controlador.set_model(snok)
    controlador.set_menu(message)

    limitFPS = 1.0 / 4.0

    lastTime = 0
    timer = 0

    deltaTime = 0
    nowTime = 0
    
    frames = 0
    updates = 0

    death_time = 0
    Ida = True

    asyncio.run(playsound("sound/Conga.mp3", block = False))

    while not glfw.window_should_close(window):  # Dibujando --> 1. obtener el input
        
        # Using GLFW to check for input events
        glfw.poll_events()  # OBTIENE EL INPUT --> CONTROLADOR --> MODELOS

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT)

        if message.start:
            message.draw_main_menu(pipeline_texture)
            glfw.swap_buffers(window)
            continue
        elif not message.start and lastTime == 0:
            lastTime = glfw.get_time()
            timer = lastTime
        
        # Calculamos el dt
        nowTime = glfw.get_time()
        deltaTime += (nowTime - lastTime) / limitFPS
        lastTime = nowTime

        vinyls.create_vinyl()
            
        while deltaTime >= 1.0:
            snok.movement()
            floor.anim_counter += 1
            floor.color_counter =  snok.body_size
            updates += 1
            deltaTime -= 1
        
        snok.collide(vinyls)
        vinyls.update()

        # DIBUJAR LOS MODELOS
        if snok.alive:
            glUniformMatrix4fv(glGetUniformLocation(pipeline_texture.shaderProgram, "transform"), 1, GL_TRUE,
                    tr.matmul([tr.scale(2, 2, 1),tr.identity()]))
            pipeline_texture.drawShape(gpuSky)
            
            floor.draw(pipeline_texture)
            glUseProgram(pipeline.shaderProgram)
            vinyls.draw(pipeline)
            glUseProgram(pipeline_texture.shaderProgram)
            snok.draw_body(pipeline_texture)
            snok.draw(pipeline_texture)

        if not snok.alive:
            message.draw_background(pipeline_texture)
            message.draw(pipeline_texture,death_time)

            if Ida:   
                death_time += 0.001
                if death_time >= 1.5:
                    Ida = False
            else:
                death_time -= 0.001
                if death_time <= -1.5:
                    Ida = True

        frames += 1

        # Once the render is done, buffers are swapped, showing only the complete scene.
        glfw.swap_buffers(window)

        if glfw.get_time() - timer > 1.0:
            timer += 1
            print("FPS: ",frames," Updates: ",updates)
            updates = 0
            frames = 0

    glfw.terminate()
