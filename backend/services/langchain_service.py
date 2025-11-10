from typing import Optional
import os
from langchain.chat_models import ChatOpenAI
from langchain import LLMChain
from langchain.prompts import PromptTemplate


def generate_answer_with_langchain(user_input: str, model_name: Optional[str] = None, temperature: float = 1.0) -> str:
    """Generate an answer using LangChain (ChatOpenAI + LLMChain).

    This wrapper reads OPENAI_API_KEY from the environment, constructs a small prompt
    and returns the model output as a string.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured in environment")

    model_name = model_name or os.getenv("OPENAI_MODEL", "gpt-5-nano-2025-08-07")

    template_text = (
        "Du bist ein hilfreicher Assistent für den Fahrzeugservice. "
        "Beantworte die Nutzerfrage sachlich und so knapp wie möglich. Frage: {user_input}"
    )
    prompt = PromptTemplate(input_variables=["user_input"], template=template_text)

    llm = ChatOpenAI(openai_api_key=api_key, model_name=model_name, temperature=temperature)
    chain = LLMChain(llm=llm, prompt=prompt)

    # run synchronously
    answer = chain.run(user_input)
    return answer
