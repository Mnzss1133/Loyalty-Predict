SELECT dtRef,
       Categoria,
       cluster,
       count(*) as qtd_cliente

FROM life_cycle

WHERE Categoria <> '05-ZUMBI'

group by dtRef, Categoria
order by dtRef, Categoria