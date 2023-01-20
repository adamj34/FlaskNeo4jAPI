import os
import asyncio
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()
uri = os.getenv("URI")
user = os.getenv("USERNAME")
password = os.getenv("PASSWORD")
driver = GraphDatabase.driver(uri, auth=(user, password), database="neo4j")
