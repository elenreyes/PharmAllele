from flask import Flask, render_template

PharmaAllele = Flask(__name__)

@PharmaAllele.route("/")

def home ():
    return render_template("index.html")

if __name__ == "__main__":
    PharmaAllele.run(debug=True)