from __future__ import unicode_literals
import os
import sys
cwd = os.getcwd()
sys.path.insert(0,'../Datavalidation')
from datavalidation import DataValidation


class FirebaseFunctions():
    update = "update"
    delete = "delete"
    append = "append"
    
class FieldObjectTypes():
        organization = "organization"
        user= "user"
        attribute = "attribute"
        object = "object"
        processor = "system"
        email = "email"
        
        
class FieldKeys():

## universal keys
    country_uid = "country_uid"
    region_uid = "region_uid"
    area_uid = "area_uid"
    last_updated = "last_updated"
    description = "description"
    cluster_uid = "cluster_uid"
    needer_uid = "needer_uid"
    deletion_prevention_key = "deletion_prevention_key"

##</end> universal keys    

## user/ keys
    user_first_name = "first_name"
    user_last_name = "last_name"
    user_uid = "user_uid"
    phone_1 ="phone_1"
    phone_2 = "phone_2"
    phone_texts = 'phone_texts'
    user_contact_email = "email_address"
    preferred_radius = "preferred_radius"
    account_flags = "account_flags"
    location_cord_long = "location_cord_long"
    location_cord_lat = "location_cord_lat"
##</end> user/ keys

## cluster keys
    expiration_date = "expiration_date"
##</end> cluster keys


