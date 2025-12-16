"""
InspireWorks IVR Demo System
A multi-level IVR system using Plivo Voice API

Features:
- Outbound call initiation
- Level 1: Language selection (English/Spanish)
- Level 2: Audio playback or connect to associate
- Graceful error handling for invalid inputs
"""

import os
from flask import Flask, request, Response, render_template, jsonify, url_for
from plivo import plivoxml
import plivo
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# =============================================================================
# CONFIGURATION
# =============================================================================

PLIVO_AUTH_ID = os.getenv('PLIVO_AUTH_ID')
PLIVO_AUTH_TOKEN = os.getenv('PLIVO_AUTH_TOKEN')
PLIVO_PHONE_NUMBER = os.getenv('PLIVO_PHONE_NUMBER', '+14692463990')
ASSOCIATE_NUMBER = os.getenv('ASSOCIATE_NUMBER', '+918031274121')

# Public audio files for demo (you can replace with your own)
AUDIO_FILES = {
    'english': 'https://s3.amazonaws.com/plivocloud/Trumpet.mp3',
    'spanish': 'https://s3.amazonaws.com/plivocloud/Trumpet.mp3'
}

# =============================================================================
# MESSAGES
# =============================================================================

MESSAGES = {
    'welcome': {
        'english': "Welcome to InspireWorks. ",
        'spanish': "Bienvenido a InspireWorks. "
    },
    'language_select': (
        "Press 1 for English. "
        "Para Español, oprima 2. "
    ),
    'main_menu': {
        'english': (
            "You have selected English. "
            "Press 1 to hear a short audio message. "
            "Press 2 to speak with a live associate. "
        ),
        'spanish': (
            "Ha seleccionado Español. "
            "Oprima 1 para escuchar un mensaje de audio. "
            "Oprima 2 para hablar con un asociado. "
        )
    },
    'playing_audio': {
        'english': "Now playing your audio message.",
        'spanish': "Reproduciendo su mensaje de audio."
    },
    'connecting': {
        'english': "Please wait while we connect you to a live associate.",
        'spanish': "Por favor espere mientras lo conectamos con un asociado."
    },
    'invalid_input': {
        'english': "Sorry, that is not a valid option. Please try again.",
        'spanish': "Lo siento, esa no es una opción válida. Por favor intente de nuevo."
    },
    'no_input': {
        'english': "We did not receive any input.",
        'spanish': "No recibimos ninguna entrada."
    },
    'goodbye': {
        'english': "Thank you for calling InspireWorks. Goodbye!",
        'spanish': "Gracias por llamar a InspireWorks. ¡Adiós!"
    }
}

# =============================================================================
# FRONTEND ROUTE
# =============================================================================

@app.route('/')
def index():
    """Render the frontend page to trigger outbound calls"""
    return render_template('index.html')


# =============================================================================
# OUTBOUND CALL API
# =============================================================================

