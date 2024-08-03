import openai
import pandas as pd
import sys
import subprocess
import os
from contact_finder import main as find_contact
import re
import yaml

def load_config(config_file='config.yml'):
    with open(config_file, 'r') as file:
        return yaml.safe_load(file)
    
# <-----------------------------------------------------------------------> #
# Function to split the text into the required parts
def split_text(text):
    # Define the keywords to search for
    content_keyword = "내용: "
    follow_up_keyword = "Follow up task:"

    # Find the positions of the keywords
    content_pos = text.find(content_keyword)
    follow_up_pos = text.find(follow_up_keyword)

    # Extract the parts of the text based on the positions of the keywords
    content = text[content_pos + len(content_keyword):follow_up_pos].strip()
    follow_up = text[follow_up_pos + len(follow_up_keyword):].strip()

    return content, follow_up
# <-----------------------------------------------------------------------> #

# <-----------------------------------------------------------------------> #
# OpenAI API key setup
# TODO:: Sehyoun: I recommend using the system environment variable for the API key
config = load_config('config.yml')
openai.api_key = config['openai_api']['key']
# <-----------------------------------------------------------------------> #

# <-----------------------------------------------------------------------> #
def process_audio_file(audio_file_path):
    # Read audio file and convert to text using OpenAI's Whisper
    with open(audio_file_path, 'rb') as audio_file:
        transcription = openai.Audio.transcribe("whisper-1", audio_file)
        text_content = transcription['text']
        
    phone_match = re.search(r"-(\d+)_", audio_file_path)
    if phone_match:
        phone_content = phone_match.group(1)
    else:
        phone_content = "발신자 정보 없음"

    date_content = audio_file_path.split("_")[1][ :8]                          
    # <-----------------------------------------------------------------------> #

    # <-----------------------------------------------------------------------> #
    # Text parsing and summarization (GPT model)
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that extracts and summarizes information."},
            {"role": "user", "content": f"다음 텍스트에서 내용을 자세하게 추출하고(내용은 넘버링 하지 말 것) follow up task는 요약하여 숫자를 넘버링해 생성해 주세요:\n\n{text_content}\n\n포맷은 다음과 같습니다:내용: [추출된 내용]\nFollow up task: [생성된 follow up task]"},
        ]
    )
    parsed_response = response['choices'][0]['message']['content'].strip()
    # <-----------------------------------------------------------------------> #

    # <-----------------------------------------------------------------------> #
    # result to DataFrame processing
    content, follow_up = split_text(parsed_response)
    # phone을 parameter로 contact_finder.py 실행
    contact_details = find_contact(phone_content)

    data = {
        '시간(날짜)': [date_content],
        '번호': [str(phone_content)],
        '내용': [content],
        'Follow up task': [follow_up],
        '연락처': [contact_details]
    }
    df = pd.DataFrame(data)
    # <-----------------------------------------------------------------------> #

    # <-----------------------------------------------------------------------> #
    # Save DataFrame to a temporary file
    temp_file = 'temp.xlsx'
    df.to_excel(temp_file, index=False)

    # Execute file_save.py with the temporary file as argument
    try:
        subprocess.run(["python", "file_save.py", temp_file], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error during processing: {e.stderr}")

    # Remove the temporary file
    os.remove(temp_file)

    print(f"'{temp_file}' has been processed and deleted")
    # <-----------------------------------------------------------------------> #

# <-----------------------------------------------------------------------> #
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python summarize_audio.py <audio_file_path>")
        sys.exit(1)

    audio_file_path = sys.argv[1]
    process_audio_file(audio_file_path)
# <-----------------------------------------------------------------------> #
