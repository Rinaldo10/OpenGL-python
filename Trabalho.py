import sys
import numpy as np
import math
import pywavefront
import cmd
import pyrr
import glm


from OpenGL.GL import *
from OpenGL.GL import shaders
from OpenGL.GLU import *
from OpenGL.GLUT import *
from PIL import Image
from PIL import ImageOps


##-------------------------------------------##
##-------------Variaveis globais-------------##
##-------------------------------------------##

vao = None
vbo = None
shaderProgram = None
shaderProgramLuz = None
shaderProgramAxis = None
shaderProgramNone = None
window = 0

#Variaveis de controle
#Objetos
objetos = []
objCurrent = 0
#Luzes
MAX_NUMERO_LUZES = 10
luzes = []
luzCurrent = 0
numeroDeLuzes = 0
ADEIntensity = [.2, .2, .2] #[ambiente, difusa, especular]
#Camera
camPos = np.array([0, 0, 0], dtype='f')
lookAt = np.array([0, 0, -1], dtype='f')
up = np.array([0, 1, 0], dtype='f')
#Configuracoes
checkWire = 0
luzSwitch = 0
axisSwitch = 0
#Shaders
currShader = None
#/Variaveis de controle

##--------------------------------------------##
##-------------/Variaveis globais-------------##
##--------------------------------------------##

##---------------------------------------------##
##-------------Funcoes auxiliares--------------##

def getObjByName(name):
	global objetos

	for i in range(len(objetos)):
		if(objetos[i].name == name):
			return i
	return -1

def translate(id, x, y, z):
	global objetos
	
	matTransl = np.array([
			[1, 0, 0, 0],
			[0, 1, 0, 0],
			[0, 0, 1, 0],
			[x, y, z, 1]], dtype='f')

	objetos[id].model = np.dot(objetos[id].model, matTransl)


def rotate(id, angle, x, y, z):
	global objetos
	
	'''matRX = np.array([
		[1, 0, 0, 0],
		[0, math.cos(angle), -math.sin(angle), 0],
		[0, math.sin(angle), math.cos(angle), 0],
		[0, 0, 0, 1]], dtype='f').T

	matRY= np.array([
		[math.cos(angle), 0, math.sin(angle), 0],
		[0, 1, 0, 0],
		[-math.sin(angle), 0,  math.cos(angle), 0],
		[0, 0, 0, 1]], dtype='f').T
			
	matRZ = np.array([
		[math.cos(angle), -math.sin(angle), 0, 0],
		[math.sin(angle), math.cos(angle), 0, 0],
		[0, 0, 1, 0],
		[0, 0, 0, 1]], dtype='f').T

	if(x):
		objetos[id].model = np.dot(objetos[id].model,(matRX))
	if(y):
		objetos[id].model = np.dot(objetos[id].model, (matRY))
	if(z):
		objetos[id].model = np.dot(objetos[id].model, (matRZ))'''

	objetos[id].model = np.array(glm.rotate(objetos[id].model, angle, glm.vec3(x, y, z)), dtype ='f')
		

def scale(id, x, y, z):
	global objetos
	
	matEsc = np.array([
			[x, 0, 0, 0],
			[0, y, 0, 0],
			[0, 0, z, 0],
			[0, 0, 0, 1]], dtype='f')

	objetos[id].model = np.dot(objetos[id].model, matEsc)

def shear(id, XY, XZ, YX, YZ, ZX, ZY):
	global objetos

	matShear = np.array([
			[1, YX, XZ, 0],
			[XY, 1, YZ, 0],
			[XZ, YZ, 1, 0],
			[0, 0, 0, 1]], dtype='f')

	objetos[id].model = np.dot(objetos[id].model, matShear)

def colorir_obj(id, r, g, b):
	global objetos
	objetos[id].cor = np.array([r, g, b], dtype='f')

def getLuzByName(name):
	global luzes
	for i in range(len(luzes)):
		if(luzes[i].name == name):
			return i
	return -1

def shellCommands():
	ComandosTerminal().cmdloop()
	glutPostRedisplay()

# Comandos para abrir terminal de execucao
def keyPressed(key, x, y):
	#ROTACAO
	if key == b'\x1b':
		glutDestroyWindow(window)
	if key == b'm':
			shellCommands()

##----------------------------------------------##
##-------------/Funcoes auxiliares--------------##
##----------------------------------------------##


