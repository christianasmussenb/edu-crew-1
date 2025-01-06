from flask import Flask, render_template, request, jsonify
import subprocess
import os

app = Flask(__name__, 
    template_folder='templates',
    static_folder='static'
)

@app.route('/', methods=['GET', 'POST'])
def generate():
    if request.method == 'POST':
        topic = request.form.get('topic', '').strip()
        level = request.form.get('level', 'beginner')
        
        # Validar que el topic no esté vacío
        if not topic:
            return jsonify({
                "success": False, 
                "error": "Please enter a topic"
            })
        
        try:
            # Escribir las variables en el archivo config.py
            config_path = 'src/edu_flow2/config.py'
            with open(config_path, 'r') as file:
                lines = file.readlines()
            
            # Actualizar las variables
            for i, line in enumerate(lines):
                if '"topic":' in line:
                    lines[i] = f'    "topic": "{topic}",\n'
                elif '"audience_level":' in line:
                    lines[i] = f'    "audience_level": "{level}",\n'
            
            # Guardar el archivo actualizado
            with open(config_path, 'w') as file:
                file.writelines(lines)
            
            # Ejecutar el proceso
            result = subprocess.run(
                ['crewai', 'flow', 'kickoff'],
                capture_output=True,
                text=True,
                check=True
            )
            
            return jsonify({
                "success": True,
                "message": "Content generated successfully",
                "topic": topic,
                "level": level,
                "output": result.stdout
            })
            
        except subprocess.CalledProcessError as e:
            return jsonify({
                "success": False,
                "error": f"Process error: {e.stderr}"
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            })
    
    # Para GET, mostrar el formulario con valores por defecto
    return render_template('index.html', 
        default_topic="Healthcare, latest advancements in medicine using AI",
        default_level="beginner"
    )

if __name__ == '__main__':
    app.run(debug=True) 