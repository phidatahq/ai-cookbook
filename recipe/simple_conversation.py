from phi.conversation import Conversation
from phi.llm.openai import OpenAIChat

conversation = Conversation(llm=OpenAIChat(model="gpt-3.5-turbo-1106"))

# -*- Print response
conversation.print_response("Share a quick healthy breakfast recipe.")
