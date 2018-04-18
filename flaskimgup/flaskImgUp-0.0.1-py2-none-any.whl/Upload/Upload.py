import os
from flask import redirect, flash
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = "content/images"
ALLOWED_EXTENSIONS = ("png", "jpg", "jpeg", "gif")

def accept_filetype(filename):
    filetype = filename.rsplit('.', 1)[1].lower()
    return '.' in filename and filetype in ALLOWED_EXTENSIONS

def upload(request):

    if request.method == "POST":
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == "":
            flash("No file selected")
            return redirect(request.url)
        if file and accept_filetype(file.filename):
            filename = secure_filename(file.filename)
            end = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), UPLOAD_FOLDER, filename)
            if not os.path.exists(os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), UPLOAD_FOLDER)):
                os.makedirs(os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), UPLOAD_FOLDER))
            file.save(end)
            return "OK"
    return '''
        <!doctype HTML>
        <title> Upload new File</title>
        <h1>Upload new File</h1>
        <form method = POST enctype = multipart/form-data>
        <p><input type = file name = file>
        <input type = submit value = Upload>
        </form>'''