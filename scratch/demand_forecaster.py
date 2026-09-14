"""
Destino Vivo RMS - 4-Model Ensemble Demand Forecasting Pipeline
Implements ARIMA, Prophet-style, LSTM-style, and XGBoost-style models for 1d, 7d, 30d, 90d occupancy forecasting.
"""

import math
import random
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("DemandForecaster")

# Standard seed for reproducibility
random.seed(42)

class FeatureEngineer:
    """Feature engineering pipeline for time-series ML demand forecasting."""
    
    @staticmethod
    def extract_features(historical_series: List[Dict[str, Any]], target_idx: int) -> Dict[str, float]:
        """Extract lag features, rolling statistics, seasonal indicators, and external drivers."""
        if target_idx < 30:
            padding_len = 30 - target_idx
            first_val = historical_series[0]["occupancy"] if historical_series else 0.5
            pad = [{"occupancy": first_val, "comp_price": 100.0, "temp": 25.0, "is_holiday": 0} for _ in range(padding_len)]
            series = pad + historical_series[:target_idx]
            curr_idx = 29
        else:
            series = historical_series[:target_idx]
            curr_idx = len(series) - 1

        recent_vals = [s["occupancy"] for s in series]
        
        # Lag features
        lag_1 = recent_vals[curr_idx] if curr_idx >= 0 else 0.5
        lag_2 = recent_vals[curr_idx - 1] if curr_idx >= 1 else lag_1
        lag_7 = recent_vals[curr_idx - 6] if curr_idx >= 6 else lag_1
        lag_14 = recent_vals[curr_idx - 13] if curr_idx >= 13 else lag_7
        lag_30 = recent_vals[curr_idx - 29] if curr_idx >= 29 else lag_14
        
        delta_1d = lag_1 - lag_2
        
        # Rolling averages
        r7_vals = recent_vals[max(0, curr_idx - 6):curr_idx + 1]
        roll_mean_7 = sum(r7_vals) / len(r7_vals)
        r30_vals = recent_vals[max(0, curr_idx - 29):curr_idx + 1]
        roll_mean_30 = sum(r30_vals) / len(r30_vals)
        
        current_data = series[curr_idx]
        day_of_week = current_data.get("day_of_week", 3)
        is_weekend = 1.0 if day_of_week in [5, 6] else 0.0
        is_holiday = float(current_data.get("is_holiday", 0))
        comp_price = float(current_data.get("comp_price", 100.0))
        temp = float(current_data.get("temp", 25.0))
        
        return {
            "lag_1": lag_1,
            "lag_2": lag_2,
            "lag_7": lag_7,
            "lag_14": lag_14,
            "lag_30": lag_30,
            "delta_1d": delta_1d,
            "roll_mean_7": roll_mean_7,
            "roll_mean_30": roll_mean_30,
            "day_of_week": float(day_of_week),
            "is_weekend": is_weekend,
            "is_holiday": is_holiday,
            "comp_price": comp_price,
            "temp": temp
        }

class ARIMAModel:
    """AutoRegressive Integrated Moving Average (ARIMA) Model approximation."""
    
    def __init__(self, p: int = 2, d: int = 1, q: int = 1):
        self.p = p
        self.d = d
        self.q = q
        self.phi = [0.5, 0.2]
        self.theta = [0.15]
        
    def fit_predict(self, series: List[float], horizons: List[int]) -> Dict[int, float]:
        """Fit ARIMA model on historical series and forecast target horizons."""
        if len(series) < 7:
            last_val = series[-1] if series else 0.5
            return {h: last_val for h in horizons}
            
        diff = [series[i] - series[i-1] for i in range(1, len(series))]
        mean_diff = sum(diff) / len(diff)
        
        last_val = series[-1]
        forecasts = {}
        
        for h in horizons:
            ar_part = sum(self.phi[i] * diff[-1-i] for i in range(min(self.p, len(diff))))
            ma_part = self.theta[0] * (diff[-1] - mean_diff) if diff else 0.0
            
            pred_diff = mean_diff + ar_part + ma_part
            decay = math.exp(-0.01 * h)
            pred = last_val + (pred_diff * decay)
            forecasts[h] = max(0.10, min(0.98, pred))
            
        return forecasts

