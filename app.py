import gradio as gr
from education_conversation import EducationConversation

education_conversation_instance = EducationConversation()

def education_convo(message, history):
    """
    function that handles a user query about education in london.

    parameters:
        Message: the last user message
        gradio_history:  list of two-element lists of the form [[user_message, bot_message]]

    returns chat_message:str
    """
    bot_message = education_conversation_instance.find_school_chat(message, history)
    history.append((message, bot_message))
    return "", history


# create chatbot using gradio
with gr.Blocks() as demo:
    chatbot = gr.Chatbot(value=[["", "How can I help you find a school?"]])
    msg = gr.Textbox()
    clear = gr.ClearButton([msg, chatbot])

    msg.submit(education_convo, [msg, chatbot], [msg, chatbot], queue=False)

demo.launch(
    server_port=8080)
