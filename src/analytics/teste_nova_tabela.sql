--select * from abt_fiel where dtRef >='2026-02-01';


SELECT dtRef, COUNT(*) as qtd FROM abt_fiel GROUP BY dtRef ORDER BY dtRef;