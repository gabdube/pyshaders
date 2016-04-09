#version 150
#extension GL_ARB_gpu_shader_fp64 : require

out vec4 color_frag;

uniform double test_double = 0.0; 
uniform dvec2 test_dvec2 = dvec2(0, 0); 
uniform dvec3 test_dvec3 = dvec3(0, 0, 0); 
uniform dvec4 test_dvec4 = dvec4(0, 0, 0, 0); 

uniform double[3] test_double_3 = double[](0, 0, 0);
uniform dvec2[2] test_dvec2_2 = dvec2[](uvec2(0,0), uvec2(1,1));

uniform dmat2 test_dmat2 = dmat2(1.0);
uniform dmat3 test_dmat3 = dmat3(1.0);
uniform dmat4 test_dmat4 = dmat4(1.0);

uniform dmat2x3 test_dmat2_3 = dmat2x3(1.0);
uniform dmat2x4 test_dmat2_4 = dmat2x4(1.0);

uniform dmat3x2 test_dmat3_2 = dmat3x2(1.0);
uniform dmat3x4 test_dmat3_4 = dmat3x4(1.0);

uniform dmat4x2 test_dmat4_2 = dmat4x2(1.0);
uniform dmat4x3 test_dmat4_3 = dmat4x3(1.0);

uniform dmat2[2] test_dmat2_2 = dmat2[](dmat2(1), dmat2(1));

void main()
{
  double x = test_double + test_dvec2[0] + test_dvec2[1];
  dvec4 y = dvec4(test_dvec2[0], test_dvec2[1], 0, 0);
  double z = test_dvec4[3] + test_dvec3[2] + test_double_3[2];

  z += test_dmat2[0][0]+test_dmat2[1][1]+test_dmat3[1][1]+test_dmat4[2][2];
  x += test_dmat2_3[0][1]+test_dmat2_4[0][1]+test_dmat3_2[1][1];
  x += test_dmat3_4[0][1]+test_dmat4_2[0][1]+test_dmat4_3[0][1];
  x += test_dmat2_2[0][1][1] + test_dmat2_2[1][1][0];
color_frag = vec4(x, y[1], z, test_dvec2_2[1][1]);
}