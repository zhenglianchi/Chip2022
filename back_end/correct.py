from correction.similar import similar
from flask_cors import CORS
from flask import Flask, request, jsonify
app = Flask(__name__)
CORS(app)
def is_Chinese(word):
    for ch in word:
        if '\u4e00' <= ch <= '\u9fff':
            return True
    return False

def error_correct_(correct,text):
    result={}
    rate=0.8
    for item1 in correct:
        window=len(item1)
        for p in range(len(text)):
            num=0
            for i,j in zip(range(window),range(p,p+window)):
                if not (is_Chinese(item1[i]) and is_Chinese(text[j])):
                    break

                if similar(item1[i],text[j])>0.65:
                    num+=1

                if num/window > rate:
                    result[text[p:p+window]]=item1
                    break

            if item1 in result.keys():
                break
            
            if p+window ==len(text):
                break

    return result

@app.route('/error_correct', methods=['GET'])
def error_correct():
    print("成功接收数据......")
    R={}
    text = str(request.args["message"])
    correct = str(request.args["correct"])
    correct = correct.split(" ")
    print(correct,text)
    res=error_correct_(correct,text)
    txt=""
    print(res)
    for key,value in res.items():
        txt=txt+key+"->"+value+"\n"
    for key,value in res.items():
        text=text.replace(key,value)
    R["result"]=txt
    R["message"]=text
    print(R)
    return jsonify(R)

if __name__ == "__main__":
    app.run(port=83,debug = False)