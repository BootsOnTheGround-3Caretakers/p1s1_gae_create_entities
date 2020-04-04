from __future__ import absolute_import
from __future__ import unicode_literals

import os
import sys
from datetime import datetime

import webapp2
from google.appengine.ext import ndb

cwd = os.getcwd()
sys.path.insert(0, 'includes')
from datavalidation import DataValidation
from GCP_return_codes import FunctionReturnCodes as RC
from task_queue_functions import TaskQueueFunctions
from p1_services import Services, TaskArguments
from p1_global_settings import PostDataRules
from p1_datastores import Datastores
from datastore_functions import DatastoreFunctions as DSF


class CommonPostHandler(DataValidation):
    def post(self):
        task_id = "create-entities:CommonPostHandler:post"
        debug_data = []
        call_result = self.processPushTask()
        debug_data.append(call_result)
        task_results = call_result['task_results']

        params = {}
        for key in self.request.arguments():
            params[key] = self.request.get(key, None)
        task_functions = TaskQueueFunctions()

        if call_result['success'] != RC.success:
            task_functions.logError(
                call_result['success'], task_id, params,
                self.request.get('X-AppEngine-TaskName', None),
                self.request.get('transaction_id', None), call_result['return_msg'], debug_data,
                self.request.get('transaction_user_uid', None)
            )
            task_functions.logTransactionFailed(self.request.get('transaction_id', None), call_result['success'])
            if call_result['success'] < RC.retry_threshold:
                self.response.set_status(500)
            else:
                #any other failure scenario will continue to fail no matter how many times its called.
                self.response.set_status(200)
            return

        # go to the next function
        task_functions = TaskQueueFunctions()
        call_result = task_functions.nextTask(task_id, task_results, params)
        debug_data.append(call_result)
        if call_result['success'] != RC.success:
            task_functions.logError(
                call_result['success'], task_id, params,
                self.request.get('X-AppEngine-TaskName', None),
                self.request.get('transaction_id', None), call_result['return_msg'], debug_data,
                self.request.get('transaction_user_uid', None)
            )
        # </end> go to the next function
        self.response.set_status(200)


class CreateNeed(webapp2.RequestHandler, CommonPostHandler):
    def processPushTask(self):
        task_id = "create-entities:CreateNeed:processPushTask"
        return_msg = task_id + ": "
        debug_data = []
        task_results = {}

        # verify input data
        transaction_id = unicode(self.request.get("transaction_id", ""))
        transaction_user_uid = unicode(self.request.get("transaction_user_uid", ""))
        name = unicode(self.request.get(TaskArguments.s1t1_name, ""))
        requirements = unicode(self.request.get(TaskArguments.s1t1_requirements, "")) or None

        call_result = self.ruleCheck([
            [transaction_id, PostDataRules.required_name],
            [transaction_user_uid, PostDataRules.internal_uid],
            [name, Datastores.needs._rule_need_name],
            [requirements, Datastores.needs._rule_requirements],
        ])
        debug_data.append(call_result)
        if call_result['success'] != RC.success:
            return_msg += "input validation failed"
            return {
                'success': RC.input_validation_failed, 'return_msg': return_msg, 'debug_data': debug_data,
                'task_results': task_results,
            }
        # </end> verify input data

        needs = Datastores.needs()
        needs.need_name = name
        needs.requirements = requirements
        call_result = needs.kput()
        debug_data.append(call_result)
        if call_result['success'] != RC.success:
            return_msg += "failed to write needs to datastore"
            return {
                'success': call_result['success'], 'return_msg': return_msg, 'debug_data': debug_data,
                'task_results': task_results
            }

        task_results['uid'] = call_result['put_result'].id()

        return {'success': RC.success, 'return_msg': return_msg, 'debug_data': debug_data, 'task_results': task_results}


