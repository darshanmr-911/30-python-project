"""
House Price Prediction using Machine Learning
Pipeline: Collect data -> Preprocess -> Feature engineering -> Train -> Evaluate -> Tune -> Deploy
"""

import json
import joblib
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
PROJECT_DIR = Path(__file__).parent
DATA_DIR = PROJECT_DIR / "data"
MODEL_DIR = PROJECT_DIR / "models"
DATA_FILE = DATA_DIR / "california_housing.csv"
MODEL_FILE = MODEL_DIR / "house_price_model.joblib"
METADATA_FILE = MODEL_DIR / "model_metadata.json"

RANDOM_STATE = 42
TEST_SIZE = 0.2

FEATURE_COLUMNS = [
    "MedInc",
    "HouseAge",
    "AveRooms",
    "AveBedrms",
    "Population",
    "AveOccup",
    "Latitude",
    "Longitude",
    "RoomsPerPerson",
    "BedroomsPerRoom",
    "PopulationPerHousehold",
    "IncomePerRoom",
    "LocationScore",
]


# ---------------------------------------------------------------------------
# Step 1: Collect Data
# ---------------------------------------------------------------------------
def collect_data() -> pd.DataFrame:
    """Load California Housing dataset and save locally."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if DATA_FILE.exists():
        print(f"Loading saved dataset from: {DATA_FILE}")
        df = pd.read_csv(DATA_FILE)
    else:
        print("Downloading California Housing dataset...")
        sklearn_data_dir = DATA_DIR / "sklearn_cache"
        sklearn_data_dir.mkdir(parents=True, exist_ok=True)
        housing = fetch_california_housing(as_frame=True, data_home=str(sklearn_data_dir))
        df = housing.frame.copy()
        df.to_csv(DATA_FILE, index=False)
        print(f"Dataset saved to: {DATA_FILE}")

    print(f"\nDataset shape: {df.shape[0]} rows, {df.shape[1]} columns")
    print(f"Target (MedHouseVal): median house value in $100,000s")
    print("\nFirst 5 rows:")
    print(df.head().to_string(index=False))
    print("\nDataset summary:")
    print(df.describe().round(2).to_string())

    return df


# ---------------------------------------------------------------------------
# Step 2: Preprocess
# ---------------------------------------------------------------------------
def preprocess_data(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Clean data, handle outliers, and separate features from target."""
    print("\nPreprocessing data...")

    df = df.copy()
    df.dropna(inplace=True)
    df.drop_duplicates(inplace=True)

    # Remove extreme outliers (top/bottom 1% of target)
    lower = df["MedHouseVal"].quantile(0.01)
    upper = df["MedHouseVal"].quantile(0.99)
    before = len(df)
    df = df[(df["MedHouseVal"] >= lower) & (df["MedHouseVal"] <= upper)]
    print(f"Removed {before - len(df)} outlier rows (1st–99th percentile on target)")

    # Cap unrealistic occupancy values
    df = df[df["AveOccup"] < 20]

    x = df.drop(columns=["MedHouseVal"])
    y = df["MedHouseVal"]

    print(f"Final dataset: {len(df)} samples")
    return x, y


# ---------------------------------------------------------------------------
# Step 3: Feature Engineering
# ---------------------------------------------------------------------------
def engineer_features(x: pd.DataFrame) -> pd.DataFrame:
    """Create new features from existing columns."""
    print("\nEngineering features...")

    x = x.copy()

    x["RoomsPerPerson"] = x["AveRooms"] / x["AveOccup"].replace(0, np.nan)
    x["BedroomsPerRoom"] = x["AveBedrms"] / x["AveRooms"].replace(0, np.nan)
    x["PopulationPerHousehold"] = x["Population"] / x["AveOccup"].replace(0, np.nan)
    x["IncomePerRoom"] = x["MedInc"] / x["AveRooms"].replace(0, np.nan)
    x["LocationScore"] = x["Latitude"] * x["Longitude"]

    x.replace([np.inf, -np.inf], np.nan, inplace=True)
    x.fillna(x.median(), inplace=True)

    engineered = x[FEATURE_COLUMNS]
    print(f"Features used ({len(FEATURE_COLUMNS)}): {', '.join(FEATURE_COLUMNS)}")
    return engineered


# ---------------------------------------------------------------------------
# Step 4: Train Models
# ---------------------------------------------------------------------------
def get_models() -> dict:
    """Return regression models to compare."""
    return {
        "Linear Regression": LinearRegression(),
        "Ridge": Ridge(random_state=RANDOM_STATE),
        "Lasso": Lasso(random_state=RANDOM_STATE, max_iter=5000),
        "Random Forest": RandomForestRegressor(
            n_estimators=100, random_state=RANDOM_STATE, n_jobs=-1
        ),
        "Gradient Boosting": GradientBoostingRegressor(random_state=RANDOM_STATE),
    }


