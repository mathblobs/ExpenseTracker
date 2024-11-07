import os
import argparse
import csv
from datetime import datetime
import json

csv_file = "Expenses.csv"

def load():
    data = {}
    try:
        with open(csv_file, newline="") as file:
             reader = csv.DictReader(file)
             for row in reader:
                 row_id = row["ID"]
                 row_data = dict(row)
                 data[row_id] = row_data
    except FileNotFoundError:
        with open(csv_file, mode='w', newline='') as file:
            pass
    return data

def save(data):
    fieldnames = ["ID"] + list(data[next(iter(data))].keys()) # needs to be adjusted on the number of Expenses in there
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for key, value in data.items():
            row = {"ID": key}
            row.update(value)
            writer.writerow(row)


def set_budget(setting_budget, setting_month):
    threshold_month = {"threshold" : setting_budget, "month" : setting_month}
    with open("threshold.json", "w") as file:
        json.dump(threshold_month, file)
    print(threshold_month)



def add(description, amount, category):
    data = load()
    if not data:
        id = "1"
    else:
        blub2 = []
        for i in data.keys():
            blub2.append(int(i))
        id = str(max(blub2) + 1)
    
    data[id] = {
        "description": description,
        "amount": amount,
        "category": category,
        "createdAt": datetime.today().isoformat(),
        "updatedAt": datetime.today().isoformat()
    }
    save(data)

    if os.path.exists("threshold.json"):
        with open("threshold.json", "r") as file:
            threshold_month = json.load(file)

    if threshold_month["threshold"] != 0 and threshold_month["month"] != 0:
       keys = filters(threshold_month["month"])
       print(threshold_month["threshold"], threshold_month["month"])
       print(keys)
       sum_of_expenses_for_month = 0
       for i in keys:
           sum_of_expenses_for_month = sum_of_expenses_for_month + int(data[i]["amount"])
       if sum_of_expenses_for_month >= threshold_month["threshold"]:
           print("Warning, the monthly budget is more than what planned")


def update(id, new_description, new_amount, new_category):
    data = load()
    data[id]["description"] = new_description
    data[id]["amount"] = new_amount
    data[id]["category"] = new_category
    data[id]["updatedAt"] = datetime.today().isoformat()
    save(data)

def delete(ID):
    data = load()
    if ID in data:
        del(data[ID])
    else:
        print("Id not found")
    save(data)



def filters(time_category):
    data = load()
    id_filtered_expenses = []
    if type(time_category) == int and len(list(str(time_category))) == 2:
        for i in data.keys():
            if data[i]["createdAt"][5:7] == str(time_category):
                id_filtered_expenses.append(i)
    elif type(time_category) == int and len(list(str(time_category))) == 4:
        for i in data.keys():
            if data[i]["createdAt"][0:4] == str(time_category):
                id_filtered_expenses.append(i)
    else:
        for i in data.keys():
            if data[i]["category"] == time_category:
                id_filtered_expenses.append(i)
    return id_filtered_expenses


def summary(kinds = "all" ):
    data = load()
    sum1 = 0
    print(type(kinds), kinds)
    if kinds == "all":
        print(sum1)
        for i in data.keys():
            sum1 = int(data[i]["amount"]) + sum1
    else:
        try:
            kinds = int(kinds)
        except ValueError:
            pass
        keys = filters(kinds)
        print(keys)
        for i in keys:
            sum1 = int(data[i]["amount"]) + sum1
        print(sum1)
    print("Total expenses: ", sum1)

def view(kinds="all"):
    data = load()
    if kinds == "all":
        for i in data.keys():
            print(i)
            print(data[i]["createdAt"][0:10])
            print(data[i]["description"])
            print(data[i]["amount"])
    else:
        try:
            kinds = int(kinds)
        except ValueError:
            pass
        keys = filters(kinds)
        for i in keys:
            print("Expenses sorted after ", kinds)
            print(i)
            print(data[i]["createdAt"][0:10])
            print(data[i]["description"])
            print(data[i]["amount"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="ExpenseTracker", description="Expenses")
    subparsers = parser.add_subparsers(dest="command")

    add_parser = subparsers.add_parser("add", help="Add a new expense.")
    add_parser.add_argument("description", type=str, help="The description of the expense.")
    add_parser.add_argument("amount", type=int, help="The amount of the expense.")
    add_parser.add_argument("category", type=str, help="The type of expense.")

    update_parser = subparsers.add_parser("update", help="Update an existing expense.")
    update_parser.add_argument("id", type=int, help="The ID od the expense to update.")
    update_parser.add_argument("description", type=str, help="the new description of the expense.")
    update_parser.add_argument("amount", type=str, help="the new amount of the expense.")

    delete_parser = subparsers.add_parser("delete", help="Delete an existing task.")
    delete_parser.add_argument("id", type=str, help="The ID of the task to delete.")

    summary_parser = subparsers.add_parser("summary", help="Total amount of expenses")
    summary_parser.add_argument("time_category", type=str, help="The category or timeframe.")

    view_parser = subparsers.add_parser("viewing", help="Marking a Task as done.")
    view_parser.add_argument("time_category", type=str, help="Status of the expenses at hand.")

    budget_parser = subparsers.add_parser("budgeting", help="Setting a budget for the month.")
    budget_parser.add_argument("budget", type=int, help="The Budget amount.")
    budget_parser.add_argument("month", type=int, help="The budget for the specific month.")

    args = parser.parse_args()

    if args.command == "add":
        add(args.description, args.amount, args.category)
    elif args.command == "update":
        update(args.id, args.description, args.amount)
    elif args.command == "delete":
        delete(args.id)
    elif args.command == "summary":
        summary(args.time_category)
    elif args.command == "viewing":
        view(args.time_category)
    elif args.command == "budgeting":
        set_budget(args.budget, args.month)