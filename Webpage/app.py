from flask import Flask, render_template, request
import pandas as pd
from Detector import detect
import multiprocessing 

process = multiprocessing.Process(target=detect) 

app = Flask(__name__)

i = 0
df = pd.read_csv('./Database.csv')
name = ''
roll = ''
def add_in_df(name, rollno):
    df.loc[len(df)] = [name, rollno] 
    df.to_csv('./Database.csv',index=False)

@app.route('/')
def index():
    global i, name , roll
    if(len(df) != 0):
        name = df['Full Name'][0]
        roll = df['Roll Number'][0]
    return render_template('home.html', name = name, roll = roll)

@app.route('/add')
def add():
    global i, name , roll
    add_in_df(request.args.get('first'),request.args.get('last'))
    return render_template('home.html', name = name, roll = roll )

@app.route('/next')
def next():
    global i, name , roll
    if(i==0 and len(df) == 1):
        name = df['Full Name'][0]
        roll = df['Roll Number'][0]
    if i + 1 != len(df) and i != len(df):
        i = i + 1
        name = df['Full Name'][i]
        roll = df['Roll Number'][i]
    return render_template('home.html', name = name, roll = roll)

@app.route('/prev')
def prev():
    global i, name , roll
    if(i==0 and len(df) == 1):
        name = df['Full Name'][0]
        roll = df['Roll Number'][0]
    if i - 1 != -1:
        i = i - 1
        name = df['Full Name'][i]
        roll = df['Roll Number'][i]
    return render_template('home.html', name = name, roll = roll)

@app.route('/detect_on')
def detect_on(): 
    global i, name , roll
    #####
    ##### execute detect()
    #####
    process.start()
    return render_template('home.html', name = name, roll = roll)

@app.route('/detect_off')
def detect_off():
    global i, name , roll
    #####
    ##### stop detect()
    #####
    process.terminate()
    process.exitcode
    return render_template('home.html', name = name, roll = roll)

@app.errorhandler(404)
def page(e):
    return render_template('error.html'), 404

if __name__ == '__main__':
    app.run(debug = True)