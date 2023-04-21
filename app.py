import whisper

from flask import Flask, render_template, request,jsonify,url_for, session,redirect,flash, send_file

import torch

import sqlite3

import os

from apscheduler.schedulers.background import BackgroundScheduler

from datetime import timedelta

import zipfile

import time

import datetime

import io

import shutil

import threading

from datetime import datetime

from email.mime.multipart import MIMEMultipart

from email.mime.base import MIMEBase

from email.mime.text import MIMEText

from email import encoders

import smtplib

from constants import Constants

from gtts import gTTS

from googletrans import Translator
from pydub import AudioSegment
import docx



app = Flask(__name__,template_folder="template")



app.secret_key = Constants.SECRET_KEY

app.config['AUDIO_MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024 

app.config['VIDEO_MAX_CONTENT_LENGTH'] = 300 * 1024 * 1024

BASE_DIR="/home/mechatt.tk/"

CONVERTED_DIR="/home/mechatt.tk/converted/"

app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'media')

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = app.secret_key
    UPLOAD_FOLDER = os.path.join(basedir, 'static/uploads')
    ALLOWED_EXTENSIONS = {'.mp3', '.wav'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
app.config.from_object(Config)

#using scheduling to delete the files after 24 hour

def check_old_files():

    for root,dirs,files in os.walk("/home/mechatt.tk/converted/SrtFiles/audio/"):

        for name in files:

            if name.endswith(".srt") or name.endswith(".txt"):

                os.remove(os.path.join(root,name))

               

    for root,dirs,files in os.walk("/home/mechatt.tk/converted/SrtFiles/video/"):

        for name in files:

            if name.endswith(".srt")  or name.endswith(".txt"):

                os.remove(os.path.join(root,name))

                

    for root,dirs,files in os.walk("/home/mechatt.tk/converted/TxtFiles/"):

        for name in files:

            if  name.endswith(".txt"):

                os.remove(os.path.join(root,name))

               

    for root,dirs,files in os.walk("/home/mechatt.tk/uploads/"):

        for name in files:

            if  name.endswith(".mp3") or name.endswith(".mp4") or name.endswith(".wav") or name.endswith(".avi"):

                os.remove(os.path.join(root,name))

               

sched = BackgroundScheduler(daemon=True)

sched.add_job(check_old_files,'interval',minutes=240)

sched.start()



filename=""

wav_filename=""

result={}



model = whisper.load_model("base")

@app.route('/')

def home():

    if 'logged_in' in session and session['logged_in']:

        sent = request.args.get('sent', False, type=bool)

        data=session.get('data','')

        username = session['username']

        return render_template('home.html', logged_in=True,username=username,data=data,sent=sent)

    else:

        return render_template('home.html',logged_in=False)

    
@app.route('/text-to-speech')
def textToSpeech():
    if 'logged_in' in session and session['logged_in']:
        data=session.get('data','')
        username = session['username']
        return render_template('textToSpeech.html', logged_in=True,username=username,data=data)
    else:
        return render_template('textToSpeech.html',logged_in=False)

@app.route('/login', methods=['GET', 'POST'])

def login():

    if request.method == 'POST':

        username = request.form['username']

        password = request.form['password']

        conn = sqlite3.connect('db_user.db')

        c = conn.cursor()

        c.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))

        

        user = c.fetchone()

        if user:

            session['user_id'] = user[0]

            session['username']=user[1]

            session['logged_in'] = True

            session['Email']=user[3]

            return redirect(url_for('home'))

        else:

            return render_template('login.html', message='Invalid username or password')

    else:

        return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])

def signup():

    if request.method == 'POST':

        username = request.form['username']

        password = request.form['password']

        email = request.form['email']

        if(len(password)<6):

            return render_template('signup.html',message="Please enter your password at least 6 characters")

        else:

            conn = sqlite3.connect('db_user.db')

            c = conn.cursor()

            c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")

            result = c.fetchone()



            if result:

                print("Table 'users' exists")

                c.execute('SELECT * FROM users WHERE username=?', (username,))

                if c.fetchone():

                    return render_template('signup.html', message='Username already exists')

                

                else:

                    c.execute('INSERT INTO users (username, password, email) VALUES (?, ?, ?)', (username, password,email))

                    conn.commit()

                    return redirect(url_for('login'))

            else:

                c.execute('CREATE TABLE users (user_id INTEGER PRIMARY KEY, username TEXT, password TEXT,Email TEXT)')   

                c.execute('SELECT * FROM users WHERE username=?', (username,))

                if c.fetchone():

                    return render_template('signup.html', message='Username not Availaible')

                else:

                    c.execute('INSERT INTO users (username, password,email) VALUES (?, ?, ?)', (username, password, email))

                    conn.commit()

                    return redirect(url_for('login'))

    else:

        return render_template('signup.html')

