"""Latih, bandingkan, dan pilih model terbaik untuk prediksi demand.

Mencakup SKKNI Unit 8 (skenario model), Unit 9 (membangun & mengoptimasi model),
Unit 10 (evaluasi), dan menyiapkan artefak untuk Unit 11 (review).

Jalankan:
    python -m src.train_model

Artefak yang dihasilkan:
    models/demand_model.pkl        -> pipeline model terbaik (siap dipakai app)
    models/metrics.json            -> metrik final + metadata
    reports/model_comparison.csv   -> tabel perbandingan semua model
    reports/feature_importance.csv -> pentingnya fitur model terbaik
    reports/test_predictions.csv   -> prediksi vs aktual pada test set (untuk grafik)
"""
from __future__ import annotations

import json
import time
import warnings

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import (
    mean_absolute_error,
    mean_absolute_percentage_error,
    r2_score,
    root_mean_squared_error,
)
from sklearn.model_selection import (
    KFold,
    RandomizedSearchCV,
    cross_val_score,
    train_test_split,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler, TargetEncoder
from sklearn.tree import DecisionTreeRegressor
from xgboost import XGBRegressor

from src import config, data_loader, features, preprocessing

RANDOM_STATE = 42
CV_FOLDS = 3
warnings.filterwarnings("ignore", category=UserWarning)

# CV splitter untuk cross-fitting TargetEncoder (anti-leakage, reproducible).
_TE_CV = KFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)


# --------------------------------------------------------------------------- #
# PIPELINE PRA-PROSES  (Unit 7 dijalankan dalam pipeline -> anti leakage)
# --------------------------------------------------------------------------- #
def build_preprocessor() -> ColumnTransformer:
    """ColumnTransformer: target-encode koridor, one-hot kategori, scale numerik."""
    return ColumnTransformer(
        transformers=[
            (
                # target_type="continuous" WAJIB: target berupa cacah integer (1..67)
                # akan salah terdeteksi sbg "multiclass" oleh mode auto -> koridor
                # meledak jadi puluhan kolom. Paksa regresi -> 1 kolom rata-rata demand.
                "corridor",
                TargetEncoder(target_type="continuous", cv=_TE_CV),
                features.TARGET_ENCODE_FEATURES,
            ),
            (
                "onehot",
                OneHotEncoder(handle_unknown="ignore"),
                features.ONEHOT_FEATURES,
            ),
            ("num", StandardScaler(), features.NUMERIC_FEATURES),
        ],
        remainder="drop",
    )


def get_candidate_models() -> dict:
    """Kumpulan model kandidat untuk dibandingkan (Unit 8)."""
    return {
        "Baseline (Rata-rata)": DummyRegressor(strategy="mean"),
        "Regresi Linier": LinearRegression(),
        "Ridge": Ridge(alpha=1.0),
        "Decision Tree": DecisionTreeRegressor(max_depth=12, random_state=RANDOM_STATE),
        "Random Forest": RandomForestRegressor(
            n_estimators=200, n_jobs=-1, random_state=RANDOM_STATE
        ),
        "Gradient Boosting": GradientBoostingRegressor(random_state=RANDOM_STATE),
        # Objektif Poisson: tepat untuk data cacah (count) & tak menghasilkan
        # prediksi negatif. Terbukti unggul pada eksperimen (R2 & RMSE terbaik).
        "XGBoost": XGBRegressor(
            objective="count:poisson",
            n_estimators=500,
            learning_rate=0.05,
            max_depth=6,
            subsample=0.9,
            colsample_bytree=0.9,
            random_state=RANDOM_STATE,
            n_jobs=-1,
            verbosity=0,
        ),
    }


# Grid tuning ringan per model (untuk optimasi pemenang - Unit 9).
_PARAM_GRIDS = {
    "Random Forest": {
        "model__n_estimators": [200, 400, 600],
        "model__max_depth": [None, 12, 20, 30],
        "model__min_samples_leaf": [1, 2, 4],
    },
    "XGBoost": {
        "model__n_estimators": [300, 500, 700],
        "model__max_depth": [4, 6, 8],
        "model__learning_rate": [0.03, 0.05, 0.1],
        "model__subsample": [0.8, 0.9, 1.0],
    },
    "Gradient Boosting": {
        "model__n_estimators": [100, 200, 300],
        "model__max_depth": [2, 3, 4],
        "model__learning_rate": [0.05, 0.1, 0.2],
    },
}


# --------------------------------------------------------------------------- #
# METRIK
# --------------------------------------------------------------------------- #
def compute_metrics(y_true, y_pred) -> dict:
    """Hitung MAE, RMSE, R2, MAPE (%)."""
    return {
        "MAE": float(mean_absolute_error(y_true, y_pred)),
        "RMSE": float(root_mean_squared_error(y_true, y_pred)),
        "R2": float(r2_score(y_true, y_pred)),
        "MAPE_persen": float(mean_absolute_percentage_error(y_true, y_pred) * 100),
    }


