import openai
import json
from dotenv import load_dotenv
import os
from datetime import datetime
import wikipedia
import time

# 環境変数を読み込む
load_dotenv()

start_time = time.time()

wikipedia.set_lang("ja")

# OpenAI APIキーを設定
openai.api_key = os.getenv('OPENAI_API_KEY')

def retrieve_information(theme):
    try:
        # Wikipediaからテーマに関連する情報を取得
        page = wikipedia.page(theme)
        return page.content[:1500]  # 最初の1500文字を取得
    except:
        return None
    
def extract_questions_and_answers(text):
    # 問題と答えのペアを格納するリスト
    qa_pairs = []

    # 問題と答えのテキストを分割
    parts = text.split("問題")
    
    # 最初の要素は空なので、2番目の要素から処理を開始
    for part in parts[1:]:
        # 各部分から問題と答えを抽出
        question_part, answer = part.split("答え：")
        # "問題" と数字の間にある余分なスペースや記号を削除
        question = "問題" + question_part.strip()
        # 答えの余分なスペースを削除
        answer = answer.strip()
        # 抽出した問題と答えのペアをリストに追加
        qa_pairs.append((question, answer))

    return qa_pairs
    
def generate_quiz(theme, model="gpt-4", temperature=0):
    retrieved_content = retrieve_information(theme)
    prompt = (
        f"以下の情報に基づいて、テーマ:{theme}に関する早押しクイズの問題文とその答えを3つ作成してください。\n"
        "答えは必ず単語で答えられる問題を生成してください。\n"
        "ただし、答えは「答え：」で始めてください。...\n"
        "問題作成のポイント：\n"
        "- 問題文から答えが一意に絞り込めるか。\n"
        "- 問題文と想定解が正しく対応しているか。\n"
        "- 問題文と想定解が正しい内容と言えるか。\n"
        f"情報：{retrieved_content}\n"
    )
    response = openai.chat.completions.create(
        model=model,
        messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
        temperature=temperature,
        max_tokens=1000,
    )
    text = response.choices[0].message.content.strip()
    qa_pairs = extract_questions_and_answers(text)
    if "答え" in text:
        print("generate\n")
        print(qa_pairs)
        return qa_pairs
    else:
        return None, None

def choise_quiz(theme, qa_pairs, model="gpt-4", temperature=0):
    prompt = (
        f"以下の、テーマ:{theme}に関する3つの早押しクイズの問題文と答えのうち、最も良いクイズと答えをセットで出力してください。\n"
        f"{qa_pairs}\n"
        "評価のポイント：\n"
        "- 問題文から答えが一意に絞り込めるか。\n"
        "- 問題文と想定解が正しく対応しているか。\n"
        "- 問題文と想定解が正しい内容と言えるか。\n"
        "出力は、問題と答えのみにしてください。余計な日本語は入れないでください。\n"
        "問題は、「問題：」、答えは「答え：」で始めてください。\n"
    )
    response = openai.chat.completions.create(
        model=model,
        messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
        temperature=temperature,
        max_tokens=1000,
    )
    text = response.choices[0].message.content.strip()
    question, answer = text.split("答え：")
    question = question[3:].strip()
    answer = answer.strip()
    print("choise\n")
    print(question)
    print(answer)
    return question, answer

def review_quiz(quiz_question, quiz_answer, model="gpt-4", temperature=0):
    prompt = (
        f"以下のクイズの問題と答えをレビューしてください。\n\n"
        f"問題：{quiz_question}\n"
        f"答え：{quiz_answer}\n\n"
        "このクイズの質はどうですか？ 問題や答えに改善が必要な点はありますか？\n"
        "レビューのポイント：\n"
        "- 問題の語句に修飾語を付けるとしたらどこに何を付けるか。\n"
        "- 問題文から答えが一意に絞り込めるか。\n"
        "- 問題文と想定解が正しく対応しているか。\n"
        "- 問題文に雑学的なトピックや興味深い情報などが適切に盛り込まれているか。具体的にどんなトピックを入れるかを考えてください。\n"
        "上記のポイントに基づいて、クイズの質を評価し、改善が必要な点を指摘してください。"
        "簡潔な文よりも、冗長な文の方が好ましいです。"
        "ただし、問題文は複数になってはいけません。"
        "また、解答も単語にならなければなりません。" 
        "補足情報は名詞を修飾する形で、必ず問題文に入れてください。"           
    )

    response = openai.chat.completions.create(
        model=model,
        messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
        temperature=temperature,
        max_tokens=1000,
    )

    review_result = response.choices[0].message.content
    print("review\n")
    print(review_result)
    return quiz_question, quiz_answer, review_result.strip()

def final_quiz(theme, quiz_question, quiz_answer, review_result, model="gpt-4", temperature=0):
    prompt = (
        f"以下のレビューを参考にして最終的な問題と答えを作成してください。\n\n"
            "ただし、答えは「答え：」で始めてください。...\n\n"
            "また、問題文は複数の文にならないようにしてください。"
            "日本語として違和感のない文章にしてください。"
            f"テーマ：{theme}\n"
            f"問題：{quiz_question}\n"
            f"答え：{quiz_answer}\n\n"
            f"レビュー：{review_result}"  
        )
    response = openai.chat.completions.create(
        model=model,
        messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
        temperature=temperature,
        max_tokens=1000,
    )
    text = response.choices[0].message.content
    question, answer = text.split("答え：")
    question = question[3:].strip()
    answer = answer.strip()
    print("final\n")
    print(question)
    print(answer)
    return question, answer

# JSONファイルを読み込む
data = []
with open('input_data1.jsonl', 'r', encoding='utf-8') as file:
    for line in file:
        data.append(json.loads(line))

# テーマに基づいてクイズを生成し、結果を格納
quiz_results = []
for item in data:
    theme = item.get("theme")
    if theme:
        # generate_quizで問題を生成
        questions_and_answers = generate_quiz(theme)
        if questions_and_answers:
            # choise_quizでクイズの選択を行い、結果を取得
            question, answer = choise_quiz(theme, questions_and_answers)
            if question and answer:
                question, answer, review = review_quiz(question, answer)
                if question and answer and review:  
                    question, answer = final_quiz(theme, question, answer, review)
                    quiz_results.append({"theme": theme, "quiz": question, "answer": answer})
                
# タイムスタンプを取得してファイル名を生成
timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
output_filename = f"output_GPTRAG_{timestamp}.jsonl"

# 結果をJSONLファイルに保存
with open(output_filename, 'w', encoding='utf-8') as file:
    for item in quiz_results:
        json.dump(item, file, ensure_ascii=False)
        file.write('\n')