class FirebaseField(DataValidation):
    functions = FirebaseFunctions
    object_types = FieldObjectTypes
    keys = FieldKeys
    
    def __init__(self):
        self.__field = {"id": "", "object type" : "", "function" : "" , "value" : "", "key" : "" }
        #~tracks if a key was manually set instead of selected from FieldKeys class. if this is true validate function does not check key against the class
        self.manual_key_set = False

    def setFieldValues(self,new_id=None,object_type=None,function=None,value=None,key=None):
        return_msg = "FirebaseField:setFieldValues "
        debug_data = []
        if key != None:
            debug_data.append(self.setKey(key))
        
        if object_type != None:
            debug_data.append(self.setObjectType(object_type))
        
        if function != None:
            debug_data.append(self.setFunction(function))

        if value != None:
            debug_data.append(self.setValue(value))
            
        if key != None:
            debug_data.append(self.setKey(key))
            
        if id != None:
            debug_data.append(self.setId(new_id))
        
        for data in debug_data:
            if data['success'] != True:
                return_msg += "setting a value failed. see debug data for details"
                return {'success': False, 'return_msg': return_msg,'debug_data' :debug_data}
            
        return {'success': True, 'return_msg': return_msg,'debug_data' :debug_data}

    
    #~used to set a key that doesn't exist in the FieldKeys class


    def setManualKey(self,new_key=None):
        debug_data = []
        return_msg = "FirebaseField:setManualKey "
        
        
        call_result = self.checkValues([[new_key,True,unicode,"len1"]])
        debug_data.append(call_result)
        if call_result['success'] != True:
            return_msg += "input validation failed"
            return {'success': False, 'return_msg': return_msg,'debug_data' :debug_data}
        
        self.manual_key_set = True
        self.__field["key"] = new_key
        return {'success': True, 'return_msg': return_msg,'debug_data' :debug_data}

        
    def setKey(self,new_key=""):
        debug_data = []
        return_msg = "FirebaseField:setKey "
        key_found_flag = False
        
        #make sure the new key exists in the our keys class
        for key in self.keys.__dict__:
            if self.keys.__dict__[key] == new_key:
                key_found_flag = True
                break
        
        if key_found_flag != True:
            return_msg+= "invalid key %s." % new_key
            return {'success': False, 'return_msg': return_msg,'debug_data' :debug_data}
        
        self.__field["key"] = new_key
        
        return {'success': True, 'return_msg': return_msg,'debug_data' :debug_data}
      
    def setValue(self,new_value=None):
        debug_data = []
        return_msg = "FirebaseField:setValue "
        
        call_result = self.checkValues([[new_value,False,unicode]])
        debug_data.append(call_result)
        if call_result['success'] != True:
            return_msg += "input validation failed"
            return {'success': False, 'return_msg': return_msg,'debug_data' :debug_data}
        
        self.__field["value"] = new_value
        return {'success': True, 'return_msg': return_msg,'debug_data' :debug_data}

    def setFunction(self,new_function=""):
        debug_data = []
        return_msg = "FirebaseField:setFunction "
        function_found_flag = False
        
        #make sure the new function exists in the our functions class
        for key in self.functions.__dict__:
            if self.functions.__dict__[key] == new_function:
                function_found_flag = True
                break
        
        if function_found_flag != True:
            return_msg+= "invalid function %s." % new_function
            return {'success': False, 'return_msg': return_msg,'debug_data' :debug_data}
        
        self.__field["function"] = new_function
        
        return {'success': True, 'return_msg': return_msg,'debug_data' :debug_data}
          
    def setObjectType(self,new_object_type=""):
        debug_data = []
        return_msg = "FirebaseField:setObjectType "
        type_found_flag = False
        
        #make sure the new type exists in the our object types class
        for key in self.object_types.__dict__:
            if self.object_types.__dict__[key] == new_object_type:
                type_found_flag = True
                break
        
        if type_found_flag != True:
            return_msg+= "invalid object type %s." % new_object_type
            return {'success': False, 'return_msg': return_msg,'debug_data' :debug_data}
        
        self.__field['object type'] = new_object_type
        
        return {'success': True, 'return_msg': return_msg,'debug_data' :debug_data}
  
    def setId(self,new_id=None):
        call_result = {}
        debug_data = []
        return_msg = "FirebaseField:setIdToUid "
        
        
        #root is the only non-uid value the id can be
        if type(new_id) == unicode and new_id.lower() == "root":
            self.__field["id"] = "root"
            return {'success': True, 'return_msg': return_msg,'debug_data' :debug_data}
    
        
        call_result = self.checkValues([[new_id,True,unicode,"len1"]])
        debug_data.append(call_result)
        if call_result['success'] != True:
            return_msg += "input validation failed"
            return {'success': False, 'return_msg': return_msg,'debug_data' :debug_data}
        
        self.__field["id"] = new_id
        return {'success': True, 'return_msg': return_msg,'debug_data' :debug_data}
    
    def validate(self):
        debug_data = []
        return_msg = "FirebaseField:validate "
        
        fail_flag = False
        
        if self.__field["id"] == None or self.__field["id"] == "":
            return_msg += " msg:id value isn't set."
            fail_flag = True
        
        if self.__field["object type"] == None or self.__field["object type"] == "":
            return_msg += " msg:object type isn't set."
            fail_flag = True
        
        if self.__field["function"] == None or self.__field["function"] == "":
            return_msg += " msg:function isn't set."
            fail_flag = True
        
        if self.__field["key"] == None or self.__field["key"] == "":
            return_msg += " msg:key isn't set."
            fail_flag = True
        
        if (self.__field["function"] != "delete" and 
            (self.__field["value"] == "" or self.__field["value"] == None)):
            return_msg += " msg:value isn't set."
            fail_flag = True
        
        if fail_flag == False:
            return {'success': True, 'return_msg': return_msg,'debug_data' :debug_data}
        else:
            return {'success': False, 'return_msg': return_msg,'debug_data' :debug_data}
        
    def toDict(self):
        debug_data = []
        return_msg = "FirebaseField:toDict "
        
        call_result = self.validate()
        debug_data.append(call_result)
        if call_result['success'] != True:
            return_msg += "validation of values inside class failed see debug data"                
            return {'success': False, 'return_msg': return_msg,'debug_data' :debug_data, 'field': {}}
        
        return {'success': True, 'return_msg': return_msg,'debug_data' :debug_data,'field':self.__field}
        
        
        
    