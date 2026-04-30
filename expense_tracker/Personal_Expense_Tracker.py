##import libaries


from pathlib import Path
from datetime import datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import csv
import sys
from typing import Optional

#configuration start

CSV_FILE = Path("expenses.csv")
REQUIRED_FIELDS = ("date", "category", "amount", "description")
                   
def validate_date(date_text: str) :
   
    try:
        d = datetime.strptime(date_text.strip(), "%Y-%m-%d").date()
        return d.isoformat()
    except Exception:
        raise ValueError("Date must be formatted as YYYY-MM-DD.")



def parse_amount(text: str | float | int | Decimal):

##force into float with two decimals
    try:
        value = Decimal(str(text).strip())
    except (InvalidOperation, ValueError):
        raise ValueError("Amount inputted must a valid number.")
    if value < 0:
        raise ValueError("Negative numbers are not accepted.")
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

##verify record for completion
def entry_complete(rec: dict):
 
    missing = [a for a in REQUIRED_FIELDS if a not in rec or str(rec[a]).strip() == ""]
    if missing:
        return False, f"Missing field: {', '.join(missing)}"
    
    try:
        _ = validate_date(str(rec["date"]))
    except ValueError as e:
        return False, str(e)
    
    try:
        _ = parse_amount(rec["amount"])
    except ValueError as e:
        return False, str(e)
    return True, ""

##add expense entries

def add_expense(expenses: list[dict]):
   
    print("\nAdd an expense")
    keep_prompting = True
    while keep_prompting:
    
        try:
            date_input = input("Date (YYYY-MM-DD): ").strip()
            category = input("Category : ").strip()
            amount_input = input("Amount spent: ").strip()
            description = input("Brief description: ").strip()
            
            date_norm: str | None = None
            amount_dec: Decimal | None = None
            
            try:
                date_norm = validate_date(date_input)
            except ValueError as e:
                print(f" {e}. Incorrect Please try again\n")
                date_norm = None
                
            if date_norm is not None:
                try:
                    amount_dec = parse_amount(amount_input)
                except ValueError as e:
                    print(f" {e} incorrect try again\n")
                    amount_dec = None
                    
            if (date_norm is not None) and (amount_dec is not None):
                rec = {
                    "date": date_norm,
                    "category": category,
                    "amount": float(amount_dec),
                    "description": description,
                }
            
                ok, err = entry_complete(rec)
                if ok:
                    expenses.append(rec)
                    print("Expense added.")
                    keep_prompting = False
            
                else:
                    print(f"nvalid entry: {err}\n")
            else:
                print("You need to try again")
                
        except KeyboardInterrupt:
            print("\nAdd expense canceled.")
            keep_prompting = False
        except Exception as e:
             print(f"{e} please try again.\n")

## dislay expenses

def view_expenses(expenses: list[dict]):
    
    print("\nYour expenses are as follows:")
    if not expenses:
        print("  (no expenses documented)")
        return

    shown = 0
    for idx, rec in enumerate(expenses, start=1):
        ok, err = entry_complete(rec)
        if ok:
            amt = Decimal(str(rec["amount"])).quantize(Decimal("0.00"))
            print(f"  {idx} {rec['date']} | {rec['category']} | ${amt} | {rec['description']}")
            shown += 1
        else:
            print(f"  · Skipping entry #{idx} :{err}")

    if shown == 0:
        print("  (no valid expenses to display)")


display = view_expenses

## create budget tracker

def total_expenses(expenses: list[dict]):
  
    total = Decimal("0.00")
    for rec in expenses:
        ok, _ = entry_complete(rec)
        if ok:
            try:
                total += parse_amount(rec["amount"])
            except ValueError:
                pass
    return total.quantize(Decimal("0.00"))


def set_monthly_budget():
   
    asking = True
    while asking:
        try:
            raw = input("What is your monthly budget: ").strip()
            value = parse_amount(raw)
            return value
        except ValueError as e:
            print(f"{e}. Please try again.")
        except KeyboardInterrupt:
            print("\nSet budget not inputted.")
            asking = False
        return Decimal("0.00")


def track_budget (expenses: list[dict], budget: Decimal | None):
    if budget is None or budget == Decimal("0.00"):
        print("Budget has not been established.")
        budget = set_monthly_budget()
        if budget is None or budget == Decimal("0.00"):
            print("  (budget not set)")
            return budget

    spent = total_expenses(expenses)
    print("\nBudget info:")
    print(f"  Spent: ${spent}")
    print(f"  budget: ${budget}")

    if spent > budget:
        over = (spent - budget).quantize(Decimal("0.00"))
        print(f"You are over budget by ${over}!")
    else:
        remaining = (budget - spent).quantize(Decimal("0.00"))
        print(f"You have  ${remaining} left for the month.")
    return budget

