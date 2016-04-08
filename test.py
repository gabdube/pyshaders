# -*- coding: utf-8 -*-

import unittest, gc
from io import SEEK_END
from ctypes import c_char_p, cast

import pyglet
from pyglet.gl import (glIsShader, GL_FALSE, GL_VERTEX_SHADER, GL_FRAGMENT_SHADER,
  glCreateShader, GL_TRUE, glDeleteShader, glIsProgram, glCreateProgram,
  glDeleteProgram, gl_info, glGetString, GL_SHADING_LANGUAGE_VERSION)

import pyshaders
from pyshaders import (ShaderObject, ShaderCompilationError, shader_source,
  ShaderProgram, from_files, from_files_names, current_program, GL_FLOAT_MAT3,
  GL_FLOAT_VEC3, load_extension, check_extension, PyShadersExtensionError,
  extension_loaded)

vert_path = lambda fname: 'fixtures\\{}.glsl.vert'.format(fname)
frag_path = lambda fname: 'fixtures\\{}.glsl.frag'.format(fname)

def eof(f):
    pos = f.tell()
    f.seek(0, SEEK_END)
    return pos == f.tell()

class TestShaderObjects(unittest.TestCase):
    
    def test_create(self):
        " Test ShaderObject.vertex and ShaderObject.fragment "
        vert_obj = ShaderObject.vertex()
        frag_obj = ShaderObject.fragment()
        
        self.assertIs(type(vert_obj), ShaderObject, 'vertex did not returned a ShaderObject.')
        self.assertIs(type(frag_obj), ShaderObject, 'fragment did not returned a ShaderObject.')
        
    def test_repr(self):
        vert_obj = ShaderObject.vertex()
        self.assertEqual('ShaderObject {}'.format(vert_obj.sid), repr(vert_obj), "Repr do not match")        
        
    def test_eq(self):
        vert_obj = ShaderObject.vertex()
        vert_obj_clone = ShaderObject(vert_obj.sid)
        
        self.assertEqual(vert_obj, vert_obj_clone, 'vert and vert clone are not equal')
        
    def test_valid(self):
        " Test if generated objects are valid"
        vert_obj = ShaderObject.vertex()
        frag_obj = ShaderObject.fragment()
        bad_obj = ShaderObject(8000, owned=True)
        borrowed_obj = ShaderObject(glCreateShader(GL_VERTEX_SHADER), owned=True)          
        
        self.assertTrue(vert_obj.valid(), 'vertex shader is not valid')
        self.assertTrue(frag_obj.valid(), 'fragment shader is not valid')
        self.assertTrue(borrowed_obj.valid(), 'other vertex shader is not valid')
        self.assertFalse(bad_obj.valid(), 'bad shader is valid')
        self.assertTrue(vert_obj, 'vertex shader is not valid')
        self.assertFalse(bad_obj, 'bad shader is valid')
        
    def test_freeing(self):
        " Test if the shaders are freed correctly"
        vert_obj = ShaderObject.vertex()
        
        # Warning, borrowed_obj do not own the underlying shader so it will not be freed automatically
        borrowed_obj = ShaderObject(glCreateShader(GL_VERTEX_SHADER), owned=False)          
        
        borrowed_sid = borrowed_obj.sid
        sid = vert_obj.sid
        del vert_obj
        del borrowed_obj
        gc.collect()
        
        self.assertEqual(GL_FALSE, glIsShader(sid), 'shader object is still valid')
        self.assertEqual(GL_TRUE, glIsShader(borrowed_sid), 'shader object was deleted')
        
        #Free the shader object
        glDeleteShader(borrowed_sid)
        
    def test_convert_source(self):
        " Test if shader_source convert strings like it should "
        srcf = open(vert_path('shader1'), 'r')
        src = srcf.read()
        src_ptr = shader_source(src.encode('UTF-8')) 
        src2 = cast(src_ptr.contents, c_char_p).value.decode('UTF-8')
        
        self.assertIsNot(src, src2)
        self.assertEqual(src, src2)
        
        srcf.close()
        
    def test_source(self):
        " Test shader set/get source & source_length descriptor "
        srcf = open(vert_path('shader1'), 'r')
        src = srcf.read()
             
        vert_obj = ShaderObject.vertex()
        
        self.assertEqual("", vert_obj.source) 
        self.assertEqual(0, vert_obj.source_length)  
        vert_obj.source = src
        self.assertEqual(len(src)+1, vert_obj.source_length)      # +1 because source_length includes a null byte
        
        src2 = vert_obj.source[0:-1]                              # Remove the null byte
        self.assertIsNot(src, src2)
        self.assertEqual(src, src2)        
        
        srcf.close()
        
    def test_compile(self):
        " Test compile "
        srcf = open(vert_path('shader1'), 'r')
        src = srcf.read()
        
        vert_obj = ShaderObject.vertex()
        vert_obj.source = src
        
        self.assertEqual(0, vert_obj.log_length, 'Log length is not zero')
        self.assertFalse(vert_obj.compiled, 'compiled returned True')
        self.assertTrue(vert_obj.compile(), 'compilation failed')    
        self.assertTrue(vert_obj.compiled, 'compiled returned False')
        self.assertEqual(0, vert_obj.log_length, 'Log length is not zero')
        self.assertEqual('', vert_obj.logs, 'Logs are not empty')
        
        srcf.close()
        
    def test_fail_compile(self):
        " Test fail compile and logs " 
        srcf = open(frag_path('shader_bad'), 'r')
        src = srcf.read() 
        
        frag_obj = ShaderObject.fragment()
        frag_obj.source = src
        
        self.assertFalse(frag_obj.compile(), 'shader was compiled successfully')
        self.assertFalse(frag_obj.compiled, 'compiled returned True')
        self.assertNotEqual(0, frag_obj.log_length, 'Log length is 0')
        
        logs = frag_obj.logs
        self.assertIn('Undeclared identifier: x', logs, 'Error not found')
        self.assertIn('Undeclared identifier: y', logs, 'Error not found')
        self.assertIn('Syntax error: "}" parse error', logs, 'Error not found')
        self.assertIn('3 compilation errors.  No code generated', logs, 'Error not found')
        
        srcf.close()
        
    def test_shader_type(self):
        " Test descriptors "
        vert_obj = ShaderObject.vertex()
        frag_obj = ShaderObject.fragment()
        
        self.assertEqual(GL_VERTEX_SHADER, vert_obj.type, 'type is not vertex')
        self.assertEqual(GL_FRAGMENT_SHADER, frag_obj.type, 'type is not fragment')