@app.route('/process_text', methods=['POST'])
def process_text():
    global filename,temp_timestamp,result
    textFile = ""
    if "file" in request.files:
        textFile = request.files['file']
    language = request.form.get('language')
    translation = request.form.get('translation')
    volume = request.form.get('volume')
    speed = request.form.get('speed')
    content = request.form.get('content')
    text = ""   
    if textFile:
        print("filemode")
        def allowed_file(filename):
            ALLOWED_EXTENSIONS = {'txt', 'srt', 'docx'}
            return '.' in filename and \
                filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
        if not allowed_file(textFile.filename):
            flash('Only .txt, .docx, and .srt files are allowed.')
            return redirect(url_for('textToSpeech'))
        
        # save the file temporary for processing

        textFile.save(f"{os.curdir}\\uploads\\{textFile.filename}")

        if(textFile.filename.endswith(".txt") or textFile.filename.endswith(".srt")):
            file_txt = open(f"uploads\\{textFile.filename}", 'r')
            text = file_txt.read()
            file_txt.close()
        if(textFile.filename.endswith(".docx")):
            doc = docx.Document(f"uploads\\{textFile.filename}")
            text = ''

            # loop through each paragraph in the document and append the text to the string
            for para in doc.paragraphs:
                text += para.text


    # filename = textFile.filename
    # print(filename)
    elif content:
        text = content
        # create and save the file temporary for processing
    else:
        return jsonify({'success': False})
    
    # translate the content
    if(translation!="0" and text !=""):
        translator = Translator()
        translation_1 = translation
        if translation_1 in ['en-in', 'en-au']:
            translation_1 = "en"
        elif translation_1 == "fr-ca":
            translation_1 = "fr"
        text = translator.translate(text,src=language, dest=translation_1).text

        language = translation
    
    # set the language here
    audio_file = os.path.join(Config.UPLOAD_FOLDER, 'audio.mp3')
    file_name = 'audio.mp3'
    i=0
    while(os.path.isfile(audio_file)):
        audio_file = os.path.join(Config.UPLOAD_FOLDER, f'audio{i}.mp3')
        file_name = f'audio{i}.mp3'
        i+=1

    tld = {
        'en-in':'co.in',
        'en-au':'com.au',
        'fr-ca':'ca',
    }
    if language =="en-in":
        myobj = gTTS(text=text, lang='en', tld=tld[language])

        myobj.save(audio_file)
    elif language =="en-au":
        myobj = gTTS(text=text, lang='en', tld=tld[language])

        myobj.save(audio_file)
    elif language =="fr-ca":
        myobj = gTTS(text=text, lang='fr', tld=tld[language])

        myobj.save(audio_file)
    else:
        myobj = gTTS(text=text, lang=language)
        myobj.save(audio_file)

    speed = float(speed)
    if speed>1:
        audio = AudioSegment.from_file(audio_file, format='mp3')
        if(volume=="fast"):
            audio = audio + 6
        if(volume=="slow"):
            audio = audio - 3
        audio_faster = audio.speedup(speed)
        audio_faster.export(audio_file, format='mp3')

    return jsonify({'file_name': file_name})



@app.route('/process_file', methods=['POST'])

def process_file():

    global filename,temp_timestamp,result

    file = request.files['file']

    if "file" not in request.files:

            flash("No file selected", "error")

            return render_template("home.html")

    if not allowed_file(file.filename):

        flash('Only mp3, wav, mp4, and AVI files are allowed.')

        return redirect(url_for('home'))

    if file.content_length > app.config['VIDEO_MAX_CONTENT_LENGTH']:

        if str(file.filename).endswith('.mp3'):

            flash("Audio file size exceeds the maximum allowed limit of 20MB")

            return redirect(url_for('home'))

        else:

            flash('Video File size exceeds the maximum allowed limit of 300MB.')

            return redirect(url_for('home'))

    filename = file.filename

    file.save(f"/home/mechatt.tk/uploads/"+filename)

    model=whisper.load_model("base")

    result=model.transcribe("/home/mechatt.tk/uploads/"+filename)

    recognized_text = result['text']

    session['data']=recognized_text

    segments = result['segments']

    

    if(filename.endswith(".mp4") or filename.endswith(".avi")):

        mp4Srtfilename = os.path.join("/home/mechatt.tk/converted/SrtFiles/video", filename[:-4]+".srt")

        make_Subtitle(segments, mp4Srtfilename)

        Txtfilename = os.path.join("/home/mechatt.tk/converted/SrtFiles/video", filename[:-4]+".txt")

        with open(Txtfilename, 'w', encoding='utf-8') as txtFile:

            for res in recognized_text:

                txtFile.write(res)             

    else:

        Srtfilename = os.path.join("/home/mechatt.tk/converted/SrtFiles/audio", filename[:-4]+".srt")

        make_Subtitle(segments, Srtfilename)

    txtFilename=os.path.join("/home/mechatt.tk/converted/TxtFiles", filename[:-4]+".txt")

    with open(txtFilename, 'w', encoding='utf-8') as txtFile:

        for res in recognized_text:

            txtFile.write(res)

    if os.path.exists("/home/mechatt.tk/uploads/"+filename):

        os.remove("/home/mechatt.tk/uploads/"+filename)

    return jsonify({'text': recognized_text})

