import zmq
import sys
import hashlib
import argparse
import os

BUF_SIZE = 1024 * 1024 * 10
BUF_HASH = 65536

def calcularhash(nombrearchivo):
	sha1 = hashlib.sha1()
	with open(nombrearchivo, 'rb') as f:
		while True:
			data = f.read(BUF_HASH)
			if not data:
				break
			sha1.update(data)
	return sha1

def receive(dictionary, hashf, filename, part, npart):
	file = open('data/'+hashf,'wb') 
	file.write(part)
	file.close()
	socketlisten.send_string(npart) 
	print('part of client = '+npart)
	dictionary[hashf]=filename
	print('stored on servers'+'\n')
	return dictionary

def send(dictionary, hashf, npart):
	filename=dictionary[hashf]
	file = open('data/'+hashf, 'rb') 
	part = file.read(BUF_SIZE)
	print(filename)
	msg = ([bytes(part),filename.encode('utf-8')])
	socketlisten.send_multipart(msg)
	print('send to client = '+str(npart))
	file.close()

if __name__=='__main__':

	dictionary={}
	option='3'
	capacity='1000'

	parser = argparse.ArgumentParser()
	parser.add_argument('ipserver')
	parser.add_argument('serverport')
	parser.add_argument('proxyport')
	args = parser.parse_args()

	context=zmq.Context()
	socketlisten=context.socket(zmq.REP)
	socketlisten.bind('tcp://*:'+args.serverport)
	socketbalancer=context.socket(zmq.REQ)
	socketbalancer.connect("tcp://"+args.proxyport)

	myipserver=args.ipserver+":"+args.serverport

	msg = ([option.encode('utf-8'),capacity.encode('utf-8'),myipserver.encode('utf-8')])
	socketbalancer.send_multipart(msg)
	msg=socketbalancer.recv_string()
	print(msg)

	print('server listening on the port '+args.serverport+' and proxy '+args.proxyport)

	while True:
		m = socketlisten.recv_multipart()                                                                                                                                    
		if m[0].decode('utf-8')=='1':
			dictionary=receive(dictionary,m[1].decode('utf-8'),m[2].decode('utf-8'),m[3],m[4].decode('utf-8'))
			

		elif m[0].decode('utf-8')=='2':
			send(dictionary,m[1].decode('utf-8'),int(m[2].decode('utf-8')))
			