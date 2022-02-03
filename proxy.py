import sys
import zmq
import os
import argparse
import json

BUF_SIZE = 1024 * 1024 * 10

def distributor(index, hashf,filename,dic,servers,nservers):
	duplicate = query(index, hashf)
	if duplicate == True:
		answer = "file is already stored"
		socket.send_multipart([hashf.encode('utf-8'), answer.encode('utf-8')])
	else:
		file = open('temptablehashproxy.json','wb')
		file.write(dic)
		file.close()
		i = 0
		with open('temptablehashproxy.json') as file:
			temphash = json.load(file)
		file.close()
		index[hashf]={}
		for key in temphash:
			index[hashf][key] = "tcp://"+servers[i][0]
			i = i+1
			if i > nservers:
				i = 0
			servers[i][1] = int(servers[i][1])-1
		with open('temptablehashproxy.json', 'w') as file:
			json.dump(index[hashf], file)
		file.close()
		file = open('temptablehashproxy.json', 'rb')
		part = file.read(BUF_SIZE)
		msg = ([hashf.encode('utf-8'), bytes(part)])
		socket.send_multipart(msg)
		file.close()

def search(index, hashf):
	tmpdic = index[hashf]
	with open('temptablehashclient.json', 'w') as file:
		json.dump(tmpdic,file, indent=4)
	file.close()
	file = open('temptablehashclient.json', 'rb')
	part = file.read(BUF_SIZE)
	socket.send(bytes(part))
	file.close()
	os.remove('temptablehashclient.json')
	
	
def query(index, hashf):
	if hashf in index:
		return True
	else:
		return False

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('proxyport')
	args = parser.parse_args()

	context = zmq.Context()
	socket = context.socket(zmq.REP)
	socket.bind("tcp://*:"+args.proxyport)
	print("Proxy ready... listening port "+args.proxyport)

	nservers =-1
	servers = []
	index = {}

while True:
	print( "|      servers       | capacity  |")
	print(servers)
	print("servers online: "+str(nservers+1))
	for key in index:
		print(key)

	msg = socket.recv_multipart()
	if msg[0].decode('utf-8') == '1':
		print("distributor")
		distributor(index, msg[1].decode('utf-8'), msg[2].decode('utf-8'), msg[3], servers, nservers)
	if msg[0].decode('utf-8') == '2':
		print("searching: "+msg[1].decode('utf-8'))
		search(index, msg[1].decode('utf-8'))
	if msg[0].decode('utf-8') == '3':
		print("adding server")
		servers.append([msg[2].decode('utf-8'), msg[1].decode('utf-8')])
		nservers = nservers + 1
		socket.send_string("server added successfully")