class CreateHashtag(webapp2.RequestHandler, CommonPostHandler):
    def processPushTask(self):
        task_id = "create-entities:CreateHashtag:processPushTask"
        return_msg = task_id + ": "
        debug_data = []
        task_results = {}

        # verify input data
        transaction_id = unicode(self.request.get("transaction_id", ""))
        transaction_user_uid = unicode(self.request.get("transaction_user_uid", ""))
        name = unicode(self.request.get(TaskArguments.s1t2_name, ""))
        description = unicode(self.request.get(TaskArguments.s1t2_description, "")) or None

        call_result = self.ruleCheck([
            [transaction_id, PostDataRules.required_name],
            [transaction_user_uid, PostDataRules.internal_uid],
            [name, Datastores.hashtags._rule_name],
            [description, Datastores.hashtags._rule_description],
        ])
        debug_data.append(call_result)
        if call_result['success'] != RC.success:
            return_msg += "input validation failed"
            return {
                'success': RC.input_validation_failed, 'return_msg': return_msg, 'debug_data': debug_data,
                'task_results': task_results,
            }
        # </end> verify input data

        hashtag = Datastores.hashtags()
        hashtag.name = name
        hashtag.description = description
        call_result = hashtag.kput()
        debug_data.append(call_result)
        if call_result['success'] != RC.success:
            return_msg += "failed to write hashtag to datastore"
            return {
                'success': call_result['success'], 'return_msg': return_msg, 'debug_data': debug_data,
                'task_results': task_results
            }

        task_results['uid'] = call_result['put_result'].id()

        return {'success': RC.success, 'return_msg': return_msg, 'debug_data': debug_data, 'task_results': task_results}


class CreateNeeder(webapp2.RequestHandler, CommonPostHandler):
    def processPushTask(self):
        task_id = "create-entities:CreateNeeder:processPushTask"
        return_msg = task_id + ": "
        debug_data = []
        task_results = {}

        # verify input data
        transaction_id = unicode(self.request.get("transaction_id", ""))
        transaction_user_uid = unicode(self.request.get("transaction_user_uid", ""))
        user_uid = unicode(self.request.get(TaskArguments.s1t3_user_uid, ""))

        call_result = self.ruleCheck([
            [transaction_id, PostDataRules.required_name],
            [transaction_user_uid, PostDataRules.internal_uid],
            [user_uid, PostDataRules.required_name],
        ])
        debug_data.append(call_result)
        if call_result['success'] != RC.success:
            return_msg += "input validation failed"
            return {
                'success': RC.input_validation_failed, 'return_msg': return_msg, 'debug_data': debug_data,
                'task_results': task_results,
            }

        try:
            existings_keys = [
                ndb.Key(Datastores.users._get_kind(), long(user_uid)),
            ]
        except Exception as exc:
            return_msg += str(exc)
            return {
                'success': RC.input_validation_failed, 'return_msg': return_msg, 'debug_data': debug_data,
                'task_results': task_results,
            }

        for existing_key in existings_keys:
            call_result = DSF.kget(existing_key)
            debug_data.append(call_result)
            if call_result['success'] != RC.success:
                return_msg += "Datastore access failed"
                return {
                    'success': RC.datastore_failure, 'return_msg': return_msg, 'debug_data': debug_data,
                    'task_results': task_results,
                }
            if not call_result['get_result']:
                return_msg += "{} not found".format(existing_key.kind())
                return {
                    'success': RC.input_validation_failed, 'return_msg': return_msg, 'debug_data': debug_data,
                    'task_results': task_results,
                }
        # </end> verify input data

        parent_key = ndb.Key(Datastores.users._get_kind(), long(user_uid))
        needer = Datastores.needer(parent=parent_key)
        needer.user_uid = user_uid
        call_result = needer.kput()
        debug_data.append(call_result)
        if call_result['success'] != RC.success:
            return_msg += "failed to write needer to datastore"
            return {
                'success': call_result['success'], 'return_msg': return_msg, 'debug_data': debug_data,
                'task_results': task_results
            }

        task_results['uid'] = call_result['put_result'].id()

        return {'success': RC.success, 'return_msg': return_msg, 'debug_data': debug_data, 'task_results': task_results}


