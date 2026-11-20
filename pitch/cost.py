"""Cost per day of the vision model, from measured tokens per call and Google's published list price.

Usage: python3 pitch/cost.py CALLS PROMPT_TOKENS OUTPUT_TOKENS
  (the three numbers from the first line of rush_summary.txt, or from GET /api/stats on a running server)

Prices: Gemini 3.1 Pro Preview, paid tier, prompts under 200k tokens: $2.00 per 1M input, $12.00 per 1M output
(aistudio.google.com/docs/pricing, read Nov 19, 2026). Gemini 3 Flash Preview is $0.50 / $3.00 but failed our glare test.
"""
import sys

IN_PRICE, OUT_PRICE = 2.00 / 1e6, 12.00 / 1e6
CAMS_LIVE = 13                 # 16 cameras, 3 were offline this week and are skipped without a model call
RUSH_CYCLES = (4 + 3) * 30     # 6:30 to 10:30 AM and 3:30 to 6:30 PM, one read every 2 minutes
ALLDAY_CYCLES = 24 * 30


def main():
    calls, p_tok, o_tok = (int(x) for x in sys.argv[1:4])
    per_call = (p_tok / calls) * IN_PRICE + (o_tok / calls) * OUT_PRICE
    rush, allday = per_call * CAMS_LIVE * RUSH_CYCLES, per_call * CAMS_LIVE * ALLDAY_CYCLES
    print(f"measured on {calls} calls: {p_tok / calls:.0f} prompt + {o_tok / calls:.0f} output tokens per call = ${per_call:.4f} per read")
    print(f"rush-hour schedule: {CAMS_LIVE * RUSH_CYCLES} reads/day = ${rush:.2f}/day (about ${rush * 30:.0f}/month)")
    print(f"all day, every 2 min: {CAMS_LIVE * ALLDAY_CYCLES} reads/day = ${allday:.2f}/day")
    print(f"\nfacts.json cost_line: Model cost: about ${rush:.0f} per day for both campuses on the rush-hour schedule "
          f"({CAMS_LIVE * RUSH_CYCLES} camera reads at ${per_call:.4f} each, measured on {calls} calls), "
          f"about ${allday:.0f} per day if read all day")


if __name__ == "__main__":
    main()
