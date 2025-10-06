import random
import os
import numpy
import re
from itertools import repeat
from configparser import ConfigParser

path = re.sub(f"{os.sep}SRC{os.sep}utils.py", "", __file__)

config = ConfigParser()
if os.path.exists(re.sub(f"src", "app.dev.ini", path)):
    config.read(re.sub(f"src", "app.dev.ini", path))
else:
  config.read(re.sub(f"src", "app.ini", path))

def getRandom(dirs):
    if not dirs:
        dirs = allDirectories([])

    weights = []
    dirSum = 0
    for dir in dirs:
        weights.append(len(next(os.walk(dir))[2]))
        dirSum += len(next(os.walk(dir))[2])
    weights = list(map(lambda x: x / dirSum, weights))

    if 0.0 in weights:
        for i in range(len(weights)):
            if weights[i] == 0.0:
                del weights[i]
                del dirs[i]

    weights = [numpy.log10(x*1/(min(weights)**2)) for x in weights] if len(weights) > 1 else weights
    weights = [x/sum(weights) for x in weights]
    
    randDir = random.choices(dirs, weights=weights, k=1)[0]
    photoArr = next(os.walk(randDir))[2]
    photoArr = [x for x in photoArr if "VID" not in x]
    randImage = random.choice(photoArr)
    imgPath = os.path.join(randDir, randImage)
    return imgPath

def directoryMapper(x, img_path = path):
    return f"{img_path}{os.sep}{x}"

def allDirectories(dir = [], img_path = path):
    global path

    # These have to be in here, but feel free to add some more
    remove_dirs = ['favourites', 'trash', 'SRC'];
    
    for i in [item.strip() for item in config.get("EXCLUDED-DIRS", "list", fallback=[]).split(", ")]:
        remove_dirs.append(i)

    for x in next(os.walk(img_path))[1]:
        dir.append(x)

    for x in remove_dirs:
        try:
            dir.remove(x)
        except:
            pass

    dir = list(map(directoryMapper, dir, repeat(img_path)))

    t = []
    for i in dir:
        if len(os.listdir(i)) > 0:
            t.append(i)

    return t