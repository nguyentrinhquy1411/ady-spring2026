# Vietnam Housing Price Analysis 🏠

A comprehensive data analysis project that explores and visualizes housing prices in Vietnam using real estate data.

## 📋 Project Overview

This project analyzes Vietnamese housing market data to uncover pricing patterns, relationships between property features, and market insights through exploratory data analysis and visualizations.

### Features
- 📊 Data collection and loading from CSV
- 🧹 Data cleaning and normalization
- 📈 Exploratory Data Analysis (EDA)
- 📉 Comprehensive visualizations with Matplotlib, Seaborn, and Plotly
- 🔍 Correlation analysis and statistical insights

## 🚀 Getting Started

### Prerequisites

- Python 3.12 or higher
- [uv](https://docs.astral.sh/uv/) package manager (recommended) or pip

### Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd ady-2026
   ```

2. **Install dependencies using uv (recommended):**
   ```bash
   uv sync
   ```

   Or using pip:
   ```bash
   pip install -e .
   ```

### 📦 Dependencies

- `pandas` - Data manipulation and analysis
- `numpy` - Numerical computing
- `matplotlib` - Data visualization
- `seaborn` - Statistical data visualization
- `plotly` - Interactive visualizations
- `ipykernel` - Jupyter notebook support

## 🎯 How to Run

### Option 1: Using Jupyter Notebook / VS Code

1. Open `main.ipynb` in Jupyter Notebook or VS Code
2. Select the Python kernel (Python 3.12+)
3. Run all cells sequentially from top to bottom

### Option 2: Using Command Line

```bash
# Activate the virtual environment (if using uv)
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate  # On Windows

# Start Jupyter Notebook
jupyter notebook main.ipynb
```

## 📁 Project Structure

```
ady-2026/
├── main.ipynb                      # Main analysis notebook
├── assets/
│   └── vietnam_housing_dataset.csv # Housing dataset
├── pyproject.toml                  # Project dependencies
├── uv.lock                         # Lock file for dependencies
├── README.md                       # This file
└── requirement-copilot.md          # agent requirements
```

## 📊 Dataset

The dataset (`vietnam_housing_dataset.csv`) contains ~30,000 housing records with the following features:

| Column | Description |
|--------|-------------|
| Address | Property location |
| Area | Property size (m²) |
| Frontage | Street frontage width (m) |
| Access Road | Road width (m) |
| House direction | Facing direction |
| Balcony direction | Balcony facing direction |
| Floors | Number of floors |
| Bedrooms | Number of bedrooms |
| Bathrooms | Number of bathrooms |
| Legal status | Property legal documentation |
| Furniture state | Furniture condition |
| **Price** | Price in billion VND (target variable) |

## 🔬 Analysis Sections

The notebook is organized into the following sections:

1. **Data Collection** - Loading the dataset
2. **Data Understanding** - Exploring structure and statistics
3. **Data Cleaning & Normalization** - Handling missing values and duplicates
4. **Exploratory Data Analysis** - Statistical analysis and correlations
5. **Data Visualization** - Charts and graphs including:
   - Price distribution (histogram & boxplot)
   - Area vs Price scatter plot
   - Correlation heatmap
   - Price by bedrooms/bathrooms
   - Price by legal status and furniture state
6. **Key Insights & Summary** - Final findings and conclusions

## 📈 Sample Visualizations

The project generates various visualizations:
- Distribution plots showing price patterns
- Correlation heatmaps revealing feature relationships
- Bar charts comparing prices across different property characteristics
- Scatter plots exploring area-price relationships

## 🛠️ Troubleshooting

### Common Issues

**Issue: ModuleNotFoundError**
```bash
# Reinstall dependencies
uv sync --reinstall
```

**Issue: Kernel not found**
```bash
# Install ipykernel in the virtual environment
uv pip install ipykernel
python -m ipykernel install --user --name=ady-2026
```

**Issue: Dataset not found**
- Ensure `vietnam_housing_dataset.csv` is in the `assets/` folder
- Check the file path in cell 4 of the notebook

## 📝 Requirements

This project follows these requirements:
- ✅ Load housing data from CSV file
- ✅ Clean and normalize data (handle missing values)
- ✅ Perform analysis using Pandas, Matplotlib, and Seaborn
- ✅ Visualize results using charts and graphs
- ❌ No machine learning or predictive modeling

## 👥 Contributing

Feel free to fork this project and submit pull requests for any improvements!

## 📄 License

This project is open source and available under the MIT License.

## 🙋 Support

If you encounter any issues or have questions, please:
1. Check the troubleshooting section above
2. Review the notebook comments for detailed explanations
3. Open an issue on GitHub

---

**Happy Analyzing! 📊🏠**
