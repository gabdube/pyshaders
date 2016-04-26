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

try:
    import pyglbuffers
    requirement_met = True
except ImportError:
    requirement_met = False

if requirement_met == False:
    try:
        from .. import pyglbuffers
        requirement_met = True
    except (ImportError, ValueError, SystemError):
        requirement_met = False
    
from ctypes import sizeof
    
def map_attributes(self, buffer):
    """
        Map the shader attributes to a buffer.
        The buffer format names must match the shader attributes.
        Attributes that cannot be mapped will not be touched.
        
        Normalized is set to false.
        
        If the buffer format is not supported by opengl, an error will be raised.
        Ex: "(6D)[foo]"
        
        Argument:
            buffer: A Buffer object.
            offset: Offset (in elements) for glVertexAttribPointer
    """
    format = buffer.format
    buffer_attributes = [ (token, getattr(self.attributes, token.name)) 
                           for token in format.tokens if token.name in self.attributes ]
                               
    stride = sizeof(format.struct)                   
                              
    for token, attr in buffer_attributes:
        offset, type, size = token[0:3]    # Tokens attributes are aligned with the point_to parameters
        attr.point_to(offset, type, size, False, stride)  
    
    
def supported():
    return requirement_met

def load(mod):
    mod.ShaderProgram.map_attributes = map_attributes
    
    