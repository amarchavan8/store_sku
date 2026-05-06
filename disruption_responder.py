# my first multi-agent project :)
# idea: when a supplier goes down, 3 small "agents" figure out
# what to do about it
#
# agent 1 = reads the event, says how bad it is
# agent 2 = checks which products will run out of stock
# agent 3 = suggests what to do (use backup supplier etc)
#
# nothing fancy here, just functions calling functions
# run it with:  python disruption_responder.py

import os
import json
import sys
from datetime import datetime
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage


load_dotenv()  # picks up keys from .env

# i use litellm at work so trying that key first, otherwise normal openai
api_key = os.getenv("LITELLM_API_KEY") or os.getenv("OPENAI_API_KEY")
api_base = os.getenv("LITELLM_API_BASE") or os.getenv("OPENAI_BASE_URL")

# TODO: maybe make model configurable later
llm = ChatOpenAI(
    model="gpt-5",
    temperature=0,
    api_key=api_key,
    base_url=api_base,
)


def load_json(path):
    # tiny helper, gets old typing it everywhere
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def ask_llm(system_prompt, user_prompt):
    # wrapper so I don't have to build the message list every time
    msgs = [SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)]
    return llm.invoke(msgs).content


# ===== AGENT 1 =====
# reads the event and tags it LOW / MEDIUM / HIGH
def event_agent(event):
    print("\n[Event Agent] reading the event...")

    system = (
        "You are an Event Agent in a supply chain team. "
        "You read incoming disruption events and classify how serious they are. "
        "Severity must be one of: LOW, MEDIUM, HIGH. "
        "Reply in this exact format:\n"
        "SEVERITY: <LOW|MEDIUM|HIGH>\n"
        "REASON: <one short sentence>"
    )
    user = f"Event details:\n{json.dumps(event, indent=2)}"

    reply = ask_llm(system, user)
    print(reply)

    # if it doesn't show up we'll just default to MEDIUM
    severity = "MEDIUM"
    for line in reply.splitlines():
        if line.upper().startswith("SEVERITY:"):
            severity = line.split(":", 1)[1].strip().upper()
            break

    return {"severity": severity, "raw_reply": reply}


# ===== AGENT 2 =====
# this one doesn't even need an LLM - just basic math
# (an "agent" is whatever does a job, doesn't have to be an LLM)
def impact_agent(event, world):
    print("\n[Impact Agent] checking which products are at risk...")

    bad_supplier = event["supplier_id"]
    days_down = event["downtime_days"]

    affected = []
    for sku_id, sku in world["skus"].items():
        # only care about products from the supplier that's down
        if sku["primary_supplier"] != bad_supplier:
            continue

        # how many days of stock do we have? simple division
        days_left = sku["stock_units"] // max(sku["daily_sales"], 1)

        will_stockout = days_left < days_down

        # rough estimate of $ we'd lose if we stock out
        revenue_at_risk = 0
        if will_stockout:
            missing_days = days_down - days_left
            revenue_at_risk = missing_days * sku["daily_sales"] * sku["unit_price"]

        affected.append({
            "sku_id": sku_id,
            "name": sku["name"],
            "days_of_stock": days_left,
            "will_stockout": will_stockout,
            "revenue_at_risk": revenue_at_risk,
            "backup_suppliers": sku["backup_suppliers"],
        })

    # print a small table so I can sanity check
    for item in affected:
        flag = "STOCK-OUT RISK" if item["will_stockout"] else "ok"
        print(
            f"  - {item['name']:25s} "
            f"days_of_stock={item['days_of_stock']:>3}  "
            f"{flag}  "
            f"$ at risk={item['revenue_at_risk']:,}"
        )

    return affected


