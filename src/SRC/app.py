from flask import Flask, render_template, send_file, abort, jsonify, url_for, request, session, redirect
import os
import shutil
import re
import sys
import random
import numpy
from itertools import repeat
import ast

def getRandom(dirs):
    global imageWindow

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

path = re.sub(f"{os.sep}SRC{os.sep}app.py", "", __file__)

def directoryMapper(x, img_path = path):
    return f"{img_path}{os.sep}{x}"

def allDirectories(dir = [], img_path = path):
    global path

    # These have to be in here, but feel free to add some more
    remove_dirs = ['favourites', 'trash', 'SRC'];

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

app = Flask(__name__)
# For dev purposes, this isn't randomized (this isn't my personal one either)
app.secret_key = 'this-is-totally-a-random-key'

directories = allDirectories()

@app.route("/")
def index():
    selected_dirs = session.get('selected_directories', directories)
    timer = session.get('timer', 2500)
    favourite = session.get('favourite', 0)

    img = re.sub(f"src{os.sep}", "", os.path.relpath(getRandom(selected_dirs)))
    image_name = re.sub(f"..{os.sep}..{os.sep}", "", img)
    return render_template('index.html', image=img, timer=timer, image_name=image_name)

@app.route("/image/<path:filename>")
def serve_image(filename):
    file_path = os.path.join(path, filename)
    if os.path.isfile(file_path):
        return send_file(file_path)
    else:
        abort(404)

@app.route("/random-image-url")
def random_image_url():
    selected_dirs = session.get('selected_directories', directories)
    timer = session.get('timer', 2500)
    favourite = session.get('favourite', 0)
    
    img = re.sub(f"src{os.sep}", "", os.path.relpath(getRandom(selected_dirs)))
    url = url_for('serve_image', filename=img)
    return jsonify({"url": url, "filename": re.sub("/image/", "", url)})

@app.route("/trash-image", methods=['GET', 'POST'])
def trash_image():
    img = request.get_json()
    rel_img_path = os.sep.join(img.get('img').split(os.sep)[-2:]).split("?")[0]
    img_folder = rel_img_path.split(os.sep)[0]
    
    trash_path = f"{path}{os.sep}trash{os.sep}"

    if not os.path.exists(f"{trash_path}{img_folder}"):
        os.makedirs(f"{trash_path}{img_folder}")
    
    shutil.move(directoryMapper(rel_img_path), f"{trash_path}{rel_img_path}")

    return ''

@app.route("/directories", methods=['GET', 'POST'])
def change_directory():
    favourite = session.get('favourite', 0)

    dirs = allDirectories([], f"{path}{os.sep}favourites" if favourite else path)

    if request.args:
        dir_list = request.args.getlist('dir_list')
        dir_list = [ast.literal_eval(item) for item in dir_list]
    else:
        dir_list = [(dir, f"♡{os.sep}{dir.split(os.sep)[-1]}" if favourite else dir.split(os.sep)[-1]) for dir in dirs]

    if request.method == 'POST':
        timer = int(request.form.get('timer'))
        session['timer'] = timer
        selected_dirs = request.form.getlist('directories')
        session['selected_directories'] = selected_dirs
        favourite = int(request.form.get('favourite'))
        session['favourite'] = favourite
        if selected_dirs:
            img = re.sub(f"src{os.sep}", "", os.path.relpath(getRandom(selected_dirs)))
            image_name = re.sub(f"..{os.sep}..{os.sep}", "", img)
            return render_template('index.html', image=img, timer=timer, image_name=image_name)
        else:
            return render_template('directories.html', directories=dir_list, selected=selected_dirs, timer=timer, favourite=favourite, error=True)
    
    selected_dirs = session.get('selected_directories', directories)
    timer = session.get('timer', 2500)
    return render_template('directories.html', directories=dir_list, selected=selected_dirs, timer=timer, favourite=favourite)

@app.route("/is-liked-img", methods=['GET', 'POST'])
def is_liked():
    img = request.get_json()
    rel_img_path = os.sep.join(img.get('img').split(os.sep)[-2:]).split("?")[0]
    img_folder = rel_img_path.split(os.sep)[0]

    favourites_path = f"{path}{os.sep}favourites{os.sep}"

    if not os.path.exists(f"{favourites_path}{img_folder}"):
        os.makedirs(f"{favourites_path}{img_folder}")

    liked = os.path.exists(f"{favourites_path}{rel_img_path}")

    return jsonify({"liked": liked})

@app.route("/like-img", methods=['GET', 'POST'])
def like_img():
    img = request.get_json()
    rel_img_path = os.sep.join(img.get('img').split(os.sep)[-2:]).split("?")[0]
    img_folder = rel_img_path.split(os.sep)[0]

    favourites_path = f"{path}{os.sep}favourites{os.sep}"

    if not os.path.exists(f"{favourites_path}{img_folder}"):
        os.makedirs(f"{favourites_path}{img_folder}")

    if img.get('liked'):
        os.symlink(directoryMapper(rel_img_path), os.path.relpath(f"{favourites_path}{rel_img_path}"))
    else:
        os.remove(f"{favourites_path}{rel_img_path}")

    return ''

@app.route('/get-favourites', methods=['GET', 'POST'])
def get_favourites():
    favourite = int(request.form.get('favourite'))
    
    if favourite:
        favourite_dirs = allDirectories([], f"{path}{os.sep}favourites")
    else:
        favourite_dirs = allDirectories([])

    dir_list = [(dir, f"♡{os.sep}{dir.split(os.sep)[-1]}" if favourite else dir.split(os.sep)[-1]) for dir in favourite_dirs]
    
    timer = int(request.form.get('timer'))
    session['timer'] = timer
    selected_dirs = request.form.getlist('directories')
    session['selected_directories'] = selected_dirs
    session['favourite'] = favourite
    return redirect(url_for('change_directory', dir_list=dir_list))
    

# By default, start it on localhost:5000, but feel free to change it
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001, debug=True)


