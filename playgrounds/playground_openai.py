from openai import OpenAI
import os



if __name__=="__main__":
	# print(os.environ.get("OPENAI_API_KEY"))

	client = OpenAI(
	    # Defaults to os.environ.get("OPENAI_API_KEY")
	    # api_key=OPENAI_KEY,
	)

	chat_completion = client.chat.completions.create(
	    model="gpt-3.5-turbo",
	    messages=[
	    	{
		    	"role": "system", 
		   		"content": "Generate 2 paragraphs from here: Hi, there"}
	    ],
	    stop = ["\n"]
	)

	# print(chat_completion)
	# print(chat_completion.choices[0].message)
	print(chat_completion.choices[0].message.content)
	print(chat_completion.choices[0].message.role)