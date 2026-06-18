import PromptTemplate from langchain_core.prompts
import ChatPromptTemplate from langchain_core.prompts

def prompt_template(thing, manner):
    template = f"explain {thing} in {manner} way"
    return PromptTemplate.from_template(template)