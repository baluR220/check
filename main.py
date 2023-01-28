from re import compile
from traceback import format_exception_only as f_exc

from sqlalchemy.engine import URL
from sqlalchemy import (
    create_engine, Column, Integer, Float, String, ForeignKey, DateTime,
    select, func
)
from sqlalchemy.orm import Session, declarative_base, relationship
from yaml import safe_load


DATETIME = 'datetime'
SHOP_NAME = 'shop_name'
SHOP_ADDR = 'shop_addr'
GOODS = 'goods'
FULL_NAME = 'full_name'
SHORT_NAME = 'short_name'
PRICE = 'price'
QUANTITY = 'quantity'
COST = 'cost'
TOTAL = 'total'
GOODS_COUNT = 5


date_re = compile('^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}$')
url = URL.create("sqlite", database="check_db")
engine = create_engine(url)
Base = declarative_base()
in_file = "data.yml"


class ShortName(Base):
    __tablename__ = "short_names"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    
    def __repr__(self):
        return(f"ShortName(id={self.id!r}, name={self.name!r})")


class Good(Base):
    __tablename__ = "goods"
    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String, nullable=False)
    short_name_id = Column(ForeignKey("short_names.id"), nullable=False)
    price = Column(Float, nullable=False)
    quantity = Column(Float, nullable=False)
    cost = Column(Float, nullable=False)

    def __repr__(self):
        return(f"Good(id={self.id!r}, full_name={self.full_name!r})")


class Shop(Base):
    __tablename__ = "shops"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    addr = Column(String, nullable=False)

    def __repr__(self):
        return(f"Shop(id={self.id!r}, name={self.name!r})")
    

class Check(Base):
    __tablename__ = "checks"
    id = Column(Integer, primary_key=True, autoincrement=True)
    datetime = Column(DateTime, nullable=False)
    shop_id = Column(ForeignKey("shops.id"), nullable=False)
    goods_hash = Column(String, nullable=False)
    total = Column(Float, nullable=False)

    def __repr__(self):
        return(f"Check(id={self.id!r}, datetime={self.datetime!r})")


class ShopList(Base):
    __tablename__ = "shopping_list"
    id = Column(Integer, primary_key=True, autoincrement=True)
    check_id = Column(ForeignKey("checks.id"), nullable=False)
    good_1 = Column(ForeignKey("goods.id"), nullable=False)
    good_2 = Column(ForeignKey("goods.id"))
    good_3 = Column(ForeignKey("goods.id"))
    good_4 = Column(ForeignKey("goods.id"))
    good_5 = Column(ForeignKey("goods.id"))

    def __repr__(self):
        return(f"Shoplist(id={self.id!r}, check_id={self.check_id!r})")


#Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)


def show_msg(*args, **kwargs):
    print(*args, **kwargs)


def check_goods(goods, date, count):
    err_msg = ''
    for i in goods:
        try:
            full_name = i[FULL_NAME]
            if not full_name:
                err_msg = f'Empty {FULL_NAME} under date {date}'
                break
            short_name = i[SHORT_NAME]
            if not short_name:
                err_msg = f'Empty {SHORT_NAME} under date {date}'
                break
            price = i[PRICE]
            if not price:
                err_msg = f'Empty {PRICE} under date {date}'
                break
            t = type(price)
            if not (t == type(float()) or t == type(int())):
                err_msg = f'Number is expected in {PRICE} under date {date}'
                break
            quan = i[QUANTITY]
            if not quan:
                err_msg = f'Empty {QUANTITY} under date {date}'
                break
            t = type(quan)
            if not (t == type(float()) or t == type(int())):
                err_msg = f'Number is expected in {QUANTITY} under date {date}'
                break
            cost = i[COST]
            if not cost:
                err_msg = f'Empty {COST} under date {date}'
                break
            t = type(cost)
            if not (t == type(float()) or t == type(int())):
                err_msg = f'Number is expected in {COST} under date {date}'
                break
        except KeyError as e:
            err_msg = f'{f_exc(e)[-1].strip()} not found in {count} check'
    return(err_msg)


def check_all(in_file):
    err_msg = ''
    count = 1
    with open(in_file) as in_f:
        data = safe_load(in_f)
        for i in data:
            try:
                date = i[DATETIME]
                if not date_re.match(str(date)):
                    err_msg = f'{date} is not matching pattern: \
                        YYYY-MM-DD HH:MM:SS'
                    break
                shop_name = i[SHOP_NAME]
                if not shop_name:
                    err_msg = f'Empty {SHOP_NAME} under date {date}'
                    break
                shop_addr = i[SHOP_ADDR]
                if not shop_name:
                    err_msg = f'Empty {SHOP_ADDR} under date {date}'
                    break
                goods = i[GOODS]
                if not goods:
                    err_msg = f'Empty {GOODS} under date {date}'
                    break
                err_msg = check_goods(goods, date, count)
                if err_msg:
                    break
                total = i[TOTAL]
                if not total:
                    err_msg = f'Empty {TOTAL} under date {date}'
                    break
                t = type(total)
                if not (t == type(float()) or t == type(int())):
                    err_msg = f'Number is expected in {TOTAL} under date {date}'
                    break

                count += 1
            except KeyError as e:
                err_msg = f'{f_exc(e)[-1].strip()} not found in {count} check'
        return((err_msg, data) if not err_msg else (err_msg, []))


