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

public class DailyForecastAdapter extends RecyclerView.Adapter<DailyForecastAdapter.ViewHolder> {

    private ArrayList<DailyForecast> dailyForecastList;

    public DailyForecastAdapter(ArrayList<DailyForecast> dailyForecastList) {
        this.dailyForecastList = dailyForecastList;
    }

    @NonNull
    @Override
    public ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext()).inflate(R.layout.daily_forecast_item, parent, false);
        return new ViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull ViewHolder holder, int position) {
        DailyForecast forecast = dailyForecastList.get(position);
        holder.dayTextView.setText(forecast.getDay());
        holder.temperatureTextView.setText(String.format(Locale.getDefault(), "%.1f°C", forecast.getTemperature()));
        Picasso.get().load(forecast.getIconUrl()).into(holder.iconImageView);
    }

    @Override
    public int getItemCount() {
        return dailyForecastList.size();
    }

    public static class ViewHolder extends RecyclerView.ViewHolder {
        TextView dayTextView, temperatureTextView;
        ImageView iconImageView;

        public ViewHolder(@NonNull View itemView) {
            super(itemView);
            dayTextView = itemView.findViewById(R.id.dailyDayTextView);
            temperatureTextView = itemView.findViewById(R.id.dailyTempTextView);
            iconImageView = itemView.findViewById(R.id.dailyIconImageView);
        }
    }
}