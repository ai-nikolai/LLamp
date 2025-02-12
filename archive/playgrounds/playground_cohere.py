import os
import cohere



if __name__=="__main__":
    API_KEY = os.environ['COHERE_API_KEY']
    co = cohere.Client(API_KEY)

    chat_history=[]

    # chat_history = [
    # 	{
    # 		"user_name":"Chatbot",
    # 		"text":""
    # 	},
    # 	{
    # 		"user_name":"User",
    # 		"text":""
    # 	},    	
    # ]

    response = co.chat(
            message="Generate from here: Hi there,",
            model="command",
            chat_history=chat_history,
            temperature=0.0
            # stop_sequences = ["\n"]
    )

    answer = response.text

    print(answer)
