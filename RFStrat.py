from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import numpy as np
from FeatureExtract import Features
from Config import Configs


class RandomForestStrat:
    def __init__(self):
        self.name = "Random_forest_classifier"
        self.model = RandomForestClassifier(
            e_estimators = 50,
            max_depth=8,
            random_state= 42
        )
        self.features = Features()
        self.is_trained = False


    def Train(self,df):
        df = self.features
        data  = df[self.features.fet_Ext+['target']].dropna()
        if len(data) < Configs.MIN_DATA_POINTS:
            #More data points are required
            return False 
        X = data[self.features.fet_Ext]
        Y = data['target']

        self.model.fit(X,Y)

        y_pred = self.model.predict(X)
        accuracy = accuracy_score(Y,y_pred)

        print(f"Accuracy:{accuracy}")
        self.is_trained = True
        return True
    
    def predict(self, df):
        """Make prediction"""
        if not self.is_trained:
            return 'hold', 0.0
        
        # Create features for latest data
        df = self.features.create_features(df)
        latest_data = df[self.features.features].iloc[-1:].fillna(0)
        
        # Get prediction and confidence
        prediction = self.model.predict(latest_data)[0]
        probabilities = self.model.predict_proba(latest_data)[0]
        confidence = max(probabilities)
        
        # Convert to signal
        if confidence > Configs.CONFIDENCE_THRESHOLD:
            if prediction == 1:
                return 'buy', confidence
            elif prediction == -1:
                return 'sell', confidence
        
        return 'hold', confidence