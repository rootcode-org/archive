# Copyright is waived. No warranty is provided. Unrestricted use and modification is permitted.

import os
import sys
import math
import zipfile
import tarfile

PURPOSE = """\
List/Compress/Decompress archive file formats

archive.py list <input_path>
archive.py compress [zip|lz4|lzma|tar.gz|tar.bz2|tar.xz] <input_file|input_folder> <output_file>
archive.py decompress <input_file> <output_file|output_folder>
"""


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(PURPOSE)

    command = sys.argv[1]
    if command == 'list':
        input_path = sys.argv[2] if len(sys.argv) > 2 else None
        if input_path and os.path.isfile(input_path):
            ext = os.path.splitext(input_path)[1]
            if ext == '.zip':
                zf = zipfile.ZipFile(input_path, "r")
                for x in zf.infolist():
                    print (x.filename)
            elif ext == '.gz':
                tf = tarfile.open(name=input_path, mode='r:gz')
                tf.list()
                tf.close()
            elif ext == '.bz2':
                tf = tarfile.open(name=input_path, mode='r:bz2')
                tf.list()
                tf.close()
            elif ext == '.xz':
                tf = tarfile.open(name=input_path, mode='r:xz')
                tf.list()
                tf.close()
            else:
                sys.exit('Unable to list this file type')
        else:
            sys.exit('Invalid input path')

    elif command == 'compress':
        if len(sys.argv) < 5:
            sys.exit(PURPOSE)
        format = sys.argv[2]
        input_path = sys.argv[3]
        output_file = sys.argv[4]

        # List input files
        input_files = []
        if os.path.isfile(input_path):
            input_files = [input_path.replace('\\', '/')]
        elif os.path.isdir(input_path):
            for root, dirs, files in os.walk(input_path):
                input_files.extend([os.path.join(root, f).replace('\\', '/') for f in files])
        else:
            sys.exit('Invalid input path')

        # Calculate relative path for files in zip and tar archives
        root_folder_name = os.path.basename(input_path)
        root_index = len(input_path) - len(root_folder_name)

        # Compress files
        if format == 'zip':
            zf = zipfile.ZipFile(output_file, mode="w", compression=zipfile.ZIP_DEFLATED, compresslevel=9, allowZip64=True)
            for f in input_files:
                zf.write(f, arcname=f[root_index:])
            zf.close()

        elif format == 'lz4':
            try:
                from lz4 import block
            except ImportError:
                sys.exit('Requires lz4 module; try "pip install lz4"')
            if len(input_files) > 1:
                sys.exit('LZ4 supports single file compression only')
            with open(output_file, "wb") as w:
                with open(input_files[0], "rb") as r:
                    compressed_data = block.compress(r.read(), mode="high_compression", compression=12)
                    w.write(compressed_data)

        elif format == 'lzma':
            try:
                import pylzma
            except ImportError:
                sys.exit('Requires pylzma module; try "pip install pylzma"')
            if len(input_files) > 1:
                sys.exit('LZMA supports single file compression only')
            with open(output_file, "wb") as w:
                with open(input_files[0], "rb") as r:
                    data = r.read()
                    dictionary_size = int(math.log(len(data), 2)) + 1
                    compressed_data = pylzma.compress(data, dictionary=dictionary_size, eos=1)
                    w.write(compressed_data)

        elif format == 'tar.gz':
            tf = tarfile.open(name=output_file, mode="w:gz")
            for f in input_files:
                tf.add(f, arcname=f[root_index:])
            tf.close()

        elif format == 'tar.bz2':
            tf = tarfile.open(name=output_file, mode="w:bz2")
            for f in input_files:
                tf.add(f, arcname=f[root_index:])
            tf.close()

        elif format == 'tar.xz':
            tf = tarfile.open(name=output_file, mode="w:xz")
            for f in input_files:
                tf.add(f, arcname=f[root_index:])
            tf.close()

        else:
            sys.exit('Invalid format')

    elif command == 'decompress':
        input_file = sys.argv[2] if len(sys.argv) > 2 else None
        if not (input_file and os.path.isfile(input_file)):
            sys.exit('Must specify input file')
        output_path = sys.argv[3] if len(sys.argv) > 3 else None
        if not output_path:
            sys.exit('Must specify output path')
        ext = os.path.splitext(input_file)[1]

        if ext == '.zip':
            zf = zipfile.ZipFile(input_file, "r")
            zf.extractall(output_path)
            zf.close()

        elif ext == '.lz4':
            try:
                from lz4 import block
            except ImportError:
                sys.exit('Requires lz4 module; try "pip install lz4"')
            with open(input_file, "rb") as r:
                with open(output_path, "wb") as w:
                    data = block.decompress(r.read())
                    w.write(data)

        elif ext == '.lzma':
            try:
                import pylzma
            except ImportError:
                sys.exit('Requires pylzma module; try "pip install pylzma"')
            with open(input_file, "rb") as r:
                with open(output_path, "wb") as w:
                    data = pylzma.decompress(r.read())
                    w.write(data)

        elif ext == '.gz':
            tf = tarfile.open(name=input_file, mode='r:gz')
            tf.extractall(path=output_path)
            tf.close()

        elif ext == '.bz2':
            tf = tarfile.open(name=input_file, mode='r:bz2')
            tf.extractall(path=output_path)
            tf.close()

        elif ext == '.xz':
            tf = tarfile.open(name=input_file, mode='r:xz')
            tf.extractall(path=output_path)
            tf.close()

        else:
            sys.exit('Unknown archive type')
