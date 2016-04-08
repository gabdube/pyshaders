#version 130

out vec4 color_frag;

uniform uint test_uint = 0; 
uniform uvec2 test_uvec2 = uvec2(0, 0); 
uniform uvec3 test_uvec3 = uvec3(0, 0, 0); 
uniform uvec4 test_uvec4 = uvec4(0, 0, 0, 0); 

uniform uint[3] test_uint_3 = uint[](0, 0, 0);
uniform uvec2[2] test_uvec2_2 = uvec2[](uvec2(0,0), uvec2(1,1));

void main()
{
  uint x = test_uint + test_uvec2[0] + test_uvec2[1];
  uvec4 y = uvec4(test_uvec2[0], test_uvec2[1], 0, 0);
  uint z = test_uvec4[3] + test_uvec3[2] + test_uint_3[2];
  color_frag = vec4(x, y[1], z, test_uvec2_2[1][1]);
}