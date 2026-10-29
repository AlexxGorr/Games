import json


def load_db(filename):
    with open(filename) as file:
        db = json.load(file)
    return db


def save_db(filename, db):
    with open(filename, 'w') as file:
        json.dump(db, file, indent=2)


def log_in(db):
    username = input('Enter name: ')
    score = input('score: ')
    db.append(
        {
            "username": username,
            "score": score
        }
    )


def main(filename):
    db = load_db(filename)
    for i in range(len(db)):
        print(f'username: {db[i]["username"]} | score: {db[i]["score"]}')

    log_in(db)
    save_db(filename, db)



main('user.json')

















