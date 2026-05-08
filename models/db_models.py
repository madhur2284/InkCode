from pydantic import Field, EmailStr
from typing import Optional, Literal
from sqlalchemy import Integer, String, Column, ForeignKey, Text, DateTime, func, Boolean
from sqlalchemy.orm import relationship
from database import Base



class User(Base):
    __tablename__="users"
    id = Column(Integer, autoincrement=True, nullable=False, primary_key=True)
    username = Column(String, nullable=False, unique=True)
    slug = Column(String, nullable=False, unique=True, index=True)
    email = Column(String, nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)
    bio = Column(String, nullable=True)
    role = Column(String, default="user", nullable=False) # "user" or "admin"
    avatar_url = Column(String, nullable=False, server_default="https://res.cloudinary.com/dvvtmttgl/image/upload/v1776195414/user_zffa2m.png")
    avatar_post_id = Column(String, nullable=True)
    token_version = Column(Integer, server_default='1', nullable=False)
    is_active = Column(Boolean, nullable=False, server_default='True')
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    posts = relationship("Post", back_populates="author")
    comments = relationship("Comment", back_populates="author")
    reactions = relationship("Reaction", back_populates="user")
    bookmarks = relationship("Bookmark", back_populates="user")
    followers = relationship("Follow", foreign_keys="Follow.following_id", back_populates="following")
    followings = relationship("Follow", foreign_keys="Follow.follower_id", back_populates="follower")
    comment_reaction = relationship("CommentReaction", back_populates="user")



class Post(Base):
    __tablename__="posts"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    title = Column(Text, nullable=False)
    slug = Column(Text, unique=True, nullable=False, index=True)
    author_id = Column(Integer, ForeignKey("users.id"), index=True)
    content = Column(Text, nullable=False)
    status= Column(String, nullable=False, default="draft") #"draft" or "published" or "archived"
    reading_time = Column(Integer, nullable=False, server_default='0')
    is_active = Column(Boolean, nullable=False, server_default='True')
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    published_at = Column(DateTime(timezone=True), nullable=True)
    view_count = Column(Integer, nullable=False, server_default='0')

    author = relationship("User", back_populates="posts")
    tags = relationship("PostTag", back_populates="post")
    comments = relationship("Comment", back_populates="post")
    reactions = relationship("Reaction", back_populates="post")
    bookmarks = relationship("Bookmark", back_populates="post")


class Tag(Base):
    __tablename__="tags"
    id = Column(Integer, autoincrement=True, nullable=False, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    slug = Column(String, nullable=False, unique=True, index=True)
    description = Column(Text, nullable=False)

    posts = relationship("PostTag", back_populates="tag")


class PostTag(Base):
    __tablename__="post_tags"
    tag_id = Column(Integer, ForeignKey("tags.id"), primary_key=True)
    post_id = Column(Integer, ForeignKey("posts.id"), primary_key=True)
    
    post = relationship("Post", back_populates="tags")
    tag = relationship("Tag", back_populates="posts")


class Reaction(Base):
    __tablename__="reactions"
    post_id = Column(Integer, ForeignKey("posts.id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    type = Column(String, nullable=False) #"like" or "dislike"

    post = relationship("Post", back_populates="reactions")
    user = relationship("User", back_populates="reactions")


class Comment(Base):
    __tablename__="comments"
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    content = Column(Text, nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id"), index=True)
    author_id = Column(Integer, ForeignKey("users.id"))
    parent_id = Column(Integer, ForeignKey("comments.id"), nullable=True)
    is_active = Column(Boolean, server_default='True', nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    edited_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    post = relationship("Post", back_populates="comments")
    author = relationship("User", back_populates="comments")
    replies = relationship("Comment", back_populates="parent")
    parent = relationship("Comment", back_populates="replies", remote_side=[id])
    reactions = relationship("CommentReaction", back_populates="comment")


class CommentReaction(Base):
    __tablename__="comment_reactions"
    comment_id = Column(Integer, ForeignKey("comments.id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    type = Column(String, nullable=False) #"like" or "dislike"

    comment = relationship("Comment", back_populates="reactions")
    user = relationship("User", back_populates="comment_reaction")


class Bookmark(Base):
    __tablename__="bookmarks"
    post_id = Column(Integer, ForeignKey("posts.id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)

    post = relationship("Post", back_populates="bookmarks")
    user =relationship("User", back_populates="bookmarks")


class Follow(Base):
    __tablename__ = "follows"
    follower_id  = Column(Integer, ForeignKey("users.id"), primary_key=True)
    following_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    created_at   = Column(DateTime(timezone=True), server_default=func.now())

    follower = relationship("User", foreign_keys=[follower_id], back_populates="followings")
    following = relationship("User", foreign_keys=[following_id], back_populates="followers")









