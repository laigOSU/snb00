from flask import Blueprint, request
from google.cloud import datastore
import json
import constants

client = datastore.Client()

bp = Blueprint('cargo', __name__, url_prefix='/cargos')

@bp.route('/', methods=['POST','GET'])
def cargos_get_post():
    #---- POST: CREATE A NEW CARGO ----#
    if request.method == 'POST':
        content = request.get_json()
        new_cargo = datastore.entity.Entity(key=client.key(constants.cargos))
        new_cargo.update({"weight": content["weight"], 'content': content['content'], 'delivery_date': content['delivery_date']})
        client.put(new_cargo)
        cargo_id = str(new_cargo.key.id)
        url = constants.appspot_url + constants.cargos + "/" + cargo_id
        new_cargo["cargo_url"] = url
        client.put(new_cargo)
        new_cargo["carrier"] = {"id": "null", "name": "null", "boat_url": "null"}
        client.put(new_cargo)
        return (str(new_cargo.key.id), 201)

    #---- GET: VIEW ALL CARGOS ----#
    elif request.method == 'GET':
        query = client.query(kind=constants.cargos)
        results = list(query.fetch())
        for e in results:
            e["id"] = e.key.id
            # url = "http://localhost:8080/cargos/" + str(e.key.id)
            # url = constants.appspot_url + constants.cargos + "/" + str(e.key.id)
            # e["cargo_url"] =url
        return json.dumps(results)

    else:
        return 'Method not recognized'

@bp.route('/<id>', methods=['PUT','DELETE','GET'])
def cargo_put_delete_get(id):
    #---- PUT: MODIFY A SPECIFIC CARGO ----#
    if request.method == 'PUT':
        content = request.get_json()
        cargo_key = client.key(constants.cargos, int(id))
        cargo = client.get(key=cargo_key)
        cargo.update({"weight": content["weight"], 'content': content['content'], 'delivery_date': content['delivery_date']})
        client.put(cargo)
        return ('',200)

    #---- DELETE: REMOVE A SPECIFIC CARGO ----#
    elif request.method == 'DELETE':
        # Get the cargo
        key = client.key(constants.cargos, int(id))

        # # Check if cargo is docked in a slip --> if cargo_id == slip["current_cargo"]
        # # Get that slip
        # query = client.query(kind=constants.slips)
        # query.add_filter('current_cargo', '=', id)
        # queryresults = list(query.fetch())
        # print("queryresults is: ", queryresults)
        # for e in queryresults:
        #     print("number is: ", e["number"])
        #     print("current_cargo is: ", e["current_cargo"])
        #     print("cargo id is: ", e.key.id)
        #     slip_id = e.key.id
        #
        #     slip_key = client.key(constants.slips, slip_id)
        #     slip = client.get(key=slip_key)
        #     slip["current_cargo"] = "null"
        #     slip["arrival_date"] = "null"
        #     client.put(slip)
        client.delete(key)

        return ('',200)

    #---- GET: VIEW A SPECIFIC CARGO ----#
    elif request.method == 'GET':
        query = client.query(kind=constants.cargos)
        cargo_key = client.key(constants.cargos,int(id))
        query.key_filter(cargo_key,'=')
        results = list(query.fetch())
        for e in results:
            e["id"] = id


        # The below is for debugging --------
        cargo_key = client.key(constants.cargos, int(id))
        cargo = client.get(key=cargo_key)
        print("cargo[carrier]: ", cargo["carrier"])
        print("cargo[carrier][name]: ", cargo["carrier"]["name"])
        print("cargo[carrier][id]: ", cargo["carrier"]["id"])
        print("cargo[carrier][boat_url]: ", cargo["carrier"]["boat_url"])
        print("cargo is", cargo)
        # The above is for debugging --------

        return json.dumps(results)


    else:
        return 'Method not recognized'
