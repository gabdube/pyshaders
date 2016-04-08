#version 130

out vec4 color_frag;

// Belongs to frag_lib.glsl.frag
vec4 secret_method();

void main()
{
  vec4 color = secret_method();
  color_frag = color;
}