@app.route('/download-audio-srt')     

def download_audio_srt():

    global wav_filename

    srtfilepath = os.path.join("/home/mechatt.tk/converted/SrtFiles/audio", wav_filename[:-4]+".srt")

    return_data = io.BytesIO()

    with open(srtfilepath, 'rb') as fo:

        return_data.write(fo.read())

    return_data.seek(0)

    #os.remove(srtfilepath)

    return send_file(return_data, mimetype='text/srt',as_attachment=True,download_name="audio.srt")

@app.route('/download-audio-txt')

def download_audio_txt():

    global wav_filename

    txtfilepath = os.path.join("/home/mechatt.tk/converted/TxtFiles/", wav_filename[:-4]+".txt")

    return_data = io.BytesIO()

    with open(txtfilepath, 'rb') as fo:

        return_data.write(fo.read())

    return_data.seek(0)

    #os.remove(txtfilepath)

    return send_file(return_data, mimetype='text/plain',as_attachment=True,download_name="audio.txt")

       

@app.route('/download-srt')     

def download_srt():

    global filename

    if(filename.endswith('.mp4') ) or (filename.endswith('.avi') ):

        my_zip=zipfile.ZipFile("/home/mechatt.tk/"+"Transcribed_Folder.zip",'w')

        my_zip.write("/home/mechatt.tk/converted/SrtFiles/video/" + filename[:-4]+".srt")

        my_zip.write("/home/mechatt.tk/converted/SrtFiles/video/" + filename[:-4]+".txt")

        my_zip.write("/home/mechatt.tk/uploads/"+filename)

        my_zip.close()

        folderename = "/home/mechatt.tk/"+"Transcribed_Folder.zip"

        return_data = io.BytesIO()

        with open(folderename, 'rb') as fo:

            return_data.write(fo.read())

        return_data.seek(0)

        os.remove("/home/mechatt.tk/converted/SrtFiles/video/" + filename[:-4]+".srt")

        os.remove("/home/mechatt.tk/converted/SrtFiles/video/" + filename[:-4]+".txt")

        if not os.path.isfile(folderename):

            return render_template('404.html')

        if os.path.exists("/home/mechatt.tk/uploads/"+filename):

            os.remove("/home/mechatt.tk/uploads/"+filename)

        

        os.remove(folderename)

        return send_file(return_data, mimetype='application/zip',as_attachment=True,download_name="Transcribed_Folder.zip")

    elif(filename.endswith('.mp3')):

        srtfilepath = os.path.join("/home/mechatt.tk/converted/SrtFiles/audio", filename[:-4]+".srt")



        return_data = io.BytesIO()

        with open(srtfilepath, 'rb') as fo:

            return_data.write(fo.read())

        return_data.seek(0)

        if not os.path.isfile(srtfilepath):

            return render_template('404.html')

        #os.remove(srtfilepath)

        if os.path.exists("/home/mechatt.tk/uploads/"+filename):

            os.remove("/home/mechatt.tk/uploads/"+filename)

        

        return send_file(return_data, mimetype='text/srt',as_attachment=True,download_name=filename[:-4]+".srt")

    else:

        srtfilepath = os.path.join("/home/mechatt.tk/converted/SrtFiles/audio", filename[:-4]+".srt")

        return_data = io.BytesIO()

        with open(srtfilepath, 'rb') as fo:

            return_data.write(fo.read())

        return_data.seek(0)

        if not os.path.isfile(srtfilepath):

            return render_template('404.html')

        if os.path.exists("/home/mechatt.tk/uploads/"+filename):

            os.remove("/home/mechatt.tk/uploads/"+filename)

        #os.remove(srtfilepath)

        return send_file(return_data, mimetype='text/srt',as_attachment=True,download_name=filename[:-4]+".srt")





