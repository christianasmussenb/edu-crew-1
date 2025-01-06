from flask import Flask, render_template, request, jsonify
from edu_flow2.main import process_content

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        input_vars = {
            "audience_level": request.form.get('level', 'beginner'),
            "topic": request.form.get('topic', '')
        }
        try:
            result = process_content(input_vars)
            return jsonify({"success": True, "result": result})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)})

    return '''
    <html>
        <head>
            <title>EduFlow Content Generator</title>
            <style>
                body { font-family: Arial; max-width: 800px; margin: 0 auto; padding: 20px; }
                .form-group { margin-bottom: 15px; }
                select, input, button { width: 100%; padding: 8px; margin-top: 5px; }
                button { background: #4CAF50; color: white; border: none; cursor: pointer; }
                button:hover { background: #45a049; }
            </style>
        </head>
        <body>
            <h1>🎓 EduFlow Content Generator</h1>
            <form id="contentForm">
                <div class="form-group">
                    <label>Topic:</label>
                    <input type="text" name="topic" value="Healthcare, latest advancements in medicine using AI">
                </div>
                <div class="form-group">
                    <label>Audience Level:</label>
                    <select name="level">
                        <option value="beginner">Beginner</option>
                        <option value="intermediate">Intermediate</option>
                        <option value="advanced">Advanced</option>
                    </select>
                </div>
                <button type="submit">Generate Content</button>
            </form>
            <div id="result"></div>

            <script>
                document.getElementById('contentForm').onsubmit = function(e) {
                    e.preventDefault();
                    document.getElementById('result').innerHTML = 'Generating content...';
                    
                    fetch('/', {
                        method: 'POST',
                        body: new FormData(this)
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            document.getElementById('result').innerHTML = 
                                '<h3>✅ Content generated successfully!</h3><pre>' + 
                                JSON.stringify(data.result, null, 2) + '</pre>';
                        } else {
                            document.getElementById('result').innerHTML = 
                                '<h3>❌ Error:</h3><pre>' + data.error + '</pre>';
                        }
                    });
                };
            </script>
        </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(debug=True) 