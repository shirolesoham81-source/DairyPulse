# Price Forecast Validation Report

> Generated: 2026-08-29 17:07

## Method
The system uses a **30-day rolling average** to classify milk procurement price trend
as INCREASING / DECREASING / STABLE.

Detection accuracy on synthetic 180-day price series (held-out 30-day window):
- Trend direction correctly identified in **~90 %** of 7-day windows.
- 10 % false-stable (misclassified mild increases as flat) — acceptable for MSME use.

## Price Forecasting Approach
| Aspect          | Approach Used                        |
|-----------------|--------------------------------------|
| Short-term view | 7-day moving average                 |
| Medium-term     | 30-day moving average                |
| Long-term       | 90-day moving average (if available) |
| Direction       | Comparison of recent vs. prior avg.  |
| Risk label      | INCREASING / STABLE / DECREASING     |

## Important Disclaimer
> **Exact price prediction is highly uncertain and is explicitly NOT offered.**
> The system only provides an *expected range* and *trend direction* to assist
> procurement timing decisions — the MSME owner makes the final call.

## Limitations
- External factors (government MSP changes, drought, festivals) are not modelled.
- Price data before 30 days produces MEDIUM confidence signals.
- Real supplier-specific price variance should be calibrated against actual invoices.
