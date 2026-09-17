"""SteadyVox Model Training Pipeline.

Supports training the 2D CNN Spectrogram Baseline and logging training curves.

RESEARCH SCREENING TOOL ONLY — NOT A MEDICAL DIAGNOSIS.
"""

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

# Ensure project root is in python path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import numpy as np
import torch
import torch.nn as nn
from sklearn.metrics import roc_auc_score, f1_score, accuracy_score

from ml.data.dataset import create_dataloaders
from ml.models.cnn_baseline import CNNBaseline
from ml.models.cnn_bilstm import CNNBiLSTM


def train_one_epoch(
    model: nn.Module,
    dataloader: torch.utils.data.DataLoader,
    criterion: nn.Module,
    optimizer: torch.optim.Optimizer,
    device: torch.device,
) -> Tuple[float, float]:
    model.train()
    total_loss = 0.0
    correct = 0
    total_samples = 0

    for batch_x, batch_y, _ in dataloader:
        batch_x = batch_x.to(device)
        batch_y = batch_y.to(device)

        optimizer.zero_grad()
        logits = model(batch_x)
        loss = criterion(logits, batch_y)
        loss.backward()
        
        # Gradient clipping
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()

        total_loss += loss.item() * len(batch_y)
        probs = torch.sigmoid(logits)
        preds = (probs >= 0.50).float()
        correct += (preds == batch_y).sum().item()
        total_samples += len(batch_y)

    epoch_loss = total_loss / max(1, total_samples)
    epoch_acc = correct / max(1, total_samples)
    return epoch_loss, epoch_acc


@torch.no_grad()
def evaluate(
    model: nn.Module,
    dataloader: torch.utils.data.DataLoader,
    criterion: nn.Module,
    device: torch.device,
) -> Dict[str, float]:
    model.eval()
    total_loss = 0.0
    all_targets = []
    all_probs = []

    for batch_x, batch_y, _ in dataloader:
        batch_x = batch_x.to(device)
        batch_y = batch_y.to(device)

        logits = model(batch_x)
        loss = criterion(logits, batch_y)

        total_loss += loss.item() * len(batch_y)
        probs = torch.sigmoid(logits).cpu().numpy().flatten()
        targets = batch_y.cpu().numpy().flatten()

        all_probs.extend(probs)
        all_targets.extend(targets)

    all_targets = np.array(all_targets)
    all_probs = np.array(all_probs)
    all_preds = (all_probs >= 0.50).astype(int)

    val_loss = total_loss / max(1, len(all_targets))
    acc = float(accuracy_score(all_targets, all_preds))
    f1 = float(f1_score(all_targets, all_preds, zero_division=0))
    
    try:
        auc = float(roc_auc_score(all_targets, all_probs))
    except ValueError:
        auc = 0.5

    return {
        "loss": float(val_loss),
        "accuracy": acc,
        "f1": f1,
        "roc_auc": auc,
    }


def train_model(
    data_dir: str = "ml/data/processed",
    output_dir: str = "ml/saved_models",
    model_type: str = "cnn_baseline",
    epochs: int = 25,
    batch_size: int = 16,
    lr: float = 1e-3,
    weight_decay: float = 1e-4,
    patience: int = 8,
    seed: int = 42,
) -> Path:
    torch.manual_seed(seed)
    np.random.seed(seed)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Training on device: {device}")

    # Create DataLoaders
    train_loader, val_loader, test_loader, pos_weight = create_dataloaders(
        data_dir=data_dir,
        batch_size=batch_size,
    )
    print(f"Dataset splits -> Train: {len(train_loader.dataset)}, Val: {len(val_loader.dataset)}, Test: {len(test_loader.dataset)}")
    print(f"Positive class weight: {pos_weight.item():.3f}")

    # Model architecture selection
    if model_type == "cnn_baseline":
        model = CNNBaseline().to(device)
    elif model_type == "cnn_bilstm":
        model = CNNBiLSTM().to(device)
    else:
        raise ValueError(f"Unknown model_type: {model_type}")

    criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight.to(device))
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)

    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    best_model_path = out_path / f"{model_type}_best.pt"

    best_val_auc = -1.0
    best_val_loss = float("inf")
    patience_counter = 0
    history = {
        "train_loss": [],
        "train_acc": [],
        "val_loss": [],
        "val_acc": [],
        "val_f1": [],
        "val_auc": [],
    }

    start_time = time.time()
    for epoch in range(1, epochs + 1):
        tr_loss, tr_acc = train_one_epoch(model, train_loader, criterion, optimizer, device)
        val_metrics = evaluate(model, val_loader, criterion, device)
        scheduler.step()

        history["train_loss"].append(tr_loss)
        history["train_acc"].append(tr_acc)
        history["val_loss"].append(val_metrics["loss"])
        history["val_acc"].append(val_metrics["accuracy"])
        history["val_f1"].append(val_metrics["f1"])
        history["val_auc"].append(val_metrics["roc_auc"])

        print(
            f"Epoch {epoch:02d}/{epochs:02d} | "
            f"Train Loss: {tr_loss:.4f} Acc: {tr_acc:.3f} | "
            f"Val Loss: {val_metrics['loss']:.4f} Acc: {val_metrics['accuracy']:.3f} "
            f"F1: {val_metrics['f1']:.3f} AUC: {val_metrics['roc_auc']:.3f}"
        )

        # Checkpoint based on Validation ROC-AUC (or loss fallback)
        if val_metrics["roc_auc"] > best_val_auc or (val_metrics["roc_auc"] == best_val_auc and val_metrics["loss"] < best_val_loss):
            best_val_auc = val_metrics["roc_auc"]
            best_val_loss = val_metrics["loss"]
            patience_counter = 0

            torch.save({
                "model_state_dict": model.state_dict(),
                "model_type": model_type,
                "epoch": epoch,
                "val_metrics": val_metrics,
                "pos_weight": pos_weight.item(),
                "disclaimer": "Research screening tool only — not a medical diagnosis.",
            }, best_model_path)
            print(f"  -> Saved new best model checkpoint (Val AUC: {best_val_auc:.4f}) to {best_model_path}")
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print(f"Early stopping triggered at epoch {epoch}")
                break

    duration = time.time() - start_time
    print(f"Training completed in {duration:.1f}s. Best Validation ROC-AUC: {best_val_auc:.4f}")

    # Save training history
    history_path = out_path / f"{model_type}_history.json"
    with open(history_path, "w") as f:
        json.dump(history, f, indent=2)

    return best_model_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train SteadyVox Model")
    parser.add_argument("--data_dir", type=str, default="ml/data/processed")
    parser.add_argument("--output_dir", type=str, default="ml/saved_models")
    parser.add_argument("--model_type", type=str, default="cnn_baseline")
    parser.add_argument("--epochs", type=int, default=25)
    parser.add_argument("--batch_size", type=int, default=16)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--patience", type=int, default=8)
    args = parser.parse_args()

    train_model(
        data_dir=args.data_dir,
        output_dir=args.output_dir,
        model_type=args.model_type,
        epochs=args.epochs,
        batch_size=args.batch_size,
        lr=args.lr,
        patience=args.patience,
    )
