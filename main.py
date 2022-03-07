from flask import Flask, send_file
import os
from flask import Flask, render_template, request, jsonify, flash, redirect, session, copy_current_request_context
from flask_socketio import SocketIO, emit
from werkzeug.utils import secure_filename
import activator
import asyncio
import time
import glob
import upload
import get
import requests
import random
from flask_socketio import SocketIO, emit, disconnect
from random import randint
from threading import Thread, Lock
import os
import sys
import paramiko
import subprocess
import shutil
import time
import credential

#from activator import bwmMain
#from activator import checkFile
from multiprocessing import Process
from celery import Celery


app = Flask(__name__)

app.secret_key = "G8zFnUoKEQ"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # upload limit of 16mb
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESUKTS_BACKEND'] = 'redis://localhost:6379/0'

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)




# Get current path
path = os.getcwd()
# file Upload
UPLOAD_FOLDER = os.path.join(path, 'uploads')  # make upload folder path
STL_FOLDER = os.path.join(path, "stl")

# Make directory if uploads is not exists
if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)
if not os.path.isdir(STL_FOLDER):
    os.mkdir(STL_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['STL_FOLDER'] = STL_FOLDER

# Allowed extension you can set your own
ALLOWED_EXTENSIONS = set(['txt'])
async_mode = "threading"

socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()


@socketio.event
def my_event(message):
    filename = message.get('data')
    file = open(".//logs//"+str(filename)+"_Live.txt", "r")
    count = 0
    while True:
        where = file.tell()
        line = file.readline()
        if not line:
            time.sleep(0.1)
            file.seek(where)
            print(line)
        socketio.sleep(0.1)
        count += 1
        if line == "" or line == " ":
            print(line)
        else:
            session['receive_count'] = session.get('receive_count', 0) + 1
            emit('my_response', {'data': line, 'count': session['receive_count']})
            if "File complete" in line:
                return
@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected', request.sid)

@socketio.event
def connect():
    global thread
    with thread_lock:
        if thread is None:
            print("")



@socketio.event
def disconnect_request():
    @copy_current_request_context
    def can_disconnect():
        disconnect()

    session['receive_count'] = session.get('receive_count', 0) + 1
    # for this emit we use a callback function
    # when the callback function is invoked we know that the message has been
    # received and it is safe to disconnect
    emit('my_response',
         {'data': 'Disconnected!', 'count': session['receive_count']},
         callback=can_disconnect)



def current_milli_time():
    randomSalt = str(round(time.time() * 1000)) + str(randint(1000, 9999))
    return randomSalt


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS




@celery.task
def bwmMain(name, hormone, population, generation, stimuli, genome, test):
    print("")
    hostname = '20.90.100.113'
    myuser = 'biohaviour_cyclecloud'
    mySSHK = '/home/biohaviour_webserver/id_rsa.pub'
    sshcon = paramiko.SSHClient()  # will create the object
    sshcon.set_missing_host_key_policy(
        paramiko.AutoAddPolicy())  # no known_hosts error
    sshcon.connect(hostname, username=myuser,
                   key_filename=mySSHK)  # no passwd needed
    if test == "lightweight":
        path = r'cd /shared/home/biohaviour_cyclecloud/workload/Biohaviour-Nursery-SingleVM && ~/anaconda3/envs/MVP-Enviroment/bin/python3 -u BwmMain.py'
    else:
        path = r'cd /shared/home/biohaviour_cyclecloud/workload/Biohaviour-Nursery\ Release/Emerginarium\ V2/Biohaviour-Nursery/ && ~/anaconda3/envs/MVP-Enviroment/bin/python3 -u BwmMain.py'
      # path = r'cd /shared/home/biohaviour_cyclecloud/workload/ && sbatch run_MVP2Backup.sh'
    if hormone == '':
        if test == "lightweight":
            command = path + " -cli -n " + name + " -s " + stimuli + " -g " + \
                genome + " -pop " + population + " -gen " + generation
        else:
            command = path + " -cli -n " + name + " -s" + stimuli + " -g " + genome + \
                " -pop " + population + " -gen " + generation + " -tasksize large"
    else:
        if test == "lightweight":
            command = path + " -cli -n " + name + " -s " + stimuli + " -g " + genome + \
                " -pop " + population + " -gen " + generation + " -H " + hormone
        else:
            command = path + " -cli -n " + name + " -s" + stimuli + " -g " + genome + " -pop " + \
                population + " -gen " + generation + " -H " + hormone + " -tasksize large"
    print("The command is: " + command)

    stdin, stdout, stderr = sshcon.exec_command(command)
    #print(stderr.readlines())
    f = open(".//logs//"+name+".txt", "w", buffering=1)
    file = open(".//logs//"+name+"_Live.txt", "w", buffering=1)
    time.sleep(0.1)
    trunCount = 0
    while True:
        line = stdout.readline()
        f.write(line)
        file.write(line)
        trunCount += 1
        time.sleep(0.1)
        if not line:
            break
        print(line, end="")
        if trunCount > 20:
            file.truncate(0)
            trunCount = 0
    while True:
        line = stderr.readline()
        f.write(line)
        file.write(line)
        time.sleep(0.1)
        if not line:
            break
        print(line, end="")
    print("Done")
    sshcon.close
    sshcon = paramiko.SSHClient()  # will create the object
    sshcon.set_missing_host_key_policy(
        paramiko.AutoAddPolicy())  # no known_hosts error
    sshcon.connect(hostname, username=myuser,
                   key_filename=mySSHK)  # no passwd needed
    if test == "lightweight":
        path = r'cd /shared/home/biohaviour_cyclecloud/scripts && ~/anaconda3/envs/webServer/bin/python3 -u upload1.py ' + name
    else:
        path = r'cd /shared/home/biohaviour_cyclecloud/scripts && ~/anaconda3/envs/webServer/bin/python3 -u uploadAdvance.py ' + name
    print(path)
    stdin, stdout, stderr = sshcon.exec_command(path)
    print(stderr.readlines())
    print(stdout.readlines())
    while True:
        line = stdout.readline()
        if not line:
            break
        print(line, end="")
    print("Done")
    time.sleep(0.1)
    f.write("File complete")
    file.write("File complete")
    f.close()
    file.close()
    sshcon.close



@app.route("/job/<name>", methods=['GET','POST'])
def job(name):
    data = {'name': name}
    my_code = ""
    my_code += "<a href=""logs/""" + name + ""+ " target=""_blank""> download log</a>"
    return render_template("loading.html", data=data, async_mode=socketio.async_mode, text = my_code)


@app.route('/<job>/<logs>/<name>', methods=['GET', 'POST'])
def downLogLink(job,logs,name):
    return send_file("./logs/" + name + ".txt", as_attachment=True)



def redirectUser(name):
    print("redirectUser method - " + name)
    return redirect('/stls/' + name)


@app.route('/stls/<stlname>')
def test(stlname):
    txtfiles = []
    formatedTxtFiles = []
    ECFile = []
    print("stlname before any processing" + stlname)
    path = ".//stl//"
    path1 = "./static/stl/"

    my_code = ""
    print("Another print statemnet")
    name = ""
    for file in glob.glob(path1 + "*.stl", recursive=True):
        name = file[13:len(file)]
        name2 = file[30:len(file)]
        txtfiles.append(name)
        formatedTxtFiles.append(name2)
        


    ECPath =  "./static/output/" 
    ECPathLength = len(ECPath)   
    for file in glob.glob(ECPath + "*.xlsx", recursive=True):
        filename = file[ECPathLength:len(file)]
        if stlname in filename:
            ECFile.append(filename)

    for file in glob.glob(ECPath + "*.csv", recursive=True):
        filename = file[ECPathLength:len(file)]
        if stlname in filename:
            ECFile.append(filename)


    for x in ECFile:
        print ("ECFile: " + x , flush=True)

    print ("The file name is :" + name + "The Stl name is : " + stlname + "ECFile(0): " + ECFile[0])
    count = 0
    for x in range(len(txtfiles)):
        if stlname in txtfiles[x]:
            if (count == 0):
                my_code = "<div class = " + stlname + ">"
                my_code += "<form method = ""post>"
                count = count + 1
            name = txtfiles[25:len(stlname)]
            my_code += "<input type = ""button"" value=" + txtfiles[x] + " onclick = changeSTL(this.value);>"


    for x in ECFile:
        my_code += "<input type = ""button"" value=" + x + " onclick = changeDownload(this.value);>"



    if (my_code is ""):
        my_code = "<p>Sorry, your files aren't ready yet!"
        return render_template('downloads.html',text=my_code)
    my_code += "</div>"
    return render_template('downloads.html', text=my_code)


@app.route('/stls/<stlname>', methods=['POST'])
def testDown(stlname):
    if request.method == 'POST':
            print("STLNAME: " + stlname)
            name = stlname[0:17]
            print("NAME: " + name)
            choice = request.form.get('download')
            print("CHOICE: " + choice)
            return redirect('/download1/' + choice)
       # return redirect('/')

@app.route('/')
def webAppPage():
    stimulis = []
    genome = []
    stimPath = ".//files//StimulusLibrary//"
    genomePath = ".//files//GenomeLibrary//"
    stim = ""
    gen = ""
    for file in glob.glob(stimPath + "*.txt", recursive=True):
        name = file[26:len(file)]
        stimulis.append(name)
    for file in glob.glob(genomePath + "*.txt", recursive=True):
        name = file[24:len(file)]
        genome.append(name)
    for x in range(len(stimulis)):
        stim += "<option value = "+stimulis[x]+">" + stimulis[x] + "</option>"
    for x in range(len(genome)):
        gen += "<option value = "+genome[x]+">" + genome[x] + "</option>"
    return render_template('app.html', stim=stim, gen=gen)


def rng():
    num = randint(1, 6)
    num2 = randint(1, 3)
    num3 = num + num2
    return num3


@app.route('/', methods=['POST'])
def webApp():
    a = []
    output = ""
    if request.method == 'POST':
        button = request.files.getlist('yesno')
        files = request.files.getlist('files[]')
        if request.files['files[]'].filename == '':
            name = current_milli_time() + "_" + request.form.get('name')
            hormone = request.form.get('hormone')
            population = request.form.get('population')
            generation = request.form.get('generation')
            stim = request.form.get('stimuli')
            gen = request.form.get('genome')
            test = request.form.get('test')
            stimuli_path = "/shared/home/biohaviour_cyclecloud/workload/scripts/uploads/"+stim
            genome_path = "/shared/home/biohaviour_cyclecloud/workload/scripts/uploads/"+gen
            MVPstim = ".//files//StimulusLibrary//"+stim
            MVPgen = ".//files//GenomeLibrary//"+gen
            print("stimLib: " + stimuli_path)
            print ("genLib: " + genome_path)
            print("name " + name)
            print("hormone " + hormone)
            print("generation " + generation)
            print("population " + population)

            a.append(MVPstim)
            a.append(MVPgen)
            print("a: " + a[0] + " b: " + a[1])
            upload.uploadFile(a[0])
            upload.uploadFile(a[1])
            num = rng()
            print(num)
            f = open(".//logs//"+name+".txt", "w", buffering=1)
            file = open(".//logs//"+name+"_Live.txt", "w", buffering=1)
            task = bwmMain.delay(name, hormone, population,
                              generation, stimuli_path, genome_path, test)
            
            #time.sleep(1.5)
            return redirect('/job/'+name)

        name = current_milli_time() + "_" + request.form.get('name')
        hormone = request.form.get('hormone')
        population = request.form.get('population')
        generation = request.form.get('generation')
        test = request.form.get('test')
        print(test)

        for file in files:
            valid = False
            if file and allowed_file(file.filename):
                filename = name + "_" + secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                a.append(filename)
                valid = True
            if valid == False:
                flash(
                    file.filename + ' Error! File not supported. Please make sure the file is .txt')
                return redirect('/')
    stimuli_path = "/shared/home/biohaviour_cyclecloud/workload/scripts/uploads/" + a[0]
    genome_path = "/shared/home/biohaviour_cyclecloud/workload/scripts/uploads/" + a[1]
    upload.uploadFile(a[0])
    upload.uploadFile(a[1])
    print("SP: " + stimuli_path + "\nGP: " + genome_path)
    print("name: " + name + "\nhormone: " + hormone +
          "\npopulation: " + population + "\ngeneration: " + generation)
    num = rng()
    print(num)
    f = open(".//logs//"+name+".txt", "w", buffering=1)
    file = open(".//logs//"+name+"_Live.txt", "w", buffering=1)
    task = bwmMain.delay(name, hormone, population, generation,
                      stimuli_path, genome_path, test)
    #time.sleep(1.5)
    return redirect('/job/' + name)


@app.route('/downloadLog/<name>')
def downloadLog(name):
    path = "./logs/" + name + ".txt"
    
    return send_file(path, as_attachment=True)

@app.route('/download/<name>')
def downloadFile(name):
    path = "./static/output/" + name 
    return send_file(path, as_attachment=True)

@app.route('/download1/<name>')
def downloadFile1(name):
    print("Download1 Name: " + name, flush=True)
    if ".xlsx" in name:
        print("Excel File!")
        path = "./static/output/" + name
        return send_file(path, as_attachment=True)
    elif ".csv" in name:
        path = "./static/output/" + name
        return send_file(path, as_attachment=True)   
    else:    
        path = "./static/stl/" + name 
        return send_file(path, as_attachment=True)



if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0")

