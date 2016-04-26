#version 130

in vec3 position;
in vec4 color;
in float secret_value;

out vec4 frag_color;

void main() {
    frag_color = color*secret_value;
    gl_Position = vec4(position, 1.0);
}