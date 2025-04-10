
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
        "MERGE (review:Review {timestamp: $timestamp}) "
        "MERGE (review)-[:MENTIONS]->(entity)"    
    )

    tx.run(
        query,
        entityName=entity.get('entity'),
        entityCategory=entity.get('category'),
        timestamp=review['timestamp']
    )


def create_aspect_relationship(tx, review, aspect):
    
    query = (
        "MERGE (aspect:Aspect {aspect: $aspectName}) "
        "ON CREATE SET aspect.category = $aspectCategory "
        "MERGE (review:Review {timestamp: $timestamp}) "
        "MERGE (review)-[:HAS_ASPECT]->(aspect)"    
    )

    tx.run(
        query,
        aspectName=aspect.get('aspect'),
        aspectCategory=aspect.get('category'),
        timestamp=review['timestamp']
    )


''' Retrieval Queries. '''

def fetch_data():

    nodes = {}
    edges = []

    with gdb_driver.session() as session:

        query = (
            "MATCH (review:Review) "
            "OPTIONAL MATCH (review)-[r]->(related) "
            "RETURN review, r, related "
            "LIMIT 30 "
        )

        results = session.run(query)

        for record in results:

            review_node = record['review']

            if review_node.id not in nodes:

                nodes[review_node.id] = {

                    'id' : review_node.id,
                    'label' : review_node.get('review', 'Review' + str(review_node.id)),
                    'sentiment':  review_node.get('sentiment', 'Positive'), ## Think here.
                    'group' : 'review'
                }

            relationship = record.get('r')
            related_node = record.get('related')

            if relationship and related_node:

                edges.append({
                    'from': review_node.id,
                    'to' : related_node.id,
                    'label' : relationship.type
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


def reformat_neo4j_timestamps(neo4j_timestamp):

    return  neo4j_timestamp.strftime("%Y-%m-%d %H:%M:%S")