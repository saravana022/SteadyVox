# SteadyVox Third-Party Attributions & Dataset Provenance

SteadyVox complies with all open-source, academic, and clinical dataset license requirements.

## 1. Datasets & Clinical Cohorts

### Oxford Parkinson's Disease Telemonitoring & Voice Dataset
- **Authors**: Max A. Little, Patrick E. McSharry, Stephen J. Roberts, Declan A. Costello, Irene M. Moroz.
- **Reference**: Little, M. A., et al. (2007). "Exploiting Nonlinear Recurrence and Fractal Scaling Properties for Voice Disorder Detection." *BioMedical Engineering OnLine*, 6(1), 23.
- **Source**: UCI Machine Learning Repository (DOI: 10.24432/C59C74).
- **License**: Creative Commons Attribution 4.0 International (CC BY 4.0).
- **Cohort**: 31 subjects (23 PD, 8 healthy controls), 195 sustained vowel phonations.
- **Usage in SteadyVox**: Used to train the 16-feature calibrated Praat acoustic model evaluated via subject-wise Leave-One-Subject-Out (LOSO) cross-validation.

## 2. Audio Processing & Scientific Libraries

### Parselmouth (Praat in Python)
- **Authors**: Yannick Jadoul, Bill Thompson, Bart de Boer.
- **Reference**: Jadoul, Y., Thompson, B., & de Boer, B. (2018). "Introducing Parselmouth: A Python interface to Praat." *Journal of Phonetics*, 71, 1-15.
- **License**: GNU General Public License v3 or later (GPLv3+).
- **Usage**: Extraction of MDVP cycle-to-cycle frequency perturbations (jitter), amplitude perturbations (shimmer), fundamental frequency (F0), and harmonics-to-noise ratio (HNR).

### PyTorch & Librosa
- **PyTorch**: BSD 3-Clause License (Meta Platforms, Inc.).
- **Librosa**: ISC License (Brian McFee et al.).

## 3. Frontend Icons & Visual Assets

### Lucide React
- **Authors**: Lucide Contributors.
- **License**: ISC License.
- **Usage**: Medical, technical, and navigation iconography throughout the user interface.

### Vectors & Illustrations
- Custom inline SVG vector illustrations (`HeroIllustration.tsx`, wave perturbations, neural nodes) created natively for SteadyVox under Apache 2.0 / MIT. No proprietary stock imagery used.

## 4. Fonts

- **Inter**: SIL Open Font License 1.1 (Rasmus Andersson).
- **JetBrains Mono**: SIL Open Font License 1.1 (JetBrains s.r.o.).
