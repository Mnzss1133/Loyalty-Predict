--curiosa -> idade < 7 
--fiel -> recencia < 7 e recencia anterios <15
--turista -> recencia <=14
--desencatado -> 14 e recencia <=28
--zumbi ->recencia >=28
--reconquistado < 7 e 14 <= recencia anterior <=28
--reborn -> recencia < 7 e recencia anterior >28
with tb_daily as (
    select DISTINCT idCliente ,
    substr(DtCriacao,0,11) as DtDia  
    from transacoes 
    where DtCriacao<'{date}'
),
tb_idade as (
    select idCliente, 
    --min(dtDia) as dtPrimeiraTransacao,
    cast(max(julianday('{date}')-julianday(DtDia)) as int) as qtdDeDiasPrimeiraTransacao,
   -- max(dtDia) as dtUltimaTransacao,
    cast(min(julianday('{date}')-julianday(DtDia)) as int) as qtdDeDiasUltimaTransacao
    from tb_daily
    group by idCliente
),
tb_rn as (
    select *, row_number() OVER (PARTITION BY idCliente ORDER BY DtDia DESC) as rnDia
    from tb_daily
),
tb_penultima_ativacao as (
    select *,
    cast(julianday('{date}')-julianday(DtDia) as INT) as qtdPenultimaTransacao 
    from tb_rn where rnDia = 2
),

tb_lifecycle as (
select t1.*,t2.qtdPenultimaTransacao,
case 
    when qtdDeDiasPrimeiraTransacao<=7 THEN '01-CURIOSO'
    when qtdDeDiasUltimaTransacao<=7 AND qtdPenultimaTransacao - qtdDeDiasUltimaTransacao <= 14 THEN '02-FIEL'
    when qtdDeDiasUltimaTransacao BETWEEN 8 and 14 THEN '03-TURISTA'
    when qtdDeDiasUltimaTransacao BETWEEN 15 and 27  THEN '04-DESENCATADA'
    when qtdDeDiasUltimaTransacao > 28 then '05-ZUMBI'
    WHEN qtdDeDiasUltimaTransacao <=7 AND qtdPenultimaTransacao - qtdDeDiasUltimaTransacao BETWEEN 15 and 27 THEN '02-RECONQUISTADO'
    WHEN qtdDeDiasUltimaTransacao <=7 AND qtdPenultimaTransacao - qtdDeDiasUltimaTransacao > 28 THEN '02-REBORN'
    END as descLifeCycle
from tb_idade as t1
left join tb_penultima_ativacao as t2
on t1.idCliente = t2.idCliente
),
tb_freq_valor AS (
    SELECT
        idCliente,
        count(DISTINCT substr(DtCriacao, 1, 10)) AS qtdeFrequencia,
        sum(
            CASE
                WHEN QtdePontos > 0 THEN QtdePontos
                ELSE 0
            END
        ) AS qtdePontosPos,
        sum(abs(QtdePontos)) AS qtdPontosAbs
    FROM transacoes
    WHERE DtCriacao < '{date}'
      AND DtCriacao >= date('{date}', '-28 days')
    GROUP BY idCliente
    ORDER BY qtdeFrequencia DESC
),

tb_cluster AS (
    SELECT
        *,
        CASE
            WHEN qtdeFrequencia <= 10 AND qtdePontosPos >= 1500 THEN '12-HYPER'
            WHEN qtdeFrequencia > 10 AND qtdePontosPos >= 1500 THEN '22-EFICIENTE'
            WHEN qtdeFrequencia <= 10 AND qtdePontosPos >= 750 THEN '11-INDECISO'
            WHEN qtdeFrequencia > 10 AND qtdePontosPos >= 750 THEN '21-ESFORÇADO'
            WHEN qtdeFrequencia < 5 THEN '00-LURKER'
            WHEN qtdeFrequencia <= 10 THEN '01-PREGUIÇOSO'
            WHEN qtdeFrequencia > 10 THEN '20-POTENCIAL'
        END AS cluster
    FROM tb_freq_valor
)

select date('{date}','-1 day') as dtRef,t1.*,t2.qtdeFrequencia,t2.qtdePontosPos,t2.cluster
from tb_lifecycle as t1 
left join tb_cluster as t2
on t1.idCliente = t2.idCliente;