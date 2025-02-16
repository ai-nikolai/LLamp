try:
    from llamp.llms.api.anthropic_chat import AnthropicChat
    from llamp.llms.api.anthropic_text import AnthropicText
except Exception as e:
    print(e)
    print("Did not import Anthropic - inside llamp")

try:
    from llamp.llms.api.cohere_chat import CohereChat
    from llamp.llms.api.cohere_text import CohereText
    from llamp.llms.api.cohere_chat_text import CohereChatText
except Exception as e:
    print(e)
    print("Did not import Cohere - inside llamp")

try:
    from llamp.llms.api.openai_chat import OpenAIChat
    from llamp.llms.api.openai_text import OpenAIText
    from llamp.llms.api.openai_chat_text import OpenAIChatText
    from llamp.llms.api.openai_chat_text_sampling import OpenAIChatTextSampling
except Exception as e:
    print(e)
    print("Did not import OpenAI - inside llamp")

try:
    from llamp.llms.api.nvidia_chat_text import NvidiaChatText
except Exception as e:
    print(e)
    print("Did not import NvidaCloud - inside llamp")

try:
    from llamp.llms.api.cerebras_chat_text import CerebrasChatText
except Exception as e:
    print(e)
    print("Did not import Cerebras - inside llamp")  
