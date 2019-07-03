import os
import tempfile

from binascii import unhexlify
from Crypto.Cipher import AES
from tqdm import tqdm

def decrypt_data(tsdata, key, iv):
    def _decrypt(d, k, iv):
        dec = AES.new(k, AES.MODE_CBC, IV=iv)
        return dec.decrypt(d)

    if iv.startswith('0x'):
        iv = iv[2:]
    iv = unhexlify(iv)

    return _decrypt(tsdata, key, iv)


def get_video(fileslist, key, iv, session, verbose):
    print('[INFO][DOWN] Creating temporary folder')
    tempdir = tempfile.mkdtemp()
    dledfiles = []

    if not verbose:
        with tqdm(total=len(fileslist), desc='Downloading', ascii=True, unit='file') as pbar:
            for tsf in fileslist:
                outputtemp = os.path.basename(tsf)
                if outputtemp.find('?tver') != -1:
                    outputtemp = outputtemp[:outputtemp.find('?tver')]
                outputtemp = tempdir + '\\' + outputtemp
                with open(outputtemp, 'wb') as outf:
                    try:
                        req = session.get(tsf)
                        outf.write(decrypt_data(req.content, key, iv))
                    except Exception as err:
                        print('[ERROR] Problem occured\nreason: {}'.format(err))
                        exit(1)
                pbar.update()
                dledfiles.append(outputtemp)
    elif verbose:
        for tsf in fileslist:
            outputtemp = os.path.basename(tsf)
            if outputtemp.find('?tver') != -1:
                outputtemp = outputtemp[:outputtemp.find('?tver')]
            otpt = outputtemp
            outputtemp = os.path.join(tempdir, outputtemp)
            with open(outputtemp, 'wb') as outf:
                try:
                    print('[DEBUG][DOWN] Requesting & decrypting content for: {}'.format(otpt))
                    req = session.get(tsf)
                    outf.write(decrypt_data(req.content, key, iv))
                except Exception as err:
                    print('[ERROR] Problem occured\nreason: {}'.format(err))
                    exit(1)
            dledfiles.append(outputtemp)

    return [dledfiles, tempdir]


def merge_video(inp, out):
    with open(out, 'wb') as outf:
        with tqdm(total=len(inp), desc='Merging', ascii=True, unit='file') as pbar:
            for i in inp:
                with open(i, 'rb') as c:
                    outf.write(c.read())
                os.remove(i)
                pbar.update()