class ProphetModel:
    """Decomposable Additive Model (Trend + Seasonality + Holiday/Event Adjustments)."""
    
    def fit_predict(self, series: List[Dict[str, Any]], horizons: List[int]) -> Dict[int, float]:
        """Decompose time-series into trend, day-of-week seasonality, and holiday impacts."""
        if not series:
            return {h: 0.50 for h in horizons}
            
        vals = [s["occupancy"] for s in series]
        recent_30 = vals[-30:] if len(vals) >= 30 else vals
        base_trend = sum(recent_30) / len(recent_30)
        
        dow_totals = {i: [] for i in range(7)}
        for s in series[-90:]:
            dow = s.get("day_of_week", 0)
            dow_totals[dow].append(s["occupancy"])
            
        dow_effects = {}
        for dow, dow_vals in dow_totals.items():
            if dow_vals:
                dow_effects[dow] = (sum(dow_vals) / len(dow_vals)) - base_trend
            else:
                dow_effects[dow] = 0.0

        last_date = series[-1].get("date", datetime.now())
        if isinstance(last_date, str):
            last_date = datetime.strptime(last_date, "%Y-%m-%d")
            
        forecasts = {}
        for h in horizons:
            target_date = last_date + timedelta(days=h)
            target_dow = target_date.weekday()
            
            recent_growth = (vals[-1] - vals[-2]) if len(vals) >= 2 else 0.0
            dampened_trend = vals[-1] + (recent_growth * math.exp(-0.05 * h))
            
            seasonality = dow_effects.get(target_dow, 0.0)
            holiday_mult = 1.12 if target_dow in [4, 5] else 1.0
            
            pred = (dampened_trend + seasonality * 0.5) * holiday_mult
            forecasts[h] = max(0.10, min(0.98, pred))
            
        return forecasts

class LSTMModel:
    """Recurrent Neural Network with memory gates for non-linear temporal dynamics."""
    
    def fit_predict(self, series: List[float], horizons: List[int]) -> Dict[int, float]:
        """Sequence forward pass through Gated Recurrent Unit abstraction."""
        if len(series) < 14:
            last_val = series[-1] if series else 0.5
            return {h: last_val for h in horizons}
            
        h_state = 0.0
        c_state = 0.0
        
        for val in series[-30:]:
            f_gate = 1.0 / (1.0 + math.exp(-(val * 0.5 + h_state * 0.3)))
            i_gate = 1.0 / (1.0 + math.exp(-(val * 0.8 - h_state * 0.2)))
            c_state = f_gate * c_state + i_gate * math.tanh(val)
            o_gate = 1.0 / (1.0 + math.exp(-(val * 0.6 + c_state * 0.4)))
            h_state = o_gate * math.tanh(c_state)
            
        forecasts = {}
        curr_h = h_state
        curr_c = c_state
        last_val = series[-1]
        
        for h in horizons:
            f_gate = 1.0 / (1.0 + math.exp(-(last_val * 0.4 + curr_h * 0.2)))
            i_gate = 1.0 / (1.0 + math.exp(-(last_val * 0.7 - curr_h * 0.1)))
            curr_c = f_gate * curr_c + i_gate * math.tanh(last_val)
            o_gate = 1.0 / (1.0 + math.exp(-(last_val * 0.5 + curr_c * 0.3)))
            curr_h = o_gate * math.tanh(curr_c)
            
            pred = last_val + (curr_h * 0.2)
            forecasts[h] = max(0.10, min(0.98, pred))
            
        return forecasts

class XGBoostModel:
    """Gradient Boosted Decision Tree ensemble for feature interactions."""
    
    def fit_predict(self, features: Dict[str, float], horizons: List[int]) -> Dict[int, float]:
        """Evaluate tree split rules on engineered feature vector."""
        lag_1 = features.get("lag_1", 0.5)
        delta_1d = features.get("delta_1d", 0.0)
        roll_7 = features.get("roll_mean_7", 0.5)
        roll_30 = features.get("roll_mean_30", 0.5)
        is_weekend = features.get("is_weekend", 0.0)
        is_holiday = features.get("is_holiday", 0.0)
        comp_price = features.get("comp_price", 100.0)
        
        base_pred = lag_1 + (0.4 * delta_1d) + 0.1 * (roll_7 - roll_30)
        
        forecasts = {}
        for h in horizons:
            residual = 0.0
            
            if is_weekend > 0.5 or is_holiday > 0.5:
                residual += 0.06
            else:
                residual -= 0.02
                
            if comp_price > 120.0:
                residual += 0.04
            elif comp_price < 80.0:
                residual -= 0.03
                
            horizon_dampener = math.exp(-0.005 * h)
            
            pred = (base_pred + residual) * horizon_dampener
            forecasts[h] = max(0.10, min(0.98, pred))
            
        return forecasts

