import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import os
import random

class WasteHotspotPredictor:
    def __init__(self, data_path='dataset/waste_data.csv'):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.is_trained = False
        self.data_path = data_path
        self.train_model()

    def train_model(self):
        if not os.path.exists(self.data_path):
            print(f"Dataset not found at {self.data_path}")
            return
            
        df = pd.read_csv(self.data_path)
        X = df[['area_population', 'past_waste_reports']]
        y = df['waste_level']
        
        self.model.fit(X, y)
        self.is_trained = True

    def predict(self, population, past_reports):
        if not self.is_trained:
            return 0 # Default to low if not trained
            
        prediction = self.model.predict([[population, past_reports]])[0]
        return int(prediction)
        
    def predict_for_location(self, lat, lng):
        """
        Since we don't have real population data per coordinates for the demo,
        we use a deterministic pseudo-random approach based on coordinates
        to generate features for the ML model.
        """
        random.seed(hash((round(lat, 4), round(lng, 4))))
        population = random.randint(500, 4000)
        past_reports = random.randint(0, 25)
        
        level = self.predict(population, past_reports)
        
        # Map to string labels
        # 0: Low waste zone, 1: Medium waste zone, 2: High waste zone
        labels = {0: "Low", 1: "Medium", 2: "High"}
        return labels.get(level, "Low")

# Singleton instance
predictor = WasteHotspotPredictor()
