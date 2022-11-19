from flask import Flask,render_template,request
from flask_mail import Mail,Message

app=Flask(__name__)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT']=465
app.config['MAIL_USERNAME']="2k19cse092@kiot.ac.in"
app.config['MAIL_PASSWORD']="2k19cse092"
app.config['MAIL_USE_TLS']=False
app.config['MAIL_USE_SSL']=True

mail=Mail(app)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/send',methods=["POST"])
def send():
    if request.method=="POST":
        recip = request.form['mail']
        message=Message('hey',sender="2k19cse092@kiot.ac.in",recipients=[recip])
        message.body="LIMIT EXCEEDED"
        mail.send(message)
        return "mail sent"
    render_template("index.html",sucess="mail_sent")

if __name__=="__main_":
    app.run("0.0.0.0",port=5000,debug=True)