def evaluate_model(y_true, y_pred) -> dict:
    """Calculate regression metrics."""
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    return {"RMSE": rmse, "MAE": mae, "R2": r2}


def train_and_evaluate(x_train, x_test, y_train, y_test) -> tuple:
    """Train all models and return the best one."""
    models = get_models()
    results = []
    best_model = None
    best_name = ""
    best_rmse = float("inf")

    print("\n" + "=" * 60)
    print("TRAINING & EVALUATION")
    print("=" * 60)

    for name, model in models.items():
        print(f"\n--- {name} ---")

        pipeline = Pipeline([
            ("scaler", StandardScaler()),
            ("model", model),
        ])

        pipeline.fit(x_train, y_train)
        y_pred = pipeline.predict(x_test)

        metrics = evaluate_model(y_test, y_pred)
        cv_scores = cross_val_score(
            pipeline, x_train, y_train, cv=5, scoring="neg_root_mean_squared_error"
        )
        cv_rmse = -cv_scores.mean()

        results.append({
            "Model": name,
            "RMSE": round(metrics["RMSE"], 4),
            "MAE": round(metrics["MAE"], 4),
            "R2": round(metrics["R2"], 4),
            "CV RMSE": round(cv_rmse, 4),
        })

        print(f"RMSE:      ${metrics['RMSE'] * 100_000:,.0f}  ({metrics['RMSE']:.4f} in $100k units)")
        print(f"MAE:       ${metrics['MAE'] * 100_000:,.0f}")
        print(f"R² Score:  {metrics['R2']:.4f}")
        print(f"5-Fold CV RMSE: ${cv_rmse * 100_000:,.0f}")

        if metrics["RMSE"] < best_rmse:
            best_rmse = metrics["RMSE"]
            best_model = pipeline
            best_name = name

    results_df = pd.DataFrame(results)
    print("\n" + "=" * 60)
    print("MODEL COMPARISON")
    print("=" * 60)
    print(results_df.to_string(index=False))
    print(f"\nBest model: {best_name} (RMSE = ${best_rmse * 100_000:,.0f})")

    return best_model, best_name, results_df


# ---------------------------------------------------------------------------
# Step 5: Hyperparameter Tuning
# ---------------------------------------------------------------------------
def tune_model(x_train, y_train, model_name: str) -> Pipeline:
    """Tune hyperparameters for the best model type using GridSearchCV."""
    print("\n" + "=" * 60)
    print(f"HYPERPARAMETER TUNING ({model_name})")
    print("=" * 60)

    param_grids = {
        "Random Forest": {
            "model": RandomForestRegressor(random_state=RANDOM_STATE, n_jobs=-1),
            "params": {
                "model__n_estimators": [100, 200],
                "model__max_depth": [None, 10, 20],
                "model__min_samples_split": [2, 5],
            },
        },
        "Gradient Boosting": {
            "model": GradientBoostingRegressor(random_state=RANDOM_STATE),
            "params": {
                "model__n_estimators": [100, 200],
                "model__learning_rate": [0.05, 0.1],
                "model__max_depth": [3, 5],
            },
        },
        "Ridge": {
            "model": Ridge(random_state=RANDOM_STATE),
            "params": {"model__alpha": [0.1, 1.0, 10.0, 100.0]},
        },
        "Lasso": {
            "model": Lasso(random_state=RANDOM_STATE, max_iter=5000),
            "params": {"model__alpha": [0.001, 0.01, 0.1, 1.0]},
        },
    }

    if model_name not in param_grids:
        print(f"No tuning grid for {model_name}. Using default parameters.")
        pipeline = Pipeline([
            ("scaler", StandardScaler()),
            ("model", get_models()[model_name]),
        ])
        pipeline.fit(x_train, y_train)
        return pipeline

    config = param_grids[model_name]
    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("model", config["model"]),
    ])

    grid = GridSearchCV(
        pipeline,
        config["params"],
        cv=5,
        scoring="neg_root_mean_squared_error",
        n_jobs=-1,
    )
    grid.fit(x_train, y_train)

    print(f"Best parameters: {grid.best_params_}")
    print(f"Best CV RMSE: ${-grid.best_score_ * 100_000:,.0f}")

    return grid.best_estimator_


# ---------------------------------------------------------------------------
# Step 6: Deploy (Save & Predict)
# ---------------------------------------------------------------------------
def deploy_model(model: Pipeline, model_name: str, metrics: dict) -> None:
    """Save trained model and metadata for production use."""
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    joblib.dump(model, MODEL_FILE)

    metadata = {
        "model_name": model_name,
        "features": FEATURE_COLUMNS,
        "target": "MedHouseVal",
        "target_unit": "USD (stored as value * 100,000)",
        "metrics": metrics,
    }
    METADATA_FILE.write_text(json.dumps(metadata, indent=2))

    print("\n" + "=" * 60)
    print("MODEL DEPLOYED")
    print("=" * 60)
    print(f"Model saved:    {MODEL_FILE}")
    print(f"Metadata saved: {METADATA_FILE}")


def load_deployed_model() -> tuple[Pipeline, dict]:
    """Load saved model and metadata."""
    if not MODEL_FILE.exists():
        raise FileNotFoundError("No deployed model found. Run training first.")

    model = joblib.load(MODEL_FILE)
    metadata = json.loads(METADATA_FILE.read_text())
    return model, metadata


def predict_price(features: dict, model: Pipeline | None = None) -> float:
    """Predict house price from feature dictionary. Returns price in USD."""
    if model is None:
        model, _ = load_deployed_model()

    row = pd.DataFrame([features])
    row = engineer_features(row)
    row = row[FEATURE_COLUMNS]

    prediction = model.predict(row)[0]
    return prediction * 100_000


def interactive_mode(model: Pipeline) -> None:
    """Interactive house price predictor."""
    print("\n" + "=" * 60)
    print("HOUSE PRICE PREDICTOR")
    print("Enter property details (or 'quit' to exit)")
    print("=" * 60)
    print("\nFeature guide:")
    print("  MedInc     = Median income in block (typical: 1–15)")
    print("  HouseAge   = Median house age in years (typical: 1–52)")
    print("  AveRooms   = Average rooms per household (typical: 3–10)")
    print("  AveBedrms  = Average bedrooms per household (typical: 0.5–2)")
    print("  Population = Block population (typical: 100–5000)")
    print("  AveOccup   = Average occupants per household (typical: 2–6)")
    print("  Latitude   = Block latitude (CA: 32–42)")
    print("  Longitude  = Block longitude (CA: -124 to -114)")

    prompts = [
        ("MedInc", "Median income"),
        ("HouseAge", "House age (years)"),
        ("AveRooms", "Average rooms"),
        ("AveBedrms", "Average bedrooms"),
        ("Population", "Population"),
        ("AveOccup", "Average occupants"),
        ("Latitude", "Latitude"),
        ("Longitude", "Longitude"),
    ]

    while True:
        print("\n" + "-" * 40)
        choice = input("Predict a house price? (y/quit): ").strip().lower()
        if choice in {"quit", "exit", "q", "n"}:
            print("Goodbye!")
            break
        if choice != "y":
            continue

        features = {}
        try:
            for key, label in prompts:
                value = float(input(f"  {label}: "))
                features[key] = value
        except ValueError:
            print("Invalid input. Please enter numbers only.")
            continue

        price = predict_price(features, model)
        print(f"\n  Predicted Price: ${price:,.0f}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    print("=" * 60)
    print("HOUSE PRICE PREDICTION - Machine Learning")
    print("=" * 60)

    # Step 1: Collect data
    df = collect_data()

    # Step 2: Preprocess
    x_raw, y = preprocess_data(df)

    # Step 3: Feature engineering
    x = engineer_features(x_raw)

    # Split data
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=TEST_SIZE, random_state=RANDOM_STATE
    )
    print(f"\nTrain set: {len(x_train)} samples | Test set: {len(x_test)} samples")

    # Step 4: Train and evaluate
    best_model, best_name, _ = train_and_evaluate(x_train, x_test, y_train, y_test)

    # Step 5: Tune best model
    tuned_model = tune_model(x_train, y_train, best_name)

    y_pred = tuned_model.predict(x_test)
    final_metrics = evaluate_model(y_test, y_pred)

    print("\n" + "=" * 60)
    print("FINAL TUNED MODEL PERFORMANCE")
    print("=" * 60)
    print(f"RMSE:     ${final_metrics['RMSE'] * 100_000:,.0f}")
    print(f"MAE:      ${final_metrics['MAE'] * 100_000:,.0f}")
    print(f"R² Score: {final_metrics['R2']:.4f}")

    # Sample predictions
    print("\n" + "=" * 60)
    print("SAMPLE PREDICTIONS")
    print("=" * 60)

    samples = x_test.head(5)
    actual = y_test.head(5).values

    for i, (_, row) in enumerate(samples.iterrows()):
        pred = tuned_model.predict([row])[0] * 100_000
        real = actual[i] * 100_000
        error = abs(pred - real)
        print(f"\n  Actual:    ${real:,.0f}")
        print(f"  Predicted: ${pred:,.0f}")
        print(f"  Error:     ${error:,.0f}")

    # Step 6: Deploy
    deploy_model(
        tuned_model,
        best_name,
        {k: round(v, 4) for k, v in final_metrics.items()},
    )

    choice = input("\nTry interactive price prediction? (y/n): ").strip().lower()
    if choice == "y":
        interactive_mode(tuned_model)


if __name__ == "__main__":
    main()
