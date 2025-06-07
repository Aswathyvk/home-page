from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os
from PyPDF2 import PdfReader
import openai  # For actual AI implementation

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Simple in-memory storage for demo purposes
user_documents = {}
user_questions = {}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, 'rb') as file:
        reader = PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
    return text

def get_ai_response(question, context):
    # In a real implementation, you would use OpenAI API or similar
    # This is a simplified version for demonstration
    
    # Example using OpenAI (uncomment and configure if you have API key)
    # openai.api_key = 'your-api-key'
    # response = openai.ChatCompletion.create(
    #     model="gpt-3.5-turbo",
    #     messages=[
    #         {"role": "system", "content": "You are a helpful tutor. Answer questions based on the provided context."},
    #         {"role": "user", "content": f"Context: {context}\n\nQuestion: {question}"}
    #     ]
    # )
    # return response.choices[0].message.content
    
    # Simple mock response for demo
    responses = [
        f"Based on the document, the answer to '{question}' would be... [simulated response]",
        "The document mentions this topic in section 3.2. [simulated response]",
        "This is an important concept covered in your materials. [simulated response]"
    ]
    return responses[len(question) % len(responses)]

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # Handle file upload
        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                # Store document text (in memory for this demo)
                document_id = len(user_documents) + 1
                document_text = extract_text_from_pdf(filepath)
                user_documents[document_id] = {
                    'filename': filename,
                    'text': document_text
                }
                
                flash('Document uploaded successfully!')
                return redirect(url_for('home', document_id=document_id))
        
        # Handle question submission
        elif 'question' in request.form:
            document_id = int(request.form.get('document_id', 0))
            question = request.form['question']
            
            if document_id in user_documents:
                context = user_documents[document_id]['text']
                answer = get_ai_response(question, context)
                
                # Store question and answer
                if document_id not in user_questions:
                    user_questions[document_id] = []
                user_questions[document_id].append({
                    'question': question,
                    'answer': answer
                })
                
                flash('Answer generated!')
            else:
                flash('Please upload a document first')
    
    document_id = request.args.get('document_id', type=int)
    current_document = user_documents.get(document_id) if document_id else None
    document_questions = user_questions.get(document_id, []) if document_id else []
    
    return render_template('index.html', 
                         current_document=current_document,
                         document_questions=document_questions,
                         document_id=document_id)

if __name__ == '__main__':
    app.run(debug=True)