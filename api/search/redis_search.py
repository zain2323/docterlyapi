from flask import jsonify, Blueprint
import redis
from redis.commands.json.path import Path
import json

class RedisSearchApi:
    
    def __init__(self, client, app=None):
        self.client = client
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.bp = Blueprint('redissearch', __name__)
    
    def add(self, model):
        payload = {}
        for field in model.__searchable__:
            payload[field] = str(getattr(model, field))
        return payload
    
    def parse_data(self, doctor):
        payload = self.add(doctor)
        user = doctor.user
        payload["user"] = self.add(user)
        payload["specializations"] = doctor.get_specializations_info()
        payload["qualifications"] = doctor.get_qualifications_info()
        slots = doctor.slots
        response = []
        for slot in slots:
            response.append(self.add(slot))        
        payload["slot"] = response
        return payload

    def add_to_index(self,doctor):
        payload = self.parse_data(doctor)
        self.client.json().set("doctor:"+ str(doctor.id), Path.root_path(), payload)
        return payload
   
    def search_by_name(self, name):
        query = f"@user_name:({name})"
        documents = self.client.ft("userIdx").search(name).docs
        return self.result_parser(documents)

    def search_by_qualification(self, qualification):
        query = "@qualification_name:{" + qualification + "}"
        documents = self.client.ft("qualificationIdx").search(query).docs
        return self.result_parser(documents)
    
    def search_by_specialization(self, specialization):
        query = f"@specialization_name:({specialization})"
        documents = self.client.ft("specializationIdx").search(query).docs
        return self.result_parser(documents)
        # query = f"""FT.SEARCH specializationIdx '@specialization_name:({specialization})'"""
        # return self.client.execute_command(query)[1:] 

    def search_by_day(self, day):
        query = "@day:{" + day + "}"
        documents = self.client.ft("slotIdx").search(query).docs
        return self.result_parser(documents)
        # query = f"""FT.SEARCH slotIdx @day:{day}"""
        # return self.client.execute_command(query)[1:]
    
    def result_parser(self, documents):
        response = []
        for document in documents:
            response.append(json.loads(document.json))
        return response