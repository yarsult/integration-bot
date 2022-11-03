import sqlite3


def get_last_asked_question(user_id, sort_of_question):
    con = sqlite3.connect("main_db.db")
    cur = con.cursor()
    res = cur.execute(f"SELECT {sort_of_question} FROM user_info WHERE user_id = {user_id}").fetchall()
    con.commit()
    con.close()
    return res[0][0]


def update_user_last_asked_question(question_id, user_id, sort_of_question):
    con = sqlite3.connect("main_db.db")
    cur = con.cursor()
    cur.execute(f"UPDATE user_info SET [{sort_of_question}] = {question_id} WHERE user_id = {user_id}")
    con.commit()
    con.close()


def get_question(question_id, sort_of_question):
    con = sqlite3.connect("main_db.db")
    cur = con.cursor()
    res = cur.execute(f"SELECT question FROM {sort_of_question} WHERE question_id = {question_id}").fetchone()[0]
    answers = cur.execute(f"SELECT answer_variants FROM {sort_of_question} WHERE question_id = {question_id}").fetchone()[0]
    right_ans = cur.execute(f"SELECT answer_right FROM {sort_of_question} WHERE question_id = {question_id}").fetchone()[0]
    con.close()
    return [res, answers, right_ans]

