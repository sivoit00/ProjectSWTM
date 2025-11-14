
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, tool
from langchain import hub


@tool
def check_policy_number(policy_number: str):
    """Prüft ob eine Versicherungsnummer formal gültig ist."""
    if policy_number.startswith("VS-") and len(policy_number) > 3:
        return f"Versicherungsnummer {policy_number} ist gültig."
    return f"{policy_number} ist keine gültige Versicherungsnummer."


llm = ChatOpenAI(model="gpt-4.1", temperature=0)


prompt = hub.pull("hwchase17/openai-tools-agent")


insurance_agent = AgentExecutor.from_agent_and_tools(
    agent=prompt,
    tools=[check_policy_number],
    llm=llm,
    verbose=True,
)

def run_insurance_agent(user_input: str):
    """Dummy-Modus: Liefert immer eine Test-Antwort"""
    return "TEST: Versicherungs-Agent läuft (Fake-Modus)"


#def run_insurance_agent(user_input: str):
#    """Einfache API-Funktion."""
#    result = insurance_agent.invoke({"input": user_input})
#    return result["output"]


