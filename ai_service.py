import json
import urllib.request
import urllib.error


def _fallback_answer(question, context):
    q = (question or "").lower()
    animals = context.get("total_animals", 0)
    milk = context.get("total_milk_litres", 0)
    income = context.get("total_income_rwf", 0)
    expenses = context.get("general_expenses_rwf", 0)
    labor = context.get("labor_cost_rwf", 0)
    sick = context.get("sick_animals", 0)
    treatment = context.get("under_treatment", 0)

    if any(k in q for k in ["health", "sick", "disease", "treatment", "medicine", "vaccin"]):
        if sick or treatment:
            return (
                f"Your records currently indicate {sick} sick animal(s) and "
                f"{treatment} animal(s) under treatment. Review the latest health "
                "records, medicine, treatment progress and veterinarian notes. "
                "For severe symptoms, seek qualified veterinary care promptly."
            )
        return (
            "No animal is currently recorded as sick or under treatment. "
            "Continue preventive care, vaccination, clean water, good nutrition "
            "and routine observation."
        )

    if any(k in q for k in ["milk", "production", "yield"]):
        return (
            f"The system has recorded {milk:,.2f} litres of milk production. "
            "If production falls, compare animals and dates and check feed, water, "
            "animal health, heat stress and milking routine."
        )

    if any(k in q for k in ["income", "expense", "cost", "profit", "finance", "money"]):
        net = income - expenses - labor
        return (
            f"Recorded income is {income:,.0f} RWF, general expenses are "
            f"{expenses:,.0f} RWF and labor cost is {labor:,.0f} RWF. "
            f"The current recorded net result is {net:,.0f} RWF. "
            "Use the Finance and Ledger sections for detailed transactions."
        )

    if any(k in q for k in ["farm", "animal", "cow", "goat"]):
        return (
            f"Your current records contain {animals} animal(s), {context.get('cows', 0)} "
            f"cow(s) and no other animal type is managed. I can help analyze health, "
            "production, labor, income, expenses and farm-management decisions. "
            "For a more specific recommendation, describe the problem, animal, "
            "crop or decision you are considering."
        )

    return (
        "I can help with livestock, animal health, production, labor, farm finance, "
        "expenses, record keeping and practical farm decisions. Ask your question "
        "in your normal language and include the relevant farm details when possible."
    )


def answer_question(question, context, api_key=None, model="gpt-4.1-mini"):
    """Use OpenAI when configured; otherwise provide a useful local agricultural assistant."""
    if not api_key:
        return _fallback_answer(question, context)

    system = """You are Farm Manager AI, a highly capable agricultural and farm-management decision-support assistant.
Give natural, human-like, practical answers. Use the supplied farm records as evidence and never invent farm facts.
Reason step by step internally, but present a clear concise explanation and actionable recommendations.
Handle livestock, animal health, crops, production, feeding, farm economics, labor, bookkeeping, risk management,
record keeping and general agricultural questions. Ask a useful clarifying question when the information is insufficient.
For diagnosis or emergencies, clearly recommend a qualified veterinarian or agricultural professional.
Do not claim to have performed laboratory tests, physical examinations, or field measurements.
When discussing money, distinguish income, general expenses, labor cost, advances and net result.
"""

    safe_context = {k: v for k, v in context.items()}
    payload = {
        "model": model,
        "input": [
            {"role": "system", "content": system},
            {"role": "user", "content": "Farm records:\n" + json.dumps(safe_context, default=str) +
             "\n\nFarmer/visitor question:\n" + question},
        ],
        "max_output_tokens": 900,
    }
    req = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=45) as response:
            data = json.loads(response.read().decode("utf-8"))
        text = data.get("output_text")
        if text:
            return text.strip()
    except Exception as exc:
        print(f"AI service error: {exc}")
    return _fallback_answer(question, context)


def dashboard_recommendations(context):
    items = []
    if context.get("sick_animals", 0):
        items.append({
            "level": "urgent",
            "title": "Animal health needs attention",
            "text": f"{context['sick_animals']} animal(s) are recorded as sick. Review their latest health records and treatment."
        })
    if context.get("under_treatment", 0):
        items.append({
            "level": "warning",
            "title": "Treatment follow-up",
            "text": f"{context['under_treatment']} animal(s) are under treatment. Confirm medicine, follow-up date and veterinary notes."
        })
    if context.get("total_income_rwf", 0) == 0:
        items.append({
            "level": "info",
            "title": "Record income",
            "text": "No income is currently recorded. Adding income makes profitability and cash-flow analysis more accurate."
        })
    net = context.get("net_result_rwf", 0)
    if net < 0:
        items.append({
            "level": "urgent",
            "title": "Financial review recommended",
            "text": "Recorded costs exceed recorded income. Review major expenses and labor costs in Finance."
        })
    if context.get("total_animals", 0) and context.get("total_milk_litres", 0) == 0:
        items.append({
            "level": "info",
            "title": "Production data check",
            "text": "No milk production is recorded. If the farm produces milk, review the Production records."
        })
    if not items:
        items.append({
            "level": "success",
            "title": "Farm records look stable",
            "text": "Continue updating health, production, labor, income and expenses regularly for stronger decisions."
        })
    return items
