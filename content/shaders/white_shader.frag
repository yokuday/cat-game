#version 330
in vec2 fragTexCoord;
in vec4 fragColor;
uniform sampler2D texture0;
uniform float whiteness; // Add this uniform
out vec4 finalColor;

void main()
{
    vec4 texelColor = texture(texture0, fragTexCoord);
    vec3 originalColor = texelColor.rgb;
    vec3 whiteColor = vec3(1.0, 1.0, 1.0);

    // Mix between original color and white based on whiteness value
    vec3 finalRGB = mix(originalColor, whiteColor, whiteness);

    finalColor = vec4(finalRGB, texelColor.a * fragColor.a);
}