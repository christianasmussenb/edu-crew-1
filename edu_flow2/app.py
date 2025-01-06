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

# Variables globales para control
process_active = False
process_completed = False

@app.route('/stream')
def stream():
    def generate():
        global process_active, process_completed
        first_message = True
        
        while not process_completed:
            try:
                if not process_active and not first_message:
                    # Si el proceso terminó, enviar mensaje final
                    process_completed = True
                    yield f"data: Proceso completado ✅\n\n"
                    break
                
                message = progress_queue.get_nowait()
                # Filtrar mensajes no deseados
                if "pydantic" not in message.lower() and "warning" not in message.lower():
                    yield f"data: {message}\n\n"
                    first_message = False
            except queue.Empty:
                if first_message:
                    yield f"data: Iniciando proceso...\n\n"
                    first_message = False
            time.sleep(5)
    
    return Response(generate(), mimetype='text/event-stream')

def monitor_process(process):
    """Monitorea el proceso y añade mensajes a la cola"""
    global process_active, process_completed
    process_active = True
    process_completed = False
    
    seen_messages = set()
    
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            process_active = False
            break
        if output:
            message = output.strip()
            if (message not in seen_messages and 
                "pydantic" not in message.lower() and 
                "warning" not in message.lower()):
                seen_messages.add(message)
                progress_queue.put(message)
    
    # Esperar un momento para asegurar que todos los mensajes se procesaron
    time.sleep(10)
    process_active = False

@app.route('/', methods=['GET', 'POST'])
def generate():
    global process_active, process_completed
    
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
            if process_active:
                return jsonify({
                    "success": False,
                    "error": "Ya hay un proceso en ejecución"
                })

            # Resetear estados
            process_active = False
            process_completed = False
            
            # Limpiar la cola
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