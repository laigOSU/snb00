from flask import Blueprint, request
from google.cloud import datastore
import json
import constants

client = datastore.Client()

bp = Blueprint('boat', __name__, url_prefix='/boats')

@bp.route('/', methods=['POST','GET'])
# def guests_get_post():
def boats_get_post():
    if request.method == 'POST':
        content = request.get_json()
        new_boat = datastore.entity.Entity(key=client.key(constants.boats))
        # print("The url is: ", url)
        new_boat.update({"name": content["name"], 'type': content['type'], 'length': content['length'], 'docked': 'null'})
        client.put(new_boat)
        url = "http://localhost:8080/boats/" + str(new_boat.key.id)
        print("Now the url is: ", url)
        new_boat["live link"] = url
        client.put(new_boat)
        return str(new_boat.key.id)
    elif request.method == 'GET':
        query = client.query(kind=constants.boats)
        results = list(query.fetch())
        for e in results:
            e["id"] = e.key.id
        return json.dumps(results)
    else:
        return 'Method not recognized'

@bp.route('/<id>', methods=['PUT','DELETE','GET'])
def boats_put_delete_get(id):
    if request.method == 'PUT':
        content = request.get_json()
        boat_key = client.key(constants.boats, int(id))
        boat = client.get(key=boat_key)
        boat.update({"name": content["name"], 'type': content['type'], 'length': content['length']})
        client.put(boat)
        return ('',200)
    elif request.method == 'DELETE':
        key = client.key(constants.boats, int(id))
        client.delete(key)
        return ('',200)
    elif request.method == 'GET':
        my_boat_key = client.key(constants.boats, int(id))
        requested_boat = client.get(key=my_boat_key)
        results = json.dumps(requested_boat)
        print("testing query filter")
        query = client.query(kind=constants.boats)
        query.add_filter('name', '=', 'Sea Witch 7')
        queryresults = list(query.fetch())
        # print("The id is", id)
        # url = "live link: http://localhost:8080/boats/" + id
        # output = url + '\n' + results
        return (json.dumps(queryresults))
        # return (output)
    else:
        return 'Method not recognized'
