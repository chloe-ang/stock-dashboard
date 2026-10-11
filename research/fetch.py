# Temporary: pulls SEC XBRL facts for new tickers so their pages can be built. Removed after use.
import json, sys, traceback, urllib.request, pathlib, time
UA = "stock-dashboard research (github.com/chloe-ang/stock-dashboard)"
OUT = pathlib.Path(__file__).parent
TICKERS = sys.argv[1:]
KEEP = {"Revenues","RevenueFromContractWithCustomerExcludingAssessedTax","RevenueFromContractWithCustomerIncludingAssessedTax",
 "CostOfRevenue","CostOfGoodsAndServicesSold","GrossProfit","OperatingIncomeLoss","NetIncomeLoss","EarningsPerShareDiluted","EarningsPerShareBasic",
 "NetCashProvidedByUsedInOperatingActivities","PaymentsToAcquirePropertyPlantAndEquipment","PaymentsToAcquireProductiveAssets",
 "CashAndCashEquivalentsAtCarryingValue","ShortTermInvestments","AvailableForSaleSecuritiesDebtSecuritiesCurrent","LongTermDebt","LongTermDebtNoncurrent",
 "PremiumsEarnedNet","GrossPremiumsWritten","PremiumsWrittenGross","LossAndLossAdjustmentExpense","PolicyholderBenefitsAndClaimsIncurredNet",
 "CommonStockSharesOutstanding","EntityCommonStockSharesOutstanding","WeightedAverageNumberOfDilutedSharesOutstanding",
 "PaymentsToAcquireBusinessesNetOfCashAcquired","PaymentsForRepurchaseOfCommonStock","PaymentsOfDividends","ProceedsFromIssuanceOfCommonStock",
 "Revenue","GrossProfit","ProfitLossFromOperatingActivities","ProfitLoss","DilutedEarningsPerShare","CashFlowsFromUsedInOperatingActivities",
 "PurchaseOfPropertyPlantAndEquipmentClassifiedAsInvestingActivities","CashAndCashEquivalents"}
def get(u):
    req = urllib.request.Request(u, headers={"User-Agent": UA, "Accept-Encoding": "identity"})
    with urllib.request.urlopen(req, timeout=60) as r: return json.load(r)
print("UA", UA, flush=True)
try:
    m = {v["ticker"]: v for v in get("https://www.sec.gov/files/company_tickers.json").values()}
except Exception:
    traceback.print_exc(); m = {}
def one(t):
    e = m.get(t)
    if not e: print("no CIK", t); return
    cik = str(e["cik_str"]).zfill(10)
    f = get(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"); time.sleep(0.5)
    out = {"ticker": t, "cik": cik, "name": f.get("entityName"), "facts": {}}
    for ns, cs in f.get("facts", {}).items():
        for c, d in cs.items():
            if c in KEEP:
                out["facts"][f"{ns}:{c}"] = {u: [{k: x.get(k) for k in ("start","end","val","fy","fp","form","filed","frame")} for x in v if x.get("end","") >= "2020-06-01"] for u, v in d["units"].items()}
    try:
        sub = get(f"https://data.sec.gov/submissions/CIK{cik}.json"); r = sub["filings"]["recent"]
        out["filings"] = [[r["form"][i], r["filingDate"][i], r["reportDate"][i], r["primaryDocument"][i], r["accessionNumber"][i]] for i in range(min(60, len(r["form"])))]
        out["fiscalYearEnd"] = sub.get("fiscalYearEnd")
    except Exception as ex: print("subs", t, ex)
    (OUT / f"{t}.json").write_text(json.dumps(out))
    print(t, cik, out["name"], len(out["facts"]))

for t in TICKERS:
    try: one(t)
    except Exception: traceback.print_exc()
