from dotenv import load_dotenv
import os
import json
from datetime import datetime, timedelta, date, timezone
from dateutil.parser import parse as is_date

# Import namespaces
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.conversations import ConversationAnalysisClient

def main():
    try:
        # Load configuration settings
        load_dotenv()
        ls_prediction_endpoint = os.getenv('LS_CONVERSATIONS_ENDPOINT')
        ls_prediction_key = os.getenv('LS_CONVERSATIONS_KEY')
        
        # Get user input until they enter "quit"
        userText = ''
        while userText.lower() != 'quit':
            userText = input('\nEnter some text ("quit" to stop)\n')
            if userText.lower() != 'quit':
                # Create a client for the Language service model
                client = ConversationAnalysisClient(
                    ls_prediction_endpoint, AzureKeyCredential(ls_prediction_key)
                )
                
                # Call the Language service model to get intent and entities
                cls_project = 'Clock'
                deployment_slot = 'production'
                
                with client:
                    query = userText
                    result = client.analyze_conversation(
                        task={
                            "kind": "Conversation",
                            "analysisInput": {
                                "conversationItem": {
                                    "participantId": "1",
                                    "id": "1",
                                    "modality": "text",
                                    "language": "en",
                                    "text": query
                                },
                                "isLoggingEnabled": False
                            },
                            "parameters": {
                                "projectName": cls_project,
                                "deploymentName": deployment_slot,
                                "verbose": True
                            }
                        }
                    )
                
                top_intent = result["result"]["prediction"]["topIntent"]
                entities = result["result"]["prediction"]["entities"]
                
                print("Top intent:")
                print(f"\tIntent: {top_intent}")
                print(f"\tCategory: {result['result']['prediction']['intents'][0]['category']}")
                print(f"\tConfidence Score: {result['result']['prediction']['intents'][0]['confidenceScore']}\n")
                
                print("Entities:")
                for entity in entities:
                    print(f"\tCategory: {entity['category']}")
                    print(f"\tText: {entity['text']}")
                    print(f"\tConfidence Score: {entity['confidenceScore']}")
                
                print(f"Query: {result['result']['query']}")
                
                # Apply the appropriate action
                if top_intent == 'GetTime':
                    location = 'local'
                    for entity in entities:
                        if entity["category"] == 'Location':
                            location = entity["text"]
                    print(GetTime(location))
                
                elif top_intent == 'GetDay':
                    date_string = date.today().strftime("%m/%d/%Y")
                    for entity in entities:
                        if entity["category"] == 'Date':
                            date_string = entity["text"]
                    print(GetDay(date_string))
                
                elif top_intent == 'GetDate':
                    day = 'today'
                    for entity in entities:
                        if entity["category"] == 'Weekday':
                            day = entity["text"]
                    print(GetDate(day))
                
                else:
                    print('Try asking me for the time, the day, or the date.')
    
    except Exception as ex:
        print(ex)

def GetTime(location):
    time_offsets = {
        'local': 0,
        'london': 0,
        'sydney': 11,
        'new york': -5,
        'nairobi': 3,
        'tokyo': 9,
        'delhi': 5.5
    }
    
    location = location.lower()
    if location in time_offsets:
        time = datetime.now(timezone.utc) + timedelta(hours=time_offsets[location])
        return f"{time.hour}:{time.minute:02d}"
    else:
        return f"I don't know what time it is in {location}"

def GetDate(day):
    weekdays = {
        "monday": 0,
        "tuesday": 1,
        "wednesday": 2,
        "thursday": 3,
        "friday": 4,
        "saturday": 5,
        "sunday": 6
    }
    
    today = date.today()
    day = day.lower()
    
    if day == 'today':
        return today.strftime("%m/%d/%Y")
    elif day in weekdays:
        offset = weekdays[day] - today.weekday()
        return (today + timedelta(days=offset)).strftime("%m/%d/%Y")
    else:
        return 'I can only determine dates for today or named days of the week.'

def GetDay(date_string):
    try:
        date_object = datetime.strptime(date_string, "%m/%d/%Y")
        return date_object.strftime("%A")
    except ValueError:
        return 'Enter a date in MM/DD/YYYY format.'

if __name__ == "__main__":
    main()
