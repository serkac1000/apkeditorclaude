package com.example.myawesomeapp;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.squareup.picasso.Picasso;

import java.util.ArrayList;
import java.util.Locale;

public class HourlyForecastAdapter extends RecyclerView.Adapter<HourlyForecastAdapter.ViewHolder> {

    private ArrayList<HourlyForecast> hourlyForecastList;

    public HourlyForecastAdapter(ArrayList<HourlyForecast> hourlyForecastList) {
        this.hourlyForecastList = hourlyForecastList;
    }

    @NonNull
    @Override
    public ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext()).inflate(R.layout.hourly_forecast_item, parent, false);
        return new ViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull ViewHolder holder, int position) {
        HourlyForecast forecast = hourlyForecastList.get(position);
        holder.timeTextView.setText(forecast.getTime());
        holder.temperatureTextView.setText(String.format(Locale.getDefault(), "%.1f°C", forecast.getTemperature()));
        Picasso.get().load(forecast.getIconUrl()).into(holder.iconImageView);
    }

    @Override
    public int getItemCount() {
        return hourlyForecastList.size();
    }

    public static class ViewHolder extends RecyclerView.ViewHolder {
        TextView timeTextView, temperatureTextView;
        ImageView iconImageView;

        public ViewHolder(@NonNull View itemView) {
            super(itemView);
            timeTextView = itemView.findViewById(R.id.hourlyTimeTextView);
            temperatureTextView = itemView.findViewById(R.id.hourlyTempTextView);
            iconImageView = itemView.findViewById(R.id.hourlyIconImageView);
        }
    }
}