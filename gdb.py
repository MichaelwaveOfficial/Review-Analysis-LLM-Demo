
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
        print(user_review)

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
        "CREATE (review:Review {review: $review, sentiment: $sentiment, timestamp: $timestamp}) "
        "RETURN review"
    )

    result = tx.run(
        query,
        review=review.get('review'),
        sentiment=review.get('sentiment'),
        timestamp=review.get('timestamp')
    )
    
    return result.single()['review']


''' Relationships. '''


def create_aspect_relationship(tx, review, entity):
    
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


def create_entity_relationship(tx, review, aspect):
    
    query = (
        "MERGE (aspect:Aspect {aspect: $aspectName}) "
        "ON CREATE SET aspect.category = $aspectCategory "
        "MERGE (review:Review {timestamp: $timestamp}) "
        "MERGE (review)-[:HAS_ASPECT]->(aspect)"    
    )

    tx.run(
        query,
        aspectName=aspect.get('name'),
        aspectCategory=aspect.get('category'),
        timestamp=review['timestamp']
    )
