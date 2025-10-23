#!/usr/bin/env python3
import csv
import statistics
from collections import defaultdict
from datetime import datetime
import json

def analyze_predictions_detailed(csv_path):
    """Detailed analysis of prediction performance."""
    
    # Read data
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    # Separate analysis for rows with and without returns
    rows_with_returns = []
    all_predictions = []
    
    for r in rows:
        try:
            # Parse basic prediction data (available for all rows)
            pred_data = {
                'timestamp': r['wall_time_iso'],
                'price': float(r['mid']),
                'p_fused': float(r['p_fused']),
                'p_fused_cal': float(r['p_fused_cal']),
                'p_hcqr': float(r['p_hcqr']),
                'p_lvp': float(r['p_lvp']), 
                'p_rrf': float(r['p_rrf']),
                'ofi': float(r['ofi_w']),
                'spread': float(r['spread'])
            }
            all_predictions.append(pred_data)
            
            # Parse realized return data if available
            if r['realized_ret_30s'] and r['realized_ret_30s'].strip():
                pred_data['realized_ret'] = float(r['realized_ret_30s'])
                pred_data['realized_up'] = int(r['realized_up_30s'])
                rows_with_returns.append(pred_data)
        except (ValueError, KeyError):
            continue
    
    print(f"\n=== DATA OVERVIEW ===")
    print(f"Total predictions made: {len(all_predictions)}")
    print(f"Predictions with outcomes: {len(rows_with_returns)}")
    
    if all_predictions:
        # Price movement analysis
        prices = [p['price'] for p in all_predictions]
        start_price = prices[0]
        end_price = prices[-1]
        price_change = (end_price - start_price) / start_price
        
        print(f"\n=== MARKET MOVEMENT ===")
        print(f"Start price: ${start_price:.5f}")
        print(f"End price: ${end_price:.5f}")
        print(f"Total change: {price_change:.2%}")
        print(f"Price range: ${min(prices):.5f} - ${max(prices):.5f}")
    
    if rows_with_returns:
        # Model component analysis
        print(f"\n=== MODEL COMPONENT PERFORMANCE ===")
        components = ['p_hcqr', 'p_lvp', 'p_rrf', 'p_fused_cal']
        
        for comp in components:
            correct = sum(1 for p in rows_with_returns if 
                         (p[comp] > 0.5 and p['realized_up'] == 1) or 
                         (p[comp] <= 0.5 and p['realized_up'] == 0))
            accuracy = correct / len(rows_with_returns)
            
            # Brier score (lower is better)
            brier = sum((p[comp] - p['realized_up'])**2 for p in rows_with_returns) / len(rows_with_returns)
            
            print(f"{comp:12s}: Accuracy={accuracy:.2%}, Brier={brier:.4f}")
        
        # Trading simulation
        print(f"\n=== SIMPLE TRADING SIMULATION ===")
        print("(Assumes trade when p_fused_cal > 0.55 or < 0.45)")
        
        trades = []
        for p in rows_with_returns:
            if p['p_fused_cal'] > 0.55:
                trades.append({
                    'direction': 'long',
                    'confidence': p['p_fused_cal'],
                    'return': p['realized_ret'],
                    'spread_cost': p['spread'] / p['price']
                })
            elif p['p_fused_cal'] < 0.45:
                trades.append({
                    'direction': 'short',
                    'confidence': 1 - p['p_fused_cal'],
                    'return': -p['realized_ret'],
                    'spread_cost': p['spread'] / p['price']
                })
        
        if trades:
            gross_returns = [t['return'] for t in trades]
            costs = [t['spread_cost'] for t in trades]
            net_returns = [r - c for r, c in zip(gross_returns, costs)]
            
            print(f"Number of trades: {len(trades)}")
            print(f"Win rate: {sum(1 for r in gross_returns if r > 0) / len(trades):.2%}")
            print(f"Average gross return: {statistics.mean(gross_returns):.6f}")
            print(f"Average cost: {statistics.mean(costs):.6f}")
            print(f"Average net return: {statistics.mean(net_returns):.6f}")
            print(f"Sharpe ratio (approx): {statistics.mean(net_returns) / statistics.stdev(net_returns) if len(net_returns) > 1 else 0:.2f}")
        
        # Market regimes
        print(f"\n=== MARKET REGIME ANALYSIS ===")
        # Split by OFI strength
        high_buying = [p for p in rows_with_returns if p['ofi'] > 10]
        high_selling = [p for p in rows_with_returns if p['ofi'] < -10]
        neutral = [p for p in rows_with_returns if -10 <= p['ofi'] <= 10]
        
        for regime_name, regime_data in [("High Buying", high_buying), 
                                         ("High Selling", high_selling),
                                         ("Neutral", neutral)]:
            if regime_data:
                accuracy = sum(1 for p in regime_data if 
                              (p['p_fused_cal'] > 0.5 and p['realized_up'] == 1) or
                              (p['p_fused_cal'] <= 0.5 and p['realized_up'] == 0)) / len(regime_data)
                avg_ret = statistics.mean([p['realized_ret'] for p in regime_data])
                print(f"{regime_name:12s}: n={len(regime_data):3d}, Accuracy={accuracy:.2%}, AvgRet={avg_ret:+.6f}")

if __name__ == "__main__":
    analyze_predictions_detailed("hype_predictions_old.csv")