class CreateUser(webapp2.RequestHandler, CommonPostHandler):
    def processPushTask(self):
        task_id = "create-entities:CreateUser:processPushTask"
        return_msg = task_id + ": "
        debug_data = []
        task_results = {}

        # verify input data
        transaction_id = unicode(self.request.get("transaction_id", ""))
        transaction_user_uid = unicode(self.request.get("transaction_user_uid", ""))
        email_address = unicode(self.request.get(TaskArguments.s1t4_email_address, "")) or None
        firebase_uid = unicode(self.request.get(TaskArguments.s1t4_firebase_uid, "")) or None
        first_name = unicode(self.request.get(TaskArguments.s1t4_first_name, ""))
        last_name = unicode(self.request.get(TaskArguments.s1t4_last_name, ""))
        phone_number = unicode(self.request.get(TaskArguments.s1t4_phone_number, "")) or None
        country_uid = unicode(self.request.get(TaskArguments.s1t4_country_uid, "")) or None
        region_uid = unicode(self.request.get(TaskArguments.s1t4_region_uid, "")) or None
        area_uid = unicode(self.request.get(TaskArguments.s1t4_area_uid, "")) or None
        description = unicode(self.request.get(TaskArguments.s1t4_description, "")) or None
        preferred_radius = unicode(self.request.get(TaskArguments.s1t4_preferred_radius, "")) or None
        account_flags = unicode(self.request.get(TaskArguments.s1t4_account_flags, "")) or None
        location_coords = unicode(self.request.get(TaskArguments.s1t4_location_coords, "")) or None

        call_result = self.ruleCheck([
            [transaction_id, PostDataRules.required_name],
            [transaction_user_uid, PostDataRules.internal_uid],
            [email_address, Datastores.users._rule_email_address],
            [firebase_uid, Datastores.users._rule_firebase_uid],
            [first_name, Datastores.users._rule_first_name],
            [last_name, Datastores.users._rule_last_name],
            [phone_number, Datastores.users._rule_phone_1],
            [country_uid, Datastores.users._rule_country_uid],
            [region_uid, Datastores.users._rule_region_uid],
            [area_uid, Datastores.users._rule_area_uid],
            [description, Datastores.users._rule_description],
            [preferred_radius, Datastores.users._rule_preferred_radius],
            [account_flags, Datastores.users._rule_account_flags],
            [location_coords, Datastores.users._rule_location_cords],
        ])
        debug_data.append(call_result)
        if call_result['success'] != RC.success:
            return_msg += "input validation failed"
            return {
                'success': RC.input_validation_failed, 'return_msg': return_msg, 'debug_data': debug_data,
                'task_results': task_results,
            }

        existing_keys = []
        if country_uid:
            existing_keys.append(ndb.Key(Datastores.country_codes._get_kind(), country_uid))

            if region_uid:
                existing_keys.append(ndb.Key(
                    Datastores.country_codes._get_kind(), country_uid,
                    Datastores.region_codes._get_kind(), region_uid,
                ))

                if area_uid:
                    existing_keys.append(ndb.Key(
                        Datastores.country_codes._get_kind(), country_uid,
                        Datastores.region_codes._get_kind(), region_uid,
                        Datastores.area_codes._get_kind(), area_uid,
                    ))

        for existing_key in existing_keys:
            call_result = DSF.kget(existing_key)
            debug_data.append(call_result)
            if call_result['success'] != RC.success:
                return_msg += "Datastore access failed"
                return {
                    'success': RC.datastore_failure, 'return_msg': return_msg, 'debug_data': debug_data,
                    'task_results': task_results,
                }
            if not call_result['get_result']:
                return_msg += "{} not found".format(existing_key.kind())
                return {
                    'success': RC.input_validation_failed, 'return_msg': return_msg, 'debug_data': debug_data,
                    'task_results': task_results,
                }

        if location_coords:
            try:
                latitude, longitude = [float(val.strip()) for val in location_coords.split(",", 1)]
            except Exception as exc:
                return_msg += str(exc)
                return {
                    'success': RC.input_validation_failed, 'return_msg': return_msg, 'debug_data': debug_data,
                    'task_results': task_results,
                }

            if not ((-90 <= latitude <= 90) and (-180 <= longitude <= 180)):
                return_msg += "latitude value must be [-90, 90], longitude value must be [-180, 180]"
                return {
                    'success': RC.input_validation_failed, 'return_msg': return_msg, 'debug_data': debug_data,
                    'task_results': task_results,
                }
        # </end> verify input data

        # make sure no existing user uses the same phone
        if phone_number:
            query = Datastores.users.query(Datastores.users.phone_1 == phone_number)
            call_result = DSF.kfetch(query)
            if call_result['success'] != RC.success:
                return_msg += "fetch of users failed"
                return {
                    'success': call_result['success'], 'return_msg': return_msg, 'debug_data': debug_data,
                    'task_results': task_results
                }
            users = call_result['fetch_result']
            if users:
                return_msg += "Phone number already registered on an existing user."
                return {
                    'success': RC.input_validation_failed, 'return_msg': return_msg, 'debug_data': debug_data,
                    'task_results': task_results
                }
        # </end> make sure no existing user uses the same phone

        user = Datastores.users()
        user.email_address = email_address
        user.firebase_uid = firebase_uid
        user.first_name = first_name
        user.last_name = last_name
        user.phone_1 = phone_number
        user.country_uid = country_uid
        user.region_uid = country_uid and region_uid
        user.area_uid = country_uid and region_uid and area_uid
        user.description = description
        user.preferred_radius = preferred_radius
        user.account_flags = account_flags
        if location_coords:
            user.location_cords = ndb.GeoPt(latitude, longitude)
        call_result = user.kput()
        debug_data.append(call_result)
        if call_result['success'] != RC.success:
            return_msg += "failed to write user to datastore"
            return {
                'success': call_result['success'], 'return_msg': return_msg, 'debug_data': debug_data,
                'task_results': task_results
            }

        task_results['uid'] = call_result['put_result'].id()

        return {'success': RC.success, 'return_msg': return_msg, 'debug_data': debug_data, 'task_results': task_results}


