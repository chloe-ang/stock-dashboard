// Temporary: Yahoo quarterly fundamentals for new tickers. Removed after use.
import { writeFileSync, mkdirSync } from "node:fs";
const UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36";
const T = ["quarterlyTotalRevenue","quarterlyCostOfRevenue","quarterlyGrossProfit","quarterlyOperatingIncome","quarterlyNetIncome","quarterlyDilutedEPS",
  "quarterlyOperatingCashFlow","quarterlyCapitalExpenditure","quarterlyFreeCashFlow","quarterlyCashAndCashEquivalents","quarterlyCashCashEquivalentsAndShortTermInvestments",
  "quarterlyTotalDebt","quarterlyOrdinarySharesNumber","quarterlyDilutedAverageShares","quarterlyRepurchaseOfCapitalStock","quarterlyCashDividendsPaid",
  "annualTotalRevenue","annualOperatingCashFlow","annualCapitalExpenditure","annualGrossProfit","annualDilutedEPS"];
const r0 = await fetch("https://fc.yahoo.com", { headers: { "User-Agent": UA }, redirect: "manual" });
const cookie = (r0.headers.getSetCookie?.() || []).map(c => c.split(";")[0]).join("; ");
const crumb = await (await fetch("https://query2.finance.yahoo.com/v1/test/getcrumb", { headers: { "User-Agent": UA, Cookie: cookie } })).text();
mkdirSync("research/yf", { recursive: true });
for (const s of process.argv.slice(2)) {
  const out = { symbol: s };
  try {
    const u = `https://query2.finance.yahoo.com/ws/fundamentals-timeseries/v1/finance/timeseries/${s}?symbol=${s}&type=${T.join(",")}&period1=1483228800&period2=${Math.floor(Date.now()/1000)}&crumb=${encodeURIComponent(crumb)}`;
    const j = await (await fetch(u, { headers: { "User-Agent": UA, Cookie: cookie } })).json();
    for (const r of j?.timeseries?.result || []) { const k = r.meta?.type?.[0]; if (k && r[k]) out[k] = r[k].filter(Boolean).map(x => [x.asOfDate, x.reportedValue?.raw]); }
    const qs = `https://query2.finance.yahoo.com/v10/finance/quoteSummary/${s}?modules=incomeStatementHistoryQuarterly,cashflowStatementHistoryQuarterly,earnings,earningsHistory,earningsTrend,calendarEvents,defaultKeyStatistics,financialData,assetProfile&crumb=${encodeURIComponent(crumb)}`;
    out.summary = (await (await fetch(qs, { headers: { "User-Agent": UA, Cookie: cookie } })).json())?.quoteSummary?.result?.[0] || null;
  } catch (e) { out.error = String(e); }
  writeFileSync(`research/yf/${s}.json`, JSON.stringify(out));
  console.log(s, Object.keys(out).length, out.quarterlyTotalRevenue?.length);
}