##save expenses to csv

def save_expenses(filepath: Path | str, expenses: list[dict]) :
  
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)

    need_header = (not path.exists()) or (path.stat().st_size == 0)
    rows_appended = 0

   
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(REQUIRED_FIELDS))

        if need_header:
            writer.writeheader()

        for rec in expenses:
            ok, _ = entry_complete(rec)
            if ok:
                try:
                    amt = Decimal(str(rec.get("amount", "0"))).quantize(Decimal("0.00"))
                    row = {
                        "date": validate_date(str(rec.get("date", "")).strip()),
                        "category": str(rec.get("category", "")).strip(),
                        "amount": f"{amt}",
                        "description": str(rec.get("description", "")).strip(),
                    }
                    
                    writer.writerow(row)
                    rows_appended += 1
                except Exception:
                    
                    pass
            

    print(f"Appended {rows_appended} expense to '{path}'.")
    return rows_appended


def load_expenses(filepath: Path | str) :
   
    path = Path(filepath)
    if not path.exists():
        return []

    loaded: list[dict] = []
    try:
        with path.open("r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            expected = ["date", "category", "amount", "description"]
            found = [h.strip() for h in (reader.fieldnames or [])]

            # Warn if header mismatch; still attempt to read
            if set(found) != set(expected):
                print(
                    "  CSV header is labelled incorrectly.\n"
                    f"    expected: {set(expected)}\n"
                    f"    found:    {set(found)}\n"
                    "    Will try to read file."
                )

            for i, row in enumerate(reader, start=1):
                date_str = (row.get("date") or "").strip()
                category = (row.get("category") or "").strip()
                amount_raw = (row.get("amount") or "").strip()
                description = (row.get("description") or "").strip()

                has_all = bool(date_str and category and amount_raw and description)
                date_ok = False
                amount_ok = False
                amount_val: Decimal | None = None
                date_norm: str | None = None

                if has_all:
                    try:
                        date_norm = validate_date(date_str)
                        date_ok = True
                    except ValueError:
                        print(f"  · Skip row {i} for invalid entry '{date_str}'. date must be in this format (YYYY-MM-DD)")

                    if date_ok:
                        try:
                            amount_val = parse_amount(amount_raw)
                            amount_ok = True
                        except ValueError:
                            print(f"  · Skip row {i} due to invalid input '{amount_raw}'.")
                else:
                    print(f"  · Skip row {i} for invalid input.")

                if has_all and date_ok and amount_ok and (amount_val is not None) and (date_norm is not None):
                    loaded.append(
                        {
                            "date": date_norm,             
                            "category": category,
                            "amount": float(amount_val), 
                            "description": description,
                        }
                    )

    except Exception as e:
        print(f"Failedto load Expense from '{path}': {e}")
        return []

    return loaded

## create interactive menu


def main():
   
    # documented expense history
    
    expenses = load_expenses(CSV_FILE)

    monthly: Decimal | None = None

    print("Budget and expense tracker.")
    if expenses:
        print(f"Loaded {len(expenses)} expense(s) from '{CSV_FILE}'.")
    else:
        print("No expenses recorded.")

    try:
        running = True
        while running:
                    print("\nChoices")
                    print("  1) Add expenses")
                    print("  2) Display expenses")
                    print("  3) Track budget")
                    print("  4) Save inputs")
                    print("  5) Exit")

                    choice = input("Pick option 1-5 ").strip()

                    if choice == "1":
                        add_expense(expenses)

                    elif choice == "2":
                        display(expenses)

                    elif choice == "3":
                        monthly = track_budget(expenses, monthly)

                    elif choice == "4":
                        save_expenses(CSV_FILE, expenses)

                    elif choice == "5":
                        save_expenses(CSV_FILE, expenses)
                        print("You are now exiting.")
                        running = False 

                    else:
                        print("Choice is invalid. Please try again and select 1-5")

    except (KeyboardInterrupt, SystemExit):
                            print("\Exiting. Goodbye.")
                            save_expenses(CSV_FILE, expenses)


if __name__ == "__main__":
    main()


with open("expenses.csv", "r", encoding="utf-8") as f:
    print(f.read())



