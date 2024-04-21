import json
import os

# from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from openai import OpenAI


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


@app.route("/rank", methods=["POST"])  # Allow POST requests for this endpoint
def rank_items():
    # post_data = request.json  # Original statement
    post_data = request.get_json()  # Added this statement
    
    items = post_data.get("items")

    ranked_ids = generate_rankings(items)

    # Add new posts (not part of the candidate set) to the top of the result
    # ranked_ids = [new_post["id"] for new_post in NEW_POSTS] + ranked_ids

    result = {
        "ranked_ids": ranked_ids
    }

    return jsonify(result)


if __name__ == "__main__":
    app.run()
