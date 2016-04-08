# -*- coding: utf-8 -*-
"""
''MIT License

Copyright (c) 2016 Gabriel Dubé

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from pyglet.gl import (glGetUniformuiv, glUniform1uiv, glUniform2uiv, glUniform3uiv,
  glUniform4uiv, GLuint)

from pyglet.gl import (GL_UNSIGNED_INT, GL_UNSIGNED_INT_VEC2, GL_UNSIGNED_INT_VEC3,
  GL_UNSIGNED_INT_VEC4)

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
    " Requires OpenGL >= 3.0 && GLSL >= 1.30 "
    return check_requirements(target_gl=(3,0), target_glsl=(1,30))

def load(mod):
    # Add getters
    mod.GETTERS[GLuint] = glGetUniformuiv
    
    # To unpack array correctly
    mod.UNPACK_ARRAY.append(GL_UNSIGNED_INT)
    
    # Add uniform data
    uniform_data = {
        GL_UNSIGNED_INT: (GLuint, 1, glUniform1uiv),
        GL_UNSIGNED_INT_VEC2: (GLuint, 2, glUniform2uiv),
        GL_UNSIGNED_INT_VEC3: (GLuint, 3, glUniform3uiv),
        GL_UNSIGNED_INT_VEC4: (GLuint, 4, glUniform4uiv),
    }
    mod.UNIFORMS_DATA.update(uniform_data)
    