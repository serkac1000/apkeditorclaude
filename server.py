from flask import Flask, render_template_string, request, jsonify, send_file
from flask_cors import CORS
import os
import json
import requests
import zipfile
import datetime
from io import BytesIO
import base64

app = Flask(__name__)
CORS(app)

# Read the HTML content
html_content = ""
try:
    with open('android_app_builder.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
except FileNotFoundError:
    html_content = """
    <h1>Android App Builder</h1>
    <p>Please place the android_app_builder.html file in the same directory as this server.</p>
    """

@app.route('/')
def index():
    return render_template_string(html_content)

@app.route('/api/generate-ui', methods=['POST'])
def generate_ui():
    data = request.json
    # Here you would integrate with Gemini API for AI generation
    return jsonify({'status': 'success', 'message': 'UI generated successfully'})

@app.route('/api/test-gemini', methods=['POST'])
def test_gemini():
    data = request.json
    api_key = data.get('api_key')
    prompt = data.get('prompt')
    
    if not api_key:
        return jsonify({'status': 'error', 'message': 'API key required'})
    
    # Test Gemini API connection
    try:
        headers = {
            'Content-Type': 'application/json',
        }
        
        payload = {
            'contents': [{'parts': [{'text': prompt}]}]
        }
        
        url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={api_key}'
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0:
                content = result['candidates'][0]['content']['parts'][0]['text']
                return jsonify({
                    'status': 'success', 
                    'message': 'API connection successful',
                    'response': content
                })
            else:
                return jsonify({'status': 'error', 'message': 'No response from API'})
        else:
            error_detail = response.text if response.text else f'Status code: {response.status_code}'
            return jsonify({'status': 'error', 'message': f'API error: {error_detail}'})
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Connection failed: {str(e)}'})

@app.route('/api/generate-android-code', methods=['POST'])
def generate_android_code():
    data = request.json
    api_key = data.get('api_key')
    app_description = data.get('description', '')
    app_name = data.get('appName', 'MyApp')
    
    if not api_key:
        return jsonify({'status': 'error', 'message': 'API key required'})
    
    try:
        # Create a detailed prompt for Android app generation
        prompt = f"""
        Generate complete Android Studio project files for an app called "{app_name}".
        App description: {app_description}
        
        Please provide:
        1. MainActivity.java - Main activity with proper imports and functionality
        2. activity_main.xml - Layout file with UI elements
        3. AndroidManifest.xml - App manifest with proper permissions
        4. build.gradle (app level) - Build configuration
        5. strings.xml - String resources
        6. colors.xml - Color resources
        
        Make it a functional, complete Android app. Use modern Android development practices.
        Return the response in JSON format with each file as a separate key.
        """
        
        headers = {'Content-Type': 'application/json'}
        payload = {'contents': [{'parts': [{'text': prompt}]}]}
        
        url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={api_key}'
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0:
                content = result['candidates'][0]['content']['parts'][0]['text']
                return jsonify({
                    'status': 'success',
                    'code': content,
                    'message': 'Android code generated successfully'
                })
            else:
                return jsonify({'status': 'error', 'message': 'No code generated'})
        else:
            return jsonify({'status': 'error', 'message': f'API error: {response.status_code}'})
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Generation failed: {str(e)}'})

@app.route('/api/export-project', methods=['POST'])
def export_project():
    data = request.json
    app_name = data.get('appName', 'MyApp')
    generated_code = data.get('code', '')
    
    try:
        # Create a zip file with Android project structure
        memory_file = BytesIO()
        with zipfile.ZipFile(memory_file, 'w') as zf:
            # Create basic Android project structure
            zf.writestr(f'{app_name}/app/src/main/java/com/example/{app_name.lower()}/MainActivity.java', 
                       generated_code.get('MainActivity.java', '// MainActivity code here'))
            
            zf.writestr(f'{app_name}/app/src/main/res/layout/activity_main.xml',
                       generated_code.get('activity_main.xml', '<!-- Layout XML here -->'))
            
            zf.writestr(f'{app_name}/app/src/main/AndroidManifest.xml',
                       generated_code.get('AndroidManifest.xml', '<!-- Manifest XML here -->'))
            
            zf.writestr(f'{app_name}/app/build.gradle',
                       generated_code.get('build.gradle', '// Build gradle here'))
            
            zf.writestr(f'{app_name}/app/src/main/res/values/strings.xml',
                       generated_code.get('strings.xml', '<!-- Strings XML here -->'))
            
            zf.writestr(f'{app_name}/app/src/main/res/values/colors.xml',
                       generated_code.get('colors.xml', '<!-- Colors XML here -->'))
            
            # Add README
            zf.writestr(f'{app_name}/README.md', f'# {app_name}\n\nGenerated Android Studio project.')
        
        memory_file.seek(0)
        
        return send_file(
            memory_file,
            as_attachment=True,
            download_name=f'{app_name}_project.zip',
            mimetype='application/zip'
        )
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Export failed: {str(e)}'})

@app.route('/api/build-apk', methods=['POST'])
def build_apk():
    data = request.json
    app_name = data.get('appName', 'MyApp')
    
    # Create a dummy APK file for demonstration
    try:
        memory_file = BytesIO()
        with zipfile.ZipFile(memory_file, 'w') as zf:
            zf.writestr('META-INF/MANIFEST.MF', 'Manifest-Version: 1.0\n')
            zf.writestr('classes.dex', b'# This is a demo APK file')
            zf.writestr('AndroidManifest.xml', '<!-- Demo APK -->')
        
        memory_file.seek(0)
        
        return send_file(
            memory_file,
            as_attachment=True,
            download_name=f'{app_name}_demo.apk',
            mimetype='application/vnd.android.package-archive'
        )
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'APK build failed: {str(e)}'})

if __name__ == '__main__':
    print("===============================================")
    print("Starting Android App Builder Server...")
    print("Server will be available at: http://127.0.0.1:5000")
    print("Press Ctrl+C to stop the server")
    print("===============================================")
    app.run(host='127.0.0.1', port=5000, debug=True)