from flask import Flask,request,render_template,redirect,url_for
from keras.preprocessing.image import load_img
from keras.preprocessing.image import img_to_array
from keras.models import load_model
import cv2
import numpy
import pickle
import PIL
import os
from werkzeug import secure_filename


app = Flask(__name__) 
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

@app.route('/about')
def homepage():
    return render_template('imagewebsite.html')


@app.route('/dataset')
def datasetpage():
    return render_template('datasetimage.html')


@app.route('/login', methods=['GET','POST'])
def loginpage():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print(password)
        file = open('register.txt','r+')
        flag = 0
        for lines in file:
            line = lines.split(" ")  
            if line[0] == username :
                passcode = line[1].strip()
                if passcode == password :
                    flag = 1
                    break

        if flag == 1:
            return redirect('/main')
        else:
            return ' <script> alert("username or password wrong, try another") </script> '

    return render_template('loginpage.html')


@app.route('/register', methods=['GET','POST'])
def registerpage():
    if request.method == 'POST' :
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        mail = request.form['mail']
        phno = request.form['phno']
        
        file = open('register.txt','r+')  
        flag = 0       
        for lines in file:
            line = lines.split(" ")
            if line[0] == username :
                flag = 1
                break

        if flag == 1:
            return ' <script> alert("username already taken, try another") </script> '
        else :
            file.write(username+" "+password+"\n")
            file.close()
            return redirect('/login')
               
    return render_template('registerpage.html')


@app.route('/main')
def main():
    return render_template('index.html')

@app.route('/display')
def display():

    with open('details.txt') as details_log:
        details_lines = details_log.readlines()

        data = []
        details = len(details_lines)
        for x in range(details):
            data.append(details_lines[x].split(" "))
        
    return render_template('display.html', details=details, data=data)


@app.route('/enter_data')
def form():
    return render_template('form.html')


@app.route('/result' , methods = ['POST'])
def result():
    if request.method == 'POST':
        
        # data = request.form
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']

        spiral_image =  request.files['spiral_image']
        meander_image = request.files['meander_image']

        s_img = spiral_image.filename
        m_img = meander_image.filename

        spiral_loc = save_image(spiral_image)
        meander_loc = save_image(meander_image)

        spiral_res = predict_spiral(spiral_loc)
        meander_res = predict_meander(meander_loc)

        if spiral_res == meander_res :
            if spiral_res == 0:
                res = 'is Healthy'
                final_res = 'Healthy'
            else:
                res = 'has Parkinson'
                final_res = 'Parkinson'
        else:
            if spiral_res == 0:
                res = 'is Healthy'
                final_res = 'Healthy'
            else:
                res = 'has Parkinson'
                final_res = 'Parkinson'
        
        
        file = open('details.txt','a')
        file.write(name+" "+age+" "+gender+" "+final_res+"\n")
        file.close()
      
    return render_template('result.html',result = res,name=name, age=age, gender=gender)


#save images uploaded in image folder
def save_image(file):

    target = os.path.join(APP_ROOT, 'images')
    print(target)
    if not os.path.isdir(target):
        os.mkdir(target)
    
    filename = file.filename
    destination = "/".join([target, filename])
    print("Accept incoming file:", filename)
    print(destination)
    file.save(destination)
    return destination
    

# load and prepare the image
def predict_spiral(filename):

    img = load_img(filename, target_size=(512, 512))
    img = img_to_array(img)
    img = img.reshape(1, 512, 512, 3)

    model = pickle.load(open('spiral_model.pkl', 'rb'))
    result = model.predict(img)
    print(result[0])
    res = result[0]
    res = int(res)
    if res == 0:
        return 0
    else:
        return 1


def predict_meander(filename):

    img = load_img(filename, target_size=(512, 512))
    img = img_to_array(img)
    img = img.reshape(1, 512, 512, 3)

    model = pickle.load(open('meander_model.pkl', 'rb'))
    result = model.predict(img)
    print(result[0])
    res = result[0]
    res = int(res)
    if res == 0:
        return 0
    else:
        return 1


# main driver function 
if __name__ == '__main__': 
  
    # run() method of Flask class runs the application  
    # on the local development server. 
    app.run() 
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
