SELECT coin, DATE_TRUNC('month', date) AS month, AVG(price) AS avg_price
FROM coin_data
GROUP BY coin, month
ORDER BY coin, month