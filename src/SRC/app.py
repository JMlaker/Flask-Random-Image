from flask import Flask, render_template, send_file, abort, jsonify, url_for, request, session, redirect
import os
import shutil
import re
import ast
from pathlib import Path

from utils import allDirectories, getRandom, directoryMapper, path, config

app = Flask(__name__)
# For dev purposes, this isn't randomized (this isn't my personal one either)
app.secret_key = 'this-is-totally-a-random-key'

directories = allDirectories()

@app.route("/")
def index():
    selected_dirs = session.get('selected_directories', directories)
    timer = session.get('timer', 2500)

    image = getRandom(selected_dirs)
    print(image)
    img = os.sep.join(image.split(os.sep)[-2:])
    return render_template('index.html', image=img, timer=timer, image_name=img)

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
    
    image = getRandom(selected_dirs)
    img = os.sep.join(image.split(os.sep)[-2:])
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
            return redirect(url_for('index'))
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

    favourites_path = Path(f"{path}{os.sep}favourites{os.sep}")
    fav_folder = Path(f"{favourites_path}{os.sep}{img_folder}")

    if not os.path.exists(fav_folder):
        os.makedirs(fav_folder)

    img_path = Path(directoryMapper(rel_img_path))
    fav_img = Path(f"{favourites_path}{os.sep}{rel_img_path}")

    if img.get('liked'):
        fav_img.symlink_to(os.path.relpath(img_path, start=fav_folder))
    else:
        fav_img.unlink()

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
    app.run(host=config.get("FLASK-RUN", "host", fallback='127.0.0.1'), port=config.get("FLASK-RUN", "port", fallback='5000'), debug=True)


