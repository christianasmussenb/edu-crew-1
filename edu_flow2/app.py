from flask import Flask, render_template, request, jsonify
import subprocess

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def generate():
    if request.method == 'POST':
        topic = request.form.get('topic')
        # Ejecutar crewai
        subprocess.run(['crewai', 'flow', 'kickoff'])
        return jsonify({"success": True})
    
    # Si es GET, mostrar el formulario
    return '''
    <html>
        <body>
            <form method="POST">
                <input name="topic" placeholder="Enter topic">
                <button type="submit">Generate</button>
            </form>
        </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(debug=True) 