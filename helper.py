import os
from dotenv import load_dotenv
from connect import connect_to_database, get_database_schema_with_samples, ExecuteQuery
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from prompt import SQLprompt, explanation_prompt

load_dotenv()

class SQLChatBot:
    # def __init__(self, server, database, username, password):
    #     self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
    #     self.conn = connect_to_database(server, database, username, password)
    #     self.database = database
    #     self.chat_history = []
    #     self.schema_data = None

    #     if self.conn:
    #         self.schema_data = get_database_schema_with_samples(self.conn, self.database)
    def __init__(self, server, database, username, password):
        self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
        self.conn = connect_to_database(server, database, username, password)
        if self.conn is None:
            raise ConnectionError(f"Failed to connect to database '{database}' on server '{server}'. Please check your credentials and network.")
        self.database = database
        self.chat_history = []
        self.schema_data = get_database_schema_with_samples(self.conn, self.database)

    # def get_sql_query(self, question):
    #     prompt = ChatPromptTemplate.from_messages([
    #         ("system", SQLprompt),
    #         *self.chat_history,
    #         ("human", "{question}\nSchema:\n{schema_data}")
    #     ])

    #     chain = prompt | self.llm
    #     response = chain.invoke({
    #         "question": question,
    #         "schema_data": self.schema_data
    #     })

    #     query = response.content.strip().removeprefix("```sql").removesuffix("```").strip()

    #     # Update chat history
    #     self.chat_history.append((HumanMessage(content=question), AIMessage(content=query)))
    #     if len(self.chat_history) > 10:
    #         self.chat_history = self.chat_history[-10:]

    #     return query
    def get_sql_query(self, question):
        prompt = ChatPromptTemplate.from_messages([
            ("system", SQLprompt),
            *self.chat_history,
            ("human", "{question}\nSchema:\n{schema_data}")
        ])

        chain = prompt | self.llm
        response = chain.invoke({
            "question": question,
            "schema_data": self.schema_data
        })

        # Extract the SQL from the response
        query = response.content.strip().removeprefix("```sql").removesuffix("```").strip()

        # ✅ FIX: Use strings instead of message objects
        self.chat_history.append(("human", question))
        self.chat_history.append(("ai", query))

        if len(self.chat_history) > 10:
            self.chat_history = self.chat_history[-10:]

        return query

    def get_query_result(self, query):
        try:
            return ExecuteQuery(self.conn, query)
        except Exception as e:
            return f"❌ SQL Execution Error: {e}"

    def get_explanation(self, question, query):
        explanation_prompt_template = ChatPromptTemplate.from_messages([
            ("system", explanation_prompt),
            ("human", "User Question: {question}\nSQL Query:\n{query}")
        ])
        chain = explanation_prompt_template | self.llm
        response = chain.invoke({
            "question": question,
            "query": query
        })
        return response.content


    def get_full_response(self, question):
        sql = self.get_sql_query(question)
        result = self.get_query_result(sql)
        explanation = self.get_explanation(question, sql)

        return {
            "sql": sql,
            "result": result,
            "explanation": explanation
        }
    # def get_full_response(self, user_question):
    #     # Get the raw response from the LLM
    #     raw_response = self.llm_chain.run(user_question)

    #     # If using LangChain and AIMessage is returned, convert it to string
    #     if hasattr(raw_response, "content"):
    #         raw_response = raw_response.content

    #     # Now process raw_response (e.g., parse SQL, run it, etc.)
    #     sql_query = self.get_sql_query(raw_response)  # You need to define this
    #     df_result = self.get_query_result(sql_query)
    #     explanation = self. get_explanation(sql_query)   # Optional explanation generator

    #     return {
    #         "sql": sql_query,
    #         "result": df_result,
    #         "explanation": explanation
    #     }