err_msg, data = check_all(in_file)
if err_msg:
    show_msg(err_msg)
else:
    with Session(engine) as session:
        for i in data:
            good_ids = []
            for n in i[GOODS]:
                short_name_id = session.scalar(
                    select(ShortName.id).where(
                        func.lower(ShortName.name)==func.lower(n[SHORT_NAME])
                    )
                )
                if not short_name_id:
                    session.add(ShortName(name=n[SHORT_NAME]))
                    session.commit()
                    short_name_id = session.scalar(
                        select(ShortName.id).where(
                            func.lower(ShortName.name)==func.lower(n[SHORT_NAME])
                        )
                    )
                good_id = session.scalar(
                    select(Good.id).where(
                        func.lower(Good.full_name)==func.lower(n[FULL_NAME]),
                        Good.short_name_id==short_name_id,
                        Good.price==n[PRICE], Good.quantity==n[QUANTITY],
                        Good.cost==n[COST],
                    )
                )
                if not good_id:
                    session.add(
                        Good(
                            full_name=n[FULL_NAME], short_name_id=short_name_id,
                            price=n[PRICE], quantity=n[QUANTITY],
                            cost=n[COST]
                        )
                    )
                    session.commit()
                    good_id = session.scalar(
                        select(Good.id).where(
                            func.lower(Good.full_name)==func.lower(n[FULL_NAME]),
                            Good.short_name_id==short_name_id,
                            Good.price==n[PRICE], Good.quantity==n[QUANTITY],
                            Good.cost==n[COST],
                        )
                    )
                good_ids.append(good_id)

            shop_id = session.scalar(
                select(Shop.id).where(
                    func.lower(Shop.name)==func.lower(i[SHOP_NAME]),
                    func.lower(Shop.addr)==func.lower(i[SHOP_ADDR])
                )
            )
            if not shop_id:
                session.add(Shop(name=i[SHOP_NAME], addr=i[SHOP_ADDR]))
                session.commit()
                shop_id = session.scalar(
                    select(Shop.id).where(
                        func.lower(Shop.name)==func.lower(i[SHOP_NAME]),
                        func.lower(Shop.addr)==func.lower(i[SHOP_ADDR])
                    )
                )
            goods_hash = ','.join([str(i) for i in sorted(good_ids)])
            check_id = session.scalar(
                select(Check.id).where(
                    Check.datetime==i[DATETIME],
                    Check.shop_id==shop_id,
                    Check.goods_hash==goods_hash,
                    Check.total==i[TOTAL],
                )
            )
            if not check_id:
                session.add(
                    Check(
                        datetime=i[DATETIME], shop_id=shop_id,
                        goods_hash=goods_hash,
                        total=i[TOTAL],
                    )
                )
                session.commit()
                check_id = session.scalar(
                    select(Check.id).where(
                        Check.datetime==i[DATETIME],
                        Check.shop_id==shop_id,
                        Check.goods_hash==goods_hash,
                        Check.total==i[TOTAL],
                    )
                )
            else:
                #show_msg('similar check found, ignoring')
                continue
            shop_list_ids = session.scalars(
                select(ShopList.id).where(ShopList.check_id==check_id)
            ).all()
            if shop_list_ids:
                db_goods = []
                for i in shop_list_ids:
                    db_goods.append(i.good_1)
                    if i.good_2:
                        db_goods.append(i.good_2)
                    if i.good_3:
                        db_goods.append(i.good_3)
                    if i.good_4:
                        db_goods.append(i.good_4)
                    if i.good_5:    
                        db_goods.append(i.good_5)
                if sorted(db_goods) == sorted(good_ids):
                    continue
            count = len(good_ids) // GOODS_COUNT
            if len(good_ids) % GOODS_COUNT != 0:
                count += 1
            for i in range(count):
                session.add(
                    ShopList(
                        check_id=check_id,
                        good_1=good_ids[0],
                        good_2=good_ids[1] if len(good_ids) >= 2 else None,
                        good_3=good_ids[2] if len(good_ids) >= 3 else None,
                        good_4=good_ids[3] if len(good_ids) >= 4 else None,
                        good_5=good_ids[4] if len(good_ids) >= 5 else None,
                    )
                )
                count -= 1
                if count:
                    good_ids = good_ids[GOODS_COUNT:]
            session.commit()        
            
        for i in session.scalars(select(Check)):
            show_msg(i)
        for i in session.scalars(select(ShortName)):
            show_msg(i)
        for i in session.scalars(select(Shop)):
            show_msg(i)
        for i in session.scalars(select(Good)):
            show_msg(i)
        for i in session.scalars(select(ShopList)):
            show_msg(i)
        
