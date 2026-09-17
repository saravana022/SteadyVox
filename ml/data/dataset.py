"""SteadyVox PyTorch Dataset & DataLoader Pipeline.

Handles audio loading, preprocessing, on-the-fly Mel-Spectrogram extraction,
SpecAugment data augmentation, and target tensor creation.

RESEARCH SCREENING TOOL ONLY — NOT A MEDICAL DIAGNOSIS.
"""

from pathlib import Path
from typing import List, Tuple, Optional, Union
import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader, WeightedRandomSampler

from ml.preprocessing.audio_cleaning import preprocess_pipeline, AudioConfig
from ml.preprocessing.feature_extraction import extract_mel_spectrogram, extract_biomarkers, AcousticBiomarkers


class SpecAugment:
    """Frequency and Time masking data augmentation for spectrograms."""
    def __init__(self, freq_mask_param: int = 12, time_mask_param: int = 24, p: float = 0.5):
        self.freq_mask_param = freq_mask_param
        self.time_mask_param = time_mask_param
        self.p = p

    def __call__(self, spec: torch.Tensor) -> torch.Tensor:
        """spec: (1, n_mels, time_steps)"""
        if np.random.random() > self.p:
            return spec

        augmented = spec.clone()
        _, n_mels, time_steps = augmented.shape

        # Frequency mask
        f = np.random.randint(0, self.freq_mask_param)
        f0 = np.random.randint(0, max(1, n_mels - f))
        augmented[:, f0 : f0 + f, :] = 0.0

        # Time mask
        t = np.random.randint(0, self.time_mask_param)
        t0 = np.random.randint(0, max(1, time_steps - t))
        augmented[:, :, t0 : t0 + t] = 0.0

        return augmented


class ParkinsonVoiceDataset(Dataset):
    """PyTorch Dataset for Parkinson's Disease Voice Phonation Analysis."""

    def __init__(
        self,
        data_dir_or_df: Union[str, Path, pd.DataFrame],
        split: str = "train",
        audio_config: Optional[AudioConfig] = None,
        n_mels: int = 128,
        augment: bool = False,
    ):
        self.split = split
        self.audio_config = audio_config or AudioConfig()
        self.n_mels = n_mels
        self.augment = augment
        self.augmenter = SpecAugment() if augment else None

        if isinstance(data_dir_or_df, pd.DataFrame):
            df = data_dir_or_df
            if "split" in df.columns:
                self.df = df[df["split"] == split].reset_index(drop=True)
            else:
                self.df = df.reset_index(drop=True)
        else:
            base_dir = Path(data_dir_or_df)
            manifest_csv = base_dir / "dataset_manifest.csv"
            if manifest_csv.exists():
                df = pd.read_csv(manifest_csv)
                self.df = df[df["split"] == split].reset_index(drop=True)
            else:
                # Scan directory directly: base_dir / split / [healthy, parkinsons] / *.wav
                records = []
                split_path = base_dir / split
                for label in ["healthy", "parkinsons"]:
                    label_dir = split_path / label
                    if label_dir.exists():
                        for wav in label_dir.glob("*.wav"):
                            records.append({
                                "file_path": str(wav),
                                "label": label,
                                "target": 1 if label == "parkinsons" else 0,
                            })
                self.df = pd.DataFrame(records)

        if len(self.df) == 0:
            raise ValueError(f"No samples found for split '{split}' in {data_dir_or_df}")

        self.targets = self.df["target"].values.astype(np.float32)

    def __len__(self) -> int:
        return len(self.df)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor, str]:
        row = self.df.iloc[idx]
        file_path = row["file_path"]
        target = float(row["target"])

        # Audio preprocessing
        waveform, sr = preprocess_pipeline(file_path, self.audio_config)

        # Extract Mel-Spectrogram
        mel_spec = extract_mel_spectrogram(waveform, sr=sr, n_mels=self.n_mels)
        # Tensor shape: (1, n_mels, time_steps)
        spec_tensor = torch.from_numpy(mel_spec).unsqueeze(0)

        if self.augment and self.augmenter:
            spec_tensor = self.augmenter(spec_tensor)

        target_tensor = torch.tensor([target], dtype=torch.float32)

        return spec_tensor, target_tensor, str(file_path)

    def get_class_weights(self) -> torch.Tensor:
        """Calculates positive class weight to counter class imbalance in BCE loss."""
        num_neg = np.sum(self.targets == 0)
        num_pos = np.sum(self.targets == 1)
        if num_pos == 0 or num_neg == 0:
            return torch.tensor([1.0], dtype=torch.float32)
        pos_weight = float(num_neg) / float(num_pos)
        return torch.tensor([pos_weight], dtype=torch.float32)


def create_dataloaders(
    data_dir: str,
    batch_size: int = 16,
    num_workers: int = 0,
    n_mels: int = 128,
) -> Tuple[DataLoader, DataLoader, DataLoader, torch.Tensor]:
    """Factory creating train, val, and test DataLoaders along with loss class weights."""
    train_dataset = ParkinsonVoiceDataset(data_dir, split="train", n_mels=n_mels, augment=True)
    val_dataset = ParkinsonVoiceDataset(data_dir, split="val", n_mels=n_mels, augment=False)
    test_dataset = ParkinsonVoiceDataset(data_dir, split="test", n_mels=n_mels, augment=False)

    pos_weight = train_dataset.get_class_weights()

    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=True,
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=True,
    )
    test_loader = DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=True,
    )

    return train_loader, val_loader, test_loader, pos_weight
