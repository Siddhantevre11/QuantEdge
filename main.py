
import pandas as pd
from src.data_loader import InstitutionalDataLoader
from src.risk_system import BarclaysRiskSystem
from src.execution_engine import AdaptiveTWAP
from src.pnl_attribution import PnLAttributor
from src.stress_testing import CrisisSimulator
from src.visualization import PortfolioVisualizer

def main():
    print("Barclays Quant Research Project - Running Full Pipeline")
    
    # 1. Load and process data
    print("Loading market data...")
    data_loader = InstitutionalDataLoader(start_date='2015-01-01')
    data_loader.load_raw_data().process_signals()
    processed_data = data_loader.processed_data
    
    # 2. Generate sample positions
    positions = {
        'notional': 5000000,
        'duration': 4.2,
        'spread_duration': 3.8
    }
    
    # 3. Risk checks
    print("Running risk checks...")
    risk_system = BarclaysRiskSystem()
    violations = risk_system.check_limits(positions)
    print(f"Risk Limit Violations: {violations}")
    
    # 4. Execute sample trade
    print("Executing sample trade...")
    algo = AdaptiveTWAP('LQD', 10000)
    executions = algo.execute()
    
    # Add sample attributes for PnL attribution
    executions['credit_duration'] = 3.8
    executions['vega'] = 25000
    executions['beta'] = 0.8
    executions['notional'] = 100 * executions['price']
    
    # 5. PnL attribution
    print("Running PnL attribution...")
    attributor = PnLAttributor(executions)
    pnl_breakdown = attributor.attribute()
    print("PnL Attribution Summary:")
    print(pnl_breakdown.sum())
    
    # 6. Stress testing
    print("Running stress tests...")
    portfolio = pd.DataFrame({
        'symbol': ['SPY', 'TLT'],
        'shares': [1000, 2000],
        'price': [400, 120],
        'spread': [0.01, 0.02],
        'liquidity_factor': [0.95, 0.85]
    })
    simulator = CrisisSimulator(portfolio)
    stress_results = simulator.run_scenarios()
    print("Stress Test Results:")
    print(stress_results)
    
    # 7. Visualization
    print("Generating visualizations...")
    visualizer = PortfolioVisualizer(pnl_breakdown)
    visualizer.create_dashboard()
    
    print("Pipeline execution complete!")

if __name__ == "__main__":
    main()
