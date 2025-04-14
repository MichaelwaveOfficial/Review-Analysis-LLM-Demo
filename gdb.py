
''' Module for insertion and read operations within the NEO4J gdb. '''

from neo4j import GraphDatabase
import os 

URI = os.getenv('NEO4J_URI')

NEO4J_USERNAME = os.getenv('NEO4J_USERNAME')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD')
NEO4J_AUTHENTICATION = (NEO4J_USERNAME, NEO4J_PASSWORD)

gdb_driver = GraphDatabase.driver(URI, auth=NEO4J_AUTHENTICATION)

''' Insertion Queries. '''


def insert_review(user_sentiment):

    with gdb_driver.session() as session:
        
        # Insert user review.
        user_review = session.execute_write(create_review_node, user_sentiment)

        # Insert Entities within review.
        for entity in user_sentiment.get('entities', []):
            session.execute_write(create_entity_relationship, user_review, entity)

        # Insert Aspects within review. 
        for aspect in user_sentiment.get('aspects', []):
            session.execute_write(create_aspect_relationship, user_review, aspect)
    

''' Definition Queries. '''

''' Nodes. '''


def create_review_node(tx, review):

    query = (
        "CREATE (review:Review {review: $review, sentiment: $sentiment, timestamp: datetime()}) "
        "RETURN review"
    )

    result = tx.run(
        query,
        review=review.get('review'),
        sentiment=review.get('sentiment')
    )
    
    return result.single()['review']


''' Relationships. '''


def create_entity_relationship(tx, review, entity):
    
    query = (
        "MERGE (entity:Entity {name: $entityName}) "
        "ON CREATE SET entity.category = $entityCategory "
        "WITH entity, $review_id as review_id "
        "MATCH (review:Review) WHERE id(review) = review_id "
        "MERGE (review)-[:MENTIONS]->(entity)"  
    )

    tx.run(
        query,
        entityName=entity.get('entity'),
        entityCategory=entity.get('category'),
        review_id=review.id
    )


def create_aspect_relationship(tx, review, aspect):
    
    query = (
        "MERGE (a:Aspect {aspect: $aspectName}) "
        "ON CREATE SET a.category = $aspectCategory "
        "WITH a, $review_id AS review_id "
        "MATCH (r:Review) WHERE id(r) = review_id "
        "MERGE (r)-[:HAS_ASPECT]->(a)"
    )

    tx.run(
        query,
        aspectName=aspect.get('aspect'),
        aspectCategory=aspect.get('category'),
        review_id=review.id
    )


''' Retrieval Queries. '''

def fetch_data():

    nodes = {}
    edges = []

    with gdb_driver.session() as session:

        query = (
            "MATCH p=()-[]->() RETURN p "
        )

        results = session.run(query)

        for record in results:

            path = record['p']

            for node in path.nodes:

                node_id = str(node.id)

                if node_id not in nodes:

                    labels = list(node.labels)

                    group = labels[0] if labels else 'Node'

                    nodes[node_id] = {
                        'id' : node_id,
                        'label' : node.get('review', node.get('aspect', node.get('name', group + node_id))),
                        'sentiment':  node.get('sentiment'),
                        'group' : group,
                        'title' : str(dict(node))
                    }

            for relation in path.relationships:

                edges.append({
                    'from': str(relation.start_node.id),
                    'to' : str(relation.end_node.id),
                    'label' : relation.type,
                    'title': str(dict(relation))
                })

    return nodes, edges 


def fetch_recent_reviews(no_of_reviews):

    with gdb_driver.session() as session:

        query = (
            "MATCH (r:Review) "
            "RETURN r "
            "ORDER BY r.timestamp DESC "
            f"LIMIT {no_of_reviews}"
        )

        results = session.run(query)

        recent_reviews = [
            {
                'sentiment' : record['r'].get('sentiment'),
                'review' : record['r'].get('review'),
                'timestamp' : reformat_neo4j_timestamps(record['r'].get('timestamp')),
            }
            for record in results
        ]

    return recent_reviews


def fetch_review_aspects(limit=25):

    with gdb_driver.session() as session:

        query = (
            "MATCH (r:Review)-[has:HAS_ASPECT]->(a:Aspect) "
            "RETURN r AS review_node, r.sentiment AS review_sentiment, has AS aspect_relationship, a AS aspect_node "
            f"LIMIT {limit} "
        )

        results = session.run(query)

        nodes = {}
        edges = []

        for record in results:

            review = record['review_node']
            aspect = record['aspect_node']
            relationship = record['aspect_relationship']

            review_id = str(review.id)
            aspect_id = str(aspect.id)

            review_sentiment = str(record['review_sentiment'])

            if review_id not in nodes:

                nodes[review_id] = {
                    'id': review_id,
                    'label': review.get('review', 'Sentiment: ' + review_sentiment),
                    'sentiment': review_sentiment,
                    'group': 'Review'
                }

            if aspect_id not in nodes:

                nodes[aspect_id] = {
                    'id': aspect_id,
                    'label': aspect.get('aspect', 'Aspect' + aspect_id),
                    'group': 'Aspect'
                }

            edges.append({
                'from': review_id,
                'to': aspect_id,
                'label': relationship.type,
                'title': str(dict(relationship))
            })
    
        return nodes, edges
    

def fetch_review_entities(limit=25):

    with gdb_driver.session() as session:

        query = (
            "MATCH (r:Review)-[mention:MENTIONS]->(entity:Entity) "
            "RETURN r AS review_node, r.sentiment AS review_sentiment, mention AS entity_relationship, entity AS entity_node "
            f"LIMIT {limit} "
        )

        results = session.run(query)

        nodes = {}
        edges = []

        for record in results:

            review = record['review_node']
            entity = record['entity_node']
            relationship = record['entity_relationship']

            review_id = str(review.id)
            entity_id = str(entity.id)

            review_sentiment = str(record['review_sentiment'])

            if review_id not in nodes:

                nodes[review_id] = {
                    'id': review_id,
                    'label': review.get('review', 'Sentiment: ' + review_sentiment),
                    'sentiment': review_sentiment,
                    'group': 'Review'
                }

            if entity_id not in nodes:

                nodes[entity_id] = {
                    'id': entity_id,
                    'label': f"category: {entity.get('category')} \nentity: {entity.get('name')}",
                    'group': 'Aspect'
                }

            edges.append({
                'from': review_id,
                'to': entity_id,
                'label': relationship.type,
                'title': str(dict(relationship))
            })
    
        return nodes, edges


def reformat_neo4j_timestamps(neo4j_timestamp):

    return  neo4j_timestamp.strftime("%Y-%m-%d %H:%M:%S")