package com.example.myawesomeapp;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import android.Manifest;
import android.annotation.SuppressLint;
import android.content.pm.PackageManager;
import android.location.Location;
import android.os.Bundle;
import android.util.Log;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import com.android.volley.Request;
import com.android.volley.RequestQueue;
import com.android.volley.Response;
import com.android.volley.VolleyError;
import com.android.volley.toolbox.JsonObjectRequest;
import com.android.volley.toolbox.Volley;

import com.google.android.gms.location.FusedLocationProviderClient;
import com.google.android.gms.location.LocationServices;
import com.squareup.picasso.Picasso;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.Locale;

public class MainActivity extends AppCompatActivity {

    private static final int LOCATION_PERMISSION_REQUEST_CODE = 100;
    private static final String TAG = "MainActivity";
    private FusedLocationProviderClient fusedLocationClient;
    private TextView cityTextView, temperatureTextView, descriptionTextView, dateTextView;
    private ImageView weatherIconImageView;
    private RecyclerView hourlyForecastRecyclerView, dailyForecastRecyclerView;
    private HourlyForecastAdapter hourlyForecastAdapter;
    private DailyForecastAdapter dailyForecastAdapter;
    private ArrayList<HourlyForecast> hourlyForecastList;
    private ArrayList<DailyForecast> dailyForecastList;
    // Replace with your actual OpenWeatherMap API key
    private String apiKey = "YOUR_OPENWEATHERMAP_API_KEY"; 
    private double latitude, longitude;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        cityTextView = findViewById(R.id.cityTextView);
        temperatureTextView = findViewById(R.id.temperatureTextView);
        descriptionTextView = findViewById(R.id.descriptionTextView);
        dateTextView = findViewById(R.id.dateTextView);
        weatherIconImageView = findViewById(R.id.weatherIconImageView);
        hourlyForecastRecyclerView = findViewById(R.id.hourlyForecastRecyclerView);
        dailyForecastRecyclerView = findViewById(R.id.dailyForecastRecyclerView);

        hourlyForecastList = new ArrayList<>();
        dailyForecastList = new ArrayList<>();

        hourlyForecastRecyclerView.setLayoutManager(new LinearLayoutManager(this, LinearLayoutManager.HORIZONTAL, false));
        hourlyForecastAdapter = new HourlyForecastAdapter(hourlyForecastList);
        hourlyForecastRecyclerView.setAdapter(hourlyForecastAdapter);

        dailyForecastRecyclerView.setLayoutManager(new LinearLayoutManager(this));
        dailyForecastAdapter = new DailyForecastAdapter(dailyForecastList);
        dailyForecastRecyclerView.setAdapter(dailyForecastAdapter);

        fusedLocationClient = LocationServices.getFusedLocationProviderClient(this);

        if (ActivityCompat.checkSelfPermission(this, Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(this, new String[]{Manifest.permission.ACCESS_FINE_LOCATION}, LOCATION_PERMISSION_REQUEST_CODE);
            return;
        }

        fetchLocation();
    }

