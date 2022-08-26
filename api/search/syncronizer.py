from redis_om import get_redis_connection
from api.models import Doctor
import redis
from redis.commands.json.path import Path

class Syncronizer:
    
    def __init__(self, model):
        self.model = model
        self.client = get_redis_connection()
        self.flush()
        self.init_indexes()

    def init_indexes(self):
        doc_idx = """FT.CREATE docIdx ON JSON PREFIX 1 doctor: SCHEMA $.id AS doc_id TEXT """
        user_idx = """
                    FT.CREATE userIdx ON JSON PREFIX 1 doctor: SCHEMA $.user.id AS user_id TEXT
                    $.user.name AS user_name TEXT $.user.email AS user_email TEXT 
                    """
        qualification_idx = """
                            FT.CREATE qualificationIdx ON JSON PREFIX 1 doctor: SCHEMA $.qualifications.qualification_name[*] AS qualification_name TAG"""
        specialization_idx = """
                             FT.CREATE specializationIdx ON JSON PREFIX 1 doctor: SCHEMA $.specializations.id AS specialization_id TEXT
                             $.specializations.name AS specialization_name TEXT   
                             """
        slot_idx = """
                    FT.CREATE slotIdx ON JSON PREFIX 1 doctor: SCHEMA $.slot[0:].day AS day TAG
                   """
        self.client.execute_command(doc_idx) 
        self.client.execute_command(user_idx) 
        self.client.execute_command(qualification_idx) 
        self.client.execute_command(specialization_idx)
        self.client.execute_command(slot_idx)

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
        
    def flush(self):
        self.client.execute_command("FLUSHALL")

    def inspect(self):
        pass

    def sync(self):
        for doctor in self.model:
            self.add_to_index(doctor)
