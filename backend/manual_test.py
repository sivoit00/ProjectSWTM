from agents.insurance_agent import run_insurance_agent

res = run_insurance_agent("Ich möchte meine Prämie berechnen für ein Auto Baujahr 2019.", user_id="cust-1", context={"vehicle": {"brand":"BMW","year":2019}})
print(res)