##----------------------------------------------##
##--------------------Classes-------------------##
##----------------------------------------------##

class Objeto():
	def __init__(self, name, info, infoTam, cor):
		self.name = name
		self.info = info
		self.infoTam = infoTam
		self.cor = cor
		self.model = np.array([[1,0,0,0], [0,1,0,0], [0,0,1,0], [0,0,0,1]], dtype='f')
		self.rotacao = [0, 0, 0] #[x, y, z]
		self.escala = [1, 1, 1] #[x, y, z]
		self.translacao = [0, 0, 0] #[x, y, z]
		self.shearXY = 0
		self.shearXZ = 0
		self.shearYX = 0
		self.shearYZ = 0
		self.shearZX = 0
		self.shearZY = 0

class Luz():
	def __init__(self, name, pos, cor):
		self.name = name
		self.pos = pos
		self.cor = cor

#Comandos De terminal especificados na descricao do trabalho
class ComandosTerminal(cmd.Cmd):
	def do_add_shape(self, line):
		command = line.split(sep=" ", maxsplit=2)
		add_shape(command[0], command[1])
		glutPostRedisplay()
		return True
	
	def do_remove_shape(self, line):
		global objetos
		global objCurrent

		n = getObjByName(line)
		
		objToRemove = -1
		if line == "" or n == objCurrent:
			print("Removendo objeto corrente. (" + objetos[objCurrent].name + ")")
			objetos.pop(objCurrent)
			if len(objetos) > 0:
				objCurrent = 0
				print("Objeto corrente alterado para: " + objetos[objCurrent].name)
		else:
			if n != -1:
				print("Removendo " + objetos[n].name)
				objToRemove = n
			else:
				print("Nao ha um objeto chamado " + line)
				
		if objToRemove != -1:
			objetos.pop(objToRemove)
		return True

	def do_set_current_obj(self, line):
		global objetos
		global objCurrent
		
		n = getObjByName(line)
		if n != -1:
			objCurrent = n
			print("Objeto corrente alterada para " + objetos[n].name)
			return True
		print("Nao ha um objeto chamado " + line)
		return True

	def do_add_light(self, line):
		command = line.split(sep=" ", maxsplit=4)
		if len(command) == 1:
			add_luz(command[0], [0, 0, 0], [1, 1, 1])
			return True
		if len(command) == 4:
			add_luz(command[0], [command[1], command[2], command[3]], [1, 1, 1])
			return True
		print("Argumentos invalidos")

	def do_remove_light(self, line):
		global luzes
		global luzCurrent

		n = getLuzByName(line)
		
		luzToRemove = -1
		if line == "" or n == luzCurrent:
			print("Removendo luz corrente. (" + luzes[luzCurrent].name + ")")
			luzes.pop(luzCurrent)
			if len(luzes) > 0:
				luzCurrent = 0
				print("Luz corrente alterada para: " + luzes[luzCurrent].name)
		else:
			if n != -1:
				print("Removendo " + luzes[n].name)
				luzToRemove = n
			else:
				print("Nao ha uma luz chamada " + line)
				
		if line != -1:
			luzes.pop(luzToRemove)
		return True


	def do_set_current_luz(self, line):
		global luzes
		global luzCurrent

		n = getLuzByName(line)
		if n != -1:
			luzCurrent = n
			print("Luz corrente alterada para " + luzes[n].name)
			return True
		print("Nao ha uma luz chamada " + line)
		return True


	def do_reflection_on(self, line):
		command = line.split(sep=" ", maxsplit=2)
		if command[0] == "ambient":
			setAmbiente(command[1])
		elif command[0] == "diffuse":
			setDifusa(command[1])
		elif command[0] == "specular":
			setEspecular(command[1])
		return True

	def do_reflection_off(self, line):
		if line == "ambient":
			setAmbiente(0)
		elif line == "diffuse":
			setDifusa(0)
		elif line == "specular":
			setEspecular(0)
		return True

	def do_shading(self, line):
		if line == "phong" or line == "smooth" or line == "flat" or line == "none":
			setShader(line)
			return True
		print("Não ha um shader com nome " + line)

	def do_translate(self, line):
		global objCurrent
		global objetos
		command = line.split(sep=" ", maxsplit=4)
		if len(command) == 4:
			n = getObjByName(command[0])
			print("Transladando " + objetos[n].name + " para X: " + command[1] + ", Y: " + command[2] + ", Z: " + command[3])
			translate(n, command[1], command[2], command[3])
			return True
		elif len(command) == 3:
			print("Transladando objeto corrente (" + objetos[objCurrent].name + ") para X: " + command[0] + ", Y: " + command[1] + ", Z: " + command[2])
			translate(objCurrent, command[0], command[1], command[2])
			return True
		print("Argumentos invalidos")

	def do_scale(self, line):
		global objCurrent
		global objetos
		command = line.split(sep=" ", maxsplit=4)
		if len(command) == 4:
			n = getObjByName(command[0])
			print("Escalando " + objetos[n].name + " em X: " + command[1] + ", Y: " + command[2] + ", Z: " + command[3])
			scale(n, command[1], command[2], command[3])
			return True
		elif len(command) == 3:
			print("Escalando objeto corrente (" + objetos[objCurrent].name + ") em X: " + command[0] + ", Y: " + command[1] + ", Z: " + command[2])
			scale(objCurrent, command[0], command[1], command[2])
			return True
		print("Argumentos invalidos")


	def do_rotate(self, line):
		global objCurrent
		global objetos
		command = line.split(sep=" ", maxsplit=5)
		if len(command) == 5:
			n = getObjByName(command[0])
			print("Rotacionando " + objetos[n].name + " em X: " + command[2] + ", Y: " + command[3] + ", Z: " + command[4])
			rotate(n, float(command[1]), float(command[2]), float(command[3]), float(command[4]))
			return True
		elif len(command) == 4:
			print("Rotacionando objeto corrente (" + objetos[objCurrent].name + ") em X: " + command[1] + ", Y: " + command[1] + ", Z: " + command[2])
			rotate(objCurrent, float(command[0]), float(command[1]), float(command[2]), float(command[3]))
			return True
		print("Argumentos invalidos")

	def do_shear(self, line):
		command = line.split(sep=" ", maxsplit=7)
		print(line)
		if len(command) == 7:
			n = getObjByName(command[0])
			shear(n, command[1], command[2], command[3], command[4], command[5], command[6])
			return True
		elif len(command) == 6:
			shear(objCurrent, command[0], command[1], command[2], command[3], command[4], command[5])
			return True
		print("Argumentos invalidos")

	def do_lookat(self, line):
		global lookAt
		command = line.split(sep=" ", maxsplit=4)
		if len(command) == 3:
			lookAt = np.array([float(command[0]), float(command[1]), float(command[2])], dtype='f')
			return True
		print("Argumentos invalidos")

	def do_cam(self, line):
		global camPos
		command = line.split(sep=" ", maxsplit=4)
		if len(command) == 3:
			camPos = np.array([float(command[0]), float(command[1]), float(command[2])], dtype='f')
			return True
		print("Argumentos invalidos")

	def do_up(self, line):
		global up
		command = line.split(sep=" ", maxsplit=4)
		if len(command) == 3:
			up = np.array([command[0], command[1], command[2]], dtype='f')
			return True
		print("Argumentos invalidos")

	def do_color(self, line):
		global objCurrent
		global objetos
		command = line.split(sep=" ", maxsplit=4)
		if len(command) == 4:
			n = getObjByName(command[0])
			print("Colorindo " + objetos[n].name + " para R: " + command[1] + ", G: " + command[2] + ", B: " + command[3])
			colorir_obj(n, command[1], command[2], command[3])
			return True
		elif len(command) == 3:
			print("Rotacionando objeto corrente (" + objetos[objCurrent].name + ") em R: " + command[0] + ", G: " + command[1] + ", B: " + command[2])
			colorir_obj(objCurrent, command[0], command[1], command[2])
			return True
		print("Argumentos invalidos")

	def do_save(self, line):
		captureScreen(line)
		return True
	
	def do_wire_on(self, line):
		global checkWire
		checkWire = 1
		return True
	
	def do_wire_off(self, line):
		global checkWire
		checkWire = 0
		return True

	def do_lights_on(self, line):
		global luzSwitch
		luzSwitch = 1
		return True

	def do_lights_off(self, line):
		global luzSwitch
		luzSwitch = 0
		return True

	
	def do_axis_on(self, line):
		global axisSwitch
		axisSwitch = 1
		return True

	def do_axis_off(self, line):
		global axisSwitch
		axisSwitch = 0
		return True

	def do_exit(self, line):
		return True
	
	def do_quit(self, line):
		glutDestroyWindow(window)
		return True

	

