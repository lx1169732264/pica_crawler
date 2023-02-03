import os

path = './comics/'
dirs = os.listdir(path)
for i in range(len(dirs)):
    d = dirs[i]
    files = os.listdir(path + d)
    files.sort(key=lambda x: str(x.split('.')[0]).zfill(4))
    prefix = path + d + '/'
    for j in range(len(files) - 1, -1, -1):
        os.rename(prefix + files[j], prefix + str(j + 1).zfill(4) + '.jpg')
    print(d + ':finished------------------------------------')
