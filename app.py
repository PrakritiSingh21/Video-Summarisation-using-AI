from flask import Flask, request, redirect, url_for, render_template, send_file
import os
from werkzeug.utils import secure_filename
from models import basic

UPLOAD_FOLDER = 'static/video/input/'

app = Flask(_name_)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50*1024*1024  # upload limit 50MB
app.config['TEMPLATES_AUTO_RELOAD'] = True



"""
    HELPERS
"""
def makedirs():
    root_path = os.path.abspath(os.path.dirname(_file_))
    static_dir = os.path.join(root_path, 'static')
    os.mkdir(os.path.join(static_dir, 'video'))
    video_dir = os.path.join(static_dir, 'video')
    folders = ['output', 'input']
    for folder in folders:
        os.mkdir(os.path.join(video_dir, folder))


"""
    ROUTES
"""
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                return redirect(request.url)
            filename = secure_filename(file.filename)

            # create video, input & output folder in static dir
            if not os.path.exists(UPLOAD_FOLDER):
                makedirs()
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # run the summarizer & get fps
            fps = basic.main(os.path.join(
                    app.config['UPLOAD_FOLDER'], filename))

            return redirect(url_for('processed', filename=filename, fps=fps))
    return render_template('index.html')


@app.route('/out')
def processed():
    filename = "video.mp4"
    fps = 30.011125336362067
    metrics = basic.graph("static/video/output/output.mp4",os.path.join(app.config['UPLOAD_FOLDER'], filename), fps)
    print(filename)
    return render_template('output.html', metrics=metrics)


@app.route('/download')
def download():
    return send_file('static/video/output/output.mp4', as_attachment=True, 
                                attachment_filename='processed-video.mp4', cache_timeout=0)



if _name_ == '_main_':
    app.run(host='0.0.0.0',debug=True)