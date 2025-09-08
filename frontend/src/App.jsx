import { useState, useEffect } from "react";

const API = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export default function App() {
  const [symbol, setSymbol] = useState("AAPL");
  const [prices, setPrices] = useState([]);
  const [forecast, setForecast] = useState([]);
  const [news, setNews] = useState([]);

  async function load(sym) {
    const p = await fetch(`${API}/price?symbol=${sym}`).then(r=>r.json());
    const f = await fetch(`${API}/forecast?symbol=${sym}&horizon=30`).then(r=>r.json());
    const n = await fetch(`${API}/news?symbol=${sym}`).then(r=>r.json());
    setPrices(p.data || []);
    setForecast(f.forecast || []);
    setNews(n.news || []);
  }

  useEffect(() => { load(symbol); }, []);

  return (
    <div style={{maxWidth:900, margin:"24px auto", fontFamily:"Inter, system-ui"}}>
      <h1>Stock Forecast & News Sentiment</h1>
      <div style={{display:"flex", gap:8}}>
        <input value={symbol} onChange={e=>setSymbol(e.target.value.toUpperCase())} placeholder="AAPL" />
        <button onClick={()=>load(symbol)}>Search</button>
      </div>

      <section style={{marginTop:24}}>
        <h3>Prices (last five closes)</h3>
        <ul>
          {prices.slice(-5).map((r,i) => {
            const d = new Date(r.date);
            const label = isNaN(d) ? String(r.date) : d.toISOString().slice(0,10);
            return <li key={i}>{label}: {Number(r.close).toFixed(2)}</li>;
          })}
        </ul>
      </section>

      <section style={{marginTop:24}}>
        <h3>Forecast (next five days)</h3>
        <ul>{forecast.slice(0,5).map((r,i)=>
          <li key={i}>{r.date}: {r.yhat.toFixed(2)} [{r.lower.toFixed(2)}–{r.upper.toFixed(2)}]</li>
        )}</ul>
      </section>

      <section style={{marginTop:24}}>
        <h3>Latest News & Sentiment</h3>
        <ul>
          {news.map((n,i)=>
            <li key={i}>
              <span style={{marginRight:8}}>
                {n.label === "positive" ? "🟢" : n.label === "negative" ? "🔴" : "🟡"}
              </span>
              <a href={n.url} target="_blank" rel="noreferrer">{n.title}</a>
            </li>
          )}
        </ul>
      </section>

      <p style={{marginTop:24, fontSize:12, color:"#666"}}>Educational demo — not financial advice.</p>
    </div>
  );
}
