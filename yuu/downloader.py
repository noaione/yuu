import tempfile
from tqdm import tqdm
import requests
import os

from binascii import unhexlify
from Crypto.Cipher import AES
from .parser import fetchVideoKey, getAuthToken, parsem3u8

def decryptData(tsdata, key, iv):
	def _decrypt(d, k, iv):
		dec = AES.new(k, AES.MODE_CBC, IV=iv)
		return dec.decrypt(d)
	
	if iv.startswith('0x'):
		iv = iv[2:]
	iv = unhexlify(iv)
	
	return _decrypt(tsdata, key, iv)
	
def getVideo(fileslist, key, iv, session):
	tempdir = tempfile.mkdtemp()
	dledfiles = []
	
	with tqdm(total=len(fileslist), desc='Downloading', ascii=True, unit='file') as pbar:
		for tsf in fileslist:
			outputtemp = os.path.basename(tsf)
			if outputtemp.find('?tver') != -1:
				outputtemp = outputtemp[:outputtemp.find('?tver')]
			outputtemp = tempdir + '\\' + outputtemp
			with open(outputtemp, 'wb') as outf:
				try:
					req = session.get(tsf)
					outf.write(decryptData(req.content, key, iv))
				except Exception as err:
					print('[ERROR] Problem occured\nreason: {}'.format(err))
					import sys; sys.exit(1)
			pbar.update()
			dledfiles.append(outputtemp)
	return [dledfiles, tempdir]
	
def mergeVideo(inp, out):
	with open(out, 'wb') as outf:
		with tqdm(total=len(inp), desc='Merging', ascii=True, unit='file') as pbar:
			for i in inp:
				with open(i, 'rb') as c:
					outf.write(c.read())
				os.remove(i)
				pbar.update()