class TestShaderPrograms(unittest.TestCase):
    
    def test_create(self):
        " Test if programs are created correctly "
        prog = ShaderProgram.new_program()
        self.assertIs(ShaderProgram, type(prog), 'prog is not a shader program')
        
    def test_eq(self):
        prog = ShaderProgram.new_program()
        prog_clone = ShaderProgram(prog.pid)
        
        self.assertEqual(prog, prog_clone, 'prog and prog clone are not equal')        
        
    def test_repr(self):
        prog = ShaderProgram.new_program()
        self.assertEqual('ShaderProgram {}'.format(prog.pid), repr(prog), "Repr do not match")
        
    def test_valid(self):
        " Test if generated programs are valid"
        prog1 = ShaderProgram.new_program()
        prog2 = ShaderProgram(8000, owned = True)
        
        self.assertTrue(prog1.valid())
        self.assertFalse(prog2.valid())
        self.assertTrue(prog1)
        self.assertFalse(prog2)
        
    def get_objects(self, name='shader1'):
        vert = ShaderObject.vertex()
        frag = ShaderObject.fragment()
        
        with open(vert_path(name), 'r') as f:
            vert.source = f.read()
            self.assertEqual(True, vert.compile(), 'vert compilation failed')
            
        with open(frag_path(name), 'r') as f:
            frag.source = f.read()
            self.assertEqual(True, frag.compile(), 'frag compilation failed')
        
        return vert, frag
        
    def test_freeing(self):
        " Test if programs are freed correctly "
        prog = ShaderProgram.new_program()
        vert, frag = self.get_objects()
        prog.attach(vert, frag)
        
        # Warning, borrowed_obj do not own the underlying shader so it will not be freed automatically
        borrowed_prog = ShaderProgram(glCreateProgram(), owned=False)
        
        pid = prog.pid
        pid2 = borrowed_prog.pid
        del prog
        del borrowed_prog
        gc.collect()
        
        self.assertEqual(glIsProgram(pid), GL_FALSE, 'Program was not freed')
        self.assertEqual(glIsProgram(pid2), GL_TRUE, 'Program was freed')
        self.assertFalse(vert.valid(), 'vert was not freed')
        self.assertFalse(frag.valid(), 'frag was not freed')
        
        # Free the program object
        glDeleteProgram(pid2)        
        
    def test_attach(self):
        "Test if shader objects are attached correctly"
        prog = ShaderProgram.new_program()
        vert, frag = self.get_objects()
        
        self.assertEqual(0, prog.shaders_count, 'prog have shaders linked')
        prog.attach(vert, frag)
        self.assertEqual(2, prog.shaders_count, 'prog do not have 2 shaders linked')
        
        shaders = prog.shaders()
        self.assertEqual(2, len(shaders), 'shaders length is not 2')
        self.assertIn(vert, shaders, 'vert is not in the returned shader objects')
        self.assertIn(frag, shaders, 'frag is not in the returned shader objects')
        
        self.assertFalse(vert.owned)
        self.assertFalse(frag.owned)
        
    def test_detach(self):
        "Test if shader objects are detached correctly"
        prog = ShaderProgram.new_program()
        vert, frag = self.get_objects()
        prog.attach(vert, frag)
        
        prog.detach(vert)
        self.assertEqual(1, prog.shaders_count, 'prog do not have 1 shader linked')
        
        shaders = prog.shaders()
        self.assertEqual(1, len(shaders), 'shaders length is not 1')
        self.assertIn(frag, shaders, 'frag is not in the returned shader objects')
        self.assertNotIn(vert, shaders, 'vert is in the returned shader objects')
        
        self.assertTrue(vert.owned)
        self.assertFalse(frag.owned)
        
    def test_link(self):
        "Test if a shader program links correctly"
        prog = ShaderProgram.new_program()
        vert, frag = self.get_objects('shader2')
        lib = ShaderObject.fragment()
        
        with open(frag_path('frag_lib')) as f:
            lib.source = f.read()
            self.assertTrue(lib.compile(), 'lib did not compile successfully')
        
        prog.attach(vert, frag, lib)
        
        self.assertEqual(GL_FALSE, prog.link_status, 'link status is not false')
        self.assertTrue(prog.link(), 'link was not successful')
        self.assertEqual(GL_TRUE, prog.link_status, 'link status is not true')
        
    def test_link_fail(self):
        "Test a shader program that links incorrectly"
        prog = ShaderProgram.new_program()
        vert, frag = self.get_objects('shader2')
        prog.attach(vert, frag)
        
        self.assertEqual(GL_TRUE, frag.compiled, 'frag compilation failed')        
        self.assertFalse(prog.link(), 'link was successful')
        self.assertEqual(GL_FALSE, prog.link_status, 'link status is not false')
        
        logs = prog.logs
        self.assertNotEqual(0, prog.log_length, 'log length is 0')
        self.assertEqual(prog.log_length, len(logs), 'log_length do not match returned log length')
        self.assertIn('Function: secret_method( is not implemented', logs, 'error not found')
        
    def test_use_remove(self):
        " Test use and clear "
        prog = ShaderProgram.new_program()
        vert, frag = self.get_objects()
        prog.attach(vert, frag)
        prog.link()
        self.assertIsNone(current_program(), 'Current program is not None')
        prog.use()
        self.assertEqual(current_program(), prog, 'Program is not in use')
        ShaderProgram.clear()
        self.assertIsNone(current_program(), 'Current program is not None')        
        
