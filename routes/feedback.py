from flask import Blueprint, render_template, request, jsonify
from models import get_db_connection, add_feedback

feedback_bp = Blueprint('feedback', __name__)

@feedback_bp.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        name = request.form.get('name', '')
        email = request.form.get('email', '')
        message = request.form.get('message', '')
        
        add_feedback(name, email, message, feedback_type='general')
        
        return jsonify({"status": "success"}), 200
    
    return render_template('feedback.html')