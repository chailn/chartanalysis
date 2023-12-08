from flask import Flask, render_template, request, send_file
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import io
import base64
import os

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xlsx'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_plot(data):
    points = data[['RR', 'BB', 'LL', 'WEIGHT']].values

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    ax.scatter(points[:, 0], points[:, 1], points[:, 2], c=points[:, 3], cmap='viridis', s=100)
    plt.colorbar(ax.scatter(points[:, 0], points[:, 1], points[:, 2], c=points[:, 3], cmap='viridis', s=100), label='WEIGHT')
    ax.set_xlabel('RR')
    ax.set_ylabel('BB')
    ax.set_zlabel('LL')
    plt.title('WEIGHT')

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plot_url = base64.b64encode(buf.read()).decode('utf-8')

    return plot_url

def filter_data(data, selection):
    # 根据用户选择的值过滤数据
    selected_value = int(selection)
    filtered_data = {
        'RR': data['RR'][:selected_value],
        'BB': data['BB'][:selected_value],
        'LL': data['LL'][:selected_value],
        'WEIGHT': data['WEIGHT'][:selected_value]
    }
    return pd.DataFrame(filtered_data)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('index.html', error='No file part')
        
        file = request.files['file']
        if file.filename == '':
            return render_template('index.html', error='No selected file')

        if file and allowed_file(file.filename):
            filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filename)

            data = pd.read_excel(filename)
            
            if 'selection' in request.form:
                selection = request.form['selection']
                data = filter_data(data, selection)
                plot_url = create_plot(data)
                return render_template('index.html', plot_url=plot_url)

            plot_url = create_plot(data)
            return render_template('index.html', plot_url=plot_url)

    return render_template('index.html')

@app.route('/download_example', methods=['GET'])
def download_example():
    example_data = {
        'RR': [1, 1, 3, 4],
        'BB': [1, 6, 7, 8],
        'LL': [1, 10, 11, 12],
        'WEIGHT': [1, 14, 15, 16]
    }

    df = pd.DataFrame(example_data)
    filename = 'example_data.xlsx'
    df.to_excel(os.path.join(app.config['UPLOAD_FOLDER'], filename), index=False)

    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
