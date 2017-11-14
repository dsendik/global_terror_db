#!/usr/bin/env python2.7

"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver

To run locally:

    python server.py

Go to http://localhost:8111 in your browser.

A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

DATABASEURI = "postgresql://drs2176:123@35.196.90.148/proj1part2"

engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#

# engine.execute("""CREATE TABLE IF NOT EXISTS test (
#   id serial,
#   name text
# );""")
# engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")
# """

@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request.

  The variable g is globally accessible.
  """
  try:
    g.conn = engine.connect()
  except:
    print "uh oh, problem connecting to database"
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't, the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/

@app.route('/', methods=['POST', 'GET'])
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """

  # DEBUG: this is debugging code to see what request looks like
  print request.args


  #
  # example of a database query
  #
  cursor = g.conn.execute("SELECT attack_date FROM attacked")
  dates = []
  prev = '19700000'
  for result in cursor:
    if result[0][:8] not in prev:
      dates.append(result[0][:8])  # can also be accessed using result[0]
    prev = result[0][:8]
  cursor.close()

  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be 
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #     
  #     # creates a <div> tag for each element in data
  #     # will print: 
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #
  context = dict(data = dates)


  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  return render_template("index.html", **context)


@app.route('/lookup', methods=['POST', 'GET'])
def lookup():
  event_id = request.form['id']
  entity = request.form['option']
  l = []
  if entity == 'location':
    cursor = g.conn.execute('SELECT event_id, L.latitude, L.longitude, country, city FROM location L, located_in Loc WHERE Loc.event_id LIKE %s AND L.latitude LIKE Loc.latitude', event_id)
    l = ['event_id', 'Latitude', 'Longitude', 'Country', 'City']
  elif entity == 'weapons':
    cursor = g.conn.execute('SELECT event_id, type, subtype, details FROM weapons W, utilized U, (SELECT A.perp_id, A.event_id FROM attacked A join perpetrators P ON A.perp_id LIKE P.perp_id WHERE A.event_id LIKE %s) X WHERE X.perp_id LIKE U.perp_id AND U.wep_id = W.wep_id', event_id)
    l = ['event_id', 'Type', 'Subtype', 'Details']
  elif entity == 'govt':
    cursor = g.conn.execute('SELECT event_id, report, details FROM investigated_by_govt I, governments G WHERE I.event_id LIKE %s AND I.gov_id = G.gov_id', (event_id))
    l = ['event_id', 'Report', 'Details']
  elif entity == 'relevance':
    cursor = g.conn.execute('SELECT event_id, rel_event_id FROM related_to R WHERE R.event_id LIKE %s', (event_id))
    l = ['event_id', 'Relevant event_id']
  elif entity == 'damage':
    cursor = g.conn.execute('SELECT event_id, dmg_amt, prop_value, dmg_details FROM caused_damage_to C, property P WHERE C.event_id LIKE %s AND C.prop_id = P.prop_id',event_id)
    l = ['event_id', 'Damage amount', 'Property value', 'Damage details']

  events = []
  for result in cursor:
    #print(result)
    events.append(result)
  cursor.close()
  context = dict(data = events, lists = l)
  return render_template("lookup.html", **context)


@app.route('/search', methods=['POST', 'GET'])
def search():
  text = request.form['text'].capitalize()
  print text
  processed_text = text.upper()
  l = []
  sql = 'SELECT type,subtype,details FROM weapons WHERE weapons.type LIKE %s OR weapons.subtype LIKE %s OR weapons.details LIKE %s'
  args = ['%' + text + '%', '%' + text + '%', '%' + text + '%']
  cursor = g.conn.execute(sql, args)
  l = ['Weapon type', 'Subtype', 'Details']

  events = []
  for result in cursor:
    events.append(result)
  cursor.close()
  context = dict(data = events,lists = l)
  return render_template("search.html", **context) 

# Example of adding new data to the database
# @app.route('/add', methods=['POST'])
# def add():
#   name = request.form['name']
#   g.conn.execute('INSERT INTO test (name) VALUES (%s)', name)
#   return redirect('/')

@app.route('/nine_eleven', methods=['POST', 'GET'])
def nine_eleven():
  cursor = g.conn.execute(" SELECT DISTINCT ON (incident.event_id) incident.event_id, incident.latitude, incident.longitude, suicide_attack, num_killed, num_injured, name, affiliation, groupname, motive, summary FROM incident INNER JOIN located_in ON incident.event_id = located_in.event_id INNER JOIN attacked ON incident.event_id = attacked.event_id INNER JOIN location ON located_in.latitude = location.latitude INNER JOIN targets ON targets.targ_id = attacked.targ_id INNER JOIN perpetrators ON perpetrators.perp_id = attacked.perp_id WHERE incident.event_id LIKE '20010911%%' and incident.type = 'Hijacking' ORDER BY incident.event_id ")
  l = []
  l = ['event date', 'Latitude', 'Longitude', 'Suicide attack', 'Deaths', 'Injuries', 'Target', 'Target Affiliation', 'Terrorist Group', 'Terrorist motive', 'Summary']
  
  events = []
  for result in cursor:
    events.append(result)
  cursor.close()
  context = dict(data = events, lists = l)

  return render_template("nine_eleven.html", **context)

@app.route('/okc', methods=['POST', 'GET'])
def okc():
  cursor = g.conn.execute(" select DISTINCT ON (incident.event_id) incident.event_id, suicide_attack, num_killed, num_injured, groupname, dmg_amt, dmg_details, name, affiliation, summary from incident INNER JOIN caused_damage_to ON caused_damage_to.event_id = incident.event_id INNER JOIN property ON caused_damage_to.prop_id = property.prop_id INNER JOIN located_in ON incident.event_id = located_in.event_id INNER JOIN attacked ON incident.event_id = attacked.event_id INNER JOIN location ON located_in.latitude = location.latitude INNER JOIN targets ON targets.targ_id = attacked.targ_id INNER JOIN perpetrators ON perpetrators.perp_id = attacked.perp_id WHERE incident.event_id LIKE '19950419%%' and num_killed = 168 ORDER BY incident.event_id ")
  l = []
  l = ['event date', 'Suicide attack', 'Deaths', 'Injuries', 'Terrorist group', 'Damage', 'Damage details', 'Target', 'Target affiliation', 'Summary']

  events = []
  for result in cursor:
    events.append(result)
  cursor.close()
  context = dict(data = events, lists = l)

  return render_template("okc.html", **context)
 
@app.route('/query', methods=['POST', 'GET'])
def query():
  time = request.form['date']
  s = time + '%%'
  # options = request.form.getlist('options')
  # t = 'event_id'
  # if len(options) > 1:
  #   for i in range(len(options)-1):
  #     t += options[i] + ' , '
  #   t += options[-1]
  #   print(t)
  # #cursor = g.conn.execute('SELECT event_id FROM attacked WHERE attacked_date LIKE %s', s)
  cursor = g.conn.execute('SELECT A.event_id, groupname AS perpetrators, motive, num_perps, T.name AS Victims, nationality, type FROM attacked A, perpetrators P, targets T WHERE A.attack_date LIKE %s AND A.perp_id LIKE P.perp_id AND A.targ_id = T.targ_id', s)

  events = []
  for result in cursor:
    #print(result)
    events.append(result)  
  cursor.close()
  context = dict(data = events)

  return render_template("historical.html", **context)
#  return redirect('/')

@app.route('/login')
def login():
    abort(401)
    this_is_never_executed()


if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using:

        python server.py

    Show the help text using:

        python server.py --help

    """

    HOST, PORT = host, port
    print "running on %s:%d" % (HOST, PORT)
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()