class DemandForecastEnsemble:
    """Ensemble Orchestrator combining ARIMA, Prophet, LSTM, and XGBoost models."""
    
    def __init__(self):
        self.arima = ARIMAModel()
        self.prophet = ProphetModel()
        self.lstm = LSTMModel()
        self.xgb = XGBoostModel()
        
        self.weights = {
            "arima": 0.15,
            "prophet": 0.30,
            "lstm": 0.35,
            "xgb": 0.20
        }

    def forecast_ensemble(
        self,
        hotel_id: str,
        historical_data: List[Dict[str, Any]],
        horizons: List[int] = [1, 7, 30, 90],
        event_multiplier: float = 1.0,
        is_new_hotel: bool = False
    ) -> Dict[str, Any]:
        """Compute multi-horizon ensemble forecast with confidence intervals."""
        
        if is_new_hotel or len(historical_data) < 14:
            logger.info(f"Cold start triggered for Hotel {hotel_id}. Using market baseline ensemble.")
            return self._cold_start_forecast(hotel_id, horizons, event_multiplier)

        raw_series = [d["occupancy"] for d in historical_data]
        features = FeatureEngineer.extract_features(historical_data, len(historical_data))

        predictions = {
            "arima": self.arima.fit_predict(raw_series, horizons),
            "prophet": self.prophet.fit_predict(historical_data, horizons),
            "lstm": self.lstm.fit_predict(raw_series, horizons),
            "xgb": self.xgb.fit_predict(features, horizons)
        }

        ensemble_forecast = {}
        confidence_intervals = {}

        for h in horizons:
            ensemble_val = sum(
                predictions[m][h] * self.weights[m] for m in self.weights
            ) * event_multiplier
            
            ensemble_val = max(0.05, min(0.99, ensemble_val))
            ensemble_forecast[h] = round(ensemble_val, 4)

            model_preds = [predictions[m][h] for m in self.weights]
            mean_pred = sum(model_preds) / len(model_preds)
            variance = sum((p - mean_pred) ** 2 for p in model_preds) / len(model_preds)
            std_dev = math.sqrt(variance)
            
            horizon_uncertainty = 1.96 * (std_dev + 0.01 * math.sqrt(h))
            
            confidence_intervals[h] = {
                "lower_95": round(max(0.0, ensemble_val - horizon_uncertainty), 4),
                "upper_95": round(min(1.0, ensemble_val + horizon_uncertainty), 4)
            }

        return {
            "hotel_id": hotel_id,
            "timestamp": datetime.now().isoformat(),
            "horizons": horizons,
            "ensemble_forecast": ensemble_forecast,
            "individual_predictions": predictions,
            "confidence_intervals": confidence_intervals,
            "weights": self.weights,
            "event_multiplier": event_multiplier
        }

    def _cold_start_forecast(self, hotel_id: str, horizons: List[int], event_multiplier: float) -> Dict[str, Any]:
        """Market benchmark fallback for newly onboarded hotels."""
        market_baseline = {1: 0.65, 7: 0.70, 30: 0.60, 90: 0.55}
        forecast = {}
        ci = {}
        
        for h in horizons:
            val = market_baseline.get(h, 0.60) * event_multiplier
            val = max(0.05, min(0.99, val))
            forecast[h] = round(val, 4)
            ci[h] = {
                "lower_95": round(max(0.0, val - 0.15), 4),
                "upper_95": round(min(1.0, val + 0.15), 4)
            }
            
        return {
            "hotel_id": hotel_id,
            "cold_start": True,
            "ensemble_forecast": forecast,
            "confidence_intervals": ci,
            "weights": self.weights
        }

    @staticmethod
    def calculate_accuracy_metrics(actuals: List[float], predictions: List[float]) -> Dict[str, float]:
        """Calculate MAPE, RMSE, MAE, and Directional Accuracy."""
        if not actuals or len(actuals) != len(predictions):
            raise ValueError("Actuals and predictions must be non-empty equal-length lists.")
            
        n = len(actuals)
        mape_sum = sum(abs(act - pred) / max(0.01, act) for act, pred in zip(actuals, predictions))
        rmse_sum = sum((act - pred) ** 2 for act, pred in zip(actuals, predictions))
        mae_sum = sum(abs(act - pred) for act, pred in zip(actuals, predictions))
        
        correct_direction = 0
        total_eval = 0
        for i in range(1, n):
            act_diff = actuals[i] - actuals[i-1]
            pred_diff = predictions[i] - predictions[i-1]
            
            if abs(act_diff) > 0.002:
                total_eval += 1
                if (act_diff >= 0 and pred_diff >= 0) or (act_diff <= 0 and pred_diff <= 0):
                    correct_direction += 1
                
        dir_acc = (correct_direction / max(1, total_eval)) * 100.0
        
        return {
            "mape": round((mape_sum / n) * 100.0, 2),
            "rmse": round(math.sqrt(rmse_sum / n), 4),
            "mae": round(mae_sum / n, 4),
            "directional_accuracy": round(dir_acc, 2)
        }
