from datetime import datetime
import re

import sqlalchemy as sa
import sqlalchemy.orm as orm


DB_URL = 'sqlite:///my_blog.db'
DB_ECHO = True
engine = sa.create_engine(url=DB_URL, echo=DB_ECHO)
Base = orm.declarative_base(bind=engine)
session_factory = orm.sessionmaker(bind=engine)
Session = orm.scoped_session(session_factory)


class User(Base):
    __tablename__ = 'users'
    id = sa.Column(sa.Integer, primary_key=True)
    username = sa.Column(sa.String(30), unique=True)
    fullname = sa.Column(sa.String(100))
    is_admin = sa.Column(sa.Boolean, nullable=False, default=False)
    posts = orm.relationship('Post', backref='author')

    def __str__(self):
        return (
            f'{self.__class__.__name__}('
            f'id={self.id}, '
            f'username={self.username!r}, '
            f'fullname={self.fullname}, '
            f'is admin={self.is_admin})'
        )

    def __repr__(self):
        return str(self)


post_tag = sa.Table('post_tag', Base.metadata,
                    sa.Column('post_id', sa.Integer, sa.ForeignKey('posts.id'), primary_key=True),
                    sa.Column('tag_id', sa.Integer, sa.ForeignKey('tags.id'), primary_key=True)
                    )


class Post(Base):
    __tablename__ = 'posts'
    id = sa.Column(sa.Integer, primary_key=True)
    title = sa.Column(sa.String(150))
    slug = sa.Column(sa.String(150), unique=True)
    body = sa.Column(sa.Text)
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))

    def __init__(self, *args, **kwargs):
        super(Post, self).__init__(*args, **kwargs)
        if not self.slug:
            self.generate_slug()

    def __str__(self):
        return f'<Post id: {self.id}, title: {self.title}, slug: {self.slug}>'

    def __repr__(self):
        return str(self)

    def generate_slug(self):
        if self.title:
            pattern = r'[^\w+]'
            self.slug = re.sub(pattern, '-', self.title)


class Tag(Base):
    __tablename__ = 'tags'
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(100), unique=True)
    post = orm.relationship('Post', secondary=post_tag, backref='tags')

    def __str__(self):
        return f'tag id: {self.id} name: {self.name}'

    def __repr__(self):
        return str(self)


def create_user(username: str, fullname: str) -> User:
    user = User(username=username, fullname=fullname)
    Session.add(user)
    Session.commit()
    return user


def create_post(title: str, body: str, user_id: int) -> Post:
    post = Post(title=title, body=body, user_id=user_id)
    Session.add(post)
    Session.commit()
    return post


def create_tag(name: str) -> Tag:
    tag = Tag(name=name)
    Session.add(tag)
    Session.commit()
    return tag


def query_all_users() -> list[User]:
    return Session.query(User).all()


def main():
    Base.metadata.create_all(bind=engine)
    user1 = create_user(username='vanya', fullname='Ivanov Ivan')
    user2 = create_user(username='qwerty', fullname='Samuel L. Jackson')
    user3 = create_user(username='zorro', fullname='Peter Jackson')

    create_post(title='Post 1', body='Body of post 1', user_id=user2.id)
    create_post(title='Post 2', body='Body of post 2', user_id=user2.id)
    create_post(title='Post 3', body='Body of post 3', user_id=user1.id)
    create_post(title='Post 4', body='Body of post 4', user_id=user3.id)
    create_post(title='Post 5', body='Body of post 5', user_id=user2.id)

    create_tag(name='tag1')
    create_tag(name='tag2')

    Session.execute(post_tag.insert().values([
        {'post_id': 1, 'tag_id': 1},
        {'post_id': 2, 'tag_id': 1},
        {'post_id': 2, 'tag_id': 2},
        {'post_id': 3, 'tag_id': 2},
        {'post_id': 4, 'tag_id': 1},

    ]))
    Session.commit()

    users = query_all_users()
    print('#' * 100)
    print('Users:', users)
    print('#' * 100)
    print(f'Posts of user {user2.fullname}', user2.posts)

    Session.close()


if __name__ == '__main__':
    main()
