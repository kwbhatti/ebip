from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

def scale_features(df):

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df)

    return X_scaled

def train_model(X_scaled):

    model = IsolationForest(
        n_estimators=100,
        contamination=0.01,
        random_state=42
    )

    model.fit(X_scaled)

    return model


def score_executions(df, X_scaled):

    model = train_model(X_scaled)

    df["anomaly"] = model.predict(X_scaled)
    df["anomaly_score"] = model.decision_function(X_scaled)

    return df