@app.route('/make-call', methods=['POST'])
def make_call():
    """
    Initiate an outbound call to the target phone number.
    The call will be answered with the IVR welcome menu.
    """
    try:
        # Get target number from request
        data = request.get_json()
        target_number = data.get('target_number')
        
        if not target_number:
            return jsonify({'success': False, 'error': 'Target number is required'}), 400
        
        # Format number (ensure it has + prefix)
        if not target_number.startswith('+'):
            target_number = '+' + target_number
        
        # Initialize Plivo client
        client = plivo.RestClient(PLIVO_AUTH_ID, PLIVO_AUTH_TOKEN)
        
        # Get the base URL for callbacks
        # In production, replace with your actual domain
        base_url = os.getenv('BASE_URL', request.url_root.rstrip('/'))
        answer_url = f"{base_url}/ivr/welcome"
        
        # Make the outbound call
        response = client.calls.create(
            from_=PLIVO_PHONE_NUMBER,
            to_=target_number,
            answer_url=answer_url,
            answer_method='GET'
        )
        
        return jsonify({
            'success': True,
            'message': f'Call initiated to {target_number}',
            'call_uuid': response.request_uuid
        })
        
    except plivo.exceptions.ValidationError as e:
        return jsonify({'success': False, 'error': f'Validation error: {str(e)}'}), 400
    except plivo.exceptions.PlivoRestError as e:
        return jsonify({'success': False, 'error': f'Plivo API error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# =============================================================================
# LEVEL 1: LANGUAGE SELECTION
# =============================================================================

@app.route('/ivr/welcome', methods=['GET', 'POST'])
def ivr_welcome():
    """
    Level 1: Welcome message and language selection menu.
    - Press 1 for English
    - Press 2 for Spanish
    """
    response = plivoxml.ResponseElement()
    
    # Create GetDigits element to capture language choice
    get_digits = plivoxml.GetDigitsElement(
        action=url_for('ivr_language_handler', _external=True),
        method='POST',
        timeout=10,
        num_digits=1,
        retries=2,
        valid_digits='12'
    )
    
    # Add welcome message and language options
    get_digits.add_speak(
        content=MESSAGES['welcome']['english'] + MESSAGES['language_select'],
        voice='Polly.Joanna',
        language='en-US'
    )
    
    response.add(get_digits)
    
    # Fallback if no input received
    response.add_speak(
        content=MESSAGES['no_input']['english'] + " " + MESSAGES['goodbye']['english'],
        voice='Polly.Joanna',
        language='en-US'
    )
    response.add_hangup()
    
    return Response(response.to_string(), mimetype='text/xml')


@app.route('/ivr/language-handler', methods=['POST'])
def ivr_language_handler():
    """
    Handle the language selection input from Level 1.
    Routes to appropriate Level 2 menu based on selection.
    """
    response = plivoxml.ResponseElement()
    
    # Get the digit pressed
    digit = request.form.get('Digits', '')
    
    if digit == '1':
        # English selected - redirect to English main menu
        response.add_redirect(
            url_for('ivr_main_menu', lang='english', _external=True),
            method='GET'
        )
    elif digit == '2':
        # Spanish selected - redirect to Spanish main menu
        response.add_redirect(
            url_for('ivr_main_menu', lang='spanish', _external=True),
            method='GET'
        )
    else:
        # Invalid input - repeat language selection
        response.add_speak(
            content=MESSAGES['invalid_input']['english'],
            voice='Polly.Joanna',
            language='en-US'
        )
        response.add_redirect(
            url_for('ivr_welcome', _external=True),
            method='GET'
        )
    
    return Response(response.to_string(), mimetype='text/xml')


# =============================================================================
# LEVEL 2: MAIN MENU (Language-specific)
# =============================================================================

@app.route('/ivr/main-menu/<lang>', methods=['GET', 'POST'])
def ivr_main_menu(lang):
    """
    Level 2: Main menu in selected language.
    - Press 1 to play audio message
    - Press 2 to connect to live associate
    """
    # Validate language
    if lang not in ['english', 'spanish']:
        lang = 'english'
    
    # Set voice based on language
    voice = 'Polly.Joanna' if lang == 'english' else 'Polly.Conchita'
    voice_lang = 'en-US' if lang == 'english' else 'es-ES'
    
    response = plivoxml.ResponseElement()
    
    # Create GetDigits element for menu selection
    get_digits = plivoxml.GetDigitsElement(
        action=url_for('ivr_menu_handler', lang=lang, _external=True),
        method='POST',
        timeout=10,
        num_digits=1,
        retries=2,
        valid_digits='12'
    )
    
    # Add main menu message
    get_digits.add_speak(
        content=MESSAGES['main_menu'][lang],
        voice=voice,
        language=voice_lang
    )
    
    response.add(get_digits)
    
    # Fallback if no input received
    response.add_speak(
        content=MESSAGES['no_input'][lang] + " " + MESSAGES['goodbye'][lang],
        voice=voice,
        language=voice_lang
    )
    response.add_hangup()
    
    return Response(response.to_string(), mimetype='text/xml')


@app.route('/ivr/menu-handler/<lang>', methods=['POST'])
def ivr_menu_handler(lang):
    """
    Handle the main menu selection from Level 2.
    - 1: Play audio message
    - 2: Connect to live associate
    """
    # Validate language
    if lang not in ['english', 'spanish']:
        lang = 'english'
    
    # Set voice based on language
    voice = 'Polly.Joanna' if lang == 'english' else 'Polly.Conchita'
    voice_lang = 'en-US' if lang == 'english' else 'es-ES'
    
    response = plivoxml.ResponseElement()
    
    # Get the digit pressed
    digit = request.form.get('Digits', '')
    
    if digit == '1':
        # Play audio message
        response.add_speak(
            content=MESSAGES['playing_audio'][lang],
            voice=voice,
            language=voice_lang
        )
        response.add_play(AUDIO_FILES[lang])
        response.add_speak(
            content=MESSAGES['goodbye'][lang],
            voice=voice,
            language=voice_lang
        )
        response.add_hangup()
        
    elif digit == '2':
        # Connect to live associate
        response.add_speak(
            content=MESSAGES['connecting'][lang],
            voice=voice,
            language=voice_lang
        )
        
        # Dial the associate number
        dial = plivoxml.DialElement(
            caller_id=PLIVO_PHONE_NUMBER,
            timeout=30
        )
        dial.add_number(ASSOCIATE_NUMBER)
        response.add(dial)
        
        # If call fails or ends
        response.add_speak(
            content=MESSAGES['goodbye'][lang],
            voice=voice,
            language=voice_lang
        )
        response.add_hangup()
        
    else:
        # Invalid input - repeat main menu
        response.add_speak(
            content=MESSAGES['invalid_input'][lang],
            voice=voice,
            language=voice_lang
        )
        response.add_redirect(
            url_for('ivr_main_menu', lang=lang, _external=True),
            method='GET'
        )
    
    return Response(response.to_string(), mimetype='text/xml')


# =============================================================================
# UTILITY ENDPOINTS
# =============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'InspireWorks IVR Demo'
    })


# =============================================================================
# RUN THE APPLICATION
# =============================================================================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("  InspireWorks IVR Demo System")
    print("="*60)
    print(f"  Plivo Phone Number: {PLIVO_PHONE_NUMBER}")
    print(f"  Associate Number:   {ASSOCIATE_NUMBER}")
    print("="*60)
    print("  Starting server on http://localhost:5000")
    print("  Use ngrok to expose: ngrok http 5000")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)