##------------------------------/comandosTerminal()----------------------------##
##-----------------------------------------------------------------------##
		


##--------------------------------------------##
##------------------/Classes------------------##
##--------------------------------------------##

##--------------------------------------------##
##-------------Toggle iluminacao--------------##

def setAmbiente(a):
	global ADEIntensity
	ADEIntensity[0] = float(a)

def setDifusa(d):
	global ADEIntensity
	ADEIntensity[1] = float(d)

def setEspecular(e):
	global ADEIntensity
	ADEIntensity[2] = float(e)

##-------------/Toggle iluminacao--------------##
##---------------------------------------------##

def setShader(s):
	global currShader
	print("Setando shader para " + s)
	if s == "phong":
		currShader = shaderProgram
	elif s == "smooth":
		currShader = shaderProgramsmooth
	elif s == "flat":
		currShader = shaderProgramFlat
	elif s == "none":
		currShader = shaderProgramNone
	getLocsShader()


def getLocsShader():
	global rotate_loc
	global objCor_loc
	global luzSwitch_loc
	global luz_loc
	global luzesCount_loc
	global view_loc	
	global camPos_loc
	global matrixOrtho
	glUseProgram(currShader)

	# Guardando a localizacao dos Uniforms do shader atual (currShader)
	# Objetos
	rotate_loc = glGetUniformLocation(currShader, "model")
	objCor_loc = glGetUniformLocation(currShader, "objColor")
	# luzes
	luzSwitch_loc = glGetUniformLocation(currShader, "luzSwitch")
	luz_loc = glGetUniformLocation(currShader, "l")
	luzesCount_loc = glGetUniformLocation(currShader, "numero_luzes")
	# camera
	view_loc = glGetUniformLocation(currShader, "view")
	camPos_loc = glGetUniformLocation(currShader, "camPos")
	# Set Projection
	matrixOrtho = pyrr.matrix44.create_orthogonal_projection(-2.0, 2.0, -2.0, 2.0, -2.0, 2.0, dtype='f')
	proj_loc = glGetUniformLocation(currShader, "proj")
	glUniformMatrix4fv(proj_loc, 1, GL_FALSE, matrixOrtho)

