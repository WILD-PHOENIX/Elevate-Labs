# SVM Binary Classification - Breast Cancer Dataset

## Overview
This project implements Support Vector Machines (SVM) for binary classification using the breast cancer dataset. The implementation covers both linear and non-linear classification with proper hyperparameter tuning and visualization.

## Objectives
- Use SVMs for linear and non-linear classification
- Compare performance between linear and RBF kernels
- Visualize decision boundaries using 2D data
- Tune hyperparameters like C and gamma
- Evaluate performance using cross-validation

## Requirements
- Python 3.7+
- scikit-learn
- pandas
- numpy
- matplotlib
- seaborn

## Installation
```bash
pip install scikit-learn pandas numpy matplotlib seaborn
```

## Dataset
The project uses the breast cancer dataset with the following features:
- 30 numerical features (radius, texture, perimeter, area, smoothness, etc.)
- Binary target: M (Malignant) or B (Benign)
- 569 samples total

## Files
- `t7.ipynb` - Main implementation notebook
- `breast-cancer.csv` - Dataset file (optional, will use sklearn dataset if not found)

## Usage
1. Place the dataset file in the same directory as the notebook
2. Open the notebook in VS Code or Jupyter
3. Run all cells sequentially

## Implementation Details

### Data Preprocessing
- Feature scaling using StandardScaler
- Binary encoding of target variable
- Train-test split with stratification

### SVM Models
- Linear SVM with linear kernel
- RBF SVM with radial basis function kernel
- Hyperparameter tuning using GridSearchCV

### Hyperparameter Tuning
- C values: [0.1, 1, 10, 100]
- Gamma values: ['scale', 'auto', 0.001, 0.01, 0.1, 1]
- Kernels: ['linear', 'rbf']

### Evaluation Metrics
- Accuracy score
- Classification report (precision, recall, F1-score)
- Confusion matrix
- 5-fold cross-validation

## Visualizations
- Decision boundary plots for linear and RBF SVM
- Model performance comparison
- Confusion matrix heatmap
- Cross-validation score distribution

## Key Concepts Covered
- Margin maximization
- Kernel trick
- Hyperparameter tuning
- Cross-validation
- Decision boundaries
- Model evaluation

## Results
The implementation demonstrates:
- Comparison between linear and RBF kernel performance
- Impact of hyperparameter tuning on model accuracy
- Visual representation of decision boundaries
- Comprehensive performance evaluation

## Notes
- The code automatically handles missing dataset files by using sklearn's built-in breast cancer dataset
- All visualizations are saved and displayed inline
- Cross-validation ensures robust performance evaluation
- Feature scaling is applied to improve SVM performance