    @SuppressLint("MissingPermission")
    private void fetchLocation() {
        if (ActivityCompat.checkSelfPermission(this, Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED && 
            ActivityCompat.checkSelfPermission(this, Manifest.permission.ACCESS_COARSE_LOCATION) != PackageManager.PERMISSION_GRANTED) {
            return;
        }
        
        fusedLocationClient.getLastLocation().addOnSuccessListener(this, location -> {
            if (location != null) {
                latitude = location.getLatitude();
                longitude = location.getLongitude();
                fetchWeatherData(latitude, longitude);
            } else {
                Toast.makeText(this, "Could not get location. Using default location.", Toast.LENGTH_SHORT).show();
                // Default location (e.g., London)
                fetchWeatherData(51.5074, 0.1278);
            }
        }).addOnFailureListener(e -> {
            Log.e(TAG, "Error getting location: " + String.valueOf(e));
            Toast.makeText(this, "Error getting location. Using default location.", Toast.LENGTH_SHORT).show();
            // Default location (e.g., London)
            fetchWeatherData(51.5074, 0.1278);
        });
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions, @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == LOCATION_PERMISSION_REQUEST_CODE) {
            if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                fetchLocation();
            } else {
                Toast.makeText(this, "Location permission denied. Using default location.", Toast.LENGTH_SHORT).show();
                // Default location (e.g., London)
                fetchWeatherData(51.5074, 0.1278);
            }
        }
    }

    private void fetchWeatherData(double latitude, double longitude) {
        // Use HTTPS instead of HTTP for security
        String url = "https://api.openweathermap.org/data/2.5/forecast?lat=" + latitude + "&lon=" + longitude + "&appid=" + apiKey + "&units=metric";

        JsonObjectRequest jsonObjectRequest = new JsonObjectRequest(Request.Method.GET, url, null,
                new Response.Listener<JSONObject>() {
                    @Override
                    public void onResponse(JSONObject response) {
                        try {
                            JSONObject city = response.getJSONObject("city");
                            String cityName = city.getString("name");
                            cityTextView.setText(cityName);

                            JSONArray list = response.getJSONArray("list");
                            hourlyForecastList.clear();
                            dailyForecastList.clear();

                            SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.getDefault());
                            SimpleDateFormat dayOfWeekFormat = new SimpleDateFormat("EEE", Locale.getDefault());

                            for (int i = 0; i < list.length(); i++) {
                                JSONObject forecast = list.getJSONObject(i);
                                JSONObject main = forecast.getJSONObject("main");
                                JSONArray weatherArray = forecast.getJSONArray("weather");
                                JSONObject weather = weatherArray.getJSONObject(0);

                                String dateTimeString = forecast.getString("dt_txt");

                                Date dateTime = sdf.parse(dateTimeString);
                                if (dateTime == null) continue;

                                String time = new SimpleDateFormat("HH:mm", Locale.getDefault()).format(dateTime);
                                String dayOfWeek = dayOfWeekFormat.format(dateTime);
                                double temperature = main.getDouble("temp");
                                String description = weather.getString("description");
                                String icon = weather.getString("icon");
                                String iconUrl = "https://openweathermap.org/img/w/" + icon + ".png";

                                if (i == 0) {
                                    temperatureTextView.setText(String.format(Locale.getDefault(), "%.1f°C", temperature));
                                    descriptionTextView.setText(description);
                                    Picasso.get().load(iconUrl).into(weatherIconImageView);
                                    dateTextView.setText(new SimpleDateFormat("EEEE, MMMM d", Locale.getDefault()).format(new Date()));
                                }

                                hourlyForecastList.add(new HourlyForecast(time, temperature, iconUrl));

                                // Add to daily forecast (only once per day)
                                if (i % 8 == 0) {
                                    double dailyTemp = main.getDouble("temp");
                                    String dailyIcon = weather.getString("icon");
                                    String dailyIconUrl = "https://openweathermap.org/img/w/" + dailyIcon + ".png";
                                    dailyForecastList.add(new DailyForecast(dayOfWeek, dailyTemp, dailyIconUrl));
                                }
                            }

                            hourlyForecastAdapter.notifyDataSetChanged();
                            dailyForecastAdapter.notifyDataSetChanged();

                        } catch (JSONException e) {
                            Log.e(TAG, "JSON Error: " + String.valueOf(e));
                            Toast.makeText(MainActivity.this, "Error parsing weather data.", Toast.LENGTH_SHORT).show();
                        } catch (java.text.ParseException e) {
                            Log.e(TAG, "Parse Error: " + String.valueOf(e));
                            Toast.makeText(MainActivity.this, "Error parsing date format.", Toast.LENGTH_SHORT).show();
                        }
                    }
                },
                new Response.ErrorListener() {
                    @Override
                    public void onErrorResponse(VolleyError error) {
                        // Improved error handling
                        Log.e(TAG, "Volley Error: " + String.valueOf(error));
                        Toast.makeText(MainActivity.this, "Error fetching weather data.", Toast.LENGTH_SHORT).show();
                    }
                });

        RequestQueue requestQueue = Volley.newRequestQueue(this);
        requestQueue.add(jsonObjectRequest);
    }
}