import json
import os

# from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from openai import OpenAI


# some new posts that can be added to the response
NEW_POSTS = [
    {
        "id": "571775f3-2564-4cf5-b01c-f4cb6bab461b",
        "url": "https://reddit.com/r/PRCExample/comments/1f33ead/example_to_insert",
    },
    {
        "id": "1fcbb164-f81f-4532-b068-2561941d0f63",
        "url": "https://reddit.com/r/PRCExample/comments/ef56a23/another_example_to_insert",
    },
]


# fLoad environment variables
file = open("/etc/secrets/api_key.txt", "r")
API_TOKEN = file.read()
file.close()

# load_dotenv()  # if a .env file exists, load environment variables from it
client = OpenAI(api_key=API_TOKEN)
app = Flask(__name__)
CORS(app)

# Home
@app.route("/")
def home():
    return '''This is the take of team Unity-Feed on PRC:

Thesis:
Hope is the strongest antidote to radicalization. 

Without hope, peace is not possible.

The shift we are measuring: Can we make people more hopeful? 

Hypothesis: Yes, by displaying content that showcases unity and coexistence.

Prior evidence to suggest this: My friends and family who became jaded since the war broke out on 10/7 have said my Unity Club gives them hope. Other members in Unity Club have shared the same feedback. 

We will start with Palestine/Israelfocus and broaden it if we do notsee the variables shift.'''

def generate_rankings(items):
    prompt = ""
    for i, item in enumerate(items):
        prompt += f"ITEM: {i}:\n{item['text']}\n\n"

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": 'You are a helpful assistant that processes text and returns results in JSON format. Reorder the items you are given in terms of their positivity, with the most positive item first, and include your reasoning. Give me a JSON array in the following format: [ {"item_idx": int, "reason": str} ]. Kindly use the following as a guide for categorization of text concerning Palestine and Israel: A one-sided, Palestinian(s) view that only mentions Israel govt and/or people in a negative light should be considered as negative. A one-sided, Palestinian(s) view with no mention of Israeli govt and/or people should be considered as neutral. A one-sided, Israeli(s) view with no mention of Palestinian govt and/or people should be considered as neutral. A one-sided, Israeli(s) view which only mentions Palestinian govt and/or people in a negative light should be considered as negative. Palestinians and Israelis focusing on overcoming division should be considered as positive',
            },
            {
                "role": "user",
                "content": "ITEM 0:\nI love you.\n\nITEM 1:\nI hate you.\n\nITEM 2:\nI am indifferent to you.\nITEM 3:\nI like soup\n\n",
            },
            {
                "role": "assistant",
                "content": '[ {"item_idx": 0, "reason": "The statement is very positive."}, {"item_idx": 3, "reason": "The statement is somewhat positive."}, {"item_idx": 2, "reason": "The statement is neutral."}, {"item_idx": 1, "reason": "The statement is negative."} ]',
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )

    json_results = response.choices[0].message.content.strip()

    # From the docs
    # Warning: Be cautious when parsing JSON data from untrusted sources. A malicious JSON string may cause the decoder to
    # consume considerable CPU and memory resources. Limiting the size of data to be parsed is recommended.
    results = json.loads(json_results)

    indices = [item["item_idx"] for item in results]
    rankings = [items[i]["id"] for i in indices]

    return rankings

# FOR TESTING 
@app.route("/test", methods = ["POST", "GET"])
def homerun():
    import time
    from pprint import pprint
    
    import requests
    
    # import sample_data
    
    # This is a simple script that sends a POST request to the API and prints the response.
    # Your server should be running on localhost:5001
    
    # Sample data containing multiple text items
    
    CHATGPT_EXAMPLE = {
        "session": {
            "user_id": "193a9e01-8849-4e1f-a42a-a859fa7f2ad3",
            "user_name_hash": "6511c5688bbb87798128695a283411a26da532df06e6e931a53416e379ddda0e",
            "current_time": "2024-01-20 18:41:20",
        },
        "items": [
            {
                "id": "de83fc78-d648-444e-b20d-853bf05e4f0e",
                "title": "this is the post title, available only on reddit",
                "text": "this is the worst thing I have ever seen!",
                "author_name_hash": "60b46b7370f80735a06b7aa8c4eb6bd588440816b086d5ef7355cf202a118305",
                "type": "post",
                "platform": "reddit",
                "created_at": "2023-12-06 17:02:11",
                "enagements": {"upvote": 34, "downvote": 27},
            },
            {
                "id": "s5ad13266-8abk4-5219-kre5-2811022l7e43dv",
                "post_id": "de83fc78-d648-444e-b20d-853bf05e4f0e",
                "parent_id": "",
                "text": "this is amazing!",
                "author_name_hash": "60b46b7370f80735a06b7aa8c4eb6bd588440816b086d5ef7355cf202a118305",
                "type": "comment",
                "platform": "reddit",
                "created_at": "2023-12-08 11:32:12",
                "enagements": {"upvote": 15, "downvote": 2},
            },
            {
                "id": "a4c08177-8db2-4507-acc1-1298220be98d",
                "post_id": "de83fc78-d648-444e-b20d-853bf05e4f0e",
                "parent_id": "s5ad13266-8abk4-5219-kre5-2811022l7e43dv",
                "text": "this thing is ok.",
                "author_name_hash": "60b46b7370f80735a06b7aa8c4eb6bd588440816b086d5ef7355cf202a118305",
                "type": "comment",
                "platform": "reddit",
                "created_at": "2023-12-08 11:35:00",
                "enagements": {"upvote": 3, "downvote": 5},
            },
        ],
    }
    # http://chitimbwasc.pythonanywhere.com/
    # https://ranking-challenge-unity-feed.onrender.com/rank1
    
    # Wait for the Flask app to start up
    time.sleep(2)
    
    # Send POST request to the API
    
    headers = {"Content-Type": "application/json; charset=utf-8"}
    
    # response = requests.post("http://localhost:5001/rank", json=CHATGPT_EXAMPLE)
    response = requests.post("http://ranking-challenge-unity-feed.onrender.com/rank", headers=headers, json=CHATGPT_EXAMPLE)
    
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        try:
            # Attempt to parse the JSON response
            json_response = response.json()
            # pprint(json_response)
            return json_response
        except requests.exceptions.JSONDecodeError:
            # print("Failed to parse JSON response. Response may be empty.")
            return "Failed to parse JSON response. Response may be empty."
    else:
        # print(f"Request failed with status code: {response.status_code}")
        # print(response.text)
        return response.text
    
    return 'home again'

@app.route("/rank", methods=["POST"])  # Allow POST requests for this endpoint
def rank_items():
    # post_data = request.json  # Original statement
    post_data = request.get_json()  # Added this statement
    
    items = post_data.get("items")

    ranked_ids = generate_rankings(items)

    # Add new posts (not part of the candidate set) to the top of the result
    ranked_ids = [new_post["id"] for new_post in NEW_POSTS] + ranked_ids

    result = {
        "ranked_ids": ranked_ids,
        "new_items": NEW_POSTS,
    }

    return jsonify(result)


if __name__ == "__main__":
    app.run()