class TestAccessors(unittest.TestCase):

    def test_accessor_free(self):
        " Test accessor method when the original program was freed "
        shader = from_files_names(vert_path('shader1'), frag_path('shader1'))
        uniforms = shader.uniforms
        attributes = shader.attributes
        del shader
        gc.collect()
        
        self.assertIsNone(None, uniforms.prog())
        
        with self.assertRaises(RuntimeError, msg='reload succeed') as cm1:
            uniforms.reload()
            
        with self.assertRaises(RuntimeError, msg='reload succeed') as cm2:
            attributes.reload()
            
        self.assertEqual('Shader was freed', str(cm1.exception), 'Exception do not matches')
        self.assertEqual('Shader was freed', str(cm2.exception), 'Exception do not matches')  
        
    def test_repr(self):
        "Test if repr works"
        shader = from_files_names(vert_path('shader1'), frag_path('shader1'))
        
        uniforms_names = eval(repr(shader.uniforms))
        for name, info in shader.uniforms:
            self.assertIn(name, uniforms_names)
            uniforms_names.remove(name)
            
        attributes_names = eval(repr(shader.attributes))
        for name, info in shader.attributes:
            self.assertIn(name, attributes_names)
            attributes_names.remove(name)
        
        self.assertEqual(0, len(uniforms_names), 'Some name were not found: {}.'.format(uniforms_names))
        self.assertEqual(0, len(attributes_names), 'Some name were not found: {}.'.format(attributes_names))
        
    def test_get_information_and_contains(self):
        " Get extended information on an uniform "
        shader = from_files_names(vert_path('shader1'), frag_path('shader1'))
        
        view = shader.uniforms["view"]
        self.assertEqual('view', view.name)
        self.assertEqual(1, view.size)
        self.assertEqual(GL_FLOAT_MAT3, view.type)
        
        vert = shader.attributes["vert"]
        self.assertEqual('vert', vert.name)
        self.assertEqual(1, vert.size)
        self.assertEqual(GL_FLOAT_VEC3, vert.type)
        
        self.assertIn(view, shader.uniforms)
        self.assertIn('model', shader.uniforms)
        self.assertIn(vert, shader.attributes)
        self.assertIn('vert', shader.attributes)
        self.assertNotIn('foo', shader.uniforms)
        self.assertNotIn('foo', shader.attributes)
        
        with self.assertRaises(IndexError, msg='key found') as cm1:
            shader.uniforms['foo']
            
        with self.assertRaises(IndexError, msg='key found') as cm2:
            shader.attributes['foo']
            
        self.assertEqual('Key foo not found', str(cm1.exception), 'Exception do not matches')
        self.assertEqual('Key foo not found', str(cm2.exception), 'Exception do not matches')
        