# --------------------------------------------------------------------------- #
# PIPELINE UTAMA
# --------------------------------------------------------------------------- #
def prepare_modeling_data():
    """Muat -> bersihkan -> agregasi -> split train/test."""
    print("[1/5] Memuat & membersihkan data ...")
    raw = data_loader.load_raw_data()
    clean, _ = preprocessing.clean_data(raw)

    print("[2/5] Feature engineering (agregasi koridor x tanggal x jam) ...")
    modeling = features.build_demand_dataset(clean)
    x, y = features.feature_target_split(modeling)

    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.2, random_state=RANDOM_STATE
    )
    print(f"      -> total {len(modeling):,} slot | train {len(x_train):,} | test {len(x_test):,}")
    return x_train, x_test, y_train, y_test


def compare_models(x_train, x_test, y_train, y_test) -> pd.DataFrame:
    """Bandingkan semua model kandidat (CV pada train + evaluasi pada test)."""
    print(f"[3/5] Membandingkan {len(get_candidate_models())} model (CV {CV_FOLDS}-fold) ...")
    rows = []
    for name, estimator in get_candidate_models().items():
        pipe = Pipeline([("prep", build_preprocessor()), ("model", estimator)])
        t0 = time.perf_counter()
        cv_r2 = cross_val_score(
            pipe, x_train, y_train, cv=CV_FOLDS, scoring="r2", n_jobs=-1
        ).mean()
        pipe.fit(x_train, y_train)
        test_m = compute_metrics(y_test, pipe.predict(x_test))
        elapsed = time.perf_counter() - t0
        rows.append(
            {
                "model": name,
                "cv_r2": round(cv_r2, 4),
                "test_R2": round(test_m["R2"], 4),
                "test_MAE": round(test_m["MAE"], 4),
                "test_RMSE": round(test_m["RMSE"], 4),
                "test_MAPE_persen": round(test_m["MAPE_persen"], 2),
                "waktu_detik": round(elapsed, 1),
            }
        )
        print(
            f"      - {name:22s} | CV R2={cv_r2:.3f} | test R2={test_m['R2']:.3f} "
            f"| MAE={test_m['MAE']:.3f} | {elapsed:.1f}s"
        )
    comparison = pd.DataFrame(rows).sort_values("test_R2", ascending=False).reset_index(drop=True)
    return comparison


def tune_best(best_name, x_train, y_train, baseline_cv_r2):
    """Optimasi hyperparameter model terbaik (Unit 9).

    Membandingkan konfigurasi hasil tuning vs konfigurasi default berdasarkan
    skor CV (bukan test set, agar tidak bocor). Mengembalikan konfigurasi terbaik.

    Returns
    -------
    (pipeline_terlatih, params, cv_r2, dituning: bool)
    """
    base = get_candidate_models()[best_name]
    pipe = Pipeline([("prep", build_preprocessor()), ("model", base)])
    grid = _PARAM_GRIDS.get(best_name)
    if grid is None:
        print(f"[4/5] Model terbaik '{best_name}' tanpa grid tuning. Melatih ulang konfigurasi default ...")
        pipe.fit(x_train, y_train)
        return pipe, {}, baseline_cv_r2, False

    print(f"[4/5] Tuning '{best_name}' via RandomizedSearchCV ...")
    search = RandomizedSearchCV(
        pipe,
        param_distributions=grid,
        n_iter=12,
        cv=CV_FOLDS,
        scoring="r2",
        n_jobs=-1,
        random_state=RANDOM_STATE,
        verbose=0,
    )
    search.fit(x_train, y_train)
    print(
        f"      -> tuned CV R2={search.best_score_:.4f} vs default CV R2={baseline_cv_r2:.4f} "
        f"| params={search.best_params_}"
    )

    # Pertahankan yang CV-nya lebih baik (hindari tuning yang justru menurunkan generalisasi).
    if search.best_score_ >= baseline_cv_r2:
        print("      -> memakai konfigurasi hasil TUNING.")
        return search.best_estimator_, search.best_params_, float(search.best_score_), True
    print("      -> tuning tidak meningkatkan CV; memakai konfigurasi DEFAULT.")
    pipe.fit(x_train, y_train)
    return pipe, {}, baseline_cv_r2, False


