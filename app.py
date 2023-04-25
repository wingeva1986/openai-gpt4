import quora
import phind
from time import sleep
from flask import Flask, request, Response, render_template
import threading
import json
import requests
import os

app = Flask(__name__)


    

@app.route('/phindconv', methods=['POST'])
def phindconv():
    json_data = request.get_json()
    q = json_data.get('message', '你好')
    m = json_data.get('conversationId')
    t = json_data.get('parentMessageId')
    def event_stream(m,q,t):
        for response in phind.StreamingCompletion.create(
            model  = 'gpt-4',
            prompt = q,
            results     = phind.Search.create(q, actualSearch = False), # create search (set actualSearch to False to disable internet)
            creative    = False,
            detailed    = False,
            codeContext = '以中文回答'): # up to 3000 chars of code
            yield f'data: {json.dumps(response.completion.choices[0].text)}\n\n'
        #result=response.completion.choices[0].text.split("\r\n")
        #for r in result:
            #yield f'data: "{r}"\n\n'
        yield "data: [DONE]\n\n"

    return Response(event_stream(m,q,t), content_type='text/event-stream')

    
@app.route('/conversation', methods=['POST'])
def conversation():
    json_data = request.get_json()
    q = json_data.get('message', '你好')
    m = json_data.get('conversationId')
    t = json_data.get('parentMessageId')
    if t==None:
        t=json.loads(requests.get(os.getenv("POE_BASE_URL")+"/getGPT3").text)["_id"]
        #t = quora.Account.get()
        #sleep(2) 
    if m==None:
        m = 'gpt-3.5-turbo'
    event=json.dumps({"conversationId":m,"parentMessageId":t})
    def event_stream(m,q,t):
        for text in ask(m,q,t):  
            yield f"data: {text}\n\n"
        yield f"data: {event}\n\n"   
        yield "data: [DONE]\n\n"

    return Response(event_stream(m,q,t), content_type='text/event-stream')

@app.route('/poeconv', methods=['POST'])
def poeconv():
    json_data = request.get_json()
    q = json_data.get('message', '你好')
    m = json_data.get('conversationId')
    t = json_data.get('parentMessageId')
    if t==None:
        t=json.loads(requests.get(os.getenv("POE_BASE_URL")+"/getGPT4").text)["_id"]
        #sleep(2)
 
    if m==None:
        m = 'gpt-4'#'gpt-3.5-turbo'
    #event=json.dumps({"conversationId":m,"parentMessageId":t})
    def event_stream(m,q,t):
        for text in ask(m,q,t):  
            yield f"data: {text}\n\n"
        #yield f"data: {event}\n\n"   
        yield "data: [DONE]\n\n"

    return Response(event_stream(m,q,t), content_type='text/event-stream')

def ask(model,prompt,token):
    for response in quora.StreamingCompletion.create(model=model, prompt=prompt, token=token):
        yield json.dumps(response.completion.choices[0].text)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True, threaded=True)
