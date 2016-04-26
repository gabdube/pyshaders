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

from pyglet.gl import (GLdouble, glGetUniformdv, glUniform1dv, glUniform2dv,
  glUniform3dv, glUniform4dv, glUniformMatrix2dv, glUniformMatrix3dv, glUniformMatrix4dv,
  glUniformMatrix2x3dv, glUniformMatrix2x4dv, glUniformMatrix3x2dv,
  glUniformMatrix3x4dv, glUniformMatrix4x2dv, glUniformMatrix4x3dv)


from pyglet.gl import (GL_DOUBLE, GL_DOUBLE_VEC2, GL_DOUBLE_VEC3, GL_DOUBLE_VEC4, GL_DOUBLE_MAT2,
  GL_DOUBLE_MAT3, GL_DOUBLE_MAT4, GL_DOUBLE_MAT2x3, GL_DOUBLE_MAT2x4, GL_DOUBLE_MAT3x2, GL_DOUBLE_MAT3x4,
  GL_DOUBLE_MAT4x2, GL_DOUBLE_MAT4x3)

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
    " Requires OpenGL >= 3.2 && GLSL >= 1.50 "
    return check_requirements(target_gl=(3,2), target_glsl=(1,50)) and gl_info.have_extension('GL_ARB_gpu_shader_fp64')

def load(mod):
    # Add getters
    mod.GETTERS[GLdouble] = glGetUniformdv
    
    # To unpack array correctly
    mod.UNPACK_ARRAY.append(GL_DOUBLE)
    
    # Add uniform data
    uniform_data = {
        GL_DOUBLE: (GLdouble, 1, glUniform1dv),
        GL_DOUBLE_VEC2: (GLdouble, 2, glUniform2dv),
        GL_DOUBLE_VEC3: (GLdouble, 3, glUniform3dv),
        GL_DOUBLE_VEC4: (GLdouble, 4, glUniform4dv),
        GL_DOUBLE_MAT2: (GLdouble, 4, lambda x,y,z: glUniformMatrix2dv(x,y,True,z),      (2,2)),
        GL_DOUBLE_MAT3: (GLdouble, 9, lambda x,y,z: glUniformMatrix3dv(x,y,True,z),      (3,3)),
        GL_DOUBLE_MAT4: (GLdouble, 16, lambda x,y,z: glUniformMatrix4dv(x,y,True,z),     (4,4)),
        GL_DOUBLE_MAT2x3: (GLdouble, 6, lambda x,y,z: glUniformMatrix2x3dv(x,y,True,z),    (2,3)),
        GL_DOUBLE_MAT2x4: (GLdouble, 8, lambda x,y,z: glUniformMatrix2x4dv(x,y,True,z),    (2,4)),
        GL_DOUBLE_MAT3x2: (GLdouble, 6, lambda x,y,z: glUniformMatrix3x2dv(x,y,True,z),    (3,2)),
        GL_DOUBLE_MAT3x4: (GLdouble, 12, lambda x,y,z: glUniformMatrix3x4dv(x,y,True,z),   (3,4)),
        GL_DOUBLE_MAT4x2: (GLdouble, 8, lambda x,y,z: glUniformMatrix4x2dv(x,y,True,z),    (4,2)),
        GL_DOUBLE_MAT4x3: (GLdouble, 12, lambda x,y,z: glUniformMatrix4x3dv(x,y,True,z),   (4,3)),
    }
    mod.UNIFORMS_DATA.update(uniform_data)
    