#Le os shaders
def readShaderFile(filename):
	with open('shaders/' + filename, 'r') as myfile:
		return myfile.read()

#Tira print
def captureScreen(file_):
	glPixelStorei(GL_PACK_ALIGNMENT, 1)
	data = glReadPixels(0, 0, 640, 640, GL_RGBA, GL_UNSIGNED_BYTE)
	image = Image.frombytes("RGBA", (640, 640), data)
	image = ImageOps.flip(image)
	image.save(file_, 'png')
	
def add_shape(shape_type, shape_name):
	novoObjeto = pywavefront.Wavefront(shape_type + '.obj', collect_faces=True)
	novoObjeto.parse()
	novoObjInfo = np.array(novoObjeto.mesh_list[0].materials[0].vertices, dtype='f')
	tamInfoObj = len(novoObjInfo)
	cor = np.array([0.8, 0.8, 0.8], dtype='f')
	objetos.append(Objeto(shape_name, novoObjInfo, tamInfoObj, cor))
	print("Forma: " + shape_type + " adicionada com sucesso.(Nome: " + shape_name + ")")

def add_luz(name, pos, cor):
	global luzes
	global numeroDeLuzes
	global MAX_NUMERO_LUZES

	if numeroDeLuzes <= MAX_NUMERO_LUZES:
		print("Adicionando nova luz (" + name + ")")
		novaLuz = Luz(name, np.array(pos, dtype='f'), np.array(cor, dtype='f'))
		luzes.append(novaLuz)
		numeroDeLuzes = numeroDeLuzes + 1
		return
	print("AVISO: Não foi possivel adicionar luz (Numero maximo atingido: " + MAX_NUMERO_LUZES + ")")
	
			
		
