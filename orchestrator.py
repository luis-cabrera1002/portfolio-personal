import json
import os
import time

from config import ALL_TICKERS, UNIVERSE, TICKER_NAMES, CACHE_DIR
from agents import (
    market_analyst,
    esg_checker,
    news_sentinel,
    risk_manager,
    predictor_engine,
    macro_monitor,
    commodity_tracker,
    portfolio_strategist,
    report_generator,
)
from agents.alert_manager import check_risk_alerts
from agents.backtester import run_backtest as _run_backtest

_RESULTS_CACHE = os.path.join(CACHE_DIR, "latest_results.json")


class PortfolioOrchestrator:

    def __init__(self, tickers=None):
        self.tickers = tickers or UNIVERSE["stocks"] + UNIVERSE["etfs"]

    def run_full_analysis(self, tickers=None):
        tickers = tickers or self.tickers

        # Use cached results if < 4 hours old
        if os.path.exists(_RESULTS_CACHE):
            age = time.time() - os.path.getmtime(_RESULTS_CACHE)
            if age < 4 * 3600:
                try:
                    with open(_RESULTS_CACHE) as f:
                        cached = json.load(f)
                    print(f"  ✅ Usando caché ({age/3600:.1f}h de antigüedad)")
                    return cached
                except Exception:
                    pass

        results = {}

        print("📊 [1/9] Analizando mercado y precios históricos...")
        try:
            results["market"] = market_analyst.get_summary(tickers)
        except Exception as e:
            print(f"  ⚠ market_analyst falló: {e}")
            results["market"] = {}

        print("🌿 [2/9] Evaluando scores ESG...")
        try:
            results["esg"] = esg_checker.get_esg_report(tickers)
        except Exception as e:
            print(f"  ⚠ esg_checker falló: {e}")
            results["esg"] = {}

        print("📰 [3/9] Monitoreando noticias y sentimiento...")
        try:
            results["news"] = news_sentinel.get_portfolio_news(tickers, TICKER_NAMES)
        except Exception as e:
            print(f"  ⚠ news_sentinel falló: {e}")
            results["news"] = []

        print("⚠️  [4/9] Calculando métricas de riesgo...")
        try:
            weights = results.get("market", {}).get("allocation", {}).get("weights") or None
            results["risk"] = risk_manager.get_risk_summary(tickers, weights)
        except Exception as e:
            print(f"  ⚠ risk_manager falló: {e}")
            results["risk"] = {}

        print("🔔 [4b] Verificando alertas de riesgo...")
        try:
            results["alerts"] = check_risk_alerts(
                results.get("risk", {}),
                results.get("market", {}),
                results.get("news", []),
            )
        except Exception as e:
            print(f"  ⚠ alert_manager falló: {e}")
            results["alerts"] = []

        print("🤖 [5/9] Generando predicciones ML...")
        try:
            results["predictions"] = predictor_engine.get_predictions_summary(tickers)
        except Exception as e:
            print(f"  ⚠ predictor_engine falló: {e}")
            results["predictions"] = {}

        print("🌎 [6/9] Monitoreando entorno macroeconómico...")
        try:
            results["macro"] = macro_monitor.get_macro_summary()
        except Exception as e:
            print(f"  ⚠ macro_monitor falló: {e}")
            results["macro"] = {}

        print("🥇 [7/9] Rastreando commodities...")
        try:
            results["commodities"] = commodity_tracker.get_summary()
        except Exception as e:
            print(f"  ⚠ commodity_tracker falló: {e}")
            results["commodities"] = {}

        print("🎯 [8/9] Optimizando estrategia del portfolio...")
        try:
            extra = {
                "market": results.get("market", {}).get("metrics", {}),
                "esg": results.get("esg", {}),
                "news": results.get("news", []),
                "macro": results.get("macro", {}),
                "risk": results.get("risk", {}).get("portfolio_metrics", {}),
            }
            results["strategy"] = portfolio_strategist.get_strategy_summary(tickers, extra_data=extra)
        except Exception as e:
            print(f"  ⚠ portfolio_strategist falló: {e}")
            results["strategy"] = {}

        print("📄 [9/9] Generando reporte PDF...")
        try:
            results["report_path"] = report_generator.generate_pdf_report(results)
            print(f"  ✅ PDF guardado en: {results['report_path']}")
        except Exception as e:
            print(f"  ⚠ report_generator falló: {e}")
            results["report_path"] = None

        # Save to cache (without prices_df)
        try:
            os.makedirs(CACHE_DIR, exist_ok=True)
            serializable = {k: v for k, v in results.items() if k != "market"}
            market_copy = {k: v for k, v in results.get("market", {}).items() if k != "prices_df"}
            serializable["market"] = market_copy
            with open(_RESULTS_CACHE, "w") as f:
                json.dump(serializable, f, default=str, indent=2)
        except Exception:
            pass

        print("✅ Análisis completo finalizado.")
        return results

    def run_backtest(self, tickers=None, weights=None, start_date=None, end_date=None, benchmark="SPY"):
        tickers = tickers or self.tickers
        weights = weights or {}
        return _run_backtest(tickers, weights, start_date, end_date, benchmark)

    def run_quick_analysis(self, tickers=None):
        tickers = tickers or self.tickers
        results = {}

        print("⚡ [1/3] Precios y mercado...")
        try:
            results["market"] = market_analyst.get_summary(tickers)
        except Exception as e:
            print(f"  ⚠ {e}")
            results["market"] = {}

        print("📰 [2/3] Noticias y sentimiento...")
        try:
            results["news"] = news_sentinel.get_portfolio_news(tickers, TICKER_NAMES)
        except Exception as e:
            print(f"  ⚠ {e}")
            results["news"] = []

        print("🎯 [3/3] Estrategia rápida...")
        try:
            results["strategy"] = portfolio_strategist.get_strategy_summary(tickers)
        except Exception as e:
            print(f"  ⚠ {e}")
            results["strategy"] = {}

        print("✅ Update rápido listo.")
        return results


if __name__ == "__main__":
    orch = PortfolioOrchestrator()
    data = orch.run_full_analysis(UNIVERSE["stocks"][:5])
    print("\n=== RESUMEN ===")
    strategy = data.get("strategy", {})
    alloc = strategy.get("allocation", {})
    print(f"Sharpe optimizado: {alloc.get('sharpe_ratio', 'N/A')}")
    print(f"PDF: {data.get('report_path', 'N/A')}")