@app.route('/download-txt')     

def download_txt():

    try:

        global filename

        txtfilepath = os.path.join("/home/mechatt.tk/converted/TxtFiles", filename[:-4]+".txt")

        return_data = io.BytesIO()

        with open(txtfilepath, 'rb') as fo:

            return_data.write(fo.read())

        return_data.seek(0)

        if not os.path.isfile(txtfilepath):

            return render_template('404.html')

        if os.path.exists("/home/mechatt.tk/uploads/"+filename):

            os.remove("/home/mechatt.tk/uploads/"+filename)

       # os.remove(txtfilepath)

        return send_file(return_data, mimetype='text/plain',as_attachment=True,download_name=filename[:-4]+".txt")

    except FileNotFoundError:

        return redirect(url_for('home'))

    

@app.route('/upload', methods=['POST'])

def upload_file():

    global wav_filename                             

    file = request.files['audio']

    wav_filename=file.filename

    file.save("/home/mechatt.tk/uploads/"+wav_filename)

    result=model.transcribe("/home/mechatt.tk/uploads/"+wav_filename)

    recognized_text = result['text']

    session['data']=recognized_text

    segments = result['segments']

    txtFilename=os.path.join("/home/mechatt.tk/converted/TxtFiles", wav_filename[:-4]+".txt")

    with open(txtFilename, 'w', encoding='utf-8') as txtFile:

        for res in recognized_text:

            txtFile.write(res)

    wavSrtfilename = os.path.join("/home/mechatt.tk/converted/SrtFiles/audio", wav_filename[:-4]+".srt")

    make_Subtitle(segments, wavSrtfilename)

    if os.path.exists("/home/mechatt.tk/uploads/"+wav_filename):

            os.remove("/home/mechatt.tk/uploads/"+wav_filename)

    return recognized_text

@app.route('/download-srt-english')

def translateToEnglish():

    global filename,result

    srtfilepath=os.path.join("/home/mechatt.tk/converted/SrtFiles/audio", filename[:-4]+"_English_Subtitle"+".srt")

    recognized_text = result['text']

    session['data']=recognized_text

    segments = result['segments']

    make_Subtitle(segments, srtfilepath)

    return_data = io.BytesIO()

    with open(srtfilepath, 'rb') as fo:

        return_data.write(fo.read())

    return_data.seek(0)

    if not os.path.isfile(srtfilepath):

            return render_template('404.html')

    if os.path.exists("/home/mechatt.tk/uploads/"+filename):

            os.remove("/home/mechatt.tk/uploads/"+filename)

    #os.remove(srtfilepath)

    return send_file(return_data, mimetype='text/srt',as_attachment=True,download_name=filename[:-4]+".srt")

def send_rec_mail_background(recipient_mail):

    global wav_filename

    file = request.files['audio']

    wav_filename=file.filename

    file.save("/home/mechatt.tk/uploads/"+wav_filename)

    result=model.transcribe("/home/mechatt.tk/uploads/"+wav_filename)

    recognized_text = result['text']

    session['data']=recognized_text

    segments = result['segments']

    txtFilename=os.path.join("/home/mechatt.tk/converted/TxtFiles", wav_filename[:-4]+".txt")

    with open(txtFilename, 'w', encoding='utf-8') as txtFile:

        for res in recognized_text:

            txtFile.write(res)

    wavSrtfilename = os.path.join("/home/mechatt.tk/converted/SrtFiles/audio", wav_filename[:-4]+".srt")

    make_Subtitle(segments, wavSrtfilename)

    threading.Thread(target=send_recorded_mail, args=(recipient_mail,)).start()

    

