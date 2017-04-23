from flask import Flask, request, jsonify, session
from flask_restful import Resource, Api
from watson_developer_cloud import ConversationV1
import requests

conversation = ConversationV1(
    username='b6b2699f-0985-41a3-9c2b-3690df8f125f',
    password='nhawoSB1unoT',
    version='2016-09-20')

workspace_id = '5eead463-b709-45e5-8c08-bf3a517e9321'

content_dict = dict()

matched_number = dict()

app = Flask(__name__)
api = Api(app)


class ChatInterface(Resource):
    def post(self):
        json_content = request.json
        print("request :" + str(json_content))
        user_id = json_content["user_id"]
        print("user_id: " + str(user_id))
        if "cancel" in json_content:
            if json_content["cancel"]:
                content_dict.pop(user_id, None)
                return
        text = json_content["input"]
        if user_id in content_dict:
            response = conversation.message(workspace_id=workspace_id, message_input={'text': text},
                                            context=content_dict[user_id])
        else:
            response = conversation.message(workspace_id=workspace_id, message_input={'text': text})
        context = response["context"]
        content_dict[user_id] = context

        answer_text = response["output"]["text"]
        if "complete" in context and context["complete"]:
            #check if user is ready to start chat
            if "start_chat" in context and context["start_chat"]:
                return jsonify(responds=["START_CHAT"])

            start_location = context["startlocation"]
            end_location = context["targetlocation"]
            date = context["date"]
            time = context["time"]
            r = requests.post("http://localhost:8080/ride_location", json={"user_id": user_id, "start": start_location,
                                                                           "end": end_location, 'date': str(date) + " at "
                                                                                                        + str(time)},
                              headers={"Content-Type": "application/json"})
            if r:
                print("result matching: " + str(r.json()))
                matched_number[user_id] = True
                return r.json()
            else:
                return jsonify(responds=["We have not yet a match"])
        else:
            return jsonify(responds=answer_text)


api.add_resource(ChatInterface, '/chat')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True, threaded=True)
