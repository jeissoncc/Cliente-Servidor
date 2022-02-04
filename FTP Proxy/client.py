import zmq
import sys
import hashlib
import argparse
import os
import json

BUF_SIZE = 1024 * 1024 * 10
BUF_HASH = 65536

def hashfile(filename):
	sha1 = hashlib.sha1()
	with open(filename, 'rb') as f:
		while True:
			data = f.read(BUF_HASH)
			if not data:
				break
			sha1.update(data)
	return sha1

def hashpart(part):
	sha1 = hashlib.sha1()
	sha1.update(part)
	return sha1

def proxy(filename):
	tmpdic = {}
	option = '1'
	sha1 = hashlib.sha1()
	tmphashfile=str(hashfile(filename).hexdigest())
	file = open(filename, 'rb')
	part = file.read(BUF_SIZE)
	sizepart = sys.getsizeof(part)
	while True:
		if sizepart < BUF_SIZE:
			break
		tmphashpart = str(hashpart(part).hexdigest())
		tmpdic[tmphashpart]='None'
		part = file.read(BUF_SIZE)
		sizepart = sys.getsizeof(part)
	file.close()
	with open('data/clienthashtable.json', 'w') as file:
		json.dump(tmpdic, file, indent=4)
	file.close()
	file = open('data/clienthashtable.json', 'rb') 
	part = file.read(BUF_SIZE)
	file.close()
	s = context.socket(zmq.REQ)
	s.connect("tcp://"+args.port)
	msg = ([option.encode('utf-8'), tmphashfile.encode('utf-8'),filename.encode('utf-8'), bytes(part)])
	s.send_multipart(msg)
	msg = s.recv_multipart()
	s.close()
	if msg[1].decode('utf-8') == 'file already exists':
		print(msg[1].decode('utf-8'))
		return True
	else:
		file = open('data/clienthashtable.json', 'wb')
		file.write(msg[1])
		file.close()
		os.rename('data/clienthashtable.json', tmphashfile+filename)
		return False

def send(filename):
	option = '1'
	sha1 = hashlib.sha1()
	tmphashfile = str(hashfile(filename).hexdigest())
	i = 0
	repeat = proxy(filename)
	if repeat == False:
		with open(tmphashfile+filename) as file:
			tmphashtable = json.load(file)
		file.close()
		file = open(filename, 'rb')
		part = file.read(BUF_SIZE)
		for key in tmphashtable:
			s = context.socket(zmq.REQ)
			s.connect(tmphashtable[key])
			print(tmphashtable[key])
			msg = [option.encode('utf-8'),key.encode('utf-8'),filename.encode('utf-8'),bytes(part),str(i).encode('utf-8')]
			s.send_multipart(msg)
			msg=s.recv_string()
			part = file.read(BUF_SIZE)
			print('part '+msg+' send to the server '+tmphashtable[key])
			i = i + 1
			s.close()
		file.close()
		print("file sent correctly"+'\n')
		print("to download the file "+filename+" use the hash: "+tmphashfile)

def receive(filename):
	option = '2'
	s = context.socket(zmq.REQ)
	s.connect("tcp://"+args.port)
	msg = ([option.encode('utf-8'),filename.encode('utf-8')])
	s.send_multipart(msg)
	msg = s.recv()
	s.close()
	if msg.decode('utf-8')=='0':
		print("hash not found")
	else:
		file = open('serverhashparts.json', 'wb') 
		file.write(msg)
		file.close()
		i=0 
		with open('serverhashparts.json') as file:
			tmphashtable = json.load(file)
			file.close()
		file = open('desc-'+filename, 'wb')
		for key in tmphashtable:
			s = context.socket(zmq.REQ)
			s.connect(tmphashtable[key])
			msg = ([option.encode('utf-8'),key.encode('utf-8'),str(i).encode('utf-8')])
			s.send_multipart(msg) 
			msg = s.recv_multipart()
			file.write(msg[0])
			print('part '+str(i)+' received from the server '+tmphashtable[key])
			i=i+1
			s.close()
		file.close()
		os.rename('desc-'+filename,'download-'+msg[1].decode('utf-8'))
		print('\n'+'successfully downloaded')

def hashsearch(option, hash):
	msg = ([option.encode('utf-8'),hash.encode('utf-8')])
	s.send_multipart(msg)
	msg=s.recv()

if __name__=='__main__':
		parser = argparse.ArgumentParser()
		parser.add_argument('port')
		args = parser.parse_args()
		context=zmq.Context()

		while True:
			print("Client of Proxy Server\n")
			print('\n1 - Upload \n2 - Download \noption = ')
			option=input()
			if (option == '1'):
				print('Enter filename = ')
				filename=input()
				print(filename)
				if os.path.isfile(filename):
					send(filename)
				else:
					print(filename+' does not correspond to a file in the directory')
			
			elif(option == '2'):
				print('hash to Download: ')
				filename = input()
				receive(filename)