class TestUniforms(unittest.TestCase):

    def test_uniforms_data(self):
        " Check if uniforms data matches "
        shader = from_files_names(vert_path('shader1'), frag_path('shader1'))
        self.assertEqual(23, len(shader.uniforms))
        self.assertEqual(23, shader.uniforms_count)
        
        uniforms_names = ['model', 'view', 'test_float', 'test_vec2',
          'test_vec4', 'test_vec3', 'test_int', 'test_ivec2', 'test_ivec3',
          'test_ivec4', 'test_array_float', 'test_array_vec3', 'test_mat2',
          'test_mat3', 'test_mat4', 'test_mat2x3', 'test_mat2x4', 'test_mat3x2',
          'test_mat3x4', 'test_mat4x2', 'test_mat4x3', 'test_array_mat2',
          'test_array_float2']        
        for name, info in shader.uniforms:
            self.assertIn(name, uniforms_names)
            uniforms_names.remove(name)
        
        self.assertEqual(0, len(uniforms_names), 'Some name were not found: {}.'.format(uniforms_names))
        
    def test_get_set_uniforms_single(self):
        " Test get set uniforms as single value "
        round_tuple = lambda x: tuple([round(y, 2) for y in x])
        shader = from_files_names(vert_path('shader1'), frag_path('shader1'))
        uni = shader.uniforms
        
        shader.use()  # Shader must be in use        
        
        uni.test_float = 10.53
        self.assertEqual(10.53, round(uni.test_float, 2))
        
        uni.test_vec2 = (5.4, 2.55)
        self.assertEqual((5.4, 2.55), round_tuple(uni.test_vec2) )
        
        uni.test_vec3 = (23.2, 64.33, 2.34)
        self.assertEqual((23.2, 64.33, 2.34), round_tuple(uni.test_vec3) )
        
        uni.test_vec4 = (11.1, 623.32, 67.75, 23.63)
        self.assertEqual((11.1, 623.32, 67.75, 23.63), round_tuple(uni.test_vec4) )
        
        uni.test_int = 8
        self.assertEqual(8, uni.test_int)
        
        uni.test_ivec2 = (844, 453)
        self.assertEqual((844, 453), uni.test_ivec2)
        
        uni.test_ivec3 = (843, 92, 1374)
        self.assertEqual((843, 92, 1374), uni.test_ivec3)
        
        uni.test_ivec4 = (735, 8372, 93, 652)
        self.assertEqual((735, 8372, 93, 652), uni.test_ivec4)
        
        uni.test_mat2 = ((5.0, 8.0), (2.0, 4.0))
        self.assertEqual(((5.0, 8.0), (2.0, 4.0)), uni.test_mat2)
        
        uni.test_mat3 = ((5.0, 8.0, 7.0), (2.0, 4.0, 21.0), (2.0, 10.0, 34.0))
        self.assertEqual(((5.0, 8.0, 7.0), (2.0, 4.0, 21.0), (2.0, 10.0, 34.0)), uni.test_mat3)
        
        uni.test_mat3 = ((5.0, 8.0, 7.0), (2.0, 4.0, 21.0), (2.0, 10.0, 34.0))
        self.assertEqual(((5.0, 8.0, 7.0), (2.0, 4.0, 21.0), (2.0, 10.0, 34.0)), uni.test_mat3)
        
        uni.test_mat4 = ((5.0, 8.0,  7.0,  9.0),
                         (2.0, 4.0,  21.0, 32.0),
                         (2.0, 10.0, 34.0, 91.0),
                         (1.0, 4.0,  8.0,  19.0))
        
        self.assertEqual(((5.0, 8.0,  7.0,  9.0),
                          (2.0, 4.0,  21.0, 32.0),
                          (2.0, 10.0, 34.0, 91.0),
                          (1.0, 4.0,  8.0,  19.0)), uni.test_mat4)
        
        uni.test_mat2x3 = ((8.0, 9.0, 10.0), (20.0, 11.0, 2.0))
        self.assertEqual(((8.0, 9.0, 10.0), (20.0, 11.0, 2.0)), uni.test_mat2x3)
        
        uni.test_mat2x4 = ((8.0, 9.0, 10.0, 3.0), (20.0, 11.0, 2.0, 13.0))
        self.assertEqual(((8.0, 9.0, 10.0, 3.0), (20.0, 11.0, 2.0, 13.0)), uni.test_mat2x4)
        
        uni.test_mat3x2 = ((8.0, 9.0), (20.0, 11.0), (17.0, 16.0))
        self.assertEqual(((8.0, 9.0), (20.0, 11.0), (17.0, 16.0)), uni.test_mat3x2)
        
        uni.test_mat3x4 = ((8.0,  9.0,  10.0,  3.0),
                           (20.0, 11.0,  2.0, 13.0),
                           (14.0, 15.0, 16.0, 83.0))
        self.assertEqual(((8.0,  9.0,  10.0,  3.0),
                           (20.0, 11.0,  2.0, 13.0),
                           (14.0, 15.0, 16.0, 83.0)), uni.test_mat3x4)
        
        uni.test_mat4x2 = ((10.0, 11.0), (12.0, 13.0),
                           ( 1.0,  2.0), (14.0, 15.0))
        self.assertEqual(((10.0, 11.0), (12.0, 13.0),
                           ( 1.0,  2.0), (14.0, 15.0)), uni.test_mat4x2)
        
        uni.test_mat4x3 = ((1.0, 2.0, 3.0), ( 4.0,  5.0,  6.0),
                           (7.0, 8.0, 9.0), (10.0, 11.0, 12.0))
        self.assertEqual(((1.0, 2.0, 3.0), ( 4.0,  5.0,  6.0),
                           (7.0, 8.0, 9.0), (10.0, 11.0, 12.0)), uni.test_mat4x3)
        
    def test_get_set_uniforms_array(self):
        " Get/Set array types "        
        round_tuple = lambda x: tuple([round(y, 2) for y in x])                
        shader = from_files_names(vert_path('shader1'), frag_path('shader1'))        
        uni = shader.uniforms
        
        shader.use()  # Shader must be in use        
        
        uni.test_array_float = (8.45, 30.3, 53.67, 9.73)
        self.assertEqual((8.45, 30.3, 53.67, 9.73), round_tuple(uni.test_array_float), 'array values do not matches')
        
        uni.test_array_float2 = (7.67,)
        self.assertEqual((7.67,), round_tuple(uni.test_array_float2), 'array values do not matches')
        
        uni.test_array_vec3 = ((8.0, 6.0, 80.0), (5.0, 17.0, 45.0))
        self.assertEqual(((8.0, 6.0, 80.0), (5.0, 17.0, 45.0)),
                         uni.test_array_vec3, 'array values do not matches')
        
        uni.test_array_vec3 = ((8.0, 9.0, 10.0, 11.0, 12.0, 13.0),)
        self.assertEqual(((8.0, 9.0, 10.0), (11.0, 12.0, 13.0)),
                         uni.test_array_vec3, 'array values do not matches')
        
        uni.test_array_mat2 = (((1.0, 2.0), (3.0, 4.0)),
                               ((2.0, 3.0), (5.0, 6.0)),
                               ((7.0, 8.0), (9.0, 10.0)))
        
        self.assertEqual((((1.0, 2.0), (3.0, 4.0)),
                          ((2.0, 3.0), (5.0, 6.0)),
                          ((7.0, 8.0), (9.0, 10.0))),
                         uni.test_array_mat2, 'array values do not matches')
        
    def test_set_incomplete_overflow(self):
        " Set incomplete array uniforms "
        shader = from_files_names(vert_path('shader1'), frag_path('shader1'))        
        uni = shader.uniforms
        
        shader.use()  # Shader must be in use   
        
        # Incomplete
        uni.test_array_float = (8.45, 30.3, 53.67, 9.73)
        uni.test_array_float = ()
        self.assertEqual((0.0, 0.0, 0.0, 0.0), uni.test_array_float)
        
        uni.test_vec3 = (23.0, 64.0, 2.0)
        uni.test_vec3 = (1.0,)
        self.assertEqual((1.0, 0.0, 0.0), uni.test_vec3 )
        
        uni.test_array_vec3 = ((8.0, 6.0, 80.0), (5.0, 17.0, 45.0))
        uni.test_array_vec3 = ()
        self.assertEqual(((0.0, 0.0, 0.0), (0.0, 0.0, 0.0)), uni.test_array_vec3 )
        
        uni.test_array_vec3 = ((8.0, 6.0, 80.0), (5.0, 17.0, 45.0))
        uni.test_array_vec3 = ()
        self.assertEqual(((0.0, 0.0, 0.0), (0.0, 0.0, 0.0)), uni.test_array_vec3 )
        
        uni.test_array_vec3 = ((8.0, 6.0, 16.0, 17.0),)
        self.assertEqual(((8.0, 6.0, 16.0), (17.0, 0.0, 0.0)), uni.test_array_vec3 )
        
        uni.test_mat3 = ((5.0, 8.0, 7.0), (2.0, 4.0, 21.0))
        self.assertEqual(((5.0, 8.0, 7.0), (2.0, 4.0, 21.0), (0.0, 0.0, 0.0)), uni.test_mat3)
        
             
    def test_set_uniform_bad_values(self):
        " Set an uniform data with data of incorrect type "
        shader = from_files_names(vert_path('shader1'), frag_path('shader1'))  
        uni = shader.uniforms
        
        # Make sure no shader are used
        shader.clear()        
        
        with self.assertRaises(pyglet.gl.lib.GLException, msg='No error raised when setting uniforms without an active shader'):
            uni.test_int = 8
            
        shader.use()
        
        with self.assertRaises(TypeError, msg='No error raised when setting uniforms with bad type'):
            uni.test_int = 9.0
            
        with self.assertRaises(TypeError, msg='No error raised when setting uniforms with bad type'):
            uni.test_array_vec3 = (1,)
            
        # Overflow      
        with self.assertRaises(IndexError, msg='Overflow assign succeed'):
            uni.test_vec3 = (23.0, 64.0, 2.0, 83.0)
            
        with self.assertRaises(IndexError, msg='Overflow assign succeed'):
            uni.test_array_vec3 = ((8.0, 6.0, 16.0, 17.0, 9.0, 2.0, 8.0),)

        
    def test_get_set_unforms_fail(self):
        " Get / Set missing uniforms "
        shader = from_files_names(vert_path('shader1'), frag_path('shader1'))
        
        with self.assertRaises(AttributeError, msg='uniform found') as cm1:
            shader.uniforms.foobar

        with self.assertRaises(AttributeError, msg='uniform found') as cm2:
            shader.uniforms.foobar = 1
            
        self.assertEqual('No uniform named "foobar" found', str(cm1.exception))   
        self.assertEqual('No attribute/uniform named "foobar" found', str(cm2.exception))   