# ===== AGENT 3 =====
# asks the LLM "ok what do we actually do about it?"
def replan_agent(affected_items, world):
    print("\n[Replan Agent] suggesting what to do...")

    # only bother if something will actually run out
    at_risk = [x for x in affected_items if x["will_stockout"]]
    if not at_risk:
        print("  Nothing to replan - no stock-outs predicted.")
        return "No action needed."

    # build a little summary the LLM can read<
    lines = []
    for item in at_risk:
        backups_text = []
        for sup_id in item["backup_suppliers"]:
            sup = world["suppliers"][sup_id]
            backups_text.append(
                f"{sup['name']} (lead_time={sup['lead_time_days']}d, "
                f"cost x{sup['cost_multiplier']})"
            )
        lines.append(
            f"- {item['name']}: only {item['days_of_stock']} days of stock left. "
            f"Backups: {', '.join(backups_text)}."
        )
    summary = "\n".join(lines)

    system = (
        "You are a Replan Agent. For each at-risk product, recommend ONE clear "
        "action (switch to a specific backup supplier, expedite shipping, or "
        "raise prices to slow demand). Be brief. Use bullet points."
    )

    reply = ask_llm(system, f"At-risk products:\n{summary}")
    print(reply)
    return reply


# saves a markdown report so my manager can read it later :)
def save_report(event, severity, affected, plan, event_file=None):
    today = datetime.now().strftime("%Y_%m_%d")
    reports_dir = "incidents"
    os.makedirs(reports_dir, exist_ok=True)

    # include the event name so multiple events on the same day don't overwrite
    if event_file:
        slug = os.path.splitext(os.path.basename(event_file))[0]
        filename = os.path.join(reports_dir, f"incident_{today}_{slug}.md")
    else:
        filename = os.path.join(reports_dir, f"incident_{today}.md")

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# Incident Report - {today}\n\n")
        f.write(f"**Event:** {event['headline']}\n\n")
        f.write(f"**Severity:** {severity}\n\n")

        f.write("## Affected Products\n\n")
        if not affected:
            f.write("None.\n\n")
        else:
            f.write("| Product | Days of Stock | Stock-out? | Revenue at Risk |\n")
            f.write("|---|---|---|---|\n")
            for item in affected:
                stockout = "YES" if item["will_stockout"] else "no"
                f.write(
                    f"| {item['name']} | {item['days_of_stock']} | "
                    f"{stockout} | ${item['revenue_at_risk']:,} |\n"
                )
            f.write("\n")

        f.write("## Recommended Plan\n\n")
        f.write(plan + "\n")

    print(f"\nReport saved to: {filename}")


def report_path_for(event_file):
    today = datetime.now().strftime("%Y_%m_%d")
    slug = os.path.splitext(os.path.basename(event_file))[0]
    return os.path.join("incidents", f"incident_{today}_{slug}.md")


def is_new_event(event_file):
    # we treat an event as "new" if there's no report file for it yet
    return not os.path.exists(report_path_for(event_file))


def process_event(event_file, world):
    print("\n" + "=" * 60)
    print(f"EVENT FILE: {event_file}")
    print("=" * 60)

    event = load_json(event_file)
    print(f"\nNew event received: {event['headline']}")

    # run them one after the other - simple and easy to debug
    result = event_agent(event)
    affected = impact_agent(event, world)
    plan = replan_agent(affected, world)

    save_report(event, result["severity"], affected, plan, event_file=event_file)


def main():
    print("=" * 60)
    print("DISRUPTION RESPONDER")
    print("=" * 60)

    world = load_json("world_state.json")

    # --all forces re-processing every event in the folder
    force_all = "--all" in sys.argv
    args = [a for a in sys.argv[1:] if a != "--all"]

    if args:
        # explicit files passed -> always process them
        event_files = args
    else:
        events_dir = "events"
        all_files = sorted(
            os.path.join(events_dir, f)
            for f in os.listdir(events_dir)
            if f.endswith(".json")
        )
        if force_all:
            event_files = all_files
        else:
            # only the ones we haven't reported on yet
            event_files = [f for f in all_files if is_new_event(f)]

    if not event_files:
        print("\nNo new events to process. (Use --all to re-run everything.)")
        return

    for event_file in event_files:
        try:
            process_event(event_file, world)
        except Exception as e:
            print(f"\n[ERROR] failed on {event_file}: {e}")

    print(f"\nDone! Processed {len(event_files)} event(s).")


if __name__ == "__main__":
    main()
