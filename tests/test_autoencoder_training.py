import numpy as np
import pytest

from vantawave.ml.deep.autoencoder import (
    AutoencoderConfig,
    build_autoencoder,
    torch_available,
)
from vantawave.ml.deep.scoring import reconstruction_errors
from vantawave.ml.deep.training import TrainingConfig, train_autoencoder


@pytest.mark.skipif(not torch_available(), reason="PyTorch optional dependency not installed")
def test_autoencoder_trains_and_scores():
    rng = np.random.default_rng(42)
    train = rng.normal(0, 0.1, size=(80, 6)).astype("float32")
    validation = rng.normal(0, 0.1, size=(20, 6)).astype("float32")

    model = build_autoencoder(
        6,
        AutoencoderConfig(latent_dim=2, hidden_dim=8, dropout=0.0),
    )
    model, history, device = train_autoencoder(
        model,
        train,
        validation,
        config=TrainingConfig(
            epochs=8,
            batch_size=16,
            learning_rate=1e-2,
            patience=4,
        ),
        device="cpu",
    )

    errors = reconstruction_errors(model, validation, device=device)

    assert len(errors) == 20
    assert history.best_epoch >= 1
    assert np.isfinite(errors).all()