class CreateCluster(webapp2.RequestHandler, CommonPostHandler):
    def processPushTask(self):
        task_id = "create-entities:CreateCluster:processPushTask"
        return_msg = task_id + ": "
        debug_data = []
        task_results = {}

        # verify input data
        transaction_id = unicode(self.request.get("transaction_id", ""))
        transaction_user_uid = unicode(self.request.get("transaction_user_uid", ""))
        user_uid = unicode(self.request.get(TaskArguments.s1t5_user_uid, ""))
        expiration_date = unicode(self.request.get(TaskArguments.s1t5_expiration_date, "")) or None
        needer_uid = unicode(self.request.get(TaskArguments.s1t5_needer_uid, ""))

        call_result = self.ruleCheck([
            [transaction_id, PostDataRules.required_name],
            [transaction_user_uid, PostDataRules.internal_uid],
            [user_uid, Datastores.cluster._rule_user_uid],
            [expiration_date, PostDataRules.positive_number],
            [needer_uid, Datastores.cluster._rule_needer_uid],
        ])
        debug_data.append(call_result)
        if call_result['success'] != RC.success:
            return_msg += "input validation failed"
            return {
                'success': RC.input_validation_failed, 'return_msg': return_msg, 'debug_data': debug_data,
                'task_results': task_results,
            }

        try:
            existings_keys = [
                ndb.Key(Datastores.users._get_kind(), long(user_uid)),
                ndb.Key(Datastores.users._get_kind(), long(user_uid), Datastores.needer._get_kind(), long(needer_uid)),
            ]
        except Exception as exc:
            return_msg += str(exc)
            return {
                'success': RC.input_validation_failed, 'return_msg': return_msg, 'debug_data': debug_data,
                'task_results': task_results,
            }

        for existing_key in existings_keys:
            call_result = DSF.kget(existing_key)
            debug_data.append(call_result)
            if call_result['success'] != RC.success:
                return_msg += "Datastore access failed"
                return {
                    'success': RC.datastore_failure, 'return_msg': return_msg, 'debug_data': debug_data,
                    'task_results': task_results,
                }
            if not call_result['get_result']:
                return_msg += "{} not found".format(existing_key.kind())
                return {
                    'success': RC.input_validation_failed, 'return_msg': return_msg, 'debug_data': debug_data,
                    'task_results': task_results,
                }
        # </end> verify input data

        cluster = Datastores.cluster()
        cluster.user_uid = user_uid
        cluster.expiration_date = datetime.fromtimestamp(int(expiration_date))
        cluster.needer_uid = needer_uid
        call_result = cluster.kput()
        debug_data.append(call_result)
        if call_result['success'] != RC.success:
            return_msg += "failed to write cluster to datastore"
            return {
                'success': call_result['success'], 'return_msg': return_msg, 'debug_data': debug_data,
                'task_results': task_results
            }

        cluster_uid = call_result['put_result'].id()
        task_results['uid'] = cluster_uid

        user_key = ndb.Key(Datastores.users._get_kind(), long(user_uid))
        cluster_pointer = Datastores.cluster_pointer(parent=user_key)
        cluster_pointer.cluster_uid = cluster_uid
        call_result = cluster_pointer.kput()
        debug_data.append(call_result)
        if call_result['success'] != RC.success:
            return_msg += "failed to write cluster_pointer to datastore"
            return {
                'success': call_result['success'], 'return_msg': return_msg, 'debug_data': debug_data,
                'task_results': task_results
            }

        cluster_key = ndb.Key(Datastores.cluster._get_kind(), cluster_uid)
        cluster_joins = Datastores.cluster_joins(id="{}|{}".format(user_uid, cluster_uid), parent=cluster_key)
        cluster_joins.user_uid = user_uid
        cluster_joins.cluster_uid = unicode(cluster_uid)
        cluster_joins.roles = "needer"
        cluster_joins.kput()
        debug_data.append(call_result)
        if call_result['success'] != RC.success:
            return_msg += "failed to write cluster_joins to datastore"
            return {
                'success': call_result['success'], 'return_msg': return_msg, 'debug_data': debug_data,
                'task_results': task_results
            }

        return {'success': RC.success, 'return_msg': return_msg, 'debug_data': debug_data, 'task_results': task_results}


