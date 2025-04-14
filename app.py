
'''
    Super light-weight Flask webserver.
'''

from flask import Flask, render_template, request, jsonify,redirect, url_for
from llm import initalise_client, fetch_chatbot_response
from gdb import insert_review, fetch_data, fetch_recent_reviews, fetch_review_aspects, fetch_review_entities
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

            #print(f"LLM Raw Output: {user_sentiment}")

            try:

                # Convert str output into JSON.
                sentiment_data = json.loads(user_sentiment)

                if sentiment_data is not None:
                    # Insert model output into graph database. 
                    insert_review(sentiment_data)

                    return redirect(url_for('index'))

            except json.JSONDecodeError as e:
                print(f'JSON conversion error\n{e}')

    # Render webpage. 
    return render_template(
        'index.html',
        user_sentiment=user_sentiment,
        recent_reviews=recent_reviews
    ) 


@app.route('/gdb_data')
def fetch_gdb_data():

    graph_view = request.args.get('user_selection')

    if graph_view == 'review_aspects':
        nodes, edges = fetch_review_aspects() # reviews and their aspects.

    elif graph_view == 'review_entities':
        nodes, edges = fetch_review_entities() # reviews and the named entities. 

    else:
        nodes, edges = fetch_data() # All nodes + relationships.

    # Send results as Json response. 
    return jsonify({
        'nodes' : list(nodes.values()),
        'edges': edges 
    })
   


def main():
    app.run(debug=True)


if __name__ == '__main__':
    main()
