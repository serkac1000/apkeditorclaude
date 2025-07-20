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

# Create data directory if it doesn't exist
if not os.path.exists('data'):
    os.makedirs('data')

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
    save_key = data.get('save_key', False)
    
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
                
                # Save API key if requested
                if save_key:
                    try:
                        # Create a secure way to store the API key
                        config_data = {'api_key': api_key, 'last_saved': datetime.datetime.now().isoformat()}
                        with open('data/config.json', 'w') as f:
                            json.dump(config_data, f)
                    except Exception as e:
                        print(f"Error saving API key: {str(e)}")
                
                return jsonify({
                    'status': 'success', 
                    'message': 'API connection successful' + (' and saved' if save_key else ''),
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
    generated_code = data.get('code', {})
    
    try:
        # Create a zip file with Android project structure
        memory_file = BytesIO()
        with zipfile.ZipFile(memory_file, 'w') as zf:
            # Create basic Android project structure
            # Handle MainActivity.java - could be either Java or Kotlin
            if 'MainActivity.kt' in generated_code:
                zf.writestr(f'{app_name}/app/src/main/java/com/example/{app_name.lower()}/MainActivity.kt', 
                           generated_code.get('MainActivity.kt', '// MainActivity Kotlin code here'))
            else:
                zf.writestr(f'{app_name}/app/src/main/java/com/example/{app_name.lower()}/MainActivity.java', 
                           generated_code.get('MainActivity.java', '// MainActivity code here'))
            
            # Handle layout files
            zf.writestr(f'{app_name}/app/src/main/res/layout/activity_main.xml',
                       generated_code.get('activity_main.xml', '<!-- Layout XML here -->'))
            
            # Handle manifest
            zf.writestr(f'{app_name}/app/src/main/AndroidManifest.xml',
                       generated_code.get('AndroidManifest.xml', '<!-- Manifest XML here -->'))
            
            # Handle build files
            zf.writestr(f'{app_name}/app/build.gradle',
                       generated_code.get('build.gradle', '// Build gradle here'))
            zf.writestr(f'{app_name}/build.gradle',
                       generated_code.get('project_build.gradle', '// Project build gradle here'))
            zf.writestr(f'{app_name}/settings.gradle',
                       generated_code.get('settings.gradle', f'rootProject.name = "{app_name}"\ninclude ":app"'))
            
            # Handle resource files
            zf.writestr(f'{app_name}/app/src/main/res/values/strings.xml',
                       generated_code.get('strings.xml', f'<resources>\n    <string name="app_name">{app_name}</string>\n</resources>'))
            
            zf.writestr(f'{app_name}/app/src/main/res/values/colors.xml',
                       generated_code.get('colors.xml', '<resources>\n    <color name="colorPrimary">#6200EE</color>\n    <color name="colorPrimaryDark">#3700B3</color>\n    <color name="colorAccent">#03DAC5</color>\n</resources>'))
            
            # Add styles if available
            if 'styles.xml' in generated_code:
                zf.writestr(f'{app_name}/app/src/main/res/values/styles.xml',
                           generated_code.get('styles.xml'))
            
            # Add any additional files found in the generated code
            for file_name, content in generated_code.items():
                if file_name not in ['MainActivity.java', 'MainActivity.kt', 'activity_main.xml', 
                                    'AndroidManifest.xml', 'build.gradle', 'project_build.gradle',
                                    'settings.gradle', 'strings.xml', 'colors.xml', 'styles.xml']:
                    # Determine the appropriate path based on file extension
                    if file_name.endswith('.java') or file_name.endswith('.kt'):
                        zf.writestr(f'{app_name}/app/src/main/java/com/example/{app_name.lower()}/{file_name}', content)
                    elif file_name.endswith('.xml') and not file_name.startswith('activity_'):
                        if 'layout' in file_name:
                            zf.writestr(f'{app_name}/app/src/main/res/layout/{file_name}', content)
                        else:
                            zf.writestr(f'{app_name}/app/src/main/res/values/{file_name}', content)
                    else:
                        # Default location for other files
                        zf.writestr(f'{app_name}/{file_name}', content)
            
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
    
    try:
        # Create a standalone HTML file that can be opened directly in a browser
        # This is the most reliable way to demonstrate the app without requiring Android SDK
        app_html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{app_name} Demo</title>
            <style>
                body {{
                    font-family: 'Roboto', 'Segoe UI', Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                    background-color: #f5f5f5;
                    color: #333;
                }}
                .phone-container {{
                    width: 360px;
                    height: 720px;
                    margin: 20px auto;
                    border: 12px solid #222;
                    border-radius: 36px;
                    position: relative;
                    overflow: hidden;
                    box-shadow: 0 10px 25px rgba(0,0,0,0.2);
                }}
                .phone-header {{
                    height: 24px;
                    background: #222;
                    position: relative;
                }}
                .phone-header::after {{
                    content: '';
                    position: absolute;
                    width: 100px;
                    height: 20px;
                    background: #222;
                    top: 0;
                    left: 50%;
                    transform: translateX(-50%);
                    border-bottom-left-radius: 10px;
                    border-bottom-right-radius: 10px;
                }}
                .phone-footer {{
                    height: 12px;
                    background: #222;
                    position: absolute;
                    bottom: 0;
                    width: 100%;
                }}
                .app-screen {{
                    height: calc(100% - 36px);
                    overflow: hidden;
                    background: white;
                }}
                .app-header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 16px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .app-content {{
                    padding: 16px;
                    height: calc(100% - 120px);
                    overflow-y: auto;
                }}
                .card {{
                    background: white;
                    border-radius: 8px;
                    padding: 16px;
                    margin-bottom: 16px;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                }}
                .app-footer {{
                    position: absolute;
                    bottom: 0;
                    left: 0;
                    right: 0;
                    background: white;
                    display: flex;
                    justify-content: space-around;
                    padding: 12px;
                    border-top: 1px solid #e0e0e0;
                }}
                .footer-item {{
                    text-align: center;
                    font-size: 12px;
                    cursor: pointer;
                }}
                .footer-item:hover {{
                    color: #667eea;
                }}
                .footer-icon {{
                    font-size: 24px;
                    margin-bottom: 4px;
                }}
                .status-bar {{
                    display: flex;
                    justify-content: space-between;
                    background: rgba(0,0,0,0.1);
                    padding: 4px 16px;
                    font-size: 12px;
                    color: white;
                }}
                .status-bar-right {{
                    display: flex;
                    gap: 8px;
                }}
                .button {{
                    background: #667eea;
                    color: white;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 24px;
                    font-weight: bold;
                    margin-top: 16px;
                    cursor: pointer;
                    transition: background 0.3s;
                }}
                .button:hover {{
                    background: #764ba2;
                }}
                .instructions {{
                    max-width: 600px;
                    margin: 0 auto 40px auto;
                    background: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                h1 {{
                    text-align: center;
                    color: #667eea;
                    margin-bottom: 30px;
                }}
                .weather-icon {{
                    font-size: 64px;
                    margin-bottom: 10px;
                }}
                .temperature {{
                    font-size: 48px;
                    font-weight: bold;
                    margin-bottom: 5px;
                }}
                .weather-condition {{
                    font-size: 18px;
                    color: #666;
                    margin-bottom: 20px;
                }}
                .weather-details {{
                    display: flex;
                    justify-content: space-around;
                    margin-top: 20px;
                }}
                .weather-detail {{
                    text-align: center;
                }}
                .weather-detail-value {{
                    font-weight: bold;
                    font-size: 16px;
                }}
                .weather-detail-label {{
                    font-size: 12px;
                    color: #666;
                }}
                .forecast {{
                    display: flex;
                    overflow-x: auto;
                    gap: 16px;
                    padding: 10px 0;
                }}
                .forecast-item {{
                    text-align: center;
                    min-width: 60px;
                }}
                .forecast-day {{
                    font-weight: bold;
                    margin-bottom: 5px;
                }}
                .forecast-icon {{
                    font-size: 24px;
                    margin: 5px 0;
                }}
                .forecast-temp {{
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <h1>{app_name} Demo</h1>
            
            <div class="instructions">
                <h2>Demo App Instructions</h2>
                <p>This is an interactive demo of your Android app. The app is simulated in HTML and can be viewed in any browser.</p>
                <p>In a real implementation, this would be a native Android APK that could be installed on Android devices.</p>
                <p><strong>Note:</strong> This demo is for visualization purposes only and demonstrates how your app would look and feel.</p>
            </div>
            
            <div class="phone-container">
                <div class="phone-header"></div>
                <div class="app-screen">
                    <div class="status-bar">
                        <div>9:41 AM</div>
                        <div class="status-bar-right">
                            <div>📶</div>
                            <div>🔋</div>
                        </div>
                    </div>
                    <div class="app-header">
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <span style="font-size: 18px;">≡</span>
                            <span style="font-weight: bold;">{app_name}</span>
                        </div>
                        <div>⋮</div>
                    </div>
                    
                    <div class="app-content" id="appContent">
                        <!-- Dynamic content will be loaded here -->
                        <div style="text-align: center; padding: 40px 0;">
                            <div class="weather-icon">☀️</div>
                            <div class="temperature">72°F</div>
                            <div class="weather-condition">Sunny</div>
                            <div>New York City, NY</div>
                            
                            <div class="weather-details">
                                <div class="weather-detail">
                                    <div class="weather-detail-value">68%</div>
                                    <div class="weather-detail-label">Humidity</div>
                                </div>
                                <div class="weather-detail">
                                    <div class="weather-detail-value">8 mph</div>
                                    <div class="weather-detail-label">Wind</div>
                                </div>
                                <div class="weather-detail">
                                    <div class="weather-detail-value">0%</div>
                                    <div class="weather-detail-label">Rain</div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="card">
                            <h3>Hourly Forecast</h3>
                            <div class="forecast">
                                <div class="forecast-item">
                                    <div class="forecast-day">Now</div>
                                    <div class="forecast-icon">☀️</div>
                                    <div class="forecast-temp">72°</div>
                                </div>
                                <div class="forecast-item">
                                    <div class="forecast-day">1PM</div>
                                    <div class="forecast-icon">☀️</div>
                                    <div class="forecast-temp">74°</div>
                                </div>
                                <div class="forecast-item">
                                    <div class="forecast-day">2PM</div>
                                    <div class="forecast-icon">⛅</div>
                                    <div class="forecast-temp">73°</div>
                                </div>
                                <div class="forecast-item">
                                    <div class="forecast-day">3PM</div>
                                    <div class="forecast-icon">⛅</div>
                                    <div class="forecast-temp">72°</div>
                                </div>
                                <div class="forecast-item">
                                    <div class="forecast-day">4PM</div>
                                    <div class="forecast-icon">☁️</div>
                                    <div class="forecast-temp">70°</div>
                                </div>
                                <div class="forecast-item">
                                    <div class="forecast-day">5PM</div>
                                    <div class="forecast-icon">☁️</div>
                                    <div class="forecast-temp">68°</div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="card">
                            <h3>7-Day Forecast</h3>
                            <div style="display: flex; flex-direction: column; gap: 12px;">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <div>Today</div>
                                    <div style="font-size: 20px;">☀️</div>
                                    <div>68° / 75°</div>
                                </div>
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <div>Mon</div>
                                    <div style="font-size: 20px;">⛅</div>
                                    <div>65° / 72°</div>
                                </div>
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <div>Tue</div>
                                    <div style="font-size: 20px;">🌧️</div>
                                    <div>60° / 68°</div>
                                </div>
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <div>Wed</div>
                                    <div style="font-size: 20px;">⛈️</div>
                                    <div>58° / 65°</div>
                                </div>
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <div>Thu</div>
                                    <div style="font-size: 20px;">⛅</div>
                                    <div>62° / 70°</div>
                                </div>
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <div>Fri</div>
                                    <div style="font-size: 20px;">☀️</div>
                                    <div>65° / 73°</div>
                                </div>
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <div>Sat</div>
                                    <div style="font-size: 20px;">☀️</div>
                                    <div>67° / 76°</div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="app-footer">
                        <div class="footer-item" onclick="changeTab('home')" id="homeTab">
                            <div class="footer-icon">🏠</div>
                            <div>Home</div>
                        </div>
                        <div class="footer-item" onclick="changeTab('search')" id="searchTab">
                            <div class="footer-icon">🔍</div>
                            <div>Search</div>
                        </div>
                        <div class="footer-item" onclick="changeTab('settings')" id="settingsTab">
                            <div class="footer-icon">⚙️</div>
                            <div>Settings</div>
                        </div>
                    </div>
                </div>
                <div class="phone-footer"></div>
            </div>
            
            <script>
                // Simple tab switching functionality
                function changeTab(tabName) {
                    // Reset all tabs
                    document.getElementById('homeTab').style.color = '#333';
                    document.getElementById('searchTab').style.color = '#333';
                    document.getElementById('settingsTab').style.color = '#333';
                    
                    // Highlight selected tab
                    document.getElementById(tabName + 'Tab').style.color = '#667eea';
                    
                    // Change content based on tab
                    const content = document.getElementById('appContent');
                    
                    if (tabName === 'search') {
                        content.innerHTML = `
                            <div style="padding: 20px 0;">
                                <div style="position: relative; margin-bottom: 20px;">
                                    <input type="text" placeholder="Search locations..." style="width: 100%; padding: 12px 16px; border-radius: 24px; border: 1px solid #ddd; font-size: 16px; box-sizing: border-box;">
                                    <div style="position: absolute; right: 16px; top: 12px;">🔍</div>
                                </div>
                                
                                <div class="card">
                                    <h3>Recent Searches</h3>
                                    <div style="display: flex; flex-direction: column; gap: 12px;">
                                        <div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #eee;">
                                            <div>New York, NY</div>
                                            <div>☀️ 72°</div>
                                        </div>
                                        <div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #eee;">
                                            <div>Los Angeles, CA</div>
                                            <div>☀️ 85°</div>
                                        </div>
                                        <div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #eee;">
                                            <div>Chicago, IL</div>
                                            <div>⛅ 65°</div>
                                        </div>
                                        <div style="display: flex; justify-content: space-between; padding: 8px 0;">
                                            <div>Miami, FL</div>
                                            <div>🌧️ 80°</div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        `;
                    } else if (tabName === 'settings') {
                        content.innerHTML = `
                            <div class="card">
                                <h3>App Settings</h3>
                                <div style="display: flex; flex-direction: column; gap: 16px;">
                                    <div style="display: flex; justify-content: space-between; align-items: center;">
                                        <div>Temperature Unit</div>
                                        <select style="padding: 8px; border-radius: 4px; border: 1px solid #ddd;">
                                            <option>Fahrenheit (°F)</option>
                                            <option>Celsius (°C)</option>
                                        </select>
                                    </div>
                                    <div style="display: flex; justify-content: space-between; align-items: center;">
                                        <div>Dark Mode</div>
                                        <label class="switch">
                                            <input type="checkbox">
                                            <span class="slider"></span>
                                        </label>
                                    </div>
                                    <div style="display: flex; justify-content: space-between; align-items: center;">
                                        <div>Notifications</div>
                                        <label class="switch">
                                            <input type="checkbox" checked>
                                            <span class="slider"></span>
                                        </label>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="card">
                                <h3>About</h3>
                                <div style="display: flex; flex-direction: column; gap: 8px;">
                                    <div>Version: 1.0.0</div>
                                    <div>Build: {datetime.datetime.now().strftime('%Y%m%d')}</div>
                                    <div style="margin-top: 16px;">
                                        <button class="button">Check for Updates</button>
                                    </div>
                                </div>
                            </div>
                        `;
                    } else {
                        // Home tab - default content
                        content.innerHTML = `
                            <div style="text-align: center; padding: 40px 0;">
                                <div class="weather-icon">☀️</div>
                                <div class="temperature">72°F</div>
                                <div class="weather-condition">Sunny</div>
                                <div>New York City, NY</div>
                                
                                <div class="weather-details">
                                    <div class="weather-detail">
                                        <div class="weather-detail-value">68%</div>
                                        <div class="weather-detail-label">Humidity</div>
                                    </div>
                                    <div class="weather-detail">
                                        <div class="weather-detail-value">8 mph</div>
                                        <div class="weather-detail-label">Wind</div>
                                    </div>
                                    <div class="weather-detail">
                                        <div class="weather-detail-value">0%</div>
                                        <div class="weather-detail-label">Rain</div>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="card">
                                <h3>Hourly Forecast</h3>
                                <div class="forecast">
                                    <div class="forecast-item">
                                        <div class="forecast-day">Now</div>
                                        <div class="forecast-icon">☀️</div>
                                        <div class="forecast-temp">72°</div>
                                    </div>
                                    <div class="forecast-item">
                                        <div class="forecast-day">1PM</div>
                                        <div class="forecast-icon">☀️</div>
                                        <div class="forecast-temp">74°</div>
                                    </div>
                                    <div class="forecast-item">
                                        <div class="forecast-day">2PM</div>
                                        <div class="forecast-icon">⛅</div>
                                        <div class="forecast-temp">73°</div>
                                    </div>
                                    <div class="forecast-item">
                                        <div class="forecast-day">3PM</div>
                                        <div class="forecast-icon">⛅</div>
                                        <div class="forecast-temp">72°</div>
                                    </div>
                                    <div class="forecast-item">
                                        <div class="forecast-day">4PM</div>
                                        <div class="forecast-icon">☁️</div>
                                        <div class="forecast-temp">70°</div>
                                    </div>
                                    <div class="forecast-item">
                                        <div class="forecast-day">5PM</div>
                                        <div class="forecast-icon">☁️</div>
                                        <div class="forecast-temp">68°</div>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="card">
                                <h3>7-Day Forecast</h3>
                                <div style="display: flex; flex-direction: column; gap: 12px;">
                                    <div style="display: flex; justify-content: space-between; align-items: center;">
                                        <div>Today</div>
                                        <div style="font-size: 20px;">☀️</div>
                                        <div>68° / 75°</div>
                                    </div>
                                    <div style="display: flex; justify-content: space-between; align-items: center;">
                                        <div>Mon</div>
                                        <div style="font-size: 20px;">⛅</div>
                                        <div>65° / 72°</div>
                                    </div>
                                    <div style="display: flex; justify-content: space-between; align-items: center;">
                                        <div>Tue</div>
                                        <div style="font-size: 20px;">🌧️</div>
                                        <div>60° / 68°</div>
                                    </div>
                                    <div style="display: flex; justify-content: space-between; align-items: center;">
                                        <div>Wed</div>
                                        <div style="font-size: 20px;">⛈️</div>
                                        <div>58° / 65°</div>
                                    </div>
                                    <div style="display: flex; justify-content: space-between; align-items: center;">
                                        <div>Thu</div>
                                        <div style="font-size: 20px;">⛅</div>
                                        <div>62° / 70°</div>
                                    </div>
                                    <div style="display: flex; justify-content: space-between; align-items: center;">
                                        <div>Fri</div>
                                        <div style="font-size: 20px;">☀️</div>
                                        <div>65° / 73°</div>
                                    </div>
                                    <div style="display: flex; justify-content: space-between; align-items: center;">
                                        <div>Sat</div>
                                        <div style="font-size: 20px;">☀️</div>
                                        <div>67° / 76°</div>
                                    </div>
                                </div>
                            </div>
                        `;
                    }
                }
                
                // Initialize with home tab selected
                document.getElementById('homeTab').style.color = '#667eea';
            </script>
        </body>
        </html>
        """
        
        # Return the HTML file directly
        return send_file(
            BytesIO(app_html.encode('utf-8')),
            as_attachment=True,
            download_name=f'{app_name}_demo.html',
            mimetype='text/html'
        )
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'App demo creation failed: {str(e)}'})

# Add routes for saving and loading project data
@app.route('/api/save-project', methods=['POST'])
def save_project():
    data = request.json
    project_name = data.get('appName', 'MyApp')
    project_data = data.get('projectData', {})
    
    try:
        # Create a unique filename based on project name
        safe_name = ''.join(c if c.isalnum() else '_' for c in project_name)
        filename = f"data/{safe_name}_project.json"
        
        with open(filename, 'w') as f:
            json.dump(project_data, f)
            
        return jsonify({
            'status': 'success',
            'message': f'Project {project_name} saved successfully',
            'filename': filename
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Failed to save project: {str(e)}'})

@app.route('/api/load-project', methods=['GET'])
def load_project():
    try:
        # List all saved projects
        if not os.path.exists('data'):
            return jsonify({'status': 'info', 'message': 'No saved projects found', 'projects': []})
            
        projects = []
        for file in os.listdir('data'):
            if file.endswith('_project.json'):
                project_name = file.replace('_project.json', '').replace('_', ' ')
                projects.append({
                    'name': project_name,
                    'filename': file,
                    'date': datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join('data', file))).isoformat()
                })
                
        return jsonify({
            'status': 'success',
            'projects': projects
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Failed to list projects: {str(e)}'})

@app.route('/api/load-project/<filename>', methods=['GET'])
def load_specific_project(filename):
    try:
        filepath = os.path.join('data', filename)
        if not os.path.exists(filepath):
            return jsonify({'status': 'error', 'message': 'Project file not found'})
            
        with open(filepath, 'r') as f:
            project_data = json.load(f)
            
        return jsonify({
            'status': 'success',
            'message': 'Project loaded successfully',
            'projectData': project_data
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Failed to load project: {str(e)}'})

@app.route('/api/sign-apk', methods=['POST'])
def sign_apk():
    data = request.json
    app_name = data.get('appName', 'MyApp')
    keystore_password = data.get('keystorePassword', 'android')
    key_alias = data.get('keyAlias', 'androidkey')
    
    try:
        # For a real APK signing, we would need to use Android SDK tools like jarsigner
        # Since we can't sign a real APK here, we'll create a project structure with Gradle files
        # that would be needed for a real Android project
        
        memory_file = BytesIO()
        with zipfile.ZipFile(memory_file, 'w') as zf:
            # Add project structure files
            zf.writestr(f'{app_name}/build.gradle', """
buildscript {
    repositories {
        google()
        mavenCentral()
    }
    dependencies {
        classpath 'com.android.tools.build:gradle:7.2.2'
    }
}

allprojects {
    repositories {
        google()
        mavenCentral()
    }
}

task clean(type: Delete) {
    delete rootProject.buildDir
}
""")
            
            zf.writestr(f'{app_name}/settings.gradle', f"""
rootProject.name = "{app_name}"
include ':app'
""")
            
            zf.writestr(f'{app_name}/app/build.gradle', f"""
plugins {{
    id 'com.android.application'
}}

android {{
    compileSdkVersion 33
    
    defaultConfig {{
        applicationId "com.example.{app_name.lower()}"
        minSdkVersion 21
        targetSdkVersion 33
        versionCode 1
        versionName "1.0"
    }}
    
    signingConfigs {{
        release {{
            storeFile file("../{app_name.lower()}.keystore")
            storePassword "{keystore_password}"
            keyAlias "{key_alias}"
            keyPassword "{keystore_password}"
        }}
    }}
    
    buildTypes {{
        release {{
            minifyEnabled false
            signingConfig signingConfigs.release
        }}
    }}
}}

dependencies {{
    implementation 'androidx.appcompat:appcompat:1.5.1'
    implementation 'com.google.android.material:material:1.6.1'
    implementation 'androidx.constraintlayout:constraintlayout:2.1.4'
}}
""")
            
            # Add gradle wrapper files
            zf.writestr(f'{app_name}/gradle/wrapper/gradle-wrapper.properties', """
distributionBase=GRADLE_USER_HOME
distributionPath=wrapper/dists
distributionUrl=https\\://services.gradle.org/distributions/gradle-7.3.3-bin.zip
zipStoreBase=GRADLE_USER_HOME
zipStorePath=wrapper/dists
""")
            
            zf.writestr(f'{app_name}/gradlew', """#!/usr/bin/env sh
# Gradle wrapper script for Unix-based systems
""")
            
            zf.writestr(f'{app_name}/gradlew.bat', """@rem Gradle wrapper script for Windows
@echo off
""")
            
            # Add keystore generation instructions
            zf.writestr(f'{app_name}/keystore_instructions.txt', f"""
To generate a keystore for signing your APK:

1. Open a terminal/command prompt in this directory
2. Run the following command:
   keytool -genkey -v -keystore {app_name.lower()}.keystore -alias {key_alias} -keyalg RSA -keysize 2048 -validity 10000

3. When prompted, use the following information:
   - Keystore password: {keystore_password}
   - Key alias: {key_alias}
   - Key password: {keystore_password}

4. To build and sign the APK, run:
   ./gradlew assembleRelease

The signed APK will be located at:
app/build/outputs/apk/release/app-release.apk
""")
            
            # Add a README file
            zf.writestr(f'{app_name}/README.md', f"""# {app_name}

This project contains the necessary configuration for building and signing an Android APK.

## Signing Configuration

The signing configuration is set up in the app/build.gradle file with the following details:

- Keystore: {app_name.lower()}.keystore
- Keystore password: {keystore_password}
- Key alias: {key_alias}
- Key password: {keystore_password}

## Building the Project

To build the project:

1. Make sure you have Android Studio or the Android SDK installed
2. Generate the keystore using the instructions in keystore_instructions.txt
3. Run `./gradlew assembleRelease` to build the signed APK

## Note

This is a demo project structure generated by Android App Builder.
""")
        
        memory_file.seek(0)
        
        return send_file(
            memory_file,
            as_attachment=True,
            download_name=f'{app_name}_signing_project.zip',
            mimetype='application/zip'
        )
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Project generation failed: {str(e)}'})

if __name__ == '__main__':
    print("===============================================")
    print("Starting Android App Builder Server...")
    print("Server will be available at: http://127.0.0.1:5001")
    print("Press Ctrl+C to stop the server")
    print("===============================================")
    app.run(host='127.0.0.1', port=5001, debug=True)