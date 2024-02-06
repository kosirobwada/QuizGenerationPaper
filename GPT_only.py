import openai
import json
from dotenv import load_dotenv
import os
from datetime import datetime
import wikipedia

# 環境変数を読み込む
load_dotenv()

# OpenAI APIキーを設定
openai.api_key = os.getenv('OPENAI_API_KEY')

def generate_quiz(theme, model="gpt-4", temperature=0):
    prompt = f"テーマ:{theme}に関するクイズの問題文とその答えを1つ作成してください。\n"
    "ただし、答えは文章ではなく、単語1つのみにしてください。\n"
    response = openai.chat.completions.create(
        model=model,
        # prompt=prompt,
        messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
        temperature=temperature,
        max_tokens=1000,
    )
    text = response.choices[0].message.content.strip()
    if "答え" in text:
        print(text)    
        question, answer = text.split("答え: ", 1)
        question = question[4:].strip()
        answer = answer.strip()
        print(question)
        print(answer)
        return question, answer
    else:
        return None, None

# JSONファイルを読み込む
data = []
with open('input_data.jsonl', 'r', encoding='utf-8') as file:
    for line in file:
        data.append(json.loads(line))

# テーマに基づいてクイズを生成し、結果を格納
quiz_results = []
for item in data:
    theme = item.get("theme")
    if theme:
        question, answer = generate_quiz(theme)
        if question and answer:  # 有効なクイズが生成された場合のみ追加
            quiz_results.append({"theme": theme, "quiz": question, "answer": answer})

# タイムスタンプを取得してファイル名を生成
timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
output_dir = "GPT_only_output"
output_filename = f"output_GPTonly_{timestamp}.jsonl"
output_path = os.path.join(output_dir, output_filename)

# 結果をJSONLファイルに保存
with open(output_filename, 'w', encoding='utf-8') as file:
    for item in quiz_results:
        json.dump(item, file, ensure_ascii=False)
        file.write('\n')