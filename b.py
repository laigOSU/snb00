from flask import Blueprint, request
from google.cloud import datastore
import json
import constants

client = datastore.Client()

bp = Blueprint('boat', __name__, url_prefix='/boats')

@bp.route('/', methods=['POST','GET'])
def boats_get_post():
    #---- POST: CREATE A NEW BOAT ----#
    if request.method == 'POST':
        content = request.get_json()
        new_boat = datastore.entity.Entity(key=client.key(constants.boats))
        new_boat.update({"name": content["name"], 'type': content['type'], 'length': content['length']})
        client.put(new_boat)
        boat_id = str(new_boat.key.id)
        url = constants.appspot_url + constants.boats + "/" + boat_id
        new_boat["boat_url"] = url
        client.put(new_boat)
        return (str(new_boat.key.id), 201)

    #---- GET: VIEW ALL BOATS ----#
    elif request.method == 'GET':
        query = client.query(kind=constants.boats)
        results = list(query.fetch())
        for e in results:
            e["id"] = e.key.id
            # url = "http://localhost:8080/boats/" + str(e.key.id)
            # url = constants.appspot_url + constants.boats + "/" + str(e.key.id)
            # e["boat_url"] =url
        print("Viewing all boats.")
        return json.dumps(results)

    else:
        return 'Method not recognized'

@bp.route('/<id>', methods=['PUT','DELETE','GET'])
def boats_put_delete_get(id):
    #---- PUT: MODIFY A SPECIFIC BOAT ----#
    if request.method == 'PUT':
        content = request.get_json()
        boat_key = client.key(constants.boats, int(id))
        boat = client.get(key=boat_key)
        boat.update({"name": content["name"], 'type': content['type'], 'length': content['length']})
        client.put(boat)
        return ('',200)

    #---- DELETE: REMOVE A SPECIFIC BOAT ----#
    elif request.method == 'DELETE':
        # Get the boat
        boat_key = client.key(constants.boats, int(id))
        boat = client.get(key=boat_key)

        # 1. Check if boat is docked in a slip --> if boat_id == slip["current_boat"]
        # Get that slip
        query = client.query(kind=constants.slips)
        query.add_filter('current_boat', '=', id)
        queryresults = list(query.fetch())
        print("queryresults is: ", queryresults)
        for e in queryresults:
            # print("number is: ", e["number"])
            # print("current_boat is: ", e["current_boat"])
            # print("slip id is: ", e.key.id)
            slip_id = e.key.id

            slip_key = client.key(constants.slips, slip_id)
            slip = client.get(key=slip_key)
            slip["current_boat"] = "null"
            slip["arrival_date"] = "null"
            client.put(slip)

        # 2. Check if boat contains cargo, if so, update each cargo[carrier] to null
        if 'cargo' in boat.keys():
            print("boat[cargo] is: ", boat["cargo"])
            print("type of boat[cargo] is: ", type(boat["cargo"]))
            for i in boat["cargo"]:
                print("i is: ", i)
                print("i[id] is: ", i["id"])
                print("i[cargo_url] is: ", i["cargo_url"])
                cargo_id = i["id"]
                cargo_key = client.key(constants.cargos, int(cargo_id))
                cargo = client.get(key=cargo_key)
                print("before update cargo[carrier]")
                print("cargo[carrier][id] was: ", cargo["carrier"]["id"])
                print("cargo[carrier][name] was: ", cargo["carrier"]["name"])
                print("cargo[carrier][boat_url] was: ", cargo["carrier"]["boat_url"])

                cargo["carrier"]["id"] = "null"
                cargo["carrier"]["name"] = "null"
                cargo["carrier"]["boat_url"] = "null"
                client.put(cargo)
                print("cargo[carrier][id] is now: ", cargo["carrier"]["id"])
                print("cargo[carrier][name] is now: ", cargo["carrier"]["name"])
                print("cargo[carrier][boat_url] is now: ", cargo["carrier"]["boat_url"])

        # 3. Actually delete the boat <-- UNCOMMENT THIS AFTER DEBUG
        client.delete(boat_key)

        return ('',200)

    #---- GET: VIEW A SPECIFIC BOAT ----#
    elif request.method == 'GET':
        query = client.query(kind=constants.boats)
        first_key = client.key(constants.boats,int(id))
        query.key_filter(first_key,'=')
        results = list(query.fetch())
        for e in results:
            e["id"] = id
            # url = "http://localhost:8080/boats/" + id
            # url = constants.appspot_url + constants.boats + "/" + id
            # e["boat_url"] =url
        print("Viewing specific boat #", id)
        return json.dumps(results)

    else:
        return 'Method not recognized'

