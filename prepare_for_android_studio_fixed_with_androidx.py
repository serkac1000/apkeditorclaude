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
            
            # Add gradle.properties file with AndroidX configuration
            zf.writestr(f'{app_name}/gradle.properties', """
# Project-wide Gradle settings.
# IDE (e.g. Android Studio) users:
# Gradle settings configured through the IDE *will override*
# any settings specified in this file.
# For more details on how to configure your build environment visit
# http://www.gradle.org/docs/current/userguide/build_environment.html

# Specifies the JVM arguments used for the daemon process.
# The setting is particularly useful for tweaking memory settings.
org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8

# When configured, Gradle will run in incubating parallel mode.
# This option should only be used with decoupled projects. More details, visit
# http://www.gradle.org/docs/current/userguide/multi_project_builds.html#sec:decoupled_projects
# org.gradle.parallel=true

# AndroidX package structure to make it clearer which packages are bundled with the
# Android operating system, and which are packaged with your app's APK
# https://developer.android.com/topic/libraries/support-library/androidx-rn
android.useAndroidX=true

# Automatically convert third-party libraries to use AndroidX
android.enableJetifier=true
""")
            
            # Check if it's already an Android project
            has_build_gradle = any(file_path.endswith('build.gradle') for file_path in project_files.keys())
            has_settings_gradle = any(file_path.endswith('settings.gradle') for file_path in project_files.keys())
            has_manifest = any(file_path.endswith('AndroidManifest.xml') for file_path in project_files.keys())
            
            # If it's not an Android project, add basic Android project structure
            if not (has_build_gradle and has_settings_gradle and has_manifest):
                # Add basic Android project structure
                zf.writestr(f'{app_name}/app/build.gradle', """
apply plugin: 'com.android.application'

android {
    compileSdkVersion 33
    defaultConfig {
        applicationId "com.example.${app_name.toLowerCase()}"
        minSdkVersion 21
        targetSdkVersion 33
        versionCode 1
        versionName "1.0"
    }
    buildTypes {
        release {
            minifyEnabled false
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }
    }
}

dependencies {
    implementation 'androidx.appcompat:appcompat:1.5.1'
    implementation 'com.google.android.material:material:1.6.1'
    implementation 'androidx.constraintlayout:constraintlayout:2.1.4'
}
""".replace("${app_name.toLowerCase()}", app_name.lower()))
                
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
                
                zf.writestr(f'{app_name}/settings.gradle', f'rootProject.name = "{app_name}"\ninclude ":app"')
                
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