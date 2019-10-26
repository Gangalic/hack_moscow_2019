import flask
from flask import jsonify, request, Response
import sqlite3
import json

app = flask.Flask(__name__)

# basic API
@app.route('/', methods=['GET'])
def home():
    return "<h1>NBF Team</h1><p>This site is a prototype API for hack moscow.</p>"
    
# method to get the ranking of correctly answered times
@app.route('/api/ranking', methods=['GET'])
def get_correct_ranking():
    conn = sqlite3.connect('ranking.db')
    cur = conn.cursor()
    
    all_ranking = cur.execute('SELECT name, percent FROM ranking;').fetchall()
    
    # sort and transform to json
    all_ranking.sort(key=lambda tup:tup[1], reverse=True)
    json_string = json.dumps(all_ranking)
    
    return Response(json_string,  mimetype='application/json')
    
    
# method to update the ranking
@app.route('/api/update_ranking', methods=['GET'])
def update_ranking():
    conn = sqlite3.connect('ranking.db')
    cur = conn.cursor()
    
    if 'answered' in request.args and 'name' in request.args and 'id' in request.args:
        name = request.args['name']
        pers_id = request.args['id']
        
        # print(";" + name + ";" + pers_id)
        
        # find if it already exists or not
        query = 'select * from ranking where id=' + pers_id + ';';
        entry = cur.execute(query).fetchall()
        
        # print(entry)
        
        # we don't have it yet, so we insert
        if len(entry)==0:
            # check if answered correctly or not
            if request.args['answered'].lower()=='true':
                correct = 1
            
            total = 1
            percent = int(correct/total*100)
        
            query = 'insert into ranking values (' + pers_id \
                + ',\'' + name + '\',' + str(correct) + ',' + str(total) \
                + ',' + str(percent) + ');'
            cur.execute(query)
            conn.commit()
            
        else:
            # check if answered correctly or not
            if request.args['answered'].lower()=='true':
                # get the count and increase by 1
                correct = entry[0][2] + 1
            else:
                correct = entry[0][2]
                
            total = entry[0][3] + 1
            percent = int(correct/total*100)
            
            query = 'update ranking set correct=' + str(correct) \
                + ', total=' + str(total) + ', percent=' + str(percent) \
                + ' where id=' + str(pers_id) + ';'
            
            cur.execute(query)
            conn.commit()
        
    else:
        # tell back about wrong params
        return jsonify("Wrong parameters in request"), 422
        
    return jsonify("Ranking successfully updated"), 200

get_correct_ranking() 
app.run(host='0.0.0.0', port=5000)