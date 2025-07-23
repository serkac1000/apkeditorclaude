package com.example.myawesomeapp;

public class HourlyForecast {
    private String time;
    private double temperature;
    private String iconUrl;

    public HourlyForecast(String time, double temperature, String iconUrl) {
        this.time = time;
        this.temperature = temperature;
        this.iconUrl = iconUrl;
    }

    public String getTime() {
        return time;
    }

    public double getTemperature() {
        return temperature;
    }

    public String getIconUrl() {
        return iconUrl;
    }
}