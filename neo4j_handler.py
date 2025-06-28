import neo4j
import os


class Neo4jHandler:
    def __init__(self):
        self.uri = os.getenv("NEO4JURL")
        self.user = "neo4j"
        self.password = os.getenv("NEO4JPASSWORD")
        self.driver = neo4j.GraphDatabase.driver(
            self.uri, auth=(self.user, self.password)
        )

    def close(self):
        self.driver.close()

    def query(self, query, parameters=None, db="neo4j"):
        with self.driver.session(database=db) as session:
            result = session.run(query, parameters)
            return result.data()

    def query_returning_list(self, query, parameters=None, db="neo4j"):
        with self.driver.session(database=db) as session:
            result = session.run(query, parameters)
            return [dict(record) for record in result]

    def graph_rag(self, searchterm, parameters=None, db="neo4j"):

        token = os.getenv("NEO4J_OPENAI_TOKEN")

        query = """
                WITH genai.vector.encode($searchTerm, 'OpenAI', { token: $token }) AS embedding2Search
                CALL db.index.vector.queryRelationships('z',10,embedding2Search)
                YIELD relationship AS rel, score
                WITH collect(DISTINCT startNode(rel)) + collect(DISTINCT endNode(rel)) AS nodes

                UNWIND nodes AS node
                WITH collect(DISTINCT node) AS distinctNodes

                MATCH (n)-[r]->(m)
                WHERE n IN distinctNodes AND m IN distinctNodes
                RETURN DISTINCT n.name, r.Relationship, m.name, r.Criticality, r.`Evidence base`
                """

        parameters = {"searchTerm": searchterm, "token": token}

        with self.driver.session(database=db) as session:
            result = session.run(query, parameters)
            return result.data()
