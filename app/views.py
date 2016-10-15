from flask import render_template, flash, redirect, request, url_for
from app import app
from .forms import LoginForm
from .formNew import DestinationForm
import sys
from .Read import Read
# index view function suppressed for brevity

@app.route('/')
def home():
    return render_template("lol.html")

@app.route('/index')
def index():
    user = {'nickname': 'Miguel'}  # fake user
    posts = [  # fake array of posts
        {
            'author': {'nickname': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'nickname': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template("index.html",
                           title='Home',
                           user=user,
                           posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    return render_template('login.html',
                           title='Sign In',
                           form=form)

@app.route('/gg', methods=['GET', 'POST'])
def gg():
    form = DestinationForm(request.form)
    if form.validate() and request.method == 'POST':
        start_string = form.start.data
        checkList = request.form.getlist('checked')
        return redirect(url_for('showMap', startVal=start_string, list=checkList))
    return render_template('destination.html', form=form)

@app.route('/showMap/<startVal>/<list>')
def showMap(startVal, list):
    rdf = Read()
    rdf.extractOWl()
    start = {'location': startVal}
    checkList1 = False
    checkList2 = False
    for item in list:
        if item == "taxiNum":
            checkList1 = True
        elif item == "COP":
            checkList2 = True
    bestStand, best3TaxiStand = rdf.performSearch(startVal,checkList1,checkList2)
    if bestStand is None and best3TaxiStand is None:
        return redirect(url_for('gg'))
    endLoc = bestStand.getStandLoc()
    distanceVal = bestStand.getDistance()
    bestTaxiStand = {'bestTaxiStand' : bestStand}
    standList1 = {'standList1' : best3TaxiStand[0]}
    standList2 = {'standList2' : best3TaxiStand[1]}
    standList3 = {'standList3' : best3TaxiStand[2]}
    return render_template('map.html', start=start, bestTaxiStand=bestTaxiStand, standList1=standList1, standList2=standList2, standList3=standList3)