def init():
	global shaderProgram
	global shaderProgramLuz
	global shaderProgramAxis
	global shaderProgramsmooth
	global shaderProgramFlat
	global shaderProgramNone
	global vao
	global currShader
	
	glClearColor(0, 0, 0, 0)

	#enable depth test
	glEnable(GL_DEPTH_TEST)
	#Accept fragment if it closer to the camera than the former one
	glDepthFunc(GL_LESS)
	
	#Compilar Shaders
	vertex_code = readShaderFile('phong.vp')
	fragment_code = readShaderFile('phong.fp')
	vertexShader = shaders.compileShader(vertex_code, GL_VERTEX_SHADER)
	fragmentShader = shaders.compileShader(fragment_code, GL_FRAGMENT_SHADER)
	shaderProgram = shaders.compileProgram(vertexShader, fragmentShader)

	vertex_code_smooth = readShaderFile('smooth.vp')
	fragment_code_smooth = readShaderFile('smooth.fp')
	vertexShader_smooth = shaders.compileShader(vertex_code_smooth, GL_VERTEX_SHADER)
	fragmentShader_smooth = shaders.compileShader(fragment_code_smooth, GL_FRAGMENT_SHADER)
	shaderProgramsmooth = shaders.compileProgram(vertexShader_smooth, fragmentShader_smooth)

	vertex_code_flat = readShaderFile('flat.vp')
	fragment_code_flat = readShaderFile('flat.fp')
	vertexShader_flat = shaders.compileShader(vertex_code_flat, GL_VERTEX_SHADER)
	fragmentShader_flat = shaders.compileShader(fragment_code_flat, GL_FRAGMENT_SHADER)
	shaderProgramFlat = shaders.compileProgram(vertexShader_flat, fragmentShader_flat)

	vertex_code_none = readShaderFile('none.vp')
	fragment_code_none = readShaderFile('none.fp')
	vertexShader_none = shaders.compileShader(vertex_code_none, GL_VERTEX_SHADER)
	fragmentShader_none = shaders.compileShader(fragment_code_none, GL_FRAGMENT_SHADER)
	shaderProgramNone = shaders.compileProgram(vertexShader_none, fragmentShader_none)
	
	vertex_code_luz = readShaderFile('luz.vp')
	fragment_code_luz = readShaderFile('luz.fp')
	vertexShaderLuz = shaders.compileShader(vertex_code_luz, GL_VERTEX_SHADER)
	fragmentShaderLuz = shaders.compileShader(fragment_code_luz, GL_FRAGMENT_SHADER)
	shaderProgramLuz = shaders.compileProgram(vertexShaderLuz, fragmentShaderLuz)

	vertex_code_axis = readShaderFile('axis.vp')
	fragment_code_axis = readShaderFile('axis.fp')
	vertexShaderAxis = shaders.compileShader(vertex_code_axis, GL_VERTEX_SHADER)
	fragmentShaderAxis = shaders.compileShader(fragment_code_axis, GL_FRAGMENT_SHADER)
	shaderProgramAxis = shaders.compileProgram(vertexShaderAxis, fragmentShaderAxis)

	# Create and bind the Vertex Array Object
	vao = GLuint(0)
	glGenVertexArrays(1, vao)
	glBindVertexArray(vao)

	#seleciona o shader padrao
	setShader("none")

##------------------/init()--------------------##
##---------------------------------------------##
	

