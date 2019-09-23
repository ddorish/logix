import os

COMMENT = '###'

def read_config(files_names=None):
    if files_names is None:
        files_names = ['config.conf', 'secrets.conf']
    res = {}
    lineof = {}
    fileof = {}

    for fn in files_names:
        try:
            fh = open(fn)
        except OSError:
            print("Config file %s not found" % fn)
            return res

        for lnum, line_raw in enumerate(fh.readlines()):
            line = line_raw.split(COMMENT)[0].strip()
            if line == '':
                continue
            if not ' ' in line:
                print("    %s:%d: No space delimiter" % (fn, lnum))
                continue
            data = line.split(' ')
            name = data[0]
            value = ' '.join(data[1:])
            if name in res:
                print("%d: Key %s already defined at %s:%d as %s" % (lnum, name, fileof[name], lineof[name], res[name]))
            res[name] = value.strip()
            lineof[name] = lnum
            fileof[name] = fn
        # Replace special $VAR: device:
        for replace_from, read_key in {'$DEVICE': 'device'}.items():
            replace_to = res.get(read_key, replace_from)
            for k, v in res.items():
                if replace_from in v:
                    res[k] = v.replace(replace_from, replace_to)
    return res

