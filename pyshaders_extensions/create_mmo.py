# -*- coding: utf-8 -*-

"""
    THIS IS A TEST EXTENSION. IT IS USED TO TEST UNIMPORTABLE EXTENSIONS.
    THIS EXTENSION IS IGNORED BY SETUP.PY
"""

from pyglet.gl import glGetString, GL_SHADING_LANGUAGE_VERSION, gl_info
def check_requirements(target_gl, target_glsl):
    client_glsl = bytearray()
    for i in glGetString(GL_SHADING_LANGUAGE_VERSION):
        if i != 0: client_glsl.append(i)
        else: break
    
    client_glsl = [ int(v) for v in client_glsl.decode('utf8').split('.') ]
    
    gl_ok = gl_info.have_version(*target_gl)
    glsl_ok = ((client_glsl[0] > target_glsl[0]) or 
              (client_glsl[0] == target_glsl[0] and client_glsl[1] >= target_glsl[1]))
    
    return gl_ok and glsl_ok   

def supported():
    "Requires OpenGL >= 17.0 && GLSL >= 17.350"
    return check_requirements(target_gl=(17,0), target_glsl=(17,35))

def load(pyshaders_module):
    create_mmo_with_dragons()