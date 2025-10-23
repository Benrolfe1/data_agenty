#!/usr/bin/env python3
import csv
import statistics
from collections import defaultdict
from pathlib import Path

def analyze_predictions(csv_path):
    """Analyze the prediction performance from the CSV file."""
    
    # Read data
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    # Filter rows with realized returns
    rows_with_returns = [r for r in rows if r['realized_ret_30s'] and r['realized_ret_30s'].strip()]
    
    print(f"Total rows: {len(rows)}")
    print(f"Rows with realized returns: {len(rows_with_returns)}")
    
    if not rows_with_returns:
        print("No rows with realized returns found!")
        return
    
    # Parse data
    predictions = []
    for r in rows_with_returns:
        try:
            p_cal = float(r['p_fused_cal'])
            realized_ret = float(r['realized_ret_30s'])
            realized_up = int(r['realized_up_30s'])
            spread = float(r['spread'])
            
            predictions.append({
                'p_cal': p_cal,
                'predicted_up': 1 if p_cal > 0.5 else 0,
                'realized_ret': realized_ret,
                'realized_up': realized_up,
                'correct': (p_cal > 0.5 and realized_up == 1) or (p_cal <= 0.5 and realized_up == 0),
                'spread_ticks': spread / 0.001  # assuming 0.001 tick size
            })
        except (ValueError, KeyError):
            continue
    
    # Calculate metrics
    accuracy = sum(1 for p in predictions if p['correct']) / len(predictions)
    
    # Calibration by bins
    bins = defaultdict(list)
    for p in predictions:
        bin_idx = int(p['p_cal'] * 10)
        bins[bin_idx].append(p)
    
    print(f"\n=== OVERALL PERFORMANCE ===")
    print(f"Accuracy: {accuracy:.2%}")
    print(f"Total predictions: {len(predictions)}")
    
    # Returns analysis
    all_returns = [p['realized_ret'] for p in predictions]
    up_returns = [p['realized_ret'] for p in predictions if p['realized_up'] == 1]
    down_returns = [p['realized_ret'] for p in predictions if p['realized_up'] == 0]
    
    print(f"\n=== RETURNS ANALYSIS ===")
    print(f"Average return: {statistics.mean(all_returns):.6f}")
    print(f"Median return: {statistics.median(all_returns):.6f}")
    print(f"Std dev: {statistics.stdev(all_returns):.6f}")
    print(f"Win rate (ret > 0): {sum(1 for r in all_returns if r > 0) / len(all_returns):.2%}")
    
    # Calibration analysis
    print(f"\n=== CALIBRATION ANALYSIS ===")
    print("Prob Bin | Count | Actual Up% | Expected Up%")
    print("-" * 45)
    for bin_idx in sorted(bins.keys()):
        bin_data = bins[bin_idx]
        if len(bin_data) > 0:
            actual_up = sum(1 for p in bin_data if p['realized_up'] == 1) / len(bin_data)
            expected_up = (bin_idx * 0.1 + 0.05)
            print(f"{bin_idx*10:02d}-{(bin_idx+1)*10:02d}% | {len(bin_data):5d} | {actual_up:10.2%} | {expected_up:10.2%}")
    
    # Edge analysis
    print(f"\n=== EDGE ANALYSIS ===")
    strong_predictions = [p for p in predictions if p['p_cal'] > 0.6 or p['p_cal'] < 0.4]
    if strong_predictions:
        strong_accuracy = sum(1 for p in strong_predictions if p['correct']) / len(strong_predictions)
        strong_returns = [p['realized_ret'] for p in strong_predictions]
        print(f"Strong predictions (p < 0.4 or p > 0.6): {len(strong_predictions)}")
        print(f"Strong prediction accuracy: {strong_accuracy:.2%}")
        print(f"Average return on strong predictions: {statistics.mean(strong_returns):.6f}")
    
    # Spread analysis
    print(f"\n=== SPREAD ANALYSIS ===")
    avg_spread = statistics.mean([p['spread_ticks'] for p in predictions])
    print(f"Average spread: {avg_spread:.2f} ticks")
    
    # By confidence buckets
    confidence_buckets = {
        'Very Low': [p for p in predictions if p['p_cal'] < 0.3],
        'Low': [p for p in predictions if 0.3 <= p['p_cal'] < 0.4],
        'Neutral': [p for p in predictions if 0.4 <= p['p_cal'] < 0.6],
        'High': [p for p in predictions if 0.6 <= p['p_cal'] < 0.7],
        'Very High': [p for p in predictions if p['p_cal'] >= 0.7]
    }
    
    print(f"\n=== CONFIDENCE BUCKET ANALYSIS ===")
    print("Bucket     | Count | Accuracy | Avg Return")
    print("-" * 45)
    for bucket_name, bucket_data in confidence_buckets.items():
        if bucket_data:
            bucket_accuracy = sum(1 for p in bucket_data if p['correct']) / len(bucket_data)
            bucket_returns = [p['realized_ret'] for p in bucket_data]
            avg_return = statistics.mean(bucket_returns)
            print(f"{bucket_name:10s} | {len(bucket_data):5d} | {bucket_accuracy:7.2%} | {avg_return:+.6f}")

if __name__ == "__main__":
    # Get the first CSV file (before restart)
    csv_files = sorted(Path(".").glob("hype_predictions_*.csv"))
    if csv_files:
        print(f"Analyzing {csv_files[0]}...")
        analyze_predictions(csv_files[0])
    else:
        # Try the main file
        if Path("hype_predictions.csv").exists():
            analyze_predictions("hype_predictions.csv")
        else:
            print("No CSV file found!")