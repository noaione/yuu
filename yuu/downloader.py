import tempfile
import tqdm
import requests
import os

from binascii import unhexlify
from Crypto.Cipher import AES
from .parser import fetchVideoKey, getAuthToken, parsem3u8
from .common import yuuError

def decryptData(tsdata, key, iv):
	def _decrypt(d, k, iv):
		dec = AES.new(k, AES.MODE_CBC, IV=iv)
		return dec.decrypt(d)
	
	if iv.startswith('0x'):
		iv = iv[2:]
	iv = unhexlify(iv)
	
	return _decrypt(tsdata, key, iv)
	
def getVideo(fileslist, iv, ticket, proxy=None):
	tempdir = tempfile.mkdtemp()
	authToken = getAuthToken()
	auth = {'Authorization': authToken[0]}
	key = fetchVideoKey(ticket, authToken)
	if proxy:
		proxies = {'http': proxy, 'https': proxy}
	dledfiles = []
	
	with tqdm(total=len(fileslist), desc='Downloading', ascii=True, unit='Files') as pbar:
		for tsf in fileslist:
			outputtemp = os.path.basename(tsf)
			if outputtemp.find('?tver') != -1:
				outputtemp = outputtemp[:outputtemp.find('?tver')]
			outputtemp = tempdir + '\\' + outputtemp
			with open(outputtemp, 'wb') as outf:
				try:
					if proxy:
						req = requests.get(tsf, headers=auth, proxies=proxies)
						outf.write(req.content, key, iv)
					else:
						req = requests.get(tsf, headers=auth)
						outf.write(req.content, key, iv)
				except Exception as err:
					raise yuuError('Something wrong occured\nReason: {}'.format(err))
			pbar.update()
			dledfiles.append(outputtemp)
	return [dledfiles, tempdir]
	
def mergeVideo(inp, out):
	out = out + '.ts'
	with open(out, 'wb') as outf:
		with tqdm(total=len(inp), desc='Merging', ascii=True, unit='Files') as pbar:
			for i in inp:
				c = open(i, 'rb').read()
				outf.write(c)
				c.close()
				os.remove(i)