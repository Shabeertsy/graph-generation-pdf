## Gemini api
import google.generativeai as genai
import json


GOOGLE_API_KEY=''
def gemini_ai(prompt, model='gemini-pro', json_format=True, max_retries=10):
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel(model)

    try:
        response = model.generate_content(prompt)
        story = response.text


        if json_format:
            for _ in range(max_retries):
                try:
                    story_data = json.loads(story) 
                    return {'data': story_data, 'flag': True}
                except json.JSONDecodeError as e:
                    print(f"JSON decoding failed: {e}. Retrying...")
                    response = model.generate_content(prompt)  
                    story = response.text
            
            return {'message': 'Failed to parse JSON after retries', 'error': str(e), 'flag': False, 'data': {}}
        else:
            return {'data': story, 'flag': True}

    except Exception as e:
        print(f"Error: {e}")
        return {'message': 'Something went wrong', 'error': str(e), 'flag': False, 'data': {}}
