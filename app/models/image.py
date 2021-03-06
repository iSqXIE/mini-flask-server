from sqlalchemy import Column, Integer, String, SmallInteger

from app.models.base import Base


class Image(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    _url = Column('url', String(255), nullable=False)
    _from = Column('from', SmallInteger, default=1)  # 1表示存在本地, 2表示存在网络上

    def keys(self):
        self.hide('id', '_url', '_from').append('url')
        return self.fields

    @property
    def url(self):
        return self.get_url(self._url)

    @staticmethod
    def get_img_by_id(id):
        return Image.query.filter_by(id=id).first_or_404()
