import time
import requests
import json
from LLM_prompts import EMOTIONAL_PROMPT, PROMPT_INJECTION_PROTECTION
from data_handler import DataOperator
from typing import List
# from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT
import os
# LLM API details

#
# ANTHROPIC = Anthropic(
#     api_key="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",
# )
#set open ai api key
OPENAI_KEY ="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"
openai.api_key = OPENAI_KEY

class EducationConversation:

    def __init__(self):
        self.information_extraction_count = 0
        self.data_operator = DataOperator()

    def send_llm_message(self, message: str, temperature=0.7):
        """Sends a message to claude 2 using chat completion

        parameters:
            Message: the prompt that will be sent to our LLM
            temperature:  the temperature value that will be sent to open ai. dictates the randomness in LLM generations

        returns str"""

        return (
            openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": message}],
                temperature=temperature

            )
                .choices[0]
                .message.content
        )

    def convert_gradio_history_to_text(self, message: str, gradio_history: List  ):
        """
        converts the gradio chat history into one string
        parameters:
            Message: the last user message
            gradio_history:  list of two-element lists of the form [[user_message, bot_message]]

        returns text_history:str
        """
        text_history = ""
        for user_message, ai_message in gradio_history:
            text_history = text_history + "\n User: " + user_message + "\n You: " + ai_message
        text_history = text_history + "\n User: " + message

        return text_history

    ### QA pipeline

    example_conversation = """User: 
    Hey, I am interested in bfinding a school for my child
    You: 
    Hello, I’d be happy to assist you in finding the right shool. Could you please provide some more information? 
    Are you loooking for a primary or secondary school? are you looking in a specific location for example? 
    User: 
    I'm looking for a secondary school in hackney
    you:
    We have a variety of schools in hackney, what ofsted rating are you looking for? Do you want a religious school? 
    user: 
    a good or outstanding ofsted rating, i dont care about the religous aspect 
    you:
    Thanks for answering my questions! Here is a selection of schools that might be suited to you
    """

    def is_enough_info_for_search(self, chat_history):
        """This function checks if the chatbot has elicited enough product
        information from the customer to perform a product search

        returns bool
        """
        prompt = f"You are a friendly, conversational retail shopping assistant. You look at the chat history between yourself and customer to determine if you have enough information to search for a product \
        in the product catalogue there are many different types if product. Products are classified by their product attributes.\
        This includes things like product type (t-shirt, trousers, dress etc), product style (striped design, all over pattern, no patern etc). \
        Here is an example conversation so you know how to behave {example_conversation} \n\n \
        remember, if the user mentions a specific school then you have enough information to make a school recommendation \
        given the following chat history determine if you have enough information to make a good school recommendation. {EMOTIONAL_PROMPT}. just reply with YES! or NO!. {PROMPT_INJECTION_PROTECTION} ~~~ Here is the chat history: {chat_history}"

        response = send_llm_message(prompt)

        if response == "YES!" or response == "yes" or response == "yes!":
            return True
        else:
            return False

    def is_query_unrelated(self, query):
        """This function checks if the customers query is related to
        schools or not

        returns bool
        """
        prompt = f"You are a friendly, conversational school finding assistant. Parents ask you to help them find a school for their children. \
        some related queries include talking about school location, religous type and ofsted rating \
        Sometimes customers will ask you about topics that are unrelated to schools, such questions and queries are to be rejected.\
        This includes things like 'can you help me buy a car?' or 'i would like to purhcase a bike'. \
        given the following parent query determine if it's unrleated. just reply with YES! if unrelated or NO! if related. {EMOTIONAL_PROMPT} Don't include anything else in the response.{PROMPT_INJECTION_PROTECTION}. Here's the query: ~~~~ {query}"

        related_response = send_llm_message(prompt)

        if related_response == "YES!" or related_response == "yes" or related_response == "yes!":
            return True
        else:
            return False

    def generate_conversational_response(self, chat_history):

        """This function generates a response to the parents
        messages given a provided chat history (string)

        returns str
        """

        prompt = f"You are a friendly, conversational retail shopping assistant. {tone_prompt} You are speaking to a customer to help them with their search for womens clothes. Im going to show you the conversation between a customer and yourself. You will then ask a question that will allow you to recommend a produce for them. \
        in the product catalogue there are many different types if product. Products are classified by their product attributes.\
        This includes things like product type (t-shirt, trousers, dress etc), product style (striped design, all over pattern, no patern etc). \
        given the following chat history ask a follow up question to get the information required to make a good product recommendation. Don't respond with anything but the next qestion. Don't include 'you' or 'customer' in your response. {EMOTIONAL_PROMPT}.{PROMPT_INJECTION_PROTECTION}. Here's the chat history: ~~~~ \n\n {chat_history}"

        response = send_llm_message(prompt)

        return response

    def generate_doe_search_query(self, chat_history):

        """This function generates a search query for the parent given the parents
        messages in a provided chat history (string)

        returns str
        """

        prompt = f"You are a friendly, conversational school choosing assitant for parents. You look at the chat history between " \
                 f"yourself and parents and summarise the parents wants and needs in to a school search that can be used to find the schools that suit them. \
        in the school database there are many different types of school. Schools are classified by their attributes.\
        This includes things like         " \
                 f"EstablishmentName, TypeOfEstablishment(academy, public), PhaseOfEducation(secondary/primary), StatutoryLowAge, StatutoryHighAge, Gender(name), ReligiousEthos(name), location(name), OfstedRating(name). \
        given the following chat history on't respond with anything but the search query. {EMOTIONAL_PROMPT}. Here's the chat history: {chat_history}"

        response = send_llm_message(prompt)

        return response

    def look_at_docs_and_produce_response(self, chat_history, docs):
        """This function generates a response to the parents
        messages given a provided chat history (string) and a list
        of products that are relevant to the customer

        returns str
        """

        prompt = f"You are a friendly, conversational school choosing assistant for parents.\
        in a previous conversation with a parent you found some schools in the school database that might interest a user. \
        I'm going to show you the chat history between you and a parent aswell as the schools you found.\
        I want you to choose one or two schools to recommend to the parent. The parent needs the school name for each school. i want yout to explain your recommendation too \
        Here is the chat history: \n {chat_history} \
        \n and here are the products you found: \n {docs} \n\n\
        don't return anything but your reccomendation and explanation that will be shown to the parent. {EMOTIONAL_PROMPT}"

        response = send_llm_message(prompt)
        return response

    def are_docs_relevant_to_query(self, query, docs):
        """This function checks if the documents returned by the
        vector store are relevant to the customers query

        returns bool
        """

        prompt = f"You are a friendly, conversational education assistant that helps parents find good schools. You have used a this query '{query}' to do a school search to find relevant schools \
        look at the schools that have been returned by the search below and respond if the results are relevant. The documents are relevant if they are similar to each other \
        , aswell as to the query. it isn't enough that they are schools, they have to be a specific type of schools. Just respond with 'YES!' or 'NO!', don't respond with anything else. {EMOTIONAL_PROMPT}\
        here are the returned docs: {docs}"

        response = send_llm_message(prompt)

        if response == "YES!" or response == "yes" or response == "yes!":
            return True
        else:
            return False


    def find_school_chat(self, message:str, gradio_chat_history:List):
        """This function is the chatbot pipeline. It analyses a parents response and chooses the appropriate next message
        parameters:
            Message: the last user message
            gradio_history:  list of two-element lists of the form [[user_message, bot_message]]

        returns next_response: str
        """
        chat_history = self.convert_gradio_history_to_text(message, gradio_chat_history)

        try:
            if self.is_query_unrelated(chat_history) == True:

                next_response = "Sorry! This query is unrelated to schools :)"

            # always try and extract more information if the user has sent only one message
            elif self.information_extraction_count < 1:

                next_response = generate_conversational_response(chat_history)
                self.information_extraction_count += 1

            # check if theres enough information to search for a relevant product
            elif self.is_enough_info_for_search(chat_history) or self.information_extraction_count > 2:

                search_query = self.generate_doe_search_query(chat_history)
                doe_search_result_dict = self.data_operator.vector_search_doe_table(search_query)
                string_doe_docs = str(doe_search_result_dict["docs"])

                # check that products returned by the search match the parents prefrences
                if search_result_dict["are_relevant"] or self.information_extraction_count > 1:
                    next_response = self.look_at_docs_and_produce_response(chat_history, string_doe_docs)

                    next_response = f"{next_response} \n\n\n Here are the schools i used to make this recommendation: \n\n {string_doe_docs}"
                    self.information_extraction_count = 1


                else:

                    next_response = self.generate_conversational_response(chat_history)
                    self.information_extraction_count += 1

            else:
                next_response = self.generate_conversational_response(chat_history)
                self.information_extraction_count += 1

        except KeyboardInterrupt:
            next_response = "Chat interrupted. Keyboard interrupt"


        except Exception as e:
            next_response = "Chat interrupted due to error: " + str(e)

        return next_response