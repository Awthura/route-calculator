<img src="logo.svg" width="80" alt="Path2Anywhere logo" />

# Path2Anywhere

Route planning and road trip tools — free, no sign-up required.

**Live site → [path2anywhere.com](https://path2anywhere.com)**

---

## Tools

### Multi-Stop Route Planner
Plan a journey with up to 10 stops. Get per-leg distance, drive time, fuel cost, CO₂ footprint, and photo bubbles on the map for each stop.

→ [path2anywhere.com/route-calculator/multi-stop/](https://path2anywhere.com/route-calculator/multi-stop/)

### Road Trip Planner
Browse 445 curated road trips across 12 countries and regions. Pick a trip, optionally set a custom start/end, and open it directly in the Multi-Stop Planner with the route pre-calculated.

| Region | Trips |
|---|---|
| France | 60 |
| Italy | 60 |
| Spain | 60 |
| Norway | 50 |
| Multi-country Europe | 50 |
| Germany | 40 |
| Austria | 25 |
| Switzerland | 25 |
| Benelux | 20 |
| Poland | 20 |
| Portugal | 20 |
| Iceland | 15 |

→ [path2anywhere.com/holiday/trip-planner/](https://path2anywhere.com/holiday/trip-planner/)

### Other Route Tools
| Tool | Description |
|---|---|
| [Route Planner](https://path2anywhere.com/route-calculator/route/) | Point-to-point route with distance, duration, fuel and CO₂ |
| [Supply Chain Calculator](https://path2anywhere.com/route-calculator/supply-chain/) | 3-stop route (Supplier → Plant → Customer) |
| [Commute Calculator](https://path2anywhere.com/route-calculator/commute/) | Round-trip commute with daily/weekly/monthly estimates |
| [Away Days Calculator](https://path2anywhere.com/route-calculator/away-days/) | Football away trips across 7 European leagues |

---

## Stack

- **Frontend** — Vanilla HTML/CSS/JS, served via Cloudflare
- **Backend** — n8n Cloud webhook (route calculation via Google Directions API)
- **APIs** — Google Maps JS API, Google Directions API, Wikipedia (stop photos)
- **Auth & usage** — Supabase (freemium: 5 uses/day anonymous, 20 signed-in)
- **Autocomplete** — Photon (OpenStreetMap, free)