class TestShaders(unittest.TestCase):
    
    def test_from_files(self):
        " Test from_files "        
        vert = open(vert_path('shader1'), 'r')
        frag = open(frag_path('shader1'), 'r')
        shader = from_files(vert, frag)
        
        self.assertFalse(vert.closed, 'vertex source file must not be closed')
        self.assertFalse(frag.closed, 'fragment source file must not be closed')
        
        self.assertTrue(eof(vert), 'vertex source must have been read')
        self.assertTrue(eof(frag), 'vertex source must have been read')
        
        self.assertTrue(shader.valid(), 'generated shader is not valid')
        
        vert.close()
        frag.close()
        
    def test_from_files_multiple(self):
        " Test from_files with multiple shaders files "
        vert = open(vert_path('shader2'), 'r')
        frag = open(frag_path('shader2'), 'r')
        lib = open(frag_path('frag_lib'), 'r')
        
        shader = from_files(vert, (frag, lib))
        
        self.assertTrue(shader.valid(), 'generated shader is not valid')
        
        vert.close()
        frag.close()
        lib.close()
        
    def test_from_file_names(self):
        verts = vert_path('shader2') 
        frags = ( frag_path('shader2'), frag_path('frag_lib') )
        shader = from_files_names(verts, frags)
        
        self.assertTrue(shader.valid(), 'generated shader is not valid')
        
    def test_from_files_bad_compilation(self):
        " Test from_files with bad shaders "
        vert = open(vert_path('shader_bad'), 'r')
        frag = open(frag_path('shader_bad'), 'r')
        
        with self.assertRaises(ShaderCompilationError, msg='invalid shader was compiled') as cm:
            from_files(vert, frag)
            
        logs = cm.exception.logs     
        self.assertIn('Undeclared identifier: x', logs, 'Error not found')
        self.assertIn('Undeclared identifier: y', logs, 'Error not found')
        self.assertIn('Syntax error: "}" parse error', logs, 'Error not found')
        self.assertIn('3 compilation errors.  No code generated', logs, 'Error not found')
        self.assertIn('Syntax error: ";" parse error', logs, 'Error not found')
        self.assertIn('1 compilation errors.  No code generated', logs, 'Error not found')
            
        vert.close()
        frag.close()

    def test_from_files_bad_linking(self):
        " Test from_files with missing shaders "
        vert = open(vert_path('shader2'), 'r')
        frag = open(frag_path('shader2'), 'r')
        
        with self.assertRaises(ShaderCompilationError, msg='invalid shader was compiled') as cm:
            from_files(vert, frag)
            
        logs = cm.exception.logs
        self.assertIn('Function: secret_method( is not implemented', logs, 'Error not found')
        
        vert.close()
        frag.close()
        
    def test_from_string(self):
        """
        Because from_string is used internally by from_files and from_file_names,
        I think it is safe to say the function is well tested
        """

