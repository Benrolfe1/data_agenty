# HYPE Trading Algorithm

This repository contains trading algorithms for the Hyperliquid HYPE-PERP market.

## Files

- `30s.py` - Main 30-second prediction algorithm with multiple models (HCQR, LVP, RRF)
- `30z.py` - Alternative version of the 30s algorithm
- `s12.py` - Earlier version with different parameters
- `s13.py` - Another variant for testing
- `analyze_performance.py` - Script to analyze prediction accuracy
- `analyze_detailed.py` - Detailed performance analysis with trading simulation

## Setup

1. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the main algorithm:
```bash
python 30s.py
```

## Output

The algorithm creates a CSV file `hype_predictions.csv` with:
- Real-time market data
- Prediction probabilities for 10s, 30s, and 60s horizons
- Realized returns after 30 seconds
- Model component outputs (HCQR, LVP, RRF)

## Safety

Currently in data collection mode. To enable live trading:
1. Set confidence thresholds in the code
2. Implement position sizing
3. Add stop-loss logic
4. Monitor performance metrics

## Analysis

After collecting data, run:
```bash
python analyze_performance.py
```

This will show:
- Prediction accuracy
- Calibration analysis
- Returns by confidence level
- Market regime performance