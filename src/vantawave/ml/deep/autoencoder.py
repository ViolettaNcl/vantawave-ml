from __future__ import annotations

from dataclasses import dataclass


class TorchUnavailable(RuntimeError):
    pass


def require_torch():
    try:
        import torch
        from torch import nn
    except ImportError as exc:
        raise TorchUnavailable(
            'PyTorch is optional. Install it with: pip install -e ".[deep]"'
        ) from exc
    return torch, nn


def torch_available() -> bool:
    try:
        import torch  # noqa: F401
    except ImportError:
        return False
    return True


@dataclass(frozen=True)
class AutoencoderConfig:
    latent_dim: int = 8
    hidden_dim: int = 32
    dropout: float = 0.05
    seed: int = 42


def build_autoencoder(input_dim: int, config: AutoencoderConfig | None = None):
    torch, nn = require_torch()
    config = config or AutoencoderConfig()
    torch.manual_seed(config.seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(config.seed)

    latent_dim = max(2, min(config.latent_dim, max(2, input_dim // 2)))
    hidden_dim = max(latent_dim * 2, min(config.hidden_dim, max(8, input_dim * 2)))

    class Autoencoder(nn.Module):
        def __init__(self):
            super().__init__()
            self.encoder = nn.Sequential(
                nn.Linear(input_dim, hidden_dim),
                nn.ReLU(),
                nn.Dropout(config.dropout),
                nn.Linear(hidden_dim, latent_dim),
                nn.ReLU(),
            )
            self.decoder = nn.Sequential(
                nn.Linear(latent_dim, hidden_dim),
                nn.ReLU(),
                nn.Linear(hidden_dim, input_dim),
            )

        def forward(self, x):
            return self.decoder(self.encoder(x))

    return Autoencoder()
