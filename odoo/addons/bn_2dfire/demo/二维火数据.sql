select sum(fee) from bn_2dfire_order_orderlist where "orderId" in (
select "orderId"  from  bn_2dfire_order_ordervo where "innerCode" like '20200508%'
and "orderId"  in ( select ordersn from bn_2dfire_order where store_code='131360'))

select "orderId" ,count(*)  from  bn_2dfire_order_ordervo where "innerCode" like '20200508%'
and "orderId"  in ( select ordersn from bn_2dfire_order where store_code='131360')
group by "orderId"


delete  from bn_2dfire_order_orderlist where "orderId" in (
select "orderId"  from  bn_2dfire_order_ordervo where "innerCode" like '20200509%'
and "orderId"  in ( select ordersn from bn_2dfire_order where store_code='131360'))



delete  from bn_2dfire_order_ordervo where "orderId" in (
select "orderId"  from  bn_2dfire_order_ordervo where "innerCode" like '20200509%'
and "orderId"  in ( select ordersn from bn_2dfire_order where store_code='131360'))

select * from bn_2dfire_order order by 
where id=105160

select * from bn_2dfire_order_ordervo where  orderids not in (select id  from bn_2dfire_order)

delete  from bn_2dfire_order where id not in (select orderids from bn_2dfire_order_ordervo) and   to_char(write_date+ interval '8 H','yyyy-mm-dd')='2020-05-11'






delete  from bn_2dfire_order where to_char(write_date+ interval '8 H','yyyy-mm-dd')='2020-05-11'

select *  from  bn_2dfire_order_ordervo where "innerCode" like '20200509%'
and "orderId"

select * from bn_2dfire_order_ordervo  where "orderId" in   (
select ordersn from bn_2dfire_order where store_code='131360' and  to_char(write_date+ interval '8 H','yyyy-mm-dd')='2020-05-11')

select * from bn_2dfire_branchs


select *   from bn_2dfire_order_orderlist where "orderId" in (
select "orderId"  from  bn_2dfire_order_ordervo where "innerCode" like '20200511%'
and "orderId"  in ( select ordersn from bn_2dfire_order where store_code='131360'))


      select sum(fee)  FROM bn_2dfire_order_orderlist
                        where "orderId" in (
                        select "orderId"  from  bn_2dfire_order_ordervo where "innerCode" like '20200511%'
                        and "orderId"  in ( select ordersn from bn_2dfire_order where store_code='131360'))


