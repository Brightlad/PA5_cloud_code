import urllib2
import json
import os
import sys
import pymysql
import boto3
import logging

#ENCRYPTED_EXPECTED_TOKEN = os.environ['kmsEncryptedToken']

#kms = boto3.client('kms')
#expected_token = kms.decrypt(CiphertextBlob=b64decode(ENCRYPTED_EXPECTED_TOKEN))['Plaintext']

conn = pymysql.connect(host = 'uvaclasses.martyhumphrey.info',
                       port = 3306,
                       user = 'UVAClasses',
                       passwd ='TalkingHeads12',
                       db = 'uvaclasses')

cur = conn.cursor()

#API_BASE="http://bartjsonapi.elasticbeanstalk.com/api"

def lambda_handler(event, context):
    if (event["session"]["application"]["applicationId"] !=
            "amzn1.ask.skill.64f29c4e-8e45-48bb-9992-db125e34fe0d"):
        raise ValueError("Invalid Application ID")
    
    if event["session"]["new"]:
        on_session_started({"requestId": event["request"]["requestId"]}, event["session"])

    if event["request"]["type"] == "LaunchRequest":
        return on_launch(event["request"], event["session"])
    elif event["request"]["type"] == "IntentRequest":
        return on_intent(event["request"], event["session"])
    elif event["request"]["type"] == "SessionEndedRequest":
        return on_session_ended(event["request"], event["session"])


def on_session_started(session_started_request, session):
    print "Starting new session."

def on_launch(launch_request, session):
    return get_welcome_response()

def on_intent(intent_request, session):
    intent = intent_request["intent"]
    intent_name = intent_request["intent"]["name"]
    #print intent
    if intent_name == "GetSeats":
        return get_seats_open(intent)
    elif intent_name == "GetCourse":
        return get_class_info(intent)
    elif intent_name == "GetTeacher":
        return get_teacher_info(intent)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")

def on_session_ended(session_ended_request, session):
    print "Ending session."

def handle_session_end_request():
    card_title = "Tommy - Thanks"
    speech_output = "Thank you for using the Thomas scheduling skill.  Hope to see you again soon!"
    should_end_session = True

    return build_response({}, build_speechlet_response(card_title, speech_output, None, should_end_session))

def get_welcome_response():
    session_attributes = {}
    card_title = "Thomas"
    speech_output = "Welcome to the Alexa Thomas scheduling skill. " \
                    "You can ask me about what classes are offered in the," \
                    "upcoming semester and how many seats are open."
    reprompt_text = "Please ask me about classes for next semester, " \
                    "for example CS 21 50."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_seats_open(intent):
    class_num = intent['slots']['coursenum']['value']
    session_attributes = {}
    card_title = "Tommy Seats Open"
    reprompt_text = ""
    should_end_session = False
    n = 0
    open_seats = ''
    
    cur.execute("SELECT Section, EnrollmentLimit - Enrollment FROM CS1188Data WHERE Number = '" + class_num + "'")

    for row in cur:
        section = row[0]
        seats = row[1]
        open_seats += "Section " + str(row[0]) + " has " + str(row[1]) + " seats avaliable. "
        

    speech_output =  open_seats #"There are currently " + str(n) + " total seats available for this class."
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_teacher_info(intent):
    class_num = intent['slots']['coursenum']['value']
    session_attributes = {}
    card_title = "Tommy Teacher Information"
    reprompt_text = ""
    should_end_session = False
    profs = ''

    cur.execute("SELECT DISTINCT Instructor FROM CS1188Data WHERE Number = '" + class_num +"'") 
    for row in cur:
        profs += (row[0] + ", ")

    speech_output = "Professors " + profs +" teach this class. " 

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_class_info(intent):
    class_num = intent['slots']['coursenum']['value']
    session_attributes = {}
    card_title = "Tommy Class Information"
    speech_output = "Please ask me about classes based on a class number. For example twenty one fifty."
    reprompt_text = ""
    should_end_session = False
    title = ''
    
    cur.execute("SELECT DISTINCT Title FROM CS1188Data WHERE Number = '" + class_num + "'")
    for row in cur:
        title += row[0] + ", " 

    speech_output = "The title for this class is " + title + "." 

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        "outputSpeech": {
            "type": "PlainText",
            "text": output
        },
        "card": {
            "type": "Simple",
            "title": title,
            "content": output
        },
        "reprompt": {
            "outputSpeech": {
                "type": "PlainText",
                "text": reprompt_text
            }
        },
        "shouldEndSession": should_end_session
    }

def build_response(session_attributes, speechlet_response):
    return {
        "version": "1.0",
        "sessionAttributes": session_attributes,
        "response": speechlet_response
    }

