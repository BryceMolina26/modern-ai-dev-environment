SELECT
    risk_segment,
    SUM(debt_amount) AS total_debt,
    SUM(recovered_amount) AS total_recovered,
    ROUND(SUM(recovered_amount) / NULLIF(SUM(debt_amount), 0), 4) AS recovery_rate
FROM collections_portfolio
WHERE days_past_due > 30
GROUP BY risk_segment
ORDER BY total_debt DESC;