from flask import Flask, request,jsonify,send_from_directory
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = "upload"

@app.route("/file_rec", methods=["POST"])
def file_receive():
    file = request.files.get("filename")
    filename = file.filename.replace(" ", "")
    print("上传文件的名称为[%s]\n" % filename)
    file.save('upload/' + filename)
    return jsonify({
    'code': 200,
    'messsge': "文件上传成功",
    'fileName': filename,
    'url': 'http://xxxx.cn/upload/' + filename
    })

@app.route('/get_files')
def get_files():
    files = []
    for filename in os.listdir('upload'):
        if not os.path.isdir(filename):
            files.append({'name': filename})
    print("files:", files)
    return jsonify({'files': files})


@app.route('/download', methods=['GET'])
def download_file():
    filename = request.args.get('filename')
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)


if __name__ == "__main__":
    app.run(port=80,debug = False)