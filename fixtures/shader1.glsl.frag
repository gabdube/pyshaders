#version 330 core

out vec4 color_frag;

// Simple value
uniform float test_float = 1.0;
uniform vec2 test_vec2 = vec2(2.0, 3.0);
uniform vec3 test_vec3 = vec3(4.0, 5.0, 6.0);
uniform vec4 test_vec4 = vec4(7.0, 8.0, 9.0, 10.0);

uniform int test_int = 1;
uniform ivec2 test_ivec2 = ivec2(2, 3);
uniform ivec3 test_ivec3 = ivec3(4, 5, 6);
uniform ivec4 test_ivec4 = ivec4(7, 8, 9, 10);

// Simple array
uniform float[4] test_array_float = float[4](11.0, 12.0, 13.0, 14.0);
uniform vec3[2] test_array_vec3 = vec3[2](vec3(9.0, 10.0, 12.0), vec3(8.0, 20.0, 15.0));
uniform float[1] test_array_float2 = float[1](5.0);

// Matrix
uniform mat2 test_mat2 = mat2(1); 
uniform mat3 test_mat3 = mat3(1); 
uniform mat4 test_mat4 = mat4(1); 

uniform mat2x3 test_mat2x3 = mat2x3(1,1,1, 1,1,1); 
uniform mat2x4 test_mat2x4 = mat2x4(1,1,1,1, 1,1,1,1); 

uniform mat3x2 test_mat3x2 = mat3x2(1,1, 1,1, 1,1); 
uniform mat3x4 test_mat3x4 = mat3x4(1,1,1,1, 1,1,1,1, 1,1,1,1); 

uniform mat4x2 test_mat4x2 = mat4x2(1,1, 1,1, 1,1, 1,1); 
uniform mat4x3 test_mat4x3 = mat4x3(1,1,1, 1,1,1, 1,1,1, 1,1,1);

// Array of matrices
uniform mat2[3] test_array_mat2 = mat2[](mat2(1), mat2(1), mat2(1));


void main()
{
  vec2 a = test_vec2 * (test_float+test_ivec2[0]+test_ivec4[1]+test_mat3[2][2]);
  vec3 b = test_vec3 * (test_float+test_ivec3[0]+test_int+test_mat2[1][1]+test_mat4[3][3]);
  vec2 d = vec2(test_mat2x3[0][0]+test_mat3x2[0][0], test_mat2x4[0][0]+test_mat3x4[0][0]);
  vec2 e = vec2(test_mat4x2[0][0], test_mat4x3[0][0]+test_array_float2[0]+test_array_mat2[2][0][0]);
  vec4 c = vec4(test_vec4[0]+e[0]+e[1], a[0]+d[1]+d[0], b[0]+test_array_vec3[1][2], test_array_float[3]);
  color_frag = c;
}