class CreateCaretakerSkill(webapp2.RequestHandler, CommonPostHandler):
    def processPushTask(self):
        task_id = "create-entities:CreateCaretaker:processPushTask"
        return_msg = task_id + ": "
        debug_data = []
        task_results = {}

        # verify input data
        transaction_id = unicode(self.request.get("transaction_id", ""))
        transaction_user_uid = unicode(self.request.get("transaction_user_uid", ""))
        skill_name = unicode(self.request.get(TaskArguments.s1t6_name, ""))
        description = unicode(self.request.get(TaskArguments.s1t6_description, "")) or None
        skill_type = unicode(self.request.get(TaskArguments.s1t6_skill_type, ""))
        certs = unicode(self.request.get(TaskArguments.s1t6_certs, "")) or None

        call_result = self.ruleCheck([
            [transaction_id, PostDataRules.required_name],
            [transaction_user_uid, PostDataRules.internal_uid],
            [skill_name, Datastores.caretaker_skills._rule_skill_name],
            [skill_type, Datastores.caretaker_skills._rule_skill_type],
            [description, Datastores.caretaker_skills._rule_description],
        ])
        debug_data.append(call_result)
        if call_result['success'] != RC.success:
            return_msg += "input validation failed"
            return {
                'success': RC.input_validation_failed, 'return_msg': return_msg, 'debug_data': debug_data,
                'task_results': task_results,
            }
        # </end> verify input data

        skill = Datastores.caretaker_skills()
        skill.skill_name = skill_name
        skill.skill_type = skill_type
        skill.description = description
        call_result = skill.kput()
        debug_data.append(call_result)
        if call_result['success'] != RC.success:
            return_msg += "failed to write cluster to datastore"
            return {
                'success': call_result['success'], 'return_msg': return_msg, 'debug_data': debug_data,
                'task_results': task_results
            }

        task_results['uid'] = call_result['put_result'].id()

        return {'success': RC.success, 'return_msg': return_msg, 'debug_data': debug_data, 'task_results': task_results}


app = webapp2.WSGIApplication([
    (Services.create_entities.create_need.url, CreateNeed),
    (Services.create_entities.create_hashtag.url, CreateHashtag),
    (Services.create_entities.create_needer.url, CreateNeeder),
    (Services.create_entities.create_user.url, CreateUser),
    (Services.create_entities.create_cluster.url, CreateCluster),
    (Services.create_entities.create_caretaker_skill.url, CreateCaretakerSkill),
], debug=True)
