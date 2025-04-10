
'''
    Super light-weight Flask webserver.
'''

from flask import Flask, render_template, request, jsonify
from llm import initalise_client, fetch_chatbot_response
from gdb import insert_review, fetch_data, fetch_recent_reviews
from system_prompt import SYSTEM_PROMPT

import json 

# Initialise bits.
app = Flask(__name__)
client, model_name = initalise_client()


@app.route('/', methods=['GET', 'POST'])
def index():

    ''' Render main page to query LLM. '''

    # Fetch most recent reviews from the gdb.
    recent_reviews = fetch_recent_reviews(5)

    # Initialise variable to store user review into memory. 
    user_sentiment = None

    # Once user submits form.
    if request.method == 'POST':
        
        # Store user feedback in memory. 
        user_feedback = request.form.get('user_feedback')

        if user_feedback:
            
            # Append user feedback to messages.
            messages = [
                {
                    'role' : 'user',
                    'content' : str(user_feedback)
                }
            ]

            # Fetch user sentiment from the model.
            user_sentiment = fetch_chatbot_response(
                client=client,
                model_name=model_name,
                messages=messages,
                system_prompt=SYSTEM_PROMPT
            )

            # Convert str output into JSON.
            sentiment_data = json.loads(user_sentiment)

            ### okay -> print(sentiment_data)

            if sentiment_data:
                # Insert model output into graph database. 
                insert_review(sentiment_data)

    # Render webpage. 
    return render_template(
        'index.html',
        user_sentiment=user_sentiment,
        recent_reviews=recent_reviews
    ) 


@app.route('/gdb_data')
def fetch_gdb_data():

    # Query gdb to fetch all nodes and edges.
    nodes, edges = fetch_data()

    # Send results as Json response. 
    return jsonify({
        'nodes' : list(nodes.values()),
        'edges': edges 
    })
   


def main():
    app.run(debug=True)


if __name__ == '__main__':
    main()
