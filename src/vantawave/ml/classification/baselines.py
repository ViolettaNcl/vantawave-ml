from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

def build_baseline_models(random_state: int = 42):
    return {
        "logistic_regression": Pipeline([
            ("scale", StandardScaler()),
            ("model", LogisticRegression(
                max_iter=2000,
                class_weight="balanced",
                random_state=random_state,
            )),
        ]),
        "random_forest": RandomForestClassifier(
            n_estimators=250,
            class_weight="balanced",
            random_state=random_state,
            n_jobs=-1,
        ),
        "hist_gradient_boosting": HistGradientBoostingClassifier(
            learning_rate=0.08,
            max_iter=200,
            random_state=random_state,
        ),
    }

def build_optional_catboost(random_state: int = 42):
    try:
        from catboost import CatBoostClassifier
    except ImportError as exc:
        raise RuntimeError(
            'CatBoost is optional. Install it with: pip install -e ".[boosting]"'
        ) from exc

    return CatBoostClassifier(
        iterations=250,
        depth=6,
        learning_rate=0.08,
        verbose=False,
        random_seed=random_state,
        auto_class_weights="Balanced",
    )
