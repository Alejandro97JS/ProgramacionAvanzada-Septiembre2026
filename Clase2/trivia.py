import requests
import html
import random

def get_trivia_question(category=None, difficulty=None, amount=1, question_type="multiple"):
    base_url = "https://opentdb.com/api.php"
    params = {
        "amount": amount,
        "type": question_type
    }
    if category:
        params["category"] = category
    if difficulty:
        params["difficulty"] = difficulty
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        if data["response_code"] == 0:
            return data["results"]
        else:
            print(f"No questions found for the given parameters.")
            return []
    except requests.RequestException as e:
        print(f"Error fetching trivia questions: {e}")
        return []

def main():
    print("🔹 Trivia API Test 🔹\n")
    questions = get_trivia_question(amount=3)
    for q in questions:
        question = html.unescape(q["question"])
        correct_answer = html.unescape(q["correct_answer"])
        all_answers = q["incorrect_answers"] + [correct_answer]
        random.shuffle(all_answers)
        print(f"❓ Question: {question}")
        print("Options:")
        for i, option in enumerate(all_answers, 1):
            print(f"  {i}. {html.unescape(option)}")
        print(f"✅ Correct Answer: {correct_answer}\n")

if __name__ == "__main__":
    main()
