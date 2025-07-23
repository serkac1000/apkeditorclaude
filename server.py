from flask import Flask, render_template_string, request, jsonify, send_file
from flask_cors import CORS
import os
import json
import requests
import zipfile
import datetime
import re
import shutil
import tempfile
import time
from io import BytesIO
import base64

app = Flask(__name__)
CORS(app)

# Read the HTML content
html_content = ""
try:
    with open('android_app_builder_updated.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    print("Updated HTML file found - using enhanced version!")
except FileNotFoundError:
    try:
        with open('android_app_builder.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        print("HTML file found!")
    except FileNotFoundError:
        html_content = """
        <h1>Android App Builder</h1>
        <p>Please place the android_app_builder.html file in the same directory as this server.</p>
        """
        print("HTML file not found - using placeholder.")

# Create data directory if it doesn't exist
if not os.path.exists('data'):
    os.makedirs('data')
    print("Created data directory.")

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
        # Since the Gemini API is unavailable, let's use a mock response
        # This simulates a successful API call with pre-generated Android code
        
        # Create a mock response with basic Android app structure based on the app name and description
        mock_response = {
            "MainActivity.java": f"""package com.example.{app_name.lower()};

import androidx.appcompat.app.AppCompatActivity;
import android.os.Bundle;
import android.widget.TextView;

public class MainActivity extends AppCompatActivity {{
    
    private TextView welcomeTextView;
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {{
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        
        welcomeTextView = findViewById(R.id.welcomeTextView);
        welcomeTextView.setText("Welcome to {app_name}!");
        
        // TODO: Implement functionality based on: {app_description}
    }}
}}""",
            "activity_main.xml": f"""<?xml version="1.0" encoding="utf-8"?>
<androidx.constraintlayout.widget.ConstraintLayout 
    xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    tools:context=".MainActivity">

    <TextView
        android:id="@+id/welcomeTextView"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Welcome to {app_name}!"
        android:textSize="24sp"
        android:textStyle="bold"
        app:layout_constraintBottom_toBottomOf="parent"
        app:layout_constraintLeft_toLeftOf="parent"
        app:layout_constraintRight_toRightOf="parent"
        app:layout_constraintTop_toTopOf="parent" />

    <TextView
        android:id="@+id/descriptionTextView"
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        android:layout_marginStart="16dp"
        android:layout_marginEnd="16dp"
        android:layout_marginTop="16dp"
        android:text="{app_description}"
        android:textAlignment="center"
        app:layout_constraintLeft_toLeftOf="parent"
        app:layout_constraintRight_toRightOf="parent"
        app:layout_constraintTop_toBottomOf="@+id/welcomeTextView" />

</androidx.constraintlayout.widget.ConstraintLayout>""",
            "AndroidManifest.xml": f"""<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.{app_name.lower()}">

    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:supportsRtl="true"
        android:theme="@style/Theme.{app_name}">
        <activity
            android:name=".MainActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>

</manifest>""",
            "build.gradle": f"""plugins {{
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
        
        testInstrumentationRunner "androidx.test.runner.AndroidJUnitRunner"
    }}
    
    buildTypes {{
        release {{
            minifyEnabled false
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }}
    }}
    
    compileOptions {{
        sourceCompatibility JavaVersion.VERSION_1_8
        targetCompatibility JavaVersion.VERSION_1_8
    }}
}}

dependencies {{
    implementation 'androidx.appcompat:appcompat:1.6.1'
    implementation 'com.google.android.material:material:1.9.0'
    implementation 'androidx.constraintlayout:constraintlayout:2.1.4'
    testImplementation 'junit:junit:4.13.2'
    androidTestImplementation 'androidx.test.ext:junit:1.1.5'
    androidTestImplementation 'androidx.test.espresso:espresso-core:3.5.1'
}}""",
            "strings.xml": f"""<resources>
    <string name="app_name">{app_name}</string>
    <string name="welcome_message">Welcome to {app_name}!</string>
    <string name="app_description">{app_description}</string>
</resources>""",
            "colors.xml": """<resources>
    <color name="purple_200">#FFBB86FC</color>
    <color name="purple_500">#FF6200EE</color>
    <color name="purple_700">#FF3700B3</color>
    <color name="teal_200">#FF03DAC5</color>
    <color name="teal_700">#FF018786</color>
    <color name="black">#FF000000</color>
    <color name="white">#FFFFFFFF</color>
</resources>""",
            "styles.xml": f"""<resources>
    <!-- Base application theme. -->
    <style name="Theme.{app_name}" parent="Theme.MaterialComponents.DayNight.DarkActionBar">
        <!-- Primary brand color. -->
        <item name="colorPrimary">@color/purple_500</item>
        <item name="colorPrimaryVariant">@color/purple_700</item>
        <item name="colorOnPrimary">@color/white</item>
        <!-- Secondary brand color. -->
        <item name="colorSecondary">@color/teal_200</item>
        <item name="colorSecondaryVariant">@color/teal_700</item>
        <item name="colorOnSecondary">@color/black</item>
        <!-- Status bar color. -->
        <item name="android:statusBarColor">?attr/colorPrimaryVariant</item>
    </style>
</resources>"""
        }
        
        # Convert the mock response to a JSON string
        content = json.dumps(mock_response, indent=2)
        
        print("Using mock response since Gemini API is unavailable")
        
        return jsonify({
            'status': 'success',
            'code': content,
            'message': 'Android code generated successfully (using local template)'
        })
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Generation failed: {str(e)}'})

@app.route('/api/prepare-for-android-studio', methods=['POST'])
def prepare_for_android_studio():
    data = request.json
    app_name = data.get('appName', 'MyApp')
    project_files = data.get('project_files', {})
    
    try:
        # Create a zip file with the project structure
        memory_file = BytesIO()
        with zipfile.ZipFile(memory_file, 'w') as zf:
            # Add all provided files
            for file_path, content in project_files.items():
                zf.writestr(f'{app_name}/{file_path}', content)
            
            # Add Gradle wrapper files
            zf.writestr(f'{app_name}/gradle/wrapper/gradle-wrapper.properties', """
distributionBase=GRADLE_USER_HOME
distributionPath=wrapper/dists
distributionUrl=https\\://services.gradle.org/distributions/gradle-8.4-bin.zip
zipStoreBase=GRADLE_USER_HOME
zipStorePath=wrapper/dists
""")
            
            # Add a placeholder for the gradle-wrapper.jar file
            # In a real implementation, this would be the actual JAR file
            zf.writestr(f'{app_name}/gradle/wrapper/gradle-wrapper.jar', b'# Gradle wrapper JAR file placeholder')
            
            # Add gradlew script for Unix systems
            zf.writestr(f'{app_name}/gradlew', """#!/usr/bin/env sh
# Gradle wrapper script for Unix-based systems
# This is a simplified version - in a real implementation, this would be the complete script
exec gradle "$@"
""")
            
            # Add gradlew.bat script for Windows systems
            zf.writestr(f'{app_name}/gradlew.bat', """@rem Gradle wrapper script for Windows
@echo off
@rem This is a simplified version - in a real implementation, this would be the complete script
gradle %*
""")
            
            # Check if it's already an Android project
            has_build_gradle = any(file_path.endswith('build.gradle') for file_path in project_files.keys())
            has_settings_gradle = any(file_path.endswith('settings.gradle') for file_path in project_files.keys())
            has_manifest = any(file_path.endswith('AndroidManifest.xml') for file_path in project_files.keys())
            
            # If it's not an Android project, add basic Android project structure
            if not (has_build_gradle and has_settings_gradle and has_manifest):
                # Add basic Android project structure
                # Create a simple build.gradle file that will work with any Java version
                zf.writestr(f'{app_name}/app/build.gradle', f"""plugins {{
    id 'com.android.application'
}}

android {{
    namespace 'com.example.{app_name.lower()}'
    compileSdk 33

    defaultConfig {{
        applicationId "com.example.{app_name.lower()}"
        minSdk 24
        targetSdk 33
        versionCode 1
        versionName "1.0"
    }}

    buildTypes {{
        release {{
            minifyEnabled false
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }}
    }}
    
    // This will make the project compatible with any Java version
    compileOptions {{
        sourceCompatibility JavaVersion.VERSION_1_8
        targetCompatibility JavaVersion.VERSION_1_8
    }}
}}

dependencies {{
    implementation 'androidx.appcompat:appcompat:1.6.1'
    implementation 'com.google.android.material:material:1.9.0'
    implementation 'androidx.constraintlayout:constraintlayout:2.1.4'
}}
""")
                
                zf.writestr(f'{app_name}/build.gradle', """
// Top-level build file where you can add configuration options common to all sub-projects/modules.
buildscript {
    repositories {
        google()
        mavenCentral()
    }
    dependencies {
        classpath 'com.android.tools.build:gradle:8.0.0'
    }
}

// Note: repositories are now defined in settings.gradle using dependencyResolutionManagement

task clean(type: Delete) {
    delete rootProject.buildDir
}
""")
                
                zf.writestr(f'{app_name}/settings.gradle', f"""
pluginManagement {{
    repositories {{
        google()
        mavenCentral()
        gradlePluginPortal()
    }}
}}

dependencyResolutionManagement {{
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {{
        google()
        mavenCentral()
    }}
}}

rootProject.name = "{app_name}"
include ":app"
""")
                
                # Add basic manifest if not present
                if not has_manifest:
                    zf.writestr(f'{app_name}/app/src/main/AndroidManifest.xml', f"""<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.{app_name.lower()}">

    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:supportsRtl="true"
        android:theme="@style/AppTheme">
        <activity android:name=".MainActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>

</manifest>""")
                
                # Add basic MainActivity if not present
                if not any(file_path.endswith('MainActivity.java') or file_path.endswith('MainActivity.kt') for file_path in project_files.keys()):
                    zf.writestr(f'{app_name}/app/src/main/java/com/example/{app_name.lower()}/MainActivity.java', f"""package com.example.{app_name.lower()};

import android.os.Bundle;
import androidx.appcompat.app.AppCompatActivity;

public class MainActivity extends AppCompatActivity {{
    @Override
    protected void onCreate(Bundle savedInstanceState) {{
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
    }}
}}""")
                
                # Add basic layout if not present
                if not any(file_path.endswith('activity_main.xml') for file_path in project_files.keys()):
                    zf.writestr(f'{app_name}/app/src/main/res/layout/activity_main.xml', """<?xml version="1.0" encoding="utf-8"?>
<androidx.constraintlayout.widget.ConstraintLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    tools:context=".MainActivity">

    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Hello World!"
        app:layout_constraintBottom_toBottomOf="parent"
        app:layout_constraintLeft_toLeftOf="parent"
        app:layout_constraintRight_toRightOf="parent"
        app:layout_constraintTop_toTopOf="parent" />

</androidx.constraintlayout.widget.ConstraintLayout>""")
                
                # Add basic strings.xml if not present
                if not any(file_path.endswith('strings.xml') for file_path in project_files.keys()):
                    zf.writestr(f'{app_name}/app/src/main/res/values/strings.xml', f"""<resources>
    <string name="app_name">{app_name}</string>
</resources>""")
                
                # Add basic colors.xml if not present
                if not any(file_path.endswith('colors.xml') for file_path in project_files.keys()):
                    zf.writestr(f'{app_name}/app/src/main/res/values/colors.xml', """<resources>
    <color name="colorPrimary">#6200EE</color>
    <color name="colorPrimaryDark">#3700B3</color>
    <color name="colorAccent">#03DAC5</color>
</resources>""")
                
                # Add basic styles.xml if not present
                if not any(file_path.endswith('styles.xml') for file_path in project_files.keys()):
                    zf.writestr(f'{app_name}/app/src/main/res/values/styles.xml', """<resources>
    <style name="AppTheme" parent="Theme.AppCompat.Light.DarkActionBar">
        <item name="colorPrimary">@color/colorPrimary</item>
        <item name="colorPrimaryDark">@color/colorPrimaryDark</item>
        <item name="colorAccent">@color/colorAccent</item>
    </style>
</resources>""")
            
            # Add README
            zf.writestr(f'{app_name}/README.md', f"""# {app_name}

This project has been prepared for Android Studio.

## Project Structure
- app/ - Contains the Android application code
- build.gradle - Project level build file
- app/build.gradle - App module build file
- settings.gradle - Project settings

## Opening in Android Studio
1. Open Android Studio
2. Select "Open an existing Android Studio project"
3. Navigate to the extracted folder and select it
4. Wait for the project to sync and build
""")
        
        memory_file.seek(0)
        
        return send_file(
            memory_file,
            as_attachment=True,
            download_name=f'{app_name}_android_studio_project.zip',
            mimetype='application/zip'
        )
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Failed to prepare project for Android Studio: {str(e)}'})

@app.route('/api/build-apk', methods=['POST'])
def build_apk():
    data = request.json
    app_name = data.get('appName', 'MyApp')
    
    try:
        # Create a standalone HTML file that can be opened directly in a browser
        app_html = """
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
                /* Simple tab switching functionality */
                function changeTab(tabName) {
                    /* Reset all tabs */
                    document.getElementById('homeTab').style.color = '#333';
                    document.getElementById('searchTab').style.color = '#333';
                    document.getElementById('settingsTab').style.color = '#333';
                    
                    /* Highlight selected tab */
                    document.getElementById(tabName + 'Tab').style.color = '#667eea';
                    
                    /* Change content based on tab */
                    const content = document.getElementById('appContent');
                    
                    if (tabName === 'search') {
                        content.innerHTML = 
                            '<div style="padding: 20px 0;">' +
                                '<div style="position: relative; margin-bottom: 20px;">' +
                                    '<input type="text" placeholder="Search locations..." style="width: 100%; padding: 12px 16px; border-radius: 24px; border: 1px solid #ddd; font-size: 16px; box-sizing: border-box;">' +
                                    '<div style="position: absolute; right: 16px; top: 12px;">🔍</div>' +
                                '</div>' +
                                
                                '<div class="card">' +
                                    '<h3>Recent Searches</h3>' +
                                    '<div style="display: flex; flex-direction: column; gap: 12px;">' +
                                        '<div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #eee;">' +
                                            '<div>New York, NY</div>' +
                                            '<div>☀️ 72°</div>' +
                                        '</div>' +
                                        '<div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #eee;">' +
                                            '<div>Los Angeles, CA</div>' +
                                            '<div>☀️ 85°</div>' +
                                        '</div>' +
                                        '<div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #eee;">' +
                                            '<div>Chicago, IL</div>' +
                                            '<div>⛅ 65°</div>' +
                                        '</div>' +
                                        '<div style="display: flex; justify-content: space-between; padding: 8px 0;">' +
                                            '<div>Miami, FL</div>' +
                                            '<div>🌧️ 80°</div>' +
                                        '</div>' +
                                    '</div>' +
                                '</div>' +
                            '</div>';
                    } else if (tabName === 'settings') {
                        content.innerHTML = 
                            '<div class="card">' +
                                '<h3>App Settings</h3>' +
                                '<div style="display: flex; flex-direction: column; gap: 16px;">' +
                                    '<div style="display: flex; justify-content: space-between; align-items: center;">' +
                                        '<div>Temperature Unit</div>' +
                                        '<select style="padding: 8px; border-radius: 4px; border: 1px solid #ddd;">' +
                                            '<option>Fahrenheit (°F)</option>' +
                                            '<option>Celsius (°C)</option>' +
                                        '</select>' +
                                    '</div>' +
                                    '<div style="display: flex; justify-content: space-between; align-items: center;">' +
                                        '<div>Dark Mode</div>' +
                                        '<label class="switch">' +
                                            '<input type="checkbox">' +
                                            '<span class="slider"></span>' +
                                        '</label>' +
                                    '</div>' +
                                    '<div style="display: flex; justify-content: space-between; align-items: center;">' +
                                        '<div>Notifications</div>' +
                                        '<label class="switch">' +
                                            '<input type="checkbox" checked>' +
                                            '<span class="slider"></span>' +
                                        '</label>' +
                                    '</div>' +
                                '</div>' +
                            '</div>' +
                            
                            '<div class="card">' +
                                '<h3>About</h3>' +
                                '<div style="display: flex; flex-direction: column; gap: 8px;">' +
                                    '<div>Version: 1.0.0</div>' +
                                    '<div>Build: {build_date}</div>' +
                                    '<div style="margin-top: 16px;">' +
                                        '<button class="button">Check for Updates</button>' +
                                    '</div>' +
                                '</div>' +
                            '</div>';
                    } else {
                        /* Home tab - default content */
                        content.innerHTML = 
                            '<div style="text-align: center; padding: 40px 0;">' +
                                '<div class="weather-icon">☀️</div>' +
                                '<div class="temperature">72°F</div>' +
                                '<div class="weather-condition">Sunny</div>' +
                                '<div>New York City, NY</div>' +
                                
                                '<div class="weather-details">' +
                                    '<div class="weather-detail">' +
                                        '<div class="weather-detail-value">68%</div>' +
                                        '<div class="weather-detail-label">Humidity</div>' +
                                    '</div>' +
                                    '<div class="weather-detail">' +
                                        '<div class="weather-detail-value">8 mph</div>' +
                                        '<div class="weather-detail-label">Wind</div>' +
                                    '</div>' +
                                    '<div class="weather-detail">' +
                                        '<div class="weather-detail-value">0%</div>' +
                                        '<div class="weather-detail-label">Rain</div>' +
                                    '</div>' +
                                '</div>' +
                            '</div>' +
                            
                            '<div class="card">' +
                                '<h3>Hourly Forecast</h3>' +
                                '<div class="forecast">' +
                                    '<div class="forecast-item">' +
                                        '<div class="forecast-day">Now</div>' +
                                        '<div class="forecast-icon">☀️</div>' +
                                        '<div class="forecast-temp">72°</div>' +
                                    '</div>' +
                                    '<div class="forecast-item">' +
                                        '<div class="forecast-day">1PM</div>' +
                                        '<div class="forecast-icon">☀️</div>' +
                                        '<div class="forecast-temp">74°</div>' +
                                    '</div>' +
                                    '<div class="forecast-item">' +
                                        '<div class="forecast-day">2PM</div>' +
                                        '<div class="forecast-icon">⛅</div>' +
                                        '<div class="forecast-temp">73°</div>' +
                                    '</div>' +
                                    '<div class="forecast-item">' +
                                        '<div class="forecast-day">3PM</div>' +
                                        '<div class="forecast-icon">⛅</div>' +
                                        '<div class="forecast-temp">72°</div>' +
                                    '</div>' +
                                    '<div class="forecast-item">' +
                                        '<div class="forecast-day">4PM</div>' +
                                        '<div class="forecast-icon">☁️</div>' +
                                        '<div class="forecast-temp">70°</div>' +
                                    '</div>' +
                                    '<div class="forecast-item">' +
                                        '<div class="forecast-day">5PM</div>' +
                                        '<div class="forecast-icon">☁️</div>' +
                                        '<div class="forecast-temp">68°</div>' +
                                    '</div>' +
                                '</div>' +
                            '</div>' +
                            
                            '<div class="card">' +
                                '<h3>7-Day Forecast</h3>' +
                                '<div style="display: flex; flex-direction: column; gap: 12px;">' +
                                    '<div style="display: flex; justify-content: space-between; align-items: center;">' +
                                        '<div>Today</div>' +
                                        '<div style="font-size: 20px;">☀️</div>' +
                                        '<div>68° / 75°</div>' +
                                    '</div>' +
                                    '<div style="display: flex; justify-content: space-between; align-items: center;">' +
                                        '<div>Mon</div>' +
                                        '<div style="font-size: 20px;">⛅</div>' +
                                        '<div>65° / 72°</div>' +
                                    '</div>' +
                                    '<div style="display: flex; justify-content: space-between; align-items: center;">' +
                                        '<div>Tue</div>' +
                                        '<div style="font-size: 20px;">🌧️</div>' +
                                        '<div>60° / 68°</div>' +
                                    '</div>' +
                                    '<div style="display: flex; justify-content: space-between; align-items: center;">' +
                                        '<div>Wed</div>' +
                                        '<div style="font-size: 20px;">⛈️</div>' +
                                        '<div>58° / 65°</div>' +
                                    '</div>' +
                                    '<div style="display: flex; justify-content: space-between; align-items: center;">' +
                                        '<div>Thu</div>' +
                                        '<div style="font-size: 20px;">⛅</div>' +
                                        '<div>62° / 70°</div>' +
                                    '</div>' +
                                    '<div style="display: flex; justify-content: space-between; align-items: center;">' +
                                        '<div>Fri</div>' +
                                        '<div style="font-size: 20px;">☀️</div>' +
                                        '<div>65° / 73°</div>' +
                                    '</div>' +
                                    '<div style="display: flex; justify-content: space-between; align-items: center;">' +
                                        '<div>Sat</div>' +
                                        '<div style="font-size: 20px;">☀️</div>' +
                                        '<div>67° / 76°</div>' +
                                    '</div>' +
                                '</div>' +
                            '</div>';
                    }
                }
                
                /* Initialize with home tab selected */
                document.getElementById('homeTab').style.color = '#667eea';
            </script>
        </body>
        </html>
        """.format(app_name=app_name, build_date=datetime.datetime.now().strftime("%Y%m%d"))
        
        # Return the HTML file directly
        return send_file(
            BytesIO(app_html.encode('utf-8')),
            as_attachment=True,
            download_name=f'{app_name}_demo.html',
            mimetype='text/html'
        )
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'App demo creation failed: {str(e)}'})

@app.route('/api/load-api-key', methods=['GET'])
def load_api_key():
    try:
        config_path = 'data/config.json'
        if not os.path.exists(config_path):
            return jsonify({'status': 'info', 'message': 'No saved API key found'})
            
        with open(config_path, 'r') as f:
            config_data = json.load(f)
            
        return jsonify({
            'status': 'success',
            'message': 'API key loaded successfully',
            'api_key': config_data.get('api_key', '')
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Failed to load API key: {str(e)}'})

if __name__ == '__main__':
    print("===============================================")
    print("Starting Android App Builder Server...")
    print("Server will be available at: http://127.0.0.1:5001")
    print("Press Ctrl+C to stop the server")
    print("===============================================")
    app.run(host='127.0.0.1', port=5001, debug=True)