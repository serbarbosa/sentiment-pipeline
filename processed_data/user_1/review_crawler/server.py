from flask import Flask, render_template, request
import crawl_reviews as b
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('template.html')

@app.route('/', methods=['POST'])
def my_link():
    text = request.form['text']
    b.run_crawler(text.lower())
    return True
    

if __name__ == '__main__':
    app.run(debug=True) 
