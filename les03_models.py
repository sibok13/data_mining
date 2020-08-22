from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship

Base = declarative_base()

tag_post = Table('tag_post', Base.metadata,
                 Column('post_id', Integer, ForeignKey('post.id')),
                 Column('tags_id', Integer, ForeignKey('tags.id'))
                 )


class Post(Base):
    __tablename__ = 'post'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, unique=False, nullable=False)
    url = Column(String, unique=True, nullable=False)
    writer_id = Column(Integer, ForeignKey('writer.id'), nullable=False)
    tags = relationship('Tags', secondary=tag_post, back_populates='post')

    def __init__(self, title: str, url: str, writer_id=None, tags=[]):
        self.title = title
        self.url = url
        self.writer_id = writer_id
        self.tags = tags


class Writer(Base):
    __tablename__ = 'writer'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=False, nullable=False)
    url = Column(String)

    def __init__(self, name, url):
        self.name = name
        self.url = url


class Tags(Base):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=False, nullable=False)
    url = Column(String, unique=True, nullable=False)
    post = relationship('Post', secondary=tag_post, back_populates='tags')

    def __init__(self, name, url):
        self.name = name
        self.url = url

class Hubs(Base):
    __tablename__ = 'hubs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=False, nullable=False)
    url = Column(String, unique=True, nullable=False)
#    post = relationship('Post', secondary=tag_post, back_populates='tags')

    def __init__(self, name, url):
        self.name = name
        self.url = url
