# shaders.py

import numpy as np

VERTEX_SHADER = """#version 410 core
layout (location = 0) in vec3 aPos;
uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
out float lightIntensity;

void main() {
    gl_Position = projection * view * model * vec4(aPos, 1.0);
    vec3 normal = normalize(aPos);
    vec3 lightDir = normalize(vec3(1.0, 1.0, 1.0));
    lightIntensity = max(dot(normal, lightDir), 0.5;) // 0.2 is ambient light
}
"""

FRAGMENT_SHADER = """#version 410 core
in float lightIntensity;
out vec4 FragColor;
uniform vec4 objectColor;

void main() {
    // Increase the power to make the 'center-facing' spot tighter and brighter
    float glow = pow(lightIntensity, 2.0);
    FragColor = vec4(objectColor.rgb, objectColor.a);
}
"""





VERTEX_SHADER = """
#version 410 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec3 inColour; // Incoming color for now. Will calculate light intensity with more variables later.

out vec3 vertColour;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main() {
    gl_Position = projection * view * model * vec4(aPos, 1.0);
    vertColour = inColour;
}
"""

# Change gl_Position: projection * view * model * vec4(aPos, 1.0);

FRAGMENT_SHADER = """
#version 410 core
precision highp float;
in vec3 vertColour;
out vec4 fragColour;
uniform vec4 objectColor;

void main() {
    fragColour = vec4(vertColour, 1.0);
}
"""
