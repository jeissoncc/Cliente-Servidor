import zmq
import sys
import os
import json
# -*- coding: utf-8 -*-

def writeFile(filename, bytes):
    with open(filename, "wb") as f:
        #Read the whole file at once
        f.write(bytes)

def readFile(filename):
	with open(filename, "rb") as f:
		data = f.read()
		return data

def send(socket, str):
	socket.send(str.encode("utf-8"))


def recv(socket):
	str = socket.recv(socket)
	return str.decode("utf-8")

context = zmq.Context()
print("Connecting to fileserver... \n\n")
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")




######################################################################################

def upload():
	name = input("Ingrese el nombre del archivo con su extension: ")
	byte = readFile("archivos/"+name)
	send(socket, "1")# send 1
	msg = socket.recv() # recv 1
	socket.send_multipart([name.encode('utf-8'), byte])# send 2 
	serv = socket.recv() # recv 2
	mensaje = str(serv)
	print (mensaje + " uploaded successfully" + '\n\n')
	

#######################################################################################

def listar():
	send(socket, "3")# send 1
	message = socket.recv().decode('utf-8')# recv 1
	send(socket, '')
	listado = socket.recv().decode('utf-8')
	print("archivos: ",listado + "\n\n")
	
######################################################################################

def download():
	name = input("Ingrese el nombre del archivo con su extension: ")
	send(socket, "2")# send 1 
	msg = socket.recv() # recv 1
	send(socket, name) # send 2
	nom, size = socket.recv_multipart() # recv 2 
	nm = str(nom.decode('utf-8'))
	writeFile("archivos/" + nm,size)
	print(nm + " uploaded successfully" +"\n\n")
	
######################################################################################


while True:

	print("      MENU     \n")
	print("1. Cargar archivo")
	print("2. Descargar archivo")
	print("3. Listar archivos")
	opcion=input("Ingrese la opcion requerida: ")
	if (opcion == "1"):
		upload()
		 
	elif(opcion == "2"):

		download()
	elif(opcion == "3"):
		
		listar()

	else:
		print("Opcion incorrecta, digitela nuevamente. \n\n")
		os.system('cls')

