from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User

# imports for oauth
from flask import session as login_session
import random
import string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
"""
Project 3 - Item Catalog
authored by Dean Schieve
October 2015
"""

from flask import Flask, render_template
from flask import url_for, flash, request, redirect, jsonify
app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Item Catalog App"

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/login')
def showLogin():
    '''
    login
    '''

    if 'username' not in login_session:
        loggedIn = False
    else:
        loggedIn = True
    state = ''.join(random.choice(
                    string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    categories = session.query(Category).all()
    return render_template('login.html', categories=categories,
                           STATE=state, loggedIn=loggedIn)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
                'Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # check if existing user
    user_id = getUserId(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = " "
    flash("you are now logged in as %s" % login_session['username'])
    return output


@app.route('/gdisconnect')
def gdisconnect():
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(json.dumps(
                    'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    google_url = 'https://accounts.google.com/o/oauth2/revoke?token=%s'
    url = google_url % credentials.access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        flash("Successful Logout")
        return redirect(url_for('HomePage'))
    else:
        response = make_response(
                    json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/')
@app.route('/catalog')
@app.route('/catalog/')
def HomePage():
    """
    Item Catalog Home Page - login not required to view this page
    """
    if 'username' not in login_session:
        loggedIn = False
    else:
        loggedIn = True
    categories = session.query(Category).all()
    items = session.query(Item).join(Category).order_by(
                           Item.item_id.desc()).limit(10)
    return render_template('index.html', categories=categories,
                           items=items, loggedIn=loggedIn)


@app.route('/catalog/<string:category_name>/items/')
def ItemList(category_name):
    """
    List Items in a Category - login not required to view this page
    """
    if 'username' not in login_session:
        loggedIn = False
    else:
        loggedIn = True

    categories = session.query(Category).all()
    category = session.query(Category).filter_by(
                category_name=category_name).first()
    items = session.query(Item).filter_by(
                category_id=category.category_id).all()

    return render_template('category.html', categories=categories,
                           category=category, items=items,
                           loggedIn=loggedIn)


@app.route('/catalog/<string:category_name>/<string:item_name>/')
def ItemDetail(category_name, item_name):
    """
    Display Item Detail - login not required to view this page
    """
    if 'username' not in login_session:
        loggedIn = False
    else:
        loggedIn = True

    categories = session.query(Category).all()
    category = session.query(Category).filter_by(
                category_name=category_name).first()
    items = session.query(Item).filter_by(item_name=item_name).first()

    # check user_id to see if this user created this item_name
    if loggedIn:
        owner = getUserinfo(items.user_id)
        if owner.user_id != login_session['user_id']:
            ownThisItem = False
        else:
            ownThisItem = True
    else:
        # define owner as 0 for guest user (ie not logged in)
        owner = 0
        ownThisItem = False

    return render_template('item.html', categories=categories,
                           category=category, items=items,
                           loggedIn=loggedIn, ownThisItem=ownThisItem)


@app.route('/catalog/item/add/', methods=['GET', 'POST'])
def ItemAdd():
    """
    Add Item - any user can add an item as long as they are logged in
    """
    if 'username' not in login_session:
        loggedIn = False
        return redirect('/login')
    else:
        loggedIn = True

    categories = session.query(Category).all()
    if request.method == 'POST':
        itemToAdd = Item()
        itemToAdd.item_name = request.form['item_name']
        itemToAdd.item_description = request.form['item_description']
        itemToAdd.category_id = request.form['category']
        itemToAdd.user_id = login_session['user_id']
        session.add(itemToAdd)
        session.commit()
        flash("Item Added")
        return redirect(url_for('HomePage'))
    else:
        return render_template('item_add.html',
                               categories=categories,
                               loggedIn=loggedIn)


@app.route('/catalog/<string:item_name>/edit/', methods=['GET', 'POST'])
def ItemEdit(item_name):
    """
    Edit Item - the user that created an item is the
                only one allowed to edit that item
    """
    if 'username' not in login_session:
        loggedIn = False
        return redirect('/login')
    else:
        loggedIn = True

    items = session.query(Item).filter_by(item_name=item_name).first()
    categories = session.query(Category).all()

    # check user_id to see if this user created this item
    owner = getUserinfo(items.user_id)
    if owner.user_id != login_session['user_id']:
        flash("You do not have permission to edit item (%s)!" % item_name)
        return redirect(url_for('HomePage'))

    itemToEdit = session.query(Item).filter_by(item_name=item_name).one()

    if request.method == 'POST':
        itemToEdit.item_name = request.form['item_name']
        itemToEdit.item_description = request.form['item_description']
        itemToEdit.category_id = request.form['category']
        session.add(itemToEdit)
        session.commit()
        flash("Item Details Updated")
        return redirect(url_for('HomePage'))
    else:
        return render_template('item_edit.html',
                               categories=categories,
                               items=items,
                               loggedIn=loggedIn)


@app.route('/catalog/<string:item_name>/delete/', methods=['GET', 'POST'])
def ItemDelete(item_name):
    """
    Delete Item - the user that created an item is the only
                    one allowed to delete that item
    """
    if 'username' not in login_session:
        loggedIn = False
        return redirect('/login')
    else:
        loggedIn = True

    items = session.query(Item).filter_by(item_name=item_name).first()
    categories = session.query(Category).all()

    # check user_id to see if this user created this item
    owner = getUserinfo(items.user_id)

    if owner.user_id != login_session['user_id']:
        flash("You do not have permission to delete item (%s)!" % item_name)
        return redirect(url_for('HomePage'))

    if request.method == 'POST':
        item_id = request.form['item_id']
        itemToDelete = session.query(Item).filter_by(item_id=item_id).one()
        session.delete(itemToDelete)
        session.commit()
        flash("Item Deleted")
        return redirect(url_for('HomePage'))
    else:
        return render_template('item_delete.html',
                               categories=categories,
                               items=items,
                               loggedIn=loggedIn)


@app.route('/catalog.json')
def catalogItemJSON():
    '''
    serialized JSON output
    '''
    # get a list of categories
    categories = session.query(Category).all()
    # create an empty list
    lCategories = []
    for category in categories:
        sCategory = category.serialize
        # collect items in this category, store in temporary list

        lItems = []
        for i in items:
            lItems.append(i.serialize)
        # add items to serialized Category data
        sCategory['items'] = lItems
        # add this categories complete information to master list
        lCategories.append(sCategory)
    return jsonify(categories=[lCategories])


def createUser(login_session):
    newUser = User(username=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.user_id


def getUserinfo(user_id):
    user = session.query(User).filter_by(user_id=user_id).one()
    return user


def getUserId(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.user_id
    except:
        return None

if __name__ == '__main__':
    app.secret_key = '88adkkelkadkjadicz2339858484'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
