from typing_extensions import runtime
from flask import request, Flask, render_template, url_for, flash, redirect   # Import these flask functions
import pandas as pd
import numpy as np
import os
import time,timeago, datetime

app = Flask(__name__)
rubric_folder = "data"
rubric_dir = "data/Lab2_21_Rubric.xlsx"

def read_data(path = rubric_folder):
    xlsxs = [i for i in os.listdir(path) if (".xlsx" in i)and("~$" not in i)]
    xlsxs = sorted(xlsxs, key=lambda t: -os.stat(os.path.join(path, t)).st_mtime)
    date = datetime.datetime.now()
    status = [ timeago.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime ( os.path.join(path, i) )  )) ,date) for i in xlsxs]
    return xlsxs,status

def read_rubric(path = rubric_dir):
    return pd.read_excel(path)

def render_rubric(rubric = read_rubric()):
    columns = rubric.columns
    columns = columns[0:3]
    data = []
    for index, row  in rubric.iterrows():
        data.append(row[columns].replace(np.nan, "", regex=True))
    return data, len(data)

def render_grading(rubric = read_rubric()):
    rubric=rubric.replace(np.nan, 0, regex=True)
    columns = rubric.columns
    people = [ i for i in columns[3:] if "comment" not in i]
    data  = []
    for i in range(len(people)):
        the_p = people[i]
        total_grade=np.sum(np.array(rubric[the_p].values))
        simple_comment = f"{total_grade}/100"
        comment_col = f'{the_p}-comment'
        if comment_col in columns:
            simple_comment += f". {list(rubric[comment_col].values)[-1]}"
        data.append([the_p, total_grade,simple_comment])
    return data, len(data)

def render_one_grade(pid ,rubric = read_rubric()):
    rubric = rubric.replace(np.nan, '', regex=True)
    columns = rubric.columns
    people = [ i for i in columns[3:] if "comment" not in i]
    the_p = people[pid]
    data = []
    for row  in rubric[the_p]:
        data.append(row)
    the_p_comment = f"{people[pid]}-comment"
    comments = []
    if the_p_comment not in columns:
        comments = []*len(data)
        return data, the_p,comments
    else:
        for row  in rubric[the_p_comment]:
            comments.append(row)
        return data, the_p,comments


def save_rubric(rubric,rubric_dir):
    rubric.to_excel(rubric_dir,index=False)

@app.route("/")
def main():
    xlsxs,status= read_data()
    return render_template("index.html",xlsxs=xlsxs,len = len(xlsxs),status=status)

@app.route("/view/<rfile>/<int:pid>", methods=["GET", "POST"])
def view(rfile,pid):
    rubric = read_rubric(os.path.join(rubric_folder, rfile))
    data, len = render_rubric(rubric = rubric)
    _,num_ppl = render_grading(rubric = rubric)
    grade, person,comments = render_one_grade(pid, rubric = rubric)

    if request.method.upper() == "POST":
        inputs = []
        for i in range(len):
            inputs.append(request.form.get(f"grade_{i}"))

        new_comments = []
        for i in range(len):
            new_comments.append(request.form.get(f"comment_{i}"))
        rubric[person] = inputs 
        rubric[f'{person}-comment'] = new_comments
        # print(rubric)
        save_rubric(rubric, os.path.join(rubric_folder, rfile))
        # return redirect(url_for("overview",rfile=rfile))
        return redirect(url_for("view",rfile=rfile,pid=pid+1))
    return render_template("view.html",data=data,len = len,grades=grade, person=person, comments=comments,rfile=rfile,pid=pid,num_ppl=num_ppl)

@app.route("/view/<rfile>")
def overview(rfile):
    rubric = read_rubric(os.path.join(rubric_folder, rfile))
    data, len = render_grading(rubric = rubric)
    return render_template("overview.html",data=data,len = len,rfile=rfile)


if __name__ =="__main__":
    app.run(debug=True)