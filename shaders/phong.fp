#version 330 core

uniform vec3 objColor;
uniform vec3 camPos;
uniform vec3 luzSwitch;
uniform float numero_luzes;
uniform vec3 l[10];

in vec3 Normal;
in vec3 FragPos;

out vec4 FragColor; 

void main()
{
    vec3 norm = normalize(Normal);
    vec3 viewDir = normalize(camPos - FragPos);
    vec3 lightColor = vec3(1, 1, 1);

    //AMBIENTE
    vec3 ambient = lightColor;
    vec3 diffuse = vec3(0, 0, 0);
    vec3 specular = vec3(0, 0, 0);
    vec3 lightDir;
    vec3 vetorLuz;

    for(int i = 0; i < numero_luzes; i++){
        vetorLuz = l[i] - FragPos;
        float luzDis = sqrt(pow(vetorLuz[0], 2) + pow(vetorLuz[1], 2) + pow(vetorLuz[2], 2));
        vec3 lightColorAtenuada = lightColor / (1 + luzDis + 0.25f * pow(luzDis, 2));
        //DIFUSA    
        vec3 lightDir = normalize(l[i] - FragPos);  
        float diff = max(dot(norm, lightDir), 0.0);
        diffuse = diffuse + diff * lightColorAtenuada;

        //SPECULAR
        vec3 reflectDir = reflect(-lightDir, norm);  
        float spec = pow(max(dot(viewDir, reflectDir), 0.0), 32);
        specular = specular + spec * lightColorAtenuada;
    }
    
    //RESULTAD
    vec3 result = (ambient * luzSwitch[0] + diffuse * luzSwitch[1] + specular * luzSwitch[2]) * objColor;
    FragColor = vec4(result, 1.0);
}