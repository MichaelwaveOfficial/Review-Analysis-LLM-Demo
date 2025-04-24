🌟-Review-Analysis-LLM-Demo

Hacked together minimum viable product intergrating language models into an interface, mimicking a business support system for organisations looking to 
efficiently tackle incident support management and query their clients anecdotes accordingly. 

The model is able to ingest written reviews, extracting sentiments and entities, comprising these reviews, modelling the relationships to highlight commonalities between them,
allowing or us to quickly identify how people feel about a hypothetical product / service for better or for worse. 

-> Write Review -> LLM Ingests Review -> Return Structured Output -> Insert Into Graph DB.

Might expand in the future. Who knows. Idea is there.

## Features
 ✔️ Hosted web server.  
 ✔️ Hosted Language Model (Runpod).  
 ✔️ Sentiment Analysis with prompted categories (Positive, Negative, Neutral).
 ✔️ Named Entity Recgonition with prompted entities (ORGANISATIONS, PEOPLE, LOCATIONS, SERVICE, PRODUCT, DATE, TIME, ect ect.).
 ✔️ Graph Database Integration.

## Prerequisites:
    * Python 3.11+
    * Neo4j Database.
    * Money for Runpod. (unless you host model locally).
