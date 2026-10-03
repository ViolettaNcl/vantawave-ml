from __future__ import annotations

from dataclasses import asdict, dataclass
import copy
import random
import numpy as np

from vantawave.ml.deep.autoencoder import require_torch


@dataclass(frozen=True)
class TrainingConfig:
    epochs: int = 80
    batch_size: int = 64
    learning_rate: float = 1e-3
    weight_decay: float = 1e-5
    patience: int = 10
    seed: int = 42


@dataclass
class TrainingHistory:
    train_loss: list[float]
    validation_loss: list[float]
    best_epoch: int
    best_validation_loss: float

    def to_dict(self):
        return asdict(self)


def _seed_everything(seed: int):
    torch, _ = require_torch()
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def train_autoencoder(
    model,
    X_train,
    X_validation,
    *,
    config: TrainingConfig | None = None,
    device: str | None = None,
):
    torch, nn = require_torch()
    config = config or TrainingConfig()
    _seed_everything(config.seed)

    X_train = np.asarray(X_train, dtype=np.float32)
    X_validation = np.asarray(X_validation, dtype=np.float32)

    if X_train.ndim != 2 or X_validation.ndim != 2:
        raise ValueError("Autoencoder input must be 2D.")
    if X_train.shape[1] != X_validation.shape[1]:
        raise ValueError("Train/validation feature dimensions must match.")

    device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)

    train_tensor = torch.tensor(X_train, dtype=torch.float32)
    val_tensor = torch.tensor(X_validation, dtype=torch.float32, device=device)

    dataset = torch.utils.data.TensorDataset(train_tensor)
    generator = torch.Generator().manual_seed(config.seed)
    loader = torch.utils.data.DataLoader(
        dataset,
        batch_size=min(config.batch_size, len(dataset)),
        shuffle=True,
        generator=generator,
    )

    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=config.learning_rate,
        weight_decay=config.weight_decay,
    )

    best_state = copy.deepcopy(model.state_dict())
    best_loss = float("inf")
    best_epoch = 0
    patience_left = config.patience
    train_losses = []
    validation_losses = []

    for epoch in range(1, config.epochs + 1):
        model.train()
        running = 0.0
        seen = 0

        for (batch,) in loader:
            batch = batch.to(device)
            optimizer.zero_grad()
            reconstructed = model(batch)
            loss = criterion(reconstructed, batch)
            loss.backward()
            optimizer.step()

            running += float(loss.item()) * len(batch)
            seen += len(batch)

        train_loss = running / max(seen, 1)

        model.eval()
        with torch.no_grad():
            val_reconstructed = model(val_tensor)
            val_loss = float(criterion(val_reconstructed, val_tensor).item())

        train_losses.append(train_loss)
        validation_losses.append(val_loss)

        if val_loss < best_loss - 1e-8:
            best_loss = val_loss
            best_epoch = epoch
            best_state = copy.deepcopy(model.state_dict())
            patience_left = config.patience
        else:
            patience_left -= 1

        if patience_left <= 0:
            break

    model.load_state_dict(best_state)
    model.eval()

    return model, TrainingHistory(
        train_loss=train_losses,
        validation_loss=validation_losses,
        best_epoch=best_epoch,
        best_validation_loss=best_loss,
    ), device
