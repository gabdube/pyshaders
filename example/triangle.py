# -*- coding: utf-8 -*-
"""

    Simple coloring shader example.

    Press any number key (not on the numpad) to change the triangle color

"""

try:
    import pyglet
    from pyglet.gl import GL_TRIANGLES
    from pyglet.window import key
except ImportError:
    print("Pyglet not found.")
    exit()
    
try:
    import pyshaders
except ImportError:
    import sys
    from os import getcwd
    from os.path import dirname
    sys.path.append(dirname(getcwd()))
    
    import pyshaders
    
    
frag = """
#version 330 core

out vec4 color_frag;

uniform vec3 color = vec3(1.0, 1.0, 1.0);

void main()
{
  color_frag = vec4(color, 1.0);
}
"""

vert = """
#version 330 core

layout(location = 0)in vec2 vert;

void main()
{
  gl_Position = vec4(vert, 1, 1);
}
"""
    
    
# Window creation
window = pyglet.window.Window(visible=True, width=300, height=300, resizable=True)


#Shader creation
shader = pyshaders.from_string(vert, frag)
shader.use()

#Triangle creation
tris = pyglet.graphics.vertex_list(3,
    ('v2f', (0.0, 0.95, 0.95, -0.95, -0.95, -0.95)),
)

#Uniform colors
color_map = {key._0: (1.0, 1.0, 1.0), key._1: (1.0, 0.0, 0.0),
             key._2: (0.0, 1.0, 0.0), key._3: (0.0, 0.0, 1.0),
             key._4:(1.0, 1.0, 0.0), key._5:(1.0, 0.0, 1.0),
             key._6:(0.0, 1.0, 1.0), key._7:(0.5, 0.5, 0.5),
             key._8:(1.0, 0.7, 0.0), key._9:(0.1, 0.7, 0.1)}

@window.event
def on_draw():
    window.clear()
    tris.draw(GL_TRIANGLES)
    
@window.event
def on_key_press(symbol, modifiers):
    if symbol in color_map.keys():
        shader.uniforms.color = color_map[symbol]

pyglet.app.run()
