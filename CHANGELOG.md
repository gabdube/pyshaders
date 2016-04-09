# Changelog

- [1.1.0](#oneonezero)

<a name="oneonezero"/>
### Pyshaders 1.1.0

- ##### Main module
    - Added **load_extension**, **extension_loaded** and **check_extension** to load pyshaders extensions and check if a pyshaders extension is supported.
    - Use GL types instead of c types.
    - Lowered fixtures shader GLSL versions from 330 core to 130. They should be at 120, but doing so would make me feel dirty.
- ##### Extensions
    - Added **uint_uniforms**. Add unsigned integers (single value and vector) uniforms support to pyshaders (requires opengl 3.0 & GLSL 1.30)
    - Added **double_uniforms**. Add double uniforms (single value, vector and matrices) support to pyshaders (requires opengl 3.2 & GLSL 1.50)