import os
import json
import time
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import os

from dotenv import load_dotenv
load_dotenv()


# service-functions
from services.insurance_service import (
    get_policy_details,
    calculate_premium,
    submit_claim,
    get_claim_status,
)

def safe_string(x: Any):
    if isinstance(x, (dict, list)):
        try:
            return json.dumps(x, indent=2, ensure_ascii=False)
        except:
            return str(x)
    return str(x)


# ----------------------------------------------------------
# main function: Insurance Agent
# ----------------------------------------------------------

def run_insurance_agent(user_input: str, user_id: str = None, context: Dict[str, Any] = None) -> Dict[str, Any]:

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY ist nicht gesetzt.")

    model_name = os.getenv("OPENAI_MODEL", "gpt-5-mini")

    llm = ChatOpenAI(
        api_key=api_key,
        model=model_name,
        temperature=0,
        max_tokens=1500,
    )

    if context is None:
        context = {}

    # -------------------- Agent 1: Classification ---------------------

    templates_dir = os.path.join(os.path.dirname(__file__), "templates")
    with open(os.path.join(templates_dir, "insurance_classifier.md"), "r", encoding="utf-8") as f:
        classifier_template = f.read()
    classifier_prompt = ChatPromptTemplate.from_template(classifier_template)

    agent1_messages = classifier_prompt.format_messages(
        user_input=user_input,
        context=str(context),
    )

    agent1_out = llm.invoke(agent1_messages)
    classification_text = agent1_out.content

    print("\n=== AGENT 1 CLASSIFICATION ===")
    print(classification_text)

    # -------------------- Preparation ------------------------------

    extracted = extract_parameters_from_classification(classification_text, context)

    if "WEITERLEITEN: NEIN" in classification_text:
        return {
            "ok": True,
            "response": simple_general_answer(llm, user_input)
        }

    # -------------------- Agent 2: Tools --------------------------------

    result = run_tool_logic_based_on_category(classification_text, extracted)

    summary = llm.invoke([
        {
            "role": "system",
            "content": "Fasse das folgende Tool-Ergebnis in natürlicher Sprache für einen Benutzer zusammen. "
                       "Sei kurz, hilfreich und versicherungsbezogen."
        },
        {
            "role": "user",
            "content": f"Tool-Ergebnis: {result}"
        }
    ]).content

    return {
        "ok": True,
        "category": extracted["category"],
        "data_used": safe_string(extracted),
        "tool_result_raw": safe_string(result),
        "response": summary,
    }
# ----------------------------------------------------------
# parameter extraction
# ----------------------------------------------------------

def extract_parameters_from_classification(text: str, context: Dict[str, Any]):
    if "POLICY_INFO" in text:
        category = "POLICY_INFO"
    elif "PREMIUM_CALC" in text:
        category = "PREMIUM_CALC"
    elif "CLAIM_SUBMIT" in text:
        category = "CLAIM_SUBMIT"
    elif "CLAIM_STATUS" in text:
        category = "CLAIM_STATUS"
    elif "CLAIM_CAPTURE" in text:
        category = "CLAIM_CAPTURE"
    else:
        category = "ANDERE"

    claim_id = None
    if "claim_id:" in text.lower():
        try:
            claim_id = text.split("claim_id:")[1].split("\n")[0].strip()
        except:
            pass

    return {
        "category": category,
        "context_customer": context.get("customer_id"),
        "claim_id": claim_id,
        "raw_classification": text,
        "info_provided": text,
    }

# ----------------------------------------------------------
# Agent 2: Tools
# ----------------------------------------------------------

def run_tool_logic_based_on_category(category_text: str, ext: Dict[str, Any]):

    category = ext["category"]

    if category == "POLICY_INFO":
        customer_id = ext["context_customer"] or "cust-1"
        return get_policy_details(customer_id)

    if category == "PREMIUM_CALC":
        vehicle_data = {"brand": "BMW", "model": "320d", "year": 2020}
        return calculate_premium(vehicle_data)

    if category == "CLAIM_SUBMIT":
        customer_id = int(ext["context_customer"]) if ext["context_customer"] else 1
        claim_data = {
            "customer_id": customer_id,
            "claim_id": f"CLM-{int(time.time())}", 
            "description": "Schaden gemeldet"
        }
        return submit_claim(claim_data)

    if category == "CLAIM_STATUS":
        if not ext["claim_id"]:
            return {"error": "Keine claim_id erkannt."}
        return get_claim_status(ext["claim_id"])
    if category == "CLAIM_CAPTURE":
        return {
        "next_step": "CLAIM_SUBMIT",
        "message": "Ich habe die notwendigen Informationen gesammelt. Willst du den Schaden jetzt einreichen?",
        "captured_data": ext["info_provided"]
        }

    return "Ich habe deine Frage verstanden, aber keine passende Versicherungsfunktion gefunden."

# ----------------------------------------------------------
# fallback response
# ----------------------------------------------------------

def simple_general_answer(llm, text: str) -> str:
    msg = [{"role": "user", "content": f"Antworte kurz und freundlich auf: {text}"}]
    return llm.invoke(msg).content