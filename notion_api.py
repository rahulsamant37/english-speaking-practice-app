import requests
import json

def create_block_object(block_type, rich_text_types_and_contents=None):
  if rich_text_types_and_contents is None:
    return {
            "object": "block",
            "type": block_type,
            block_type: {}
          }
  if isinstance(rich_text_types_and_contents, tuple) and len(rich_text_types_and_contents) == 2:
    t, c = rich_text_types_and_contents
    return {
              "object": "block",
              "type": block_type,
              block_type: {
                "rich_text": [
                  {
                    "type": t,
                    t: {
                      "content": c
                    }
                  }
                ]
              }
            }

def send_patch_request(url, token, data):
  headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json',
    'Notion-Version': '2022-06-28'
  }
  response = requests.patch(url, headers=headers, data=json.dumps(data))

  if response.status_code == 200:
    print("Succeeded.")
  else:
    print("Failed.")
    print("Response:", response.text)
