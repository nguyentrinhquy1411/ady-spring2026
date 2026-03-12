"""
lstm_model.py
=============
Global LSTM for multi-region ZHVI log-return prediction.

Architecture: 2-layer LSTM, hidden=64, dropout=0.2, window=12
Training:  Adam, MSE loss, early stopping (patience=10)
Input:     sequences of [lag_1 … lag_12, city_enc] of length `seq_len`
           built by sliding over the COMBINED (all-region) training set
Output:    one-step-ahead log_return
"""

from __future__ import annotations

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset


# ---------------------------------------------------------------------------
# Model definition
# ---------------------------------------------------------------------------
class LSTMNet(nn.Module):
    def __init__(self, input_size: int = 6, hidden_size: int = 64,
                 num_layers: int = 2, dropout: float = 0.2):
        super().__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers,
                            batch_first=True,
                            dropout=dropout if num_layers > 1 else 0.0)
        self.fc = nn.Linear(hidden_size, 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (batch, seq_len, features)
        out, _ = self.lstm(x)
        return self.fc(out[:, -1, :]).squeeze(-1)


# ---------------------------------------------------------------------------
# Data preparation
# ---------------------------------------------------------------------------
def build_sequences(X: np.ndarray, y: np.ndarray, seq_len: int = 12):
    """Build (X_seq, y_seq) from flat arrays."""
    Xs, ys = [], []
    for i in range(seq_len, len(X)):
        Xs.append(X[i - seq_len: i])
        ys.append(y[i])
    return np.array(Xs, dtype=np.float32), np.array(ys, dtype=np.float32)


# ---------------------------------------------------------------------------
# Training
# ---------------------------------------------------------------------------
def train_lstm(
    X_train: np.ndarray,
    y_train: np.ndarray,
    seq_len: int = 12,
    hidden_size: int = 64,
    num_layers: int = 2,
    lr: float = 1e-3,
    epochs: int = 50,
    batch_size: int = 4096,
    patience: int = 8,
    device: str = "cpu",
) -> LSTMNet:
    """Train the global LSTM and return the fitted model."""

    print(f"  [LSTM] Building sequences (window={seq_len}) …")
    X_seq, y_seq = build_sequences(X_train, y_train, seq_len)
    print(f"  [LSTM] Sequences: {X_seq.shape}  |  targets: {y_seq.shape}")

    split = int(len(X_seq) * 0.9)
    Xtr, Xv = X_seq[:split], X_seq[split:]
    ytr, yv = y_seq[:split], y_seq[split:]

    tr_ds = TensorDataset(torch.from_numpy(Xtr), torch.from_numpy(ytr))
    tr_dl = DataLoader(tr_ds, batch_size=batch_size, shuffle=True)

    model = LSTMNet(input_size=X_train.shape[1], hidden_size=hidden_size,
                    num_layers=num_layers).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = nn.MSELoss()

    best_val, patience_cnt, best_state = float("inf"), 0, None
    for epoch in range(epochs):
        model.train()
        for xb, yb in tr_dl:
            xb, yb = xb.to(device), yb.to(device)
            optimizer.zero_grad()
            criterion(model(xb), yb).backward()
            optimizer.step()

        model.eval()
        with torch.no_grad():
            xv_t = torch.from_numpy(Xv).to(device)
            yv_t = torch.from_numpy(yv).to(device)
            val_loss = criterion(model(xv_t), yv_t).item()

        if val_loss < best_val:
            best_val, patience_cnt = val_loss, 0
            best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
        else:
            patience_cnt += 1
            if patience_cnt >= patience:
                print(f"  [LSTM] Early stop at epoch {epoch+1}  val_loss={best_val:.8f}")
                break

        if (epoch + 1) % 10 == 0:
            print(f"  [LSTM] Epoch {epoch+1:3d}  val_loss={val_loss:.8f}")

    model.load_state_dict(best_state)
    return model


# ---------------------------------------------------------------------------
# Inference
# ---------------------------------------------------------------------------
def predict_lstm(
    model: LSTMNet,
    X_train: np.ndarray,
    X_test: np.ndarray,
    y_train: np.ndarray,
    seq_len: int = 12,
    device: str = "cpu",
) -> np.ndarray:
    """
    Build test sequences using the tail of training + test rows,
    then run inference.
    """
    # Concat for seamless windowing across train/test boundary
    X_full = np.concatenate([X_train[-seq_len:], X_test], axis=0).astype(np.float32)
    y_full = np.concatenate([y_train[-seq_len:], np.zeros(len(X_test))]).astype(np.float32)

    X_seq, _ = build_sequences(X_full, y_full, seq_len)
    # X_seq length == len(X_test) exactly
    assert len(X_seq) == len(X_test), (
        f"Sequence mismatch: {len(X_seq)} vs {len(X_test)}"
    )

    model.eval()
    with torch.no_grad():
        x_t = torch.from_numpy(X_seq).to(device)
        preds = model(x_t).cpu().numpy()
    return preds
