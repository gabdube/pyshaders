# Changelog

- [1.1.0](#oneonezero)
- [1.2.0](#onetwozero)
- [1.2.0](#onethreezero)

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