@bp.route('/<bid>/cargos/<cid>', methods=['PUT','DELETE'])
def add_delete_docking(bid,cid):
    #---- PUT: APPEND A CARGO ONTO THIS BOAT ----#
    if request.method == 'PUT':
        content = request.get_json()
        boat_key = client.key(constants.boats, int(bid))
        boat = client.get(key=boat_key)
        cargo_key = client.key(constants.cargos, int(cid))
        cargo = client.get(key=cargo_key)


        cargo_json = {"id": cargo.id, "cargo_url": cargo["cargo_url"]}

        print("cargo[carrier] is: ",cargo["carrier"])
        print("cargo[carrier][id] is: ", cargo["carrier"]["id"])
        print("cargo[carrier][name] is: ",cargo["carrier"]["name"])
        print("cargo[carrier][boat_url] is: ", cargo["carrier"]["boat_url"])
        print("cargo id passed in is: ", cid)
        print("cargo is: ", cargo)
        print("boat: ", boat)
        print("boat.key.id: ", boat.key.id)
        print("boat[name]: ", boat["name"])
        print("boat[boat_url]: ", boat["boat_url"])

        # A. Check if cargo not yet assigned to any boat
        if cargo["carrier"]["name"] == "null":

            # 1. Update the boat--> boat[cargo] = cid
            print("Cargo not yet assigned to any ship. So append (or add).")

            if 'cargo' in boat.keys():
                boat['cargo'].append(cargo_json)
                print("Appending subsequent cargo to this boat")
            else:
                boat['cargo'] = [cargo_json]
                print("Adding first cargo to this boat.")

            client.put(boat)

            cargo["carrier"]["id"] = boat.key.id
            cargo["carrier"]["name"] = boat["name"]
            cargo["carrier"]["boat_url"] = boat["boat_url"]

            print("After loading cargo: ")
            print("cargo[carrier] is: ",cargo["carrier"])
            print("cargo[carrier][id] is: ", cargo["carrier"]["id"])
            print("cargo[carrier][name] is: ",cargo["carrier"]["name"])
            print("cargo[carrier][boat_url] is: ", cargo["carrier"]["boat_url"])

            client.put(cargo)

            return("Cargo loaded", 200)

        # B. Otherwise, cargo already assigned somewhere, so 403 error.
        else:
            print("Cargo already assigned to a boat, cannot load here.")
            return("Cargo already assigned to a boat.", 403)


    #---- DELETE: REMOVE A SPECIFIC CARGO FROM A BOAT ----#
    if request.method == 'DELETE':
        boat_key = client.key(constants.boats, int(bid))
        boat = client.get(key=boat_key)

        cargo_key = client.key(constants.cargos, int(cid))
        cargo = client.get(key=cargo_key)

        cargo_json = {"id": cargo.id, "cargo_url": cargo["cargo_url"]}

        if 'cargo' in boat.keys():
            # 1. Update the boat[cargo] --> remove cid (cargo_json)
            print("boat[cargo] is: ", boat["cargo"])

            boat['cargo'].remove(cargo_json)
            client.put(boat)

            # 2. Update the cargo[carrier] = null
            cargo["carrier"]["id"] = "null"
            cargo["carrier"]["name"] = "null"
            cargo["carrier"]["boat_url"] = "null"

            client.put(cargo)

        print("Cargo #", cid, "unloaded.")
        return("Cargo removed", 200)