def display():	
	global vao
	global vbo
	global vbo2
	
	#clear the screen
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
	
	# load everthing back
	glUseProgram(currShader)

	# Cria a matriz de View
	matrixView = []
	matrixView = glm.lookAt(camPos, lookAt, up)
	
	matrixView = np.array(matrixView, dtype='f')
	# Vetor de posicao das luzes (para o objeto luminoso ser desenhado)
	lPositions = []
	for item in luzes:
		lPositions.append(item.pos)
	lPositions = np.array(lPositions, dtype='f')

	#############################################################
	################### Desenhar Objetos ########################

	for objToDraw in range(len(objetos)):
		vbo = glGenBuffers(1)	
		glBindBuffer(GL_ARRAY_BUFFER, vbo) 
		glBufferData(GL_ARRAY_BUFFER, objetos[objToDraw].info, GL_STATIC_DRAW)	

		vbo2 = glGenBuffers(1)			
		glBindBuffer(GL_ARRAY_BUFFER, vbo2) 
		glBufferData(GL_ARRAY_BUFFER, objetos[objToDraw].info, GL_STATIC_DRAW)
				
		
	 	# Passando a matriz de transformacao e cor do objedo a ser desenhado para o vshader
		glUniformMatrix4fv(rotate_loc, 1, GL_FALSE, objetos[objToDraw].model)
		glUniform3fv(objCor_loc, 1, objetos[objToDraw].cor)
		# Passando a cor e posicao da luz (vec3) e o switch de reflexoes para o fshader
		glUniform3fv(luz_loc, 10, lPositions)
		glUniform3fv(luzSwitch_loc, 1, ADEIntensity)
		glUniform1f(luzesCount_loc, numeroDeLuzes)
		# Passando a matriz View
		glUniform3fv(camPos_loc, 1, camPos)
		glUniformMatrix4fv(view_loc, 1, GL_FALSE, matrixView)
				
		glBindVertexArray(vao)	

		glBindBuffer(GL_ARRAY_BUFFER, vbo)
		glVertexAttribPointer(0, 3, GL_FLOAT, False,  sizeof(ctypes.c_float)*8, c_void_p(5*sizeof(ctypes.c_float)))  # first 0 is the location in shader		
		glBindAttribLocation(currShader, 0, 'vertexPosition')  # name of attribute in shader
		
		glBindBuffer(GL_ARRAY_BUFFER, vbo2)
		glVertexAttribPointer(1, 3, GL_FLOAT, False,  sizeof(ctypes.c_float)*8, c_void_p(2*sizeof(ctypes.c_float))) # Second 1 is the location in shader
		glBindAttribLocation(currShader, 1, 'aNormal')  # name of attribute in shader 

		glEnableVertexAttribArray(0)# 0=location do atributo, tem que ativar todos os atributos inicialmente sao desabilitados por padrao
		glEnableVertexAttribArray(1)# 1=location do atributo, tem que ativar todos os atributos inicialmente sao desabilitados por padrao

		#verifica se o modo wire esta ativo
		if checkWire == 0:
			glDrawArrays(GL_TRIANGLES, 0, int(objetos[objToDraw].infoTam*3/8))
		else:
			glDrawArrays(GL_LINE_LOOP, 0, int(objetos[objToDraw].infoTam*3/8))

	################### /Desenhar Objetos ########################
	#############################################################

	#clean things up
	glBindBuffer(GL_ARRAY_BUFFER, 0)
	
	# verifica se as luzes estao visiveis
	if luzSwitch == 1:
		# Modelo corpos de luz
		verticesCubo = np.array([
		[-0.01,-0.01,-0.01],
		[-0.01,-0.01, 0.01],
		[-0.01, 0.01, 0.01],
		[0.01, 0.01, -0.01],
		[-0.01,-0.01,-0.01],
		[-0.01, 0.01,-0.01],

		[0.01, -0.01, 0.01],
		[-0.01,-0.01,-0.01],
		[0.01, -0.01,-0.01],
		[0.01, 0.01, -0.01],
		[0.01,-0.01, -0.01],
		[-0.01,-0.01,-0.01],

		[-0.01,-0.01,-0.01],
		[-0.01, 0.01, 0.01],
		[-0.01, 0.01,-0.01],
		[0.01, -0.01, 0.01],
		[-0.01,-0.01, 0.01],
		[-0.01,-0.01,-0.01],

		[-0.01, 0.01, 0.01],
		[-0.01,-0.01, 0.01],
		[0.01, -0.01, 0.01],
		[0.01, 0.01,  0.01],
		[0.01,-0.01, -0.01],
		[0.01, 0.01, -0.01],

		[0.01,-0.01, -0.01],
		[0.01, 0.01,  0.01],
		[0.01, -0.01, 0.01],
		[0.01,  0.01, 0.01],
		[0.01, 0.01, -0.01],
		[-0.01, 0.01,-0.01],

		[0.01, 0.01,  0.01],
		[-0.01, 0.01,-0.01],
		[-0.01, 0.01, 0.01],
		[0.01, 0.01,  0.01],
		[-0.01, 0.01, 0.01],
		[0.01,-0.01, 0.01]], dtype='f')

		glUseProgram(shaderProgramLuz)
		glBindVertexArray(vao)	
		
		for item in lPositions:
			matTransluz = np.array([
			[1, 0, 0, 0],
			[0, 1, 0, 0],
			[0, 0, 1, 0],
			[item[0], item[1], item[2], 1]], dtype='f')
			modelLuz_loc = glGetUniformLocation(shaderProgramLuz, "modelLuz")
			glUniformMatrix4fv(modelLuz_loc, 1, GL_FALSE, matTransluz)

			viewLuz_loc = glGetUniformLocation(shaderProgramLuz, "viewLuz")
			glUniformMatrix4fv(viewLuz_loc, 1, GL_FALSE, matrixView)

			projLuz_loc = glGetUniformLocation(shaderProgramLuz, "projLuz")
			glUniformMatrix4fv(projLuz_loc, 1, GL_FALSE, matrixOrtho)

			vboLuz = glGenBuffers(1)
			glBindBuffer(GL_ARRAY_BUFFER, vboLuz)
			glBufferData(GL_ARRAY_BUFFER, verticesCubo, GL_STATIC_DRAW)

			glVertexAttribPointer(0, 3, GL_FLOAT, False,  0 , None)  # first 0 is the location in shader		
			glBindAttribLocation(shaderProgramLuz, 0, 'vertexPosition')  # name of attribute in shader

			glEnableVertexAttribArray(0)# 0=location do atributo, tem que ativar todos os atributos inicialmente sao desabilitados por padrao

			glDrawArrays(GL_TRIANGLES, 0, 36)

			glBindBuffer(GL_ARRAY_BUFFER, 0)
			
	#verifica se os eixos estao visiveis
	if axisSwitch == 1:
		glUseProgram(shaderProgramAxis)

		viewAx_loc = glGetUniformLocation(shaderProgramAxis, "viewA")
		glUniformMatrix4fv(viewAx_loc, 1, GL_FALSE, matrixView)

		projAx_loc = glGetUniformLocation(shaderProgramAxis, "projA")
		glUniformMatrix4fv(projAx_loc, 1, GL_FALSE, matrixOrtho)

		for i in range(3):
			
			if i == 0:
				verticesAxis = np.array([[2, 0, 0], [-2, 0, 0]], dtype='f')
				colorAxis = np.array([[1, 0, 0],[1, 0, 0]], dtype='f')
			elif i == 1:
				verticesAxis = np.array([[0, 2, 0], [0, -2, 0]], dtype='f')
				colorAxis = np.array([[0, 1, 0],[0, 1, 0]], dtype='f')
			elif i == 2:
				verticesAxis = np.array([[0, 0, 2], [0, 0, -2]], dtype='f')
				colorAxis = np.array([[0, 0, 1],[0, 0, 1]], dtype='f')

			#posicao
			vboAxis = glGenBuffers(1)
			glBindBuffer(GL_ARRAY_BUFFER, vboAxis) 
			glBufferData(GL_ARRAY_BUFFER, verticesAxis, GL_STATIC_DRAW)	
			glVertexAttribPointer(0, 3, GL_FLOAT, False,  0 , None)  # first 0 is the location in shader		
			glBindAttribLocation(shaderProgramAxis, 0, 'vertexPosition')  # name of attribute in shader
			

			#cor
			vboAxis2 = glGenBuffers(1)
			glBindBuffer(GL_ARRAY_BUFFER, vboAxis2) 
			glBufferData(GL_ARRAY_BUFFER, colorAxis, GL_STATIC_DRAW)			
			glVertexAttribPointer(1, 3, GL_FLOAT, False,  0 , None)  # first 0 is the location in shader		
			glBindAttribLocation(shaderProgramAxis, 1, 'color_in')  # name of attribute in shader
			

			glEnableVertexAttribArray(0)# 0=location do atributo, tem que ativar todos os atributos inicialmente sao desabilitados por padrao
			glEnableVertexAttribArray(1)

			glDrawArrays(GL_LINES, 0, 2)

	glBindBuffer(GL_ARRAY_BUFFER, 0)
	glBindVertexArray(0)
	glUseProgram(0)
	glutSwapBuffers()  # necessario para windows!
	

##----------------/display()-------------------##
##---------------------------------------------##
	

def reshape(width, height):
	glViewport(0, 0, width, height)


if __name__ == "__main__":
	glutInit()
	glutInitContextVersion(3, 0)
	glutInitContextProfile(GLUT_CORE_PROFILE)
	glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)

	glutInitWindowSize(640, 640)
	window = glutCreateWindow(b'Trabalho de Computacao Grafica')

	glutKeyboardFunc(keyPressed)
	glutReshapeFunc(reshape)
	glutDisplayFunc(display)

	init()
	glutMainLoop()

