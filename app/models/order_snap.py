from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.dialects.mysql import FLOAT
from app.models.base import Base, db
from app.models.image import Image


class OrderSnap(Base):
    __tablename__ = 'order_snap'
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_no = Column(String(20), nullable=False)
    snap_name = Column(String(80), nullable=False)
    snap_img_id = Column(Integer, ForeignKey('image.id'), nullable=False)
    price = Column(FLOAT(precision=6, scale=2), nullable=False)
    property_name = Column(String(30))
    count = Column(Integer, nullable=False)
    product_id = Column(Integer, nullable=False)
    property_id = Column(Integer)

    def keys(self):
        self.hide('order_no').append('snap_img')
        return self.fields

    @property
    def snap_img(self):
        return Image.get_img_by_id(self.snap_img_id).url

    @staticmethod
    def add_order_snap(o_products, order_no):
        with db.auto_commit():
            for product in o_products:
                if product['property']:
                    price = product['property']['price']
                    property_name = product['property']['name']
                    property_id = product['property']['id']
                else:
                    price =product['price']
                    property_name = None
                    property_id = None
                count = product['qty']
                order_snap = OrderSnap()
                order_snap.order_no = order_no
                order_snap.snap_name = product['name']
                order_snap.snap_img_id = product['main_img_id']
                order_snap.price = price
                order_snap.property_name = property_name
                order_snap.count = count
                order_snap.product_id = product['id']
                order_snap.property_id = property_id
                db.session.add(order_snap)
