with tb_daily as (
    SELECT date(substr(DtCriacao,0, 11)) AS DtDia,
       count(DISTINCT IdCliente) AS DAU,
       idCliente

    FROM transacoes
    GROUP BY 1
    ORDER BY DtDia
),
tb_distinct_day as(
select 
DISTINCT DtDia as dtRef
from tb_daily
)
select t1.dtref,count(DISTINCT idCliente) as MAU,count(DISTINCT t2.dtDia)
from tb_distinct_day as t1 
left join tb_daily as t2
on t2.DtDia <= t1.dtRef
and julianday(t1.dtRef) - julianday(t2.DtDia) < 28
group by t1.dtRef
order by t1.dtRef asc
limit 10000;