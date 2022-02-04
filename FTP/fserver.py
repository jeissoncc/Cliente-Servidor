import zmq
import os
import json
import time
from os.path import isfile, join

def send(socket, str):
	socket.send(str.encode("utf-8"))


def recv(socket):
	str = socket.recv()
	return str.decode("utf-8")

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")


def writeFile(filename, bytes):
    with open(filename, "wb") as f:
        #Read the whole file at once
        f.write(bytes)

def readFile(filename):
    with open(filename, "rb") as f:
        data = f.read()
        return data

#####################################################################

def upload():
	 name, size = socket.recv_multipart() # recv 2 
	 nm = str(name.decode('utf-8'))
	 writeFile("archivos/"+nm, size)
	 socket.send(nm.encode('utf-8')) # send 2
	 print("carga finalizada")

#####################################################################
	
def download():
	lista = os.listdir("archivos/")
	files = [file for file in lista]
	nm = recv(socket)
	if nm in files:
		byte = readFile("archivos/"+nm)
		socket.send_multipart([nm.encode('utf-8'), byte]) #send 2
	else:
		msg = "no existe este archivo"
		socket.send_multipart([msg.encode('utf-8'), b""]) #send 2

#####################################################################

def listar():
	ruta_app = os.chdir("archivos/" ) # obtiene ruta del script 
	contenido = os.listdir(ruta_app)  # obtiene lista con archivos/dir 
	jsonlist = json.dumps(contenido)
	msg = recv(socket)
	send(socket, jsonlist)

#####################################################################
	

	

while True:
	
	print("FileServer online...")
	opcion = recv(socket) # recv 1
	send(socket,'') # send 1
	if (opcion == "1"):
		print ("Opcion de carga de archivo recibida")
		upload()
		time.sleep(1.5)
		

	elif (opcion == "2"):
		print ("Opcion de descarga de archivo recibida")
		download()
		time.sleep(1.5)

	elif (opcion == "3"):
		print ("Opcion de listar archivos recibida")
		listar()
		time.sleep(1.5)
	else:
		print ("Opcion incorrecta")