def send_recorded_mail(recipient):

    with app.app_context():

        if(wav_filename.endswith(".wav")):

            temp_dir ="temp_files"

            if not os.path.exists(temp_dir):

                os.mkdir(temp_dir)

            audio_srt_path="/home/mechatt.tk/converted/SrtFiles/audio/" + wav_filename[:-4]+".srt"

            audio_text_path="/home/mechatt.tk/converted/TxtFiles/" + wav_filename[:-4]+".txt"

            file_paths = [audio_srt_path, audio_text_path]

            for file_path in file_paths:

                file_name = os.path.basename(file_path)

                dest_path = os.path.join(temp_dir, file_name)

                shutil.copy(file_path, dest_path)

            zip_file_path = 'files.zip'

            with zipfile.ZipFile(zip_file_path, 'w') as zip_file:

                for file_path in file_paths:

                    file_name = os.path.basename(file_path)

                    zip_file.write(os.path.join(temp_dir, file_name))

            message = MIMEMultipart()



            message['From'] = Constants.SENDER_EMAIL

            message['To'] = recipient_mail

            message['Subject'] = 'Zip file containing files'

            body = "Please find attached the zip file containing the requested files."

            message.attach(MIMEText(body, 'plain'))

            with open(zip_file_path, "rb") as zip_file:

                part = MIMEBase('application', 'zip')

                part.set_payload(zip_file.read())

                encoders.encode_base64(part)

                part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(zip_file_path))

                message.attach(part)

            with smtplib.SMTP(Constants.SMTP_SERVER, Constants.SMTP_PORT) as server:

                server.ehlo()

                server.starttls()

                

                server.login(Constants.SENDER_EMAIL, Constants.SENDER_PASSWORD)

                

                server.sendmail(Constants.SENDER_EMAIL, recipient_mail, message.as_string())

                



            # Remove the temporary directory and the zip file

            os.remove(zip_file_path)

            shutil.rmtree(temp_dir)

def send_rec_mail(recipient_mail):

    with app.app_context():

        if(wav_filename.endswith(".wav")):

            temp_dir ="temp_files"

            if not os.path.exists(temp_dir):

                os.mkdir(temp_dir)

            audio_srt_path="/home/mechatt.tk/converted/SrtFiles/audio/" + wav_filename[:-4]+".srt"

            audio_text_path="/home/mechatt.tk/converted/TxtFiles/" + wav_filename[:-4]+".txt"

            file_paths = [audio_srt_path, audio_text_path]

            for file_path in file_paths:

                file_name = os.path.basename(file_path)

                dest_path = os.path.join(temp_dir, file_name)

                shutil.copy(file_path, dest_path)

            zip_file_path = 'files.zip'

            with zipfile.ZipFile(zip_file_path, 'w') as zip_file:

                for file_path in file_paths:

                    file_name = os.path.basename(file_path)

                    zip_file.write(os.path.join(temp_dir, file_name))

            message = MIMEMultipart()



            message['From'] = Constants.SENDER_EMAIL

            message['To'] = recipient_mail

            message['Subject'] = 'Zip file containing files'

            body = "Please find attached the zip file containing the requested files."

            message.attach(MIMEText(body, 'plain'))

            with open(zip_file_path, "rb") as zip_file:

                part = MIMEBase('application', 'zip')

                part.set_payload(zip_file.read())

                encoders.encode_base64(part)

                part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(zip_file_path))

                message.attach(part)

            with smtplib.SMTP(Constants.SMTP_SERVER, Constants.SMTP_PORT) as server:

                server.ehlo()

                server.starttls()

                

                server.login(Constants.SENDER_EMAIL, Constants.SENDER_PASSWORD)

                

                server.sendmail(Constants.SENDER_EMAIL, recipient_mail, message.as_string())

                



            # Remove the temporary directory and the zip file

            os.remove(zip_file_path)

            shutil.rmtree(temp_dir)


def send_rec_mail_2(recipient_mail, file_name):

    with app.app_context():

        temp_dir ="temp_files"

        if not os.path.exists(temp_dir):

            os.mkdir(temp_dir)
        audio_path=f"{os.path.curdir}/static/uploads/{file_name}"

        file_paths = [audio_path]

        for file_path in file_paths:

            file_name = os.path.basename(file_path)

            dest_path = os.path.join(temp_dir, file_name)

            shutil.copy(file_path, dest_path)

        zip_file_path = 'files.zip'

        with zipfile.ZipFile(zip_file_path, 'w') as zip_file:

            for file_path in file_paths:

                file_name = os.path.basename(file_path)

                zip_file.write(os.path.join(temp_dir, file_name))

        message = MIMEMultipart()



        message['From'] = Constants.SENDER_EMAIL

        message['To'] = recipient_mail

        message['Subject'] = 'Zip file containing files'

        body = "Please find attached the zip file containing the requested files."

        message.attach(MIMEText(body, 'plain'))

        with open(zip_file_path, "rb") as zip_file:

            part = MIMEBase('application', 'zip')

            part.set_payload(zip_file.read())

            encoders.encode_base64(part)

            part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(zip_file_path))

            message.attach(part)

        with smtplib.SMTP(Constants.SMTP_SERVER, Constants.SMTP_PORT) as server:

            server.ehlo()

            server.starttls()

            

            server.login(Constants.SENDER_EMAIL, Constants.SENDER_PASSWORD)

            

            abc = server.sendmail(Constants.SENDER_EMAIL, recipient_mail, message.as_string())
            print(recipient_mail)
            print(abc)
            print("worked")

            



        # Remove the temporary directory and the zip file

        os.remove(zip_file_path)

        shutil.rmtree(temp_dir)




