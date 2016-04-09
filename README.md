PyShaders
===================


Pyshaders aims to completely wraps the opengl2.1 shader api in a python module. Pyshaders provides a pythonic OOP api that hides the lower level (ctypes) calls. Pyshaders provides a high level api and a low level api, and it can be integrated easily with existing code because it does not occlude the underlying opengl values.

PyShaders was programmed using very high standards. This means that Pyshaders is fully tested and it comes with an exhaustive documentation (this file). The code is DRYer than California in 2015 and it makes uses of many advanced python functionalities to make the code smaller, easier to use and easier to read.

----------

- [PyShaders](#)
	- [Requirements](#requirements)
	- [Installation](#installation)
		- [Pip](#pip)
		- [Manual](#manual)
	- [License](#license)
	- [Extensions](#extensions)
	  - [Overview](#extensions_overview)
	  - [Usage](#extensions_usage)
	  - [All extensions](#extensions_all)
	- [Programmer's Guide](#guide)
		- [High level api](#high)
			- [Compiling shaders](#compiling)
			- [Uniforms](#uniforms)
			- [Attributes](#attributes)
			- [Querying shader informations](#query)
		- [Low level api](#low)
			- [Overview](#lowover)
			- [Owned VS Borrowed](#owned)
			- [Integrating with existing code](#integrate)
	- [API](#api)
		- [Top level functions](#top)
		- [ShaderObject](#shaderobject)
		- [ShaderProgram](#shaderprogram)
		- [Uniforms/Attributes](#uniattr)
	- [Future](#future)


<a name="requirements"></a>

**Requirements**
-------------
- Python >= 3.3
- An GPU that supports OpenGL 2.1 core
- Pyglet (any versions) <sub><sup>(See the Future section about supporting other libraries)</sup></sub>


<a name="installation"></a>

**Installation**
-------------

<a name="pip"></a>

### Pip
Run this command
>pip install pyshaders [--install-option="--no-extensions"]

<a name="manual"></a>

### Manual
1. Download the source
2. Copy **pyshaders.py** in your project
3. **Optionally** copy **pyshaders_extensions** in the same folder (see [extensions](#extensions))  

**or**

1. Download the source
2. Run **python setup.py install [--no_extensions]** 


<a name="license"></a>

License
-------------

>MIT License

>Copyright (c) 2016 Gabriel Dubé

>Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

>The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

>THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

<a name="extensions"></a>

Extensions
--------------
**new in 1.1.0!**  

<a name="extensions_overview"></a>

### Overview
By default, pyshaders only wraps the api of opengl 2.1. In order to wrap newer features that might not be supported on older hardware, pyshaders uses **extension modules**. Extensions modules are python modules located in the **pyshaders_extensions** package. These modules **must not be imported using the import keyword**, instead they are loaded using the **load_extension** function. load_extension checks if the client supports the extension and a few other things, if something is wrong **ImportError** or a **PyShadersExtensionError** error is raised.

Extensions modules must not be imported using the **import keyword** because an extension module by itself do nothing: their roles are to register new functionalities inside the pyshaders module.

Lastly, extensions **must be loaded before using the pyshader api**. 

<a name="extensions_usage"></a>

### Usage

Pyshaders offers three top levels functions to manage extensions.

```python
def extension_loaded(extension_name):
def check_extension(extension_name):
def load_extension(extension_name):
```

**extension_name** is any of the extension under [All Extensions](%extensions_all).

**extension_loaded** checks if an extension was loaded. An extension cannot be loaded more than once.  
**check_extension** checks if the client can use the extension  
**load_extension** loads the extension

Example:  
```python
from pyshaders import load_extension, extension_loaded,  check_extension, PyShadersExtensionError
try:
    load_extension('uint_uniforms')
except PyShadersExtensionError:
    print("Your system do not meet the requirements to use this program")
    exit()
    
print(extension_loaded('uint_uniforms'))
# True

print(check_extension('uint_uniforms'))
# True
```

<a name="extensions_all"></a>

### All extensions

| Name          | Requirements             | Pyshaders Version | Description |
| ------------- | ------------------------ | ----------------- | ----------- |
| uint_uniforms | GL >= 3.0 / GLSL >= 1.30 | 1.1.0             | Add support for unsigned integers uniforms |


<a name="guide"></a>

Programmer's Guide
-------------

<a name="high"></a>

###**High level api**
Unless you are extending an existing code base, the high level api is most likely the api you want to use. 
It handles compiling, uniforms, attributes and freeing.

<a name="compiling"></a>

#### **Compiling shaders**
Pyshaders offers 3 high level functions to load and compile shaders, here are their headers:
```python
def from_string(verts, frags):
def from_files_names(verts, frags):
def from_files(verts, frags):
```
Each of these functions takes the parameters __*verts*__ and __*frags*__. These parameters accept either  a single value or any iterable of vertex sources/fragment sources. 

The returned object is called a ShaderProgram. It is the object that wraps most of the pyshaders features . For more information, see the API section. 

Additionally, if an error happens during compilation, a ShaderCompilationError is raised.  The **logs** property (available on ShaderPrograms, ShaderObjects and ShaderCompilationError ) can be used to access the error details.

Here is a simple shader loading function:
```python
from pyshaders import from_files_names, ShaderCompilationError 
try:
    shader = from_files_names("main.vert", "main.frag")
    shader2 = from_files_names("main.vert", ["main.frag", "lib.frag"])
except ShaderCompilationError as e:
    print(e.logs) 
    exit()

print(shader, shader2, sep=", ")
#ShaderProgram 1, ShaderProgram 2
```


To use or remove a shaderprogram, simply call
```python
shader.use()
ShaderProgram.clear() # or shader.clear()
```

**What happens during the compilation?**
- **from_files_names** open the files
- The files contents are loaded into strings
- For every source given, a **ShaderObject** is compiled (see Low Level API)
- The compiled **ShaderObjects** are linked to a **ShaderProgram**
- The uniforms and attributes are cached (see uniforms)
- The  **ShaderProgram** is returned



<a name="uniforms"></a>

#### **Uniforms**

My favorite feature, pyshaders allows seamless uniform writing and reading. After a shader is compiled, all its defined uniforms are accessible via the **uniforms** attribute. Example:

```python
# In the shader source:
# uniform float my_uniform;
# uniform float foo;
shader = from_files_names("main.vert", "main.frag")
shader.use()  #The shader must be in use to set uniforms

print(shader.uniforms)
#["my_uniform", "foo"]

shader.uniforms.my_uniform = 555.0
print(shader.uniforms.my_uniform)
# 555.0
```

No need to declare the *type* or the *name* of the uniforms, pyshaders already knows it! The only "limitation" is that the value are statically typed. For example, assigning an int to a uniform float will raise a **TypeError**.
Also, assigning more values than an array can contains will raise an **IndexError** 

**Accessing uniforms properties**
The properties pyshader uses in order to seamlessly get/set uniforms can queried just as easily. The fields are returned by **[glGetActiveUniform](http://docs.gl/gl2/glGetActiveUniform)**.

Example:
```python
uniform = shader.uniforms["my_uniform"]
print(uniform)
# Uniform(loc=c_long(0), type=35675, size=1, name='my_uniform',
# get=<function[...]>, set=<function[...]>)
```
**Special setting behaviour**

- Setting incomplete values

Due to ctypes initializing buffers with zeros, setting incomplete values is permitted. The ignored values will be zeroed. Example:

```python
# uniform vec4 unicorn_swag = vec4(6, 6, 6, 6);

print(shader.uniforms.unicorn_swag)
# (6.0, 6.0, 6.0, 6.0)

shader.uniforms.unicorn_swag = (1.0, 2.0, 3.0)
print(shader.uniforms.unicorn_swag)
# (1.0, 2.0, 3.0, 0.0)

shader.uniforms.unicorn_swag = ()
print(shader.uniforms.unicorn_swag)
# (0.0, 0.0, 0.0, 0.0)

shader.uniforms.unicorn_swag = (1.0, 2.0, 3.0, 4.0, 5.0)
#IndexError
```

By passing an empty tuple, you can quickly clear any array!

- Setting multi level array

When setting the value of multi-level arrays (ex: vec4[]), pyshaders flatten the values so the layout does not matter. The "depth" of the array **still** matters. Example:

```python
# uniform vec2[3] blushing_wombat;

#This works, obviously
shader.uniforms.blushing_wombat = ((1.0, 2.0), (3.0, 4.0), (8.0, 11.0))
print(shader.uniforms.blushing_wombat)
# ((1.0, 2.0), (3.0, 4.0), (8.0, 11.0))

# This is also accepted
shader.uniforms.blushing_wombat = ( (5.0, 3.0, 2.0, 7.0, 1.0, 1.5), )
print(shader.uniforms.blushing_wombat)
# ((5.0, 3.0), (2.0, 7.0), (1.0, 1.5))

# Not this!
# The underlying code is waiting for an array of array
shader.uniforms.blushing_wombat = (5.0, 3.0, 2.0, 7.0, 1.0, 1.5)
```

<a name="attributes"></a>

#### **Attributes**

Shader attributes do not have a get/set syntax like the uniforms (for now), but the properties of the attributes can be accessed like with the uniforms: using the dictionary syntax. The attributes information is queried using **[glGetActiveAttrib](http://docs.gl/gl2/glGetActiveAttrib)**

Example:
```python
# In the shader
# layout(location = 0)in vec3 vertex;
attribute = shader.attributes["vertex"]
print(attribute)
# Uniform(loc=c_long(0), type=35665, size=1, name='vertex')
```


<a name="query"></a>

#### **Querying shader informations**

With OpenGL is is possible query information about a shader (information that would be queried with a glGet* call). With pyshaders, it is possible to access these values with python properties. For an exhaustive list of every properties, see the API section. Example:

```python
shader = from_files_names("main.vert", "main.frag")
shader.compiled  # Equivalent to glGetProgram with GL_COMPILE_STATUS
#true
```

<a name="low"></a>
### **Low level api**

The low level api can be used if someone wants full control over the compilation and linking stage.


<a name="lowover"></a>

#### **Overview**

When using the low level api, it's the programmer job to create, compile, link and free the pyshaders objects. The main advantage is that it is possible share ShaderObjects with many ShaderProgram. 

To instance a new ShaderObject, the **vertex** and the **fragment** class methods must be used. The constructor is reserved to wrap existing objects. Setting the shader source is done using the **source** property. Finally, the method**compile** compiles the shader. It will return False if there was an error during the compilation. The **logs** property holds the details of the error.

For ShaderPrograms, the classmethod **new_program** creates a new empty program. Just like the ShaderObjects, the constructor is used to wrap existing objects. ShaderObjects are attached/detached using the **attach**/**detach** methods. Attach and detach take any number of ShaderObjects. Finally, a ShaderProgram can be linked using **link**. Just like the ShaderObjects compile, the method will return False if there was an error. The **logs** property holds the details of the error.

Like raw opengl, ShaderObjects can be attached/detached after the program was linked. Still, linking is an expensive function due to the caching done by pyshaders. Ideally, a shaderprogram should be linked only once.

It is possible to retrieve a shader program objects using the **shaders** method. The returned shaders borrow the gl resource.

Here is the from_string code:
```python
def from_string(verts, frags):
    if isinstance(verts, str): verts = (verts,)
    if isinstance(frags, str): frags = (frags,)
        
    logs, objs = "", []
    
    for src in verts:
        vert = ShaderObject.vertex()
        vert.source = src
        objs.append(vert)
    
    for src in frags:
        frag = ShaderObject.fragment()
        frag.source = src       
        objs.append(frag)
        
    for obj in objs:
        if obj.compile() is False:
            logs += obj.logs
    
    if len(logs) == 0:
        prog = ShaderProgram.new_program()
        prog.attach(*objs)
        if not prog.link():
            raise ShaderCompilationError(prog.logs)
            
        return prog
    
    raise ShaderCompilationError(logs)
```

<a name="owned"></a>

#### **Owned VS Borrowed**

Pyshaders objects wraps underlying globjects. Usually,  pyobjects **own** the underlying data. This means that, when the object is freed (garbage collected), the globjects is marked for deletion (ex: using **glDeleteShader**). Sometimes, a single globject can be shared with multiple pyobjects. In this situation, only one object should have the ownership. The others "borrow" the globject. When an pyobject with a borrowed status is freed,  the underlying globject is not marked for deletion.

The owned/borrowed behavior is detailed on every function where is make sense. 
The property **owned** ShaderObject/ShaderPrograms can be set to change the ownership.

**Freeing ShaderPrograms**
When a program is freed, all the linked shader objects are also marked for destruction. If the program uses a shared shader object, the object must be detached before the object is freed.  **Make sure that *delete* is set to false so that the shader is not freed after being detached.**

Example:
```python
shader.detach(shared_object, delete=False)
```

<a name="integrate"></a>

#### **Integrating with existing code**

It is possible to wrap existing object with pyshader using the ShaderObject and ShaderProgram constructors.
Object wrapped do not own the underlying resources by default. For the object to own the underlying shader, owned=True must be passed to the constructor.

Example:
```python
pid = glCreateProgram()
sid = glCreateShader(GL_VERTEX_SHADER)
shader = ShaderObject(sid)  
program = ShaderProgram(pid, owned=True)
glDeleteShader(sid)
```

Pyshaders also have the **current_program** function that returns the currently bound program in a ShaderProgram.
```python
program = pyshaders.current_program()
print(program is None)
#True

glUseProgram(my_program)
program = pyshaders.current_program()
print(program)
# ShaderProgram 1
```


<a name="api"></a>

**API**
-------------

<a name="top"/>
### **Top level functions**

>**current_program()**  
>Return the currently bound shader program or None if there is None.
>The returned shader do not own the underlying buffer.

♣
>**from_string(verts, frags)**  
>High level loading function.  
>Load a shader using sources passed in sequences of string.
>Each source is compiled in a shader unique shader object.
> Return a linked shaderprogram. The shaderprogram owns the gl resource.
>
>- *verts*: Sequence of vertex shader sources
>- *frags*: Sequence of fragment shader sources

♣
>**from_files_names(verts, frags)**  
> High level loading function.
>Open files and use 'from_files' and 'from_strings' internally
>Each source is compiled in a shader unique shader object.
>Return a linked shaderprogram. The shaderprogram owns the gl resource.
>
>- *verts*: Sequence of file names pointing to vertex shader source file
>- *frags*: Sequence of file names pointing to fragment shader source file

♣
>**from_files(verts, frags)**  
>High level loading function.  
>Create a shader from readable IO streams (Such as types returned by open()).
>from_files will *read()* all the files contents, but it will NOT close the files.
>The file must be opened with a 'r' mode, NOT 'rb'.
>
>Use from_string internally.
>Each source is compiled in a shader unique shader object.
>Return a linked shaderprogram. The shaderprogram owns the gl resource.
>
>- *verts*: Sequence of files pointing to vertex shader source file
>- *frags*: Sequence of files pointing to a fragment shader source file

♣

>**extension_loaded(extension_name)**  
>Return True if the extension is loaded, False otherwise.  
>- *extension_name*: Name of the extension to check

♣

>**check_extension(extension_name)**  
>Return True if the client can use the extension, False otherwise  
>- *extension_name*: Name of the extension to check

♣

>**load_extension(extension_name)**  
> Load the extension. Will raise an ImportError if the extension was already loaded
> or a PyShadersExtensionError if the extension is not supported by the client.  
>- *extension_name*: Name of the extension to check

<a name="shaderobject"/>
### **ShaderObject**

>**ShaderObject(object)**  
> Represent a shader object. This wrapper can be used to get information
>about a shader object.
>
>**Slots**:  
> - *sid*: Underlying opengl shader id. 
> - *owned*: If the object owns the underlying shader
>
>**Properties**:  
>- *source*: The shader source
>
>**Readonly Properties**:  
>- *logs*: The shader compilation log
>- *type*: The shader type (GL_SHADER_TYPE)
>- *delete_status*: Delete status (GL_DELETE_STATUS)
>- *compiled*: Compile status (GL_COMPILE_STATUS)
>- *log_length*: Logs length (GL_INFO_LOG_LENGTH)
>- *source_length*: Source length (GL_SHADER_SOURCE_LENGTH)

♣
>**ShaderObject.vertex(cls)**  
> Class method, create a new uninitialized vertex shader.
> The shaderobject owns the gl resource.

♣
>**ShaderObject.fragment(cls)**  
> Class method, create a new uninitialized fragment shader
> The shaderobject owns the gl resource.

♣
>**ShaderObject.compile(self)**  
> Compile the shader. Return True if the compilation was successful false otherwise 

♣
>**ShaderObject.valid(self)**  
> Check if the underlying shader is valid.
> Return True if it is, False otherwise.

♣
>**ShaderObject.\_\_init\_\_(self, shader_id, owned=False)**  
>Wrap an existing shader object.
>          
> *shader_id*: Shader id. Either a python int or a c_[u]int.
> *owned*: If the object should own the underlying buffer

♣
>**ShaderObject.\_\_bool\_\_(self)**  
> Like "ShaderObject.valid(self)"

♣
>**ShaderObject.\_\_eq\_\_(self, other)**  
> True if both shaders have the same underlying buffer id. False otherwise


<a name="shaderprogram"/>

### **ShaderProgram**
>**ShaderProgram(object)**  
> Represent a shader program. This wrapper can be used to get information
>about a shader program. It can also be used to get and set uniforms value
>of the shader
>
>**Slots**:  
>- *pid*: Underlying opengl program id.
>- *owned*: If the object owns the underlying shader
>- *uniforms*: Uniforms collection of the shader
>- *attributes*: Attributes collection of the shader
>
>**Readonly Properties**:  
>- *logs*: The shader linking log
>- *delete_status*:  program delete status (GL_DELETE_STATUS)
>- *log_length*:  Logs length (GL_INFO_LOG_LENGTH)
>- *link_status*:  If the program is linked (GL_LINK_STATUS)
>- *validate_status*:  If the program is validated (GL_VALIDATE_STATUS)
>- *shaders_count*:  Number of shaders object attached to the program (GL_ATTACHED_SHADERS)
>- *attributes_count*:  Number of attributes of the program (GL_ACTIVE_ATTRIBUTES)
>- *uniforms_count*:  Number of uniforms (GL_ACTIVE_UNIFORMS)
>- *max_attribute_length*:  Length of the longest attribute name (GL_ACTIVE_ATTRIBUTE_MAX_LENGTH)
>- *max_uniform_length*:  Length of the longest uniform name (GL_ACTIVE_UNIFORM_MAX_LENGTH)

♣
>**ShaderProgram.new_program(cls)**  
> Create a new program. The object own the ressources

♣
>**ShaderProgram.attach(*objs)**  
>Attach shader objects to the program. 
>Objs must be a list of ShaderObject. 
>
>Ownership of the underlying shaders object is transferred to the program 

♣
> **ShaderProgram.detach(self, *objs, delete=True)**  
>Detach shader objects from the program.
>Objs must be a list of ShaderObject.
>
>- *delete*: If the detached shaders should be marked for destruction

♣
> **ShaderProgram.valid(self)** 
> Check if the underlying program is valid.
> Return True if it is, False otherwise.

♣
> **ShaderProgram.link(self)**  
> Link the shader program. Return True if the linking was successful, False otherwise.
> Also reload the uniform cache is successful

♣
> **ShaderProgram.shaders(self)**  
> Return a list of shader objects linked to the program.
> The returned shader objects do not own the underlying shader.

♣
> **ShaderProgram.use(self)**  
> Use the shader program 

♣
> **ShaderProgram.clear()**  
> Remove the current shader program

♣
> **ShaderProgram.clear()**  
> Remove the current shader program

♣
>**ShaderProgram.\_\_init\_\_(self, program_id, owned=False)**  
>Wrap an existing shader program.
>          
>- *program_id*: Program id. Either a python int or a c_[u]int.
>- *owned*: If the object should own the underlying buffer

♣
>**ShaderProgram.\_\_bool\_\_(self)**  
> Like "ShaderProgram.valid(self)"

♣
>**ShaderProgram.\_\_eq\_\_(self, other)**  
> True if both programs have the same underlying buffer id. False otherwise


<a name="uniattr"/>
### **Uniforms/Attributes**

>**ShaderAccessor(object)**  
>Allow pythonic access to shader uniforms and shader attributes
>This object is created with a shaderprogram and should not be instanced manually.
>
>**Slots**:  
>- prog: Weakref to the uniforms shader program
>- cache: Data about the uniforms
>- cache_type: Type of data in cache

♣
>**ShaderAccessor.reload(self)**  
> Reload or build for the first time the uniforms/attributes cache.
>
> This can be quite expensive so it is only done on shader linking.
>
> If the shader was linked outside the api, you have to call this manually.

♣
>**ShaderAccessor.\_\_iter\_\_(self)**
>
>     for uniform in prog.uniforms
>     
> Iterate over the Uniform cached in the object. 

♣
>**ShaderAccessor.\_\_len\_\_(self)**
>
>     len(prog.uniforms)
>     
> Return the number of uniforms in the program

♣
>**ShaderAccessor.\_\_getitem\_\_(self, key)**
>
>     prog.uniforms["my_uniform"]
>     
> Return information about an uniform. Key must be the name of the uniform as a string.

♣
>**ShaderAccessor.\_\_contains\_\_(self, item)**
>
>     if 'my_uniform' in prog.uniforms
> 
> Return True if an uniform is within the program, Item can be the name of the uniform as a string OR
> a uniform object. 


<a name="future"></a>

**Future**
-------------

I dont think that I will add new features to the main module (pyshaders.py), at least, nothing that will break compatibility. Any feature not supported by OpenGL 2.1 will **never** be added to the main module. For those, extensions will be created. For more informations on extensions see [extensions](#extensions).

Could be added to the main module:

- Support for  other bindings library (ex: PyOpenGL)
- Get/Set support for attributes
- More get for attributes

Could be added as an extension:

- ~~Support for **double, uint ** uniforms~~ (implemented in 1.1.0)
- Support for multi level array ( GL_ARB_arrays_of_arrays ) 
- Uniform structures
- Uniform blocks
- Geometry/Compute shaders
- Subroutines

Will not be added:

- SPIR-V





