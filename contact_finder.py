import requests
import json
import re
import sys
import yaml

# Function to load configuration from YAML file
def load_config(config_file='config.yml'):
    with open(config_file, 'r') as file:
        return yaml.safe_load(file)
    
# Function to remove non-numeric characters
def extract_numbers(text):
    return re.sub(r'\D', '', text)

# Function to retrieve contacts
def retrieve_contacts(api_url, headers, board_id, find_phone):
    cursor = None
    all_contacts = []
    
    while True:
        # Create the query with or without the cursor
        query = f"""
        query {{
          boards(ids: {board_id}) {{
            name
            items_page (limit: 500{f', cursor: "{cursor}"' if cursor else ''}) {{
              cursor
              items {{
                name
                column_values(ids: ["dup__of_____", "____6"]) {{
                  text
                }}
              }}
            }}
          }}
        }}
        """
        data = {'query': query}
        
        # Make the API request
        response = requests.post(url=api_url, json=data, headers=headers)
        
        if response.status_code == 200:
            schema = response.json()
            items_page = schema.get('data', {}).get('boards', [])[0].get('items_page', {})
            items = items_page.get('items', [])
            
            for item in items:
                name = item.get('name')
                column_values = item.get('column_values', [])
                phone_numbers = [extract_numbers(col.get('text', '')) for col in column_values]
                all_contacts.append([name] + phone_numbers)
            
            # Update the cursor
            cursor = items_page.get('cursor')
            
            # If cursor is None, break the loop
            if cursor is None:
                break
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            break
    sw = 0
    # Find the phone in contacts
    for contact in all_contacts:
        if find_phone in contact:
            if contact[1] == find_phone:
                sw = 1
                return (contact[0] + " 학부모")

            else:
                sw = 1
                return (contact[0] + " 학생")
    if sw == 0:
      return ("찾을 수 없는 연락처")

def main(find_phone):
    config = load_config('config.yml')
    board_id = config['board']['id']
    api_key = config['monday_api']['key']
    api_url = config['monday_api']['url']
    headers = {"Authorization": api_key}
    return retrieve_contacts(api_url, headers, board_id, find_phone)

# Main function
if __name__ == "__main__":
    if len(sys.argv) > 1:
        find_phone = sys.argv[1]
        find_phone = extract_numbers(find_phone)
    else:
        print("Please provide a phone number.")
        sys.exit(1)
    