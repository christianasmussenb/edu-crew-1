from flask import Flask, render_template, request, jsonify, Response
import subprocess
import os
import threading
import time
import queue

app = Flask(__name__, 
    template_folder='templates',
    static_folder='static'
)

# Cola global para almacenar los mensajes
progress_queue = queue.Queue()

@app.route('/stream')
def stream():
    def generate():
        while True:
            try:
                # Intentar obtener un mensaje de la cola
                message = progress_queue.get_nowait()
                yield f"data: {message}\n\n"
            except queue.Empty:
                # Si no hay mensajes, enviar un heartbeat
                yield f"data: Procesando...\n\n"
            time.sleep(30)  # Esperar 30 segundos antes de la siguiente actualización
    
    return Response(generate(), mimetype='text/event-stream')

def monitor_process(process):
    """Monitorea el proceso y añade mensajes a la cola"""
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            progress_queue.put(output.strip())
    
@app.route('/', methods=['GET', 'POST'])
def generate():
    if request.method == 'POST':
        print("POST recibido")  # Debug log
        topic = request.form.get('topic', '').strip()
        level = request.form.get('level', '').strip()
        
        print(f"Topic: {topic}")  # Debug log
        print(f"Level: {level}")  # Debug log
        
        # Validaciones
        errors = []
        if not topic:
            errors.append("Topic cannot be empty")
        if len(topic) < 10:
            errors.append("Topic must be at least 10 characters long")
            
        if not level or level not in ['beginner', 'intermediate', 'advanced']:
            errors.append("Invalid audience level")
            
        if errors:
            return jsonify({
                "success": False,
                "error": " | ".join(errors)
            })
        
        try:
            # Limpiar la cola de mensajes anteriores
            while not progress_queue.empty():
                progress_queue.get()

            # Iniciar el proceso
            process = subprocess.Popen(
                ['crewai', 'flow', 'kickoff'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # Redirigir stderr a stdout
                text=True,
                bufsize=1,  # Line buffered
                env=os.environ,
                cwd=os.path.dirname(os.path.abspath(__file__))
            )
            
            # Iniciar thread para monitorear el proceso
            monitor_thread = threading.Thread(target=monitor_process, args=(process,))
            monitor_thread.daemon = True
            monitor_thread.start()
            
            return jsonify({
                "success": True,
                "message": "Process started successfully",
                "topic": topic,
                "level": level
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