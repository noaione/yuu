import os
import tempfile

from binascii import unhexlify
from Crypto.Cipher import AES
from tqdm import tqdm


def decrypt_ts(data, key, iv):
    def _decryptor(d, k, i):
        return AES.new(k, AES.MODE_CBC, IV=iv).decrypt(d)

    if iv.startswith('0x'):
        iv = iv[2:]
    iv = unhexlify(iv)

    return _decryptor(data, key, iv)


def download_chunk(files, key, iv, sesi):
    print('[INFO][DOWN] Creating temporary folder')
    if os.name == "nt":
        yuu_folder = os.path.join(os.getenv('LOCALAPPDATA'), 'yuu_data')
    else:
        yuu_folder = os.path.join('~', '.yuu_data')
    if not os.path.isdir(yuu_folder):
        os.mkdir(yuu_folder)
    
    temp_dir = tempfile.mkdtemp(dir=yuu_folder)
    dled_files = []

    try:
        with tqdm(total=len(files), desc='Downloading', ascii=True, unit='file') as pbar:
            for tsf in files:
                outputtemp = temp_dir + '\\' + os.path.basename(tsf)
                with open(outputtemp, 'wb') as outf:
                    try:
                        vid = sesi.get(tsf)
                        if key and iv: # Decrypt if there's key and IV provided
                            vid = decrypt_ts(vid.content, key, iv)
                        outf.write(vid)
                    except Exception as err:
                        print('[ERROR] Problem occured\nreason: {}'.format(err))
                        return None, temp_dir
                pbar.update()
                dled_files.append(outputtemp)
    except KeyboardInterrupt:
        print('[WARN] User pressed CTRL+C, cleaning up...')
        return None, temp_dir

    return dled_files, temp_dir


def merge_video(path, output):
    with open(output, 'wb') as out:
        with tqdm(total=len(path), desc="Merging", ascii=True, unit="file") as pbar:
            for i in path:
                out.write(open(i, 'rb').read())
                os.remove(i)
                pbar.update()

