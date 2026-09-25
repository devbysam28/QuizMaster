from app import app


def test_health():
    client = app.test_client()

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json["status"] == "ok"


def test_home_page():
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200
    assert b"QuizMaster" in response.data


def test_quiz_submission():
    client = app.test_client()

    data = {
        "question_0": "Python",
        "question_1": "Git",
        "question_2": "Application Programming Interface",
        "question_3": "Docker",
        "question_4": "Continuous Integration",
    }

    response = client.post(
        "/quiz/1/submit",
        data=data,
    )

    assert response.status_code == 200
    assert b"5<span>/5</span>" in response.data
    assert b"100%" in response.data


def test_quizzes_api():
    client = app.test_client()

    response = client.get("/api/quizzes")

    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) >= 1
    assert "title" in response.json[0]
    assert "questions" in response.json[0]


def test_invalid_quiz():
    client = app.test_client()

    response = client.get("/quiz/99999")

    assert response.status_code == 404


def test_create_page():
    client = app.test_client()

    response = client.get("/create")

    assert response.status_code == 200
    assert b"Create a New Quiz" in response.data


def test_manage_page():
    client = app.test_client()

    response = client.get("/manage")

    assert response.status_code == 200
    assert b"Your Quizzes" in response.data
