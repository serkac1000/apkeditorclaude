package com.example.myawesomeapp;

public class DailyForecast {
    private String day;
    private double temperature;
    private String iconUrl;

    public DailyForecast(String day, double temperature, String iconUrl) {
        this.day = day;
        this.temperature = temperature;
        this.iconUrl = iconUrl;
    }

    public String getDay() {
        return day;
    }

    public double getTemperature() {
        return temperature;
    }

    public String getIconUrl() {
        return iconUrl;
    }
}