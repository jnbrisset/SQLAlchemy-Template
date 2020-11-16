from sqlalchemy import create_engine, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date, Table, Text
from sqlalchemy.orm import sessionmaker, relationship, aliased
from contextlib import contextmanager


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


# Replace ":memory:" with the path to the database
engine = create_engine("sqlite:///:memory:", echo=False)

Base = declarative_base()

# Base type
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    nickname = Column(String)

    addresses = relationship("Address", back_populates='user',
                             cascade="all, delete, delete-orphan")
    posts = relationship("BlogPost", back_populates="author", lazy="dynamic")

    def __repr__(self):
        return "<User(name='%s', fullname='%s', nickname='%s')>" % (self.name, self.fullname, self.nickname)


# One to many relationship
class Address(Base):
    __tablename__ = 'addresses'
    id = Column(Integer, primary_key=True)
    email_address = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))

    user = relationship("User", back_populates="addresses")

    def __repr__(self):
        return "<Address(email_address='%s'>" % self.email_address


# Many-to-many relationship
# Association table (un-mapped table construct)
post_keywords = Table('post_keywords', Base.metadata,
                      Column('post_id', ForeignKey('posts.id'), primary_key=True),
                      Column('keyword_id', ForeignKey('keywords.id'), primary_key=True)
                      )


class BlogPost(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    headline = Column(String(255), nullable=False)
    body = Column(Text)
    date = Column(Date)
    author = relationship(User, back_populates="posts")

    keywords = relationship('Keyword',
                            secondary=post_keywords,
                            back_populates='posts')

    def __init__(self, headline, body, author):
        self.author = author
        self.headline = headline
        self.body = body

    def __repr__(self):
        return "BlogPost(%r, %r, %r)" % (self.headline, self.body, self.author)


class Keyword(Base):
    __tablename__ = 'keywords'

    id = Column(Integer, primary_key=True)
    keyword = Column(String(50), nullable=False, unique=True)
    posts = relationship('BlogPost',
                         secondary=post_keywords,
                         back_populates='keywords')

    def __init__(self, keyword):
        self.keyword = keyword


Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)

# The most comprehensive approach, recommended for more substantial applications, will try to keep the details of
# session, transaction and exception management as far as possible from the details of the program doing its work.
# As a general rule, keep the lifecycle of the session separate and external from functions and objects that access
# and/or manipulate database data. This will greatly help with achieving a predictable and consistent transactional
# scope.
# All the following transactions are all under one scope for simplicity, but each scope should be kept short to what,
# in context, we are trying to achieve.
with session_scope() as session:
    # A few rows of data being created, and different ways to add them.
    ed_user = User(name='ed', fullname='Ed Jones', nickname='edsnickname')
    jack = User(name='jack', fullname='Jack Bean', nickname='Jake')
    jack.addresses = [
        Address(email_address='jack@google.com'),
        Address(email_address='j25@yahoo.com')
    ]
    session.add(ed_user)
    session.add(jack)

    session.add_all([
        User(name='wendy', fullname='Wendy Williams', nickname='windy'),
        User(name='mary', fullname='Mary Contrary', nickname='mary'),
        User(name='fred', fullname='Fred Flintstone', nickname='freddy')])

    # session.commit()

    # session.delete(jack)
    session.delete(session.query(User).filter_by(name='fred').one())

    # We can roll back to the start of the session if changes have been made without committing
    # session.rollback()

    # Querying
    for instance in session.query(User).order_by(User.name):
        print(instance.name, instance.fullname)

    for instance in session.query(User.name, User.fullname):
        print(instance.fullname, instance.name)

    print("filter_by()")
    print(session.query(User).filter_by(name='ed').all())

    # All column operators: https://docs.sqlalchemy.org/en/13/core/sqlelement.html#sqlalchemy.sql.operators.ColumnOperators
    print(" == ")
    print(session.query(User).filter(User.name == 'ed').all())

    '''
    Returning Lists and Scalars
    Query.all() -> returns a list
    Query.first() -> applies a limit of one and returns the first result as a scalar
    Query.one() -> fully fetches all rows, and if not exactly one object identity or composite row is present in the 
    result, raises an error.
    Query.one_or_none() -> similar to Query.one(), except that if no results are found, it doesn’t raise an error; it just 
    returns None.
    Query.scalar() -> invokes the Query.one() method, and upon success returns the first column of the row
    Query.count() -> How many rows the SQL statement would return.
    '''

    # JOIN query
    for u, a in session.query(User, Address). \
            filter(User.id == Address.user_id). \
            filter(Address.email_address == 'jack@google.com'). \
            all():
        print(u)
        print(a)

    print("JOIN")
    print(session.query(User).join(Address). \
          filter(Address.email_address == 'jack@google.com'). \
          all())

    # When querying across multiple tables, if the same table needs to be referenced more than once, SQL typically
    # requires that the table be aliased with another name, so that it can be distinguished against other occurrences of
    # that table.
    adalias1 = aliased(Address)
    adalias2 = aliased(Address)
    for username, email1, email2, in \
            session.query(User.name, adalias1.email_address, adalias2.email_address). \
                    join(User.addresses.of_type(adalias1)). \
                    join(User.addresses.of_type(adalias2)). \
                    filter(adalias1.email_address == 'jack@google.com'). \
                    filter(adalias2.email_address == 'j25@yahoo.com'):
        print(username, email1, email2)

    post = BlogPost("Wendy's Blog Post",
                    "This is a test",
                    session.query(User).filter_by(name='wendy').one())
    session.add(post)

    post.keywords.append(Keyword('wendy'))
    post.keywords.append(Keyword('firstpost'))

    print(session.query(BlogPost).filter(BlogPost.keywords.any(keyword='firstpost')).all())
    print(session.query(BlogPost).count())
