import json
import os

from flask import Flask, jsonify, redirect, render_template, request, url_for

app = Flask(__name__)

DATA_FILE = "data/quizzes.json"
COMMIT = os.getenv("RENDER_GIT_COMMIT", "local")[:7]


def load_quizzes():
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_quizzes(quizzes):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(quizzes, file, indent=2)


def get_next_id(quizzes):
    if not quizzes:
        return 1

    return max(quiz["id"] for quiz in quizzes) + 1


def build_questions(form):
    questions = []

    try:
        question_count = int(form.get("question_count", 0))
    except ValueError:
        question_count = 0

    for index in range(question_count):
        question_text = form.get(
            f"question_{index}",
            "",
        ).strip()

        options = [
            form.get(f"option_{index}_0", "").strip(),
            form.get(f"option_{index}_1", "").strip(),
            form.get(f"option_{index}_2", "").strip(),
            form.get(f"option_{index}_3", "").strip(),
        ]

        answer_index = form.get(
            f"answer_{index}",
            "",
        )

        if not question_text or not all(options):
            continue

        try:
            answer = options[int(answer_index)]
        except (ValueError, IndexError):
            continue

        questions.append(
            {
                "question": question_text,
                "options": options,
                "answer": answer,
            }
        )

    return questions


@app.route("/")
def home():
    quizzes = load_quizzes()

    return render_template(
        "home.html",
        quizzes=quizzes,
        commit=COMMIT,
    )


@app.route("/quiz/<int:quiz_id>")
def take_quiz(quiz_id):
    quizzes = load_quizzes()

    quiz = next(
        (quiz for quiz in quizzes if quiz["id"] == quiz_id),
        None,
    )

    if quiz is None:
        return "Quiz not found", 404

    return render_template(
        "quiz.html",
        quiz=quiz,
        commit=COMMIT,
    )


@app.route("/quiz/<int:quiz_id>/submit", methods=["POST"])
def submit_quiz(quiz_id):
    quizzes = load_quizzes()

    quiz = next(
        (quiz for quiz in quizzes if quiz["id"] == quiz_id),
        None,
    )

    if quiz is None:
        return "Quiz not found", 404

    score = 0

    for index, question in enumerate(quiz["questions"]):
        selected = request.form.get(f"question_{index}")

        if selected == question["answer"]:
            score += 1

    total = len(quiz["questions"])
    percentage = round((score / total) * 100) if total else 0

    return render_template(
        "result.html",
        quiz=quiz,
        score=score,
        total=total,
        percentage=percentage,
        commit=COMMIT,
    )


@app.route("/create", methods=["GET", "POST"])
def create_quiz():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        questions = build_questions(request.form)

        if title and questions:
            quizzes = load_quizzes()

            quizzes.append(
                {
                    "id": get_next_id(quizzes),
                    "title": title,
                    "description": description,
                    "questions": questions,
                }
            )

            save_quizzes(quizzes)

            return redirect(url_for("home"))

    return render_template(
        "create.html",
        commit=COMMIT,
    )


@app.route("/manage")
def manage_quizzes():
    quizzes = load_quizzes()

    return render_template(
        "manage.html",
        quizzes=quizzes,
        commit=COMMIT,
    )


@app.route("/edit/<int:quiz_id>", methods=["GET", "POST"])
def edit_quiz(quiz_id):
    quizzes = load_quizzes()

    quiz = next(
        (quiz for quiz in quizzes if quiz["id"] == quiz_id),
        None,
    )

    if quiz is None:
        return "Quiz not found", 404

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        questions = build_questions(request.form)

        if title and questions:
            quiz["title"] = title
            quiz["description"] = description
            quiz["questions"] = questions

            save_quizzes(quizzes)

            return redirect(url_for("manage_quizzes"))

    return render_template(
        "edit.html",
        quiz=quiz,
        commit=COMMIT,
    )


@app.route("/delete/<int:quiz_id>", methods=["POST"])
def delete_quiz(quiz_id):
    quizzes = load_quizzes()

    quizzes = [
        quiz
        for quiz in quizzes
        if quiz["id"] != quiz_id
    ]

    save_quizzes(quizzes)

    return redirect(url_for("manage_quizzes"))


@app.route("/api/quizzes")
def api_quizzes():
    quizzes = load_quizzes()

    return jsonify(quizzes)


@app.route("/health")
def health():
    return jsonify(
        {
            "status": "ok",
            "commit": COMMIT,
        }
    )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", 5000)),
    )