EXTENSIONS_WARNINGS = []

def cannot_test(gl_version, glsl_version):
    glsl = bytearray()
    for i in glGetString(GL_SHADING_LANGUAGE_VERSION):
        if i != 0:
            glsl.append(i)
        else:
            break
    
    glsl = [ int(v) for v in glsl.decode('utf8').split('.')]
    
    gl_ok = gl_info.have_version(*gl_version)
    glsl_ok = (glsl[0] > glsl_version[0]) or (glsl[0] == glsl_version[0] and glsl[1] >= glsl_version[1])
    
    return not gl_ok or not glsl_ok

class TestExtensions(unittest.TestCase):
    
    @unittest.skipIf(cannot_test((3,0), (1,30)), "function requires opengl 3.0 and GLSL 1.30 support to be tested")    
    def test_load(self):
        " Test extension loading "
        
        load_extension('uint_uniforms')
        
        with self.assertRaises(ImportError) as cm1:
            load_extension('foo_bar')        
        
        with self.assertRaises(PyShadersExtensionError) as cm2:
            load_extension('create_mmo')
            
        with self.assertRaises(ImportError) as cm3:
            load_extension('uint_uniforms')      
        
        self.assertEqual('No extension named "foo_bar" found', str(cm1.exception), 'Exception do not matches')
        self.assertEqual('Extension "create_mmo" is not supported', str(cm2.exception), 'Exception do not matches')
        self.assertEqual('Extension "uint_uniforms" is already loaded', str(cm3.exception), 'Exception do not matches')
        
        self.assertIn('uint_uniforms', pyshaders.LOADED_EXTENSIONS, 'Extension name is not in the loaded extensions')
        self.assertTrue(extension_loaded('uint_uniforms'), 'Extension name is not in the loaded extensions')
        self.assertNotIn('create_mmo', pyshaders.LOADED_EXTENSIONS, 'Extension name is in the loaded extensions')
        self.assertNotIn('foo_bar', pyshaders.LOADED_EXTENSIONS, 'Extension name is in the loaded extensions')
        self.assertFalse(extension_loaded('create_mmo'), 'Extension name is in the loaded extensions')
        self.assertFalse(extension_loaded('foo_bar'), 'Extension name is in the loaded extensions')
    
    @unittest.skipIf(cannot_test((3,0), (1,30)), 'function requires opengl 3.0 and GLSL 1.30 support to be tested')    
    def test_check(self):
        " Test extension support "
        self.assertTrue(check_extension('uint_uniforms'))
        self.assertFalse(check_extension('create_mmo'))
    
    @unittest.skipIf(cannot_test((3,0), (1,30)), "function requires opengl 3.0 and GLSL 1.30 support to be tested")    
    def test_uint_uniforms(self):
        # Extension might have been loaded before
        if not extension_loaded('uint_uniforms'):
            load_extension('uint_uniforms') 
            
        shader = from_files_names(vert_path('shader1'), frag_path('ext_shader_uint'))
        
        self.assertEqual(8, len(shader.uniforms))
        self.assertEqual(8, shader.uniforms_count)
        
        uniforms_names = ['model', 'view', 'test_uint', 'test_uvec2', 'test_uvec4',
                          'test_uvec3', 'test_uint_3', 'test_uvec2_2']        
        for name, info in shader.uniforms:
            self.assertIn(name, uniforms_names)
            uniforms_names.remove(name)
        
        shader.use()        
        
        uni = shader.uniforms
        
        uni.test_uint = 2345
        self.assertEqual(2345, uni.test_uint)
        
        uni.test_uvec2 = (2147483648, 78)
        self.assertEqual((2147483648, 78), uni.test_uvec2 )
        
        uni.test_uvec3 = (7000, 8000, 80000)
        self.assertEqual((7000, 8000, 80000), uni.test_uvec3 )
        
        uni.test_uvec4 = (1, 2, 3, 30000)
        self.assertEqual((1, 2, 3, 30000), uni.test_uvec4)
        
        uni.test_uint_3 = (1, 3782463, 3)
        self.assertEqual((1, 3782463, 3), uni.test_uint_3) 
        
        uni.test_uvec2_2 = ((99, 88), (9345, 9456))
        self.assertEqual(((99, 88), (9345, 9456)), uni.test_uvec2_2) 
        
        
        self.assertEqual(0, len(uniforms_names), 'Some name were not found: {}.'.format(uniforms_names))

if __name__ == '__main__':
    #Create an opengl context for our tests
    window = pyglet.window.Window(visible=False)
    unittest.main()