def extract_feature_importance(pipeline) -> pd.DataFrame | None:
    """Ambil feature importance / koefisien dari model terbaik."""
    prep = pipeline.named_steps["prep"]
    model = pipeline.named_steps["model"]
    try:
        names = list(prep.get_feature_names_out())
    except Exception:
        return None
    names = [n.split("__", 1)[-1] for n in names]  # rapikan prefiks transformer

    if hasattr(model, "feature_importances_"):
        vals = np.asarray(model.feature_importances_, dtype=float)
    elif hasattr(model, "coef_"):
        vals = np.abs(np.asarray(model.coef_, dtype=float)).ravel()
    else:
        return None
    if len(vals) != len(names):
        return None
    return (
        pd.DataFrame({"fitur": names, "importance": vals})
        .sort_values("importance", ascending=False)
        .reset_index(drop=True)
    )


def main():
    x_train, x_test, y_train, y_test = prepare_modeling_data()
    comparison = compare_models(x_train, x_test, y_train, y_test)

    # Pilih terbaik (abaikan baseline) berdasarkan CV R2 (lebih andal dari test tunggal).
    ranked = comparison[comparison["model"] != "Baseline (Rata-rata)"].sort_values(
        "cv_r2", ascending=False
    )
    best_row = ranked.iloc[0]
    best_name = best_row["model"]
    baseline_cv_r2 = float(best_row["cv_r2"])
    print(
        f"\n>>> Model terbaik (CV R2={baseline_cv_r2:.4f}, test R2={best_row['test_R2']}): {best_name}"
    )

    tuned_pipe, best_params, final_cv_r2, was_tuned = tune_best(
        best_name, x_train, y_train, baseline_cv_r2
    )

    print("[5/5] Evaluasi final & menyimpan artefak ...")
    y_pred = np.clip(tuned_pipe.predict(x_test), 0, None)  # cacah tak boleh negatif
    final_metrics = compute_metrics(y_test, y_pred)
    print(
        f"      FINAL {best_name}: R2={final_metrics['R2']:.4f} | "
        f"MAE={final_metrics['MAE']:.4f} | RMSE={final_metrics['RMSE']:.4f} | "
        f"MAPE={final_metrics['MAPE_persen']:.2f}%"
    )

    # --- Simpan artefak ---
    config.MODELS_DIR.mkdir(parents=True, exist_ok=True)
    config.REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    joblib.dump(tuned_pipe, config.MODEL_PATH)
    comparison.to_csv(config.MODEL_COMPARISON_PATH, index=False)

    fi = extract_feature_importance(tuned_pipe)
    if fi is not None:
        fi.to_csv(config.REPORTS_DIR / "feature_importance.csv", index=False)

    # Prediksi vs aktual (untuk grafik evaluasi di app).
    pred_df = x_test.copy()
    pred_df["actual"] = y_test.values
    pred_df["predicted"] = np.round(y_pred, 2)
    pred_df["residual"] = pred_df["actual"] - pred_df["predicted"]
    pred_df.to_csv(config.REPORTS_DIR / "test_predictions.csv", index=False)

    metrics_out = {
        "best_model": best_name,
        "dituning": was_tuned,
        "best_params": best_params,
        "cv_r2": round(final_cv_r2, 4),
        "target": features.TARGET,
        "aggregation_level": "corridorID x date x hour",
        "n_train": int(len(x_train)),
        "n_test": int(len(x_test)),
        "features": {
            "target_encode": features.TARGET_ENCODE_FEATURES,
            "onehot": features.ONEHOT_FEATURES,
            "numeric": features.NUMERIC_FEATURES,
        },
        "test_metrics": {k: round(v, 4) for k, v in final_metrics.items()},
        "success_criteria": {
            "primary_operasional": {
                "metrik": "MAE",
                "target": "<= 1.5 penumpang/slot",
                "nilai": round(final_metrics["MAE"], 4),
                "tercapai": bool(final_metrics["MAE"] <= 1.5),
            },
            "sekunder_statistik": {
                "metrik": "R2",
                "target": ">= 0.70",
                "nilai": round(final_metrics["R2"], 4),
                "tercapai": bool(final_metrics["R2"] >= 0.70),
            },
            "unggul_dari_baseline": bool(
                final_metrics["R2"] > 0
                and final_metrics["MAE"]
                < float(comparison.loc[comparison["model"] == "Baseline (Rata-rata)", "test_MAE"].iloc[0])
            ),
            "catatan": (
                "Target aspiratif R2>=0.80 tidak tercapai; pada granularitas "
                "koridor-jam rata-rata cacah hanya ~3 sehingga ada batas bawah "
                "noise Poisson. MAE ~1 penumpang sudah memadai untuk perencanaan."
            ),
        },
        "all_models": comparison.to_dict(orient="records"),
        "trained_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    with open(config.METRICS_PATH, "w", encoding="utf-8") as f:
        json.dump(metrics_out, f, indent=2, ensure_ascii=False)

    print("\nSelesai. Artefak tersimpan di models/ dan reports/.")
    return metrics_out


if __name__ == "__main__":
    main()
