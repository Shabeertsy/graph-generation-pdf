## Gemini api
import google.generativeai as genai
import json


GOOGLE_API_KEY='AIzaSyDEV_jYzVybr77UimtNLrTKoyO-DF9Z_3s'

def gemini_ai(prompt,model='gemini-pro',json_format=True):
    # print(prompt)

    ## Using Gemini
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel(model)
    try:
        response = model.generate_content(prompt)
        story=response.text
        if json_format:
            story_data = json.loads(story) 
        else:
            story_data = story
        
    except Exception as e:
        return {'message':'something went wrong','error':str(e),'flag':False,'data':{}}
    return {'data':story_data,'flag':True}
