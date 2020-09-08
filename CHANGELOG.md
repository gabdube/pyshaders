# Changelog

- [1.1.0](#oneonezero)
- [1.2.0](#onetwozero)
- [1.3.0](#onethreezero)
- [1.4.0](#onefourzero)
- [1.4.1](#onefourone)
- [1.4.2](#onefourtwo)

<a name="onefourtwo"/>
### Pyshaders 1.4.2

- ##### Main module
	- Added context manager to shader. Use `with shader.using():`. Can be nested.

<a name="onefourone"/>
### Pyshaders 1.4.1

- ##### Main module  
    - Added the option to set the matrix transposition when setting uniforms using `pyshaders.transpose_matrices(bool)`
    - Fixed fixtures path on unix
    - Some formatting fix in the readme

<a name="onefourzero"/>
### Pyshaders 1.4.0

- ##### Main module  
    - Fixed a critical bug when compiling shaders

<a name="onetwozero"/>
### Pyshaders 1.3.0

- ##### Main module  
    - Enable and disable all attributes on shaders
    - Use relative imports to load extensions
    - Transposed is set to TRUE when setting uniforms matrices

- ##### Extensions  
    - pyglbuffers bindings extensions. Use shader.map_attributes(buffer) 
      automatically map the buffer data to the shader attributes using glVertexAttribPointer.

<a name="onetwozero"/>
### Pyshaders 1.2.0

- ##### Main module  
    - More get for attributes
    - Enable/disable vertex attrib arrays
    - Low level wrapper "attribute.point_to" over glVertexAttribPointer

- ##### Extensions  
    - Nothing new

<a name="oneonezero"/>
### Pyshaders 1.1.0

- ##### Main module  
    - Added **load_extension**, **extension_loaded** and **check_extension** to load pyshaders extensions and check if a pyshaders extension is supported.
    - Use GL types instead of c types.
    - Lowered fixtures shader GLSL versions from 330 core to 130. They should be at 120, but doing so would make me feel dirty.
- ##### Extensions  
    - Added **uint_uniforms**. Add unsigned integers (single value and vector) uniforms support to pyshaders (requires opengl 3.0 & GLSL 1.30)
    - Added **double_uniforms**. Add double uniforms (single value, vector and matrices) support to pyshaders (requires opengl 3.2 & GLSL 1.50)