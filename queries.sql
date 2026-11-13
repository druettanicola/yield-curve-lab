-- Le tue prime query SQL sul database dei rendimenti.
-- Tabella: yields(date, maturity, years, yield_pct)

-- 1) SELECT + WHERE + ORDER BY: la curva dell'ultimo giorno disponibile
SELECT maturity, years, yield_pct
FROM yields
WHERE date = (SELECT MAX(date) FROM yields)
ORDER BY years;

-- 2) Aggregazione (GROUP BY): rendimento medio del 10 anni per ogni anno
SELECT substr(date, 1, 4) AS anno,
       ROUND(AVG(yield_pct), 2) AS rendimento_medio_10y
FROM yields
WHERE maturity = '10 Yr'
GROUP BY anno
ORDER BY anno;

-- 3) Self-JOIN: lo spread 10 anni - 2 anni per ogni giorno.
--    Se è negativo la curva è "invertita": storicamente un segnale di recessione.
SELECT a.date,
       ROUND(a.yield_pct - b.yield_pct, 2) AS spread_10y_2y
FROM yields a
JOIN yields b ON a.date = b.date
WHERE a.maturity = '10 Yr' AND b.maturity = '2 Yr'
ORDER BY a.date;

-- 4) Giorni con curva invertita, raggruppati per anno
SELECT substr(a.date, 1, 4) AS anno,
       COUNT(*) AS giorni_invertita
FROM yields a
JOIN yields b ON a.date = b.date
WHERE a.maturity = '10 Yr' AND b.maturity = '2 Yr'
  AND a.yield_pct < b.yield_pct
GROUP BY anno
ORDER BY anno;

-- 5) Funzione finestra (window function): variazione del 10 anni rispetto al giorno prima
SELECT date,
       yield_pct,
       ROUND(yield_pct - LAG(yield_pct) OVER (ORDER BY date), 2) AS variazione_giornaliera
FROM yields
WHERE maturity = '10 Yr'
ORDER BY date DESC
LIMIT 20;