def send_mail_background(recipient_mail):

    global filename

    file = request.files['file']

    if "file" not in request.files:

            flash("No file selected", "error")

            return render_template("home.html")

    if not allowed_file(file.filename):

        flash('Only mp3, wav, mp4, and AVI files are allowed.')

        return redirect(url_for('home'))

    if file.content_length > app.config['VIDEO_MAX_CONTENT_LENGTH']:

        if str(file.filename).endswith('.mp3'):

            flash("Audio file size exceeds the maximum allowed limit of 20MB")

            return redirect(url_for('home'))

        else:

            flash('Video File size exceeds the maximum allowed limit of 300MB.')

            return redirect(url_for('home'))

    filename = file.filename

    print(filename)

    file.save(f"/home/mechatt.tk/uploads/"+filename)

    model=whisper.load_model("base")

    result=model.transcribe("/home/mechatt.tk/uploads/"+filename)

    recognized_text = result['text']

    session['data']=recognized_text

    segments = result['segments']

    if(filename.endswith(".mp4") or filename.endswith(".avi")):

        mp4Srtfilename = os.path.join("/home/mechatt.tk/converted/SrtFiles/video", filename[:-4]+".srt")

        make_Subtitle(segments, mp4Srtfilename)

        Txtfilename = os.path.join("/home/mechatt.tk/converted/SrtFiles/video", filename[:-4]+".txt")

        with open(Txtfilename, 'w', encoding='utf-8') as txtFile:

            for res in recognized_text:

                txtFile.write(res)             

    else:

        Srtfilename = os.path.join("/home/mechatt.tk/converted/SrtFiles/audio", filename[:-4]+".srt")

        make_Subtitle(segments, Srtfilename)

    txtFilename=os.path.join("/home/mechatt.tk/converted/TxtFiles", filename[:-4]+".txt")

    with open(txtFilename, 'w', encoding='utf-8') as txtFile:

        for res in recognized_text:

            txtFile.write(res)

    if os.path.exists("/home/mechatt.tk/uploads/"+filename):

        os.remove("/home/mechatt.tk/uploads/"+filename)

    threading.Thread(target=send_email, args=(recipient_mail,)).start()

    

def send_email(recipient_mail):

    with app.app_context():



        if(filename.endswith('.mp3') ) or filename.endswith('.wav'):



            temp_dir ="temp_files"

            if not os.path.exists(temp_dir):

                os.mkdir(temp_dir)

            audio_srt_path="/home/mechatt.tk/converted/SrtFiles/audio/" + filename[:-4]+".srt"

            audio_text_path="/home/mechatt.tk/converted/TxtFiles/" + filename[:-4]+".txt"

            file_paths = [audio_srt_path, audio_text_path]

            for file_path in file_paths:

                file_name = os.path.basename(file_path)

                dest_path = os.path.join(temp_dir, file_name)

                shutil.copy(file_path, dest_path)

            zip_file_path = 'files.zip'

            with zipfile.ZipFile(zip_file_path, 'w') as zip_file:

                for file_path in file_paths:

                    file_name = os.path.basename(file_path)

                    zip_file.write(os.path.join(temp_dir, file_name))

            

            



            # Attach the zip file to the email message'

            message = MIMEMultipart()



            message['From'] = Constants.SENDER_EMAIL

            message['To'] = recipient_mail

            message['Subject'] = 'Zip file containing files'

            body = "Please find attached the zip file containing the requested files."

            message.attach(MIMEText(body, 'plain'))

            with open(zip_file_path, "rb") as zip_file:

                part = MIMEBase('application', 'zip')

                part.set_payload(zip_file.read())

                encoders.encode_base64(part)

                part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(zip_file_path))

                message.attach(part)

            with smtplib.SMTP(Constants.SMTP_SERVER, Constants.SMTP_PORT) as server:

                server.ehlo()

                server.starttls()

                server.login(Constants.SENDER_EMAIL, Constants.SENDER_PASSWORD)

                

                server.sendmail(Constants.SENDER_EMAIL, recipient_mail, message.as_string())

                

            

            os.remove(zip_file_path)

            shutil.rmtree(temp_dir)

        elif filename.endswith(".mp4") or filename.endswith(".avi"):

            temp_dir ="temp_files"

            if not os.path.exists(temp_dir):

                os.mkdir(temp_dir)

            audio_srt_path="/home/mechatt.tk/converted/SrtFiles/video/" + filename[:-4]+".srt"

            audio_text_path="/home/mechatt.tk/converted/TxtFiles/" + filename[:-4]+".txt"

            file_paths = [audio_srt_path, audio_text_path]

            for file_path in file_paths:

                file_name = os.path.basename(file_path)

                dest_path = os.path.join(temp_dir, file_name)

                shutil.copy(file_path, dest_path)

            zip_file_path = 'files.zip'

            with zipfile.ZipFile(zip_file_path, 'w') as zip_file:

                for file_path in file_paths:

                    file_name = os.path.basename(file_path)

                    zip_file.write(os.path.join(temp_dir, file_name))

            message = MIMEMultipart()



            message['From'] = Constants.SENDER_EMAIL

            message['To'] = recipient_mail

            message['Subject'] = 'Zip file containing files'

            body = "Please find attached the zip file containing the requested files."

            message.attach(MIMEText(body, 'plain'))

            with open(zip_file_path, "rb") as zip_file:

                part = MIMEBase('application', 'zip')

                part.set_payload(zip_file.read())

                encoders.encode_base64(part)

                part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(zip_file_path))

                message.attach(part)

            with smtplib.SMTP(Constants.SMTP_SERVER, Constants.SMTP_PORT) as server:

                

                server.ehlo()

                server.starttls()

                server.login(Constants.SENDER_EMAIL, Constants.SENDER_PASSWORD)

                

                server.sendmail(Constants.SENDER_EMAIL, recipient_mail, message.as_string())

                

            



            # Remove the temporary directory and the zip file

            os.remove(zip_file_path)

            shutil.rmtree(temp_dir)





def send_mail(recipient_mail):

    with app.app_context():



        if(filename.endswith('.mp3') ) or filename.endswith('.wav'):



            temp_dir ="temp_files"

            if not os.path.exists(temp_dir):

                os.mkdir(temp_dir)

            audio_srt_path="/home/mechatt.tk/converted/SrtFiles/audio/" + filename[:-4]+".srt"

            audio_text_path="/home/mechatt.tk/converted/TxtFiles/" + filename[:-4]+".txt"

            file_paths = [audio_srt_path, audio_text_path]

            for file_path in file_paths:

                file_name = os.path.basename(file_path)

                dest_path = os.path.join(temp_dir, file_name)

                shutil.copy(file_path, dest_path)

            zip_file_path = 'files.zip'

            with zipfile.ZipFile(zip_file_path, 'w') as zip_file:

                for file_path in file_paths:

                    file_name = os.path.basename(file_path)

                    zip_file.write(os.path.join(temp_dir, file_name))

            

            

            # Attach the zip file to the email message'

            message = MIMEMultipart()



            message['From'] = Constants.SENDER_EMAIL

            message['To'] = recipient_mail

            message['Subject'] = 'Zip file containing files'

            body = "Please find attached the zip file containing the requested files."

            message.attach(MIMEText(body, 'plain'))

            with open(zip_file_path, "rb") as zip_file:

                part = MIMEBase('application', 'zip')

                part.set_payload(zip_file.read())

                encoders.encode_base64(part)

                part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(zip_file_path))

                message.attach(part)

            with smtplib.SMTP(Constants.SMTP_SERVER, Constants.SMTP_PORT) as server:

                server.ehlo()

                server.starttls()

                server.login(Constants.SENDER_EMAIL, Constants.SENDER_PASSWORD)

                

                server.sendmail(Constants.SENDER_EMAIL, recipient_mail, message.as_string())

                

            

            os.remove(zip_file_path)

            shutil.rmtree(temp_dir)

        elif filename.endswith(".mp4") or filename.endswith(".avi"):

            temp_dir ="temp_files"

            if not os.path.exists(temp_dir):

                os.mkdir(temp_dir)

            audio_srt_path="/home/mechatt.tk/converted/SrtFiles/video/" + filename[:-4]+".srt"

            audio_text_path="/home/mechatt.tk/converted/TxtFiles/" + filename[:-4]+".txt"

            file_paths = [audio_srt_path, audio_text_path]

            for file_path in file_paths:

                file_name = os.path.basename(file_path)

                dest_path = os.path.join(temp_dir, file_name)

                shutil.copy(file_path, dest_path)

            zip_file_path = 'files.zip'

            with zipfile.ZipFile(zip_file_path, 'w') as zip_file:

                for file_path in file_paths:

                    file_name = os.path.basename(file_path)

                    zip_file.write(os.path.join(temp_dir, file_name))

            message = MIMEMultipart()



            message['From'] = Constants.SENDER_EMAIL

            message['To'] = recipient_mail

            message['Subject'] = 'Zip file containing files'

            body = "Please find attached the zip file containing the requested files."

            message.attach(MIMEText(body, 'plain'))

            with open(zip_file_path, "rb") as zip_file:

                part = MIMEBase('application', 'zip')

                part.set_payload(zip_file.read())

                encoders.encode_base64(part)

                part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(zip_file_path))

                message.attach(part)

            with smtplib.SMTP(Constants.SMTP_SERVER, Constants.SMTP_PORT) as server:

                

                server.ehlo()

                server.starttls()

                server.login(Constants.SENDER_EMAIL, Constants.SENDER_PASSWORD)

                

                server.sendmail(Constants.SENDER_EMAIL, recipient_mail, message.as_string())

                



            # Remove the temporary directory and the zip file

            os.remove(zip_file_path)

            shutil.rmtree(temp_dir)

        



