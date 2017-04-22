from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from pymongo import MongoClient, GEO2D
from geopy.geocoders import Nominatim
from geopy.distance import vincenty
from bson.son import SON


app = Flask(__name__)
api = Api(app)
geolocator = Nominatim()

db = MongoClient('localhost', 27017).geo_example
db.places.create_index([("loc", GEO2D)])


class GeoDB():
    distance = 20  # 20 km distance

    @staticmethod
    def insert(user_id, start_location, end_location, date):
        result = db.places.insert_one({"loc": [start_location.latitude, start_location.longitude], "user_id": user_id,
                                       "loc_end": [end_location.latitude, end_location.longitude], "date": date})
        print("inserted in db: " + str(result))

    @staticmethod
    def match(lat, lon):
        degree_distance = GeoDB.distance / 111.12
        result = db.places.find({"loc": SON([("$near", [lat, lon]), ("$maxDistance", degree_distance)])})

        return result

    @staticmethod
    def findRides(user_id, start_location, end_location, date):
        possible_set = GeoDB.match(start_location.latitude, start_location.longitude)
        possible_result = []
        for item in possible_set:
            print("possible result: " + str(item))
            if item["user_id"] != user_id:
                ride_end_location = (item["loc_end"][0], item["loc_end"][1])
                if vincenty(ride_end_location, (end_location.latitude, end_location.longitude)).kilometers < GeoDB.distance:
                    possible_result.append(item)
                    print("result: " + str(item))
        if possible_result:
            res = possible_result[0]
            return jsonify(date=res["date"], user_id=res["user_id"])
        else:
            return




class DataInterface(Resource):

    def post(self):
        json_content = request.json
        print(json_content)
        user_id = json_content["user_id"]
        date = json_content["date"]
        start_location = geolocator.geocode(json_content["start"])
        end_location = geolocator.geocode(json_content["end"])
        GeoDB.insert(user_id, start_location, end_location, date)


        matching_result = GeoDB.findRides(user_id, start_location, end_location, date)
        if matching_result:
            return matching_result

        return



api.add_resource(DataInterface, '/ride_location')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
