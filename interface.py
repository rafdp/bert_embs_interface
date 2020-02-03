from flask import Flask, render_template, abort, redirect, url_for, session
from flask_wtf import FlaskForm
from wtforms import TextAreaField, BooleanField
import subprocess
import os
import numpy as np 
import subprocess
app = Flask(__name__)
app.config['SECRET_KEY'] = 'sk'

def EvaluateToxicity(text):
   wd = os.getcwd()
   os.chdir("/home/rafdp/Documents/tox/bert_embs/")
   with open("comment.txt", "w") as comm_file:
       comm_file.write(text)
   bashCommand = ["python", "predict.py", "hparams_full.json", "2"]
   subprocess.run(bashCommand)
   result = np.load("comment_result.npy")
   os.chdir(wd)
   print(result.tolist())
   return float(result[9]), result[:9].tolist(), result[10:].tolist()

class CommentInputForm(FlaskForm):
    comment = TextAreaField("Enter the comment to analyze:")
    toxicity_subtype = BooleanField("Toxicity subtype analysis")
    identity         = BooleanField("Mentioned identity analysis")


@app.route("/", methods = ["GET", "POST"])
def home():
    form = CommentInputForm()
    if form.validate_on_submit():
        session["results"] = EvaluateToxicity(form.comment.data)
        session["toxicity_subtype"] = form.toxicity_subtype.data
        session["identity"] = form.identity.data
        return redirect(url_for("result"))
    return render_template("home.html", form=form)

@app.route("/model_info")
def model_info():
    return render_template("model_info.html")

@app.route("/tutorial")
def tutorial():
    return render_template("tutorial.html")

@app.route("/result", methods = ["GET", "POST"])
def result():
    toxicity, identity_result, subtype_result = session["results"] 
    toxicity_subtype = session["toxicity_subtype"] 
    identity = session["identity"]
    identity_names = ["male", "female", 
                      "homosexual_gay_or_lesbian", 
                      "christian", "jewish", 
                      "muslim", "black", 
                      "white", "psychiatric_or_mental_illness"]
    subtype_names = ["severe_toxicity", 
                     "obscene", "threat", 
                     "insult", "identity_attack", 
                     "sexual_explicit"]
    identity_data = []
    print(identity, toxicity_subtype)
    for i in range(len(identity_names)):
        identity_data.append([identity_names[i], identity_result[i]]) 
    subtype_data = []
    for i in range(len(subtype_names)):
        subtype_data.append([subtype_names[i], subtype_result[i]]) 
    form = CommentInputForm()
    if form.validate_on_submit():
        session["results"] = EvaluateToxicity(form.comment.data)
        session["toxicity_subtype"] = form.toxicity_subtype.data
        session["identity"] = form.identity.data
    return render_template("result.html", 
                           form=form,
                           identity=identity,
                           toxicity_subtype=toxicity_subtype, 
                           toxicity=toxicity, 
                           subtype_data=subtype_data, 
                           identity_data=identity_data)

if __name__ == "__main__":
  app.run(host= '0.0.0.0', port=int("9999"))

