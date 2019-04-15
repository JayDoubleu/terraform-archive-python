import os
import time
import sys
import json
import zipfile
import hashlib
from base64 import standard_b64encode as b64encode


def base64sha256(zip_path):
    with open(zip_path, 'rb') as zip_file:
        sha256 = hashlib.sha256()
        sha256.update(zip_file.read())
        base64sha256 = b64encode(sha256.digest()).decode('utf-8')
    return base64sha256


def get_all_file_paths(directory):
    file_paths = []
    for root, directories, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            file_paths.append({"filepath": filepath, "filename": filename})
    return file_paths


def main():
    data = json.load(sys.stdin)
    file_paths = get_all_file_paths(data['source_dir'])
    try:
        with zipfile.ZipFile(data['output_path'], mode='w') as zf:
            for file_path in sorted(file_paths, key=lambda d: d['filename']):
                file_bytes = open(file_path['filepath'],
                                  "rb").read().decode().replace('\r\n', '\n')
                file_bytes = file_bytes.encode()
                info = zipfile.ZipInfo(
                    str(file_path['filename']),
                    date_time=(1980, 1, 1, 00, 00, 00),
                )
                info.compress_type = zipfile.ZIP_DEFLATED
                info.create_system = 0
                info.external_attr = 0o777 << 16
                zf.writestr(info, file_bytes)
            zf.close()
    finally:
        zip_data = {
            "output_path":
            str(data['output_path']),
            "output_absolute_path":
            str(os.path.abspath(data['output_path'])),
            "output_size":
            str(os.stat(data['output_path']).st_size),
            "output_md5":
            str(
                hashlib.md5(open(data['output_path'],
                                 'rb').read()).hexdigest()),
            "output_base64sha256":
            str(base64sha256(data['output_path']))
        }
        print(json.dumps(zip_data))


if __name__ == "__main__":
    main()