@app.route('/send-as-mail-background', methods=['POST'])

def send_as_email_background():

    recipient_mail=session['Email']

    send_mail_background(recipient_mail)

    return redirect(url_for('home',sent=True))

@app.route('/send-to-email/<slug>')

def send_to_email(slug):

    recipient_mail=session['Email']

    send_rec_mail_2(recipient_mail, slug)

    return redirect(url_for('textToSpeech',sent=True))

@app.route('/send-as-mail')

def send_as_email():

    recipient_mail=session['Email']

    send_mail(recipient_mail)

    return redirect(url_for('home',sent=True))



@app.route('/send-as-mail-audio-background',methods=['POST'])

def send_as_email_audio_back():

    recipient_mail=session['Email']

    print(recipient_mail)

    send_rec_mail_background(recipient_mail)

    return redirect(url_for('home',sent=True))

@app.route('/send-as-mail-audio',methods=['POST'])

def send_as_email_audio():

    recipient_mail=session['Email']

    print(recipient_mail)

    send_rec_mail_background(recipient_mail)

    return redirect(url_for('home',sent=True))









@app.route('/live')

def liveTrascribe():

    if 'logged_in' in session and session['logged_in']:

        username=session['username']

        sent=request.args.get('sent', False, type=bool)

        return render_template('liveTranscript.html',logged_in=True,username=username,sent=sent)

    else:

        return render_template("liveTranscript.html",logged_in=False)

def make_Subtitle(segments,filepath):

    with open(filepath, 'w', encoding='utf-8') as srtFile:

        for segment in segments:

            startTime = str(0)+str(timedelta(seconds=int(segment['start'])))+',000'

            endTime = str(0)+str(timedelta(seconds=int(segment['end'])))+',000'

            text = segment['text']

            segmentId = segment['id']+1

            segment = f"{segmentId}\n{startTime} --> {endTime}\n{text[1:] if text[0] is ' ' else text}\n\n"

            srtFile.write(segment)



def allowed_file(filename):

    ALLOWED_EXTENSIONS = {'mp3', 'wav', 'mp4', 'avi'}

    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/aboutus')

def aboutUs():

    return render_template('aboutUs.html')

@app.route('/tos')

def tos():

    return render_template('termsOfService.html')



@app.route('/getUser')

def getUser():

    if 'logged_in' in session['logged_in']:

        return jsonify({'username': session['username']})

    else:

        return jsonify({'username': None})

@app.route('/contactus', methods=['GET', 'POST'])

def contactUs():

    if request.method=='POST':

        subject = request.form['subject']

        query = request.form['body']

        if str(subject)=="" and str(query)=="":

            

            return render_template('contactUs.html')

        else:

            

            conn = sqlite3.connect('db_user.db')

            c = conn.cursor()

            c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='queries_table'")

            result = c.fetchone()



            if result:

                c.execute('INSERT INTO queries_table (subject, body) VALUES (?, ?)', (subject, query))

                conn.commit()

                return redirect(url_for('thankyou'))

            else:

                c.execute('CREATE TABLE queries_table (q_id INTEGER PRIMARY KEY, subject TEXT, password TEXT,body TEXT)')   

                c.execute('INSERT INTO queries_table (subject, body) VALUES (?, ?)', (subject, query))

                conn.commit()

                return redirect(url_for('thankyou'))

    else:

        return render_template('contactUs.html')





@app.route('/thankyou')

def thankyou():

    return render_template('thankyou.html')

            

@app.route('/logout')

def logout():

    session.pop('user_id', None)

    session.pop('username', None)

    session.clear()

    flash('You have been logged out.', 'success')

    return redirect(url_for('home'))

    

    

if __name__ == "__main__":

    with app.app_context():    

        app.run(port=7000)