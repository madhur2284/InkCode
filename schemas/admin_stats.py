from pydantic import BaseModel

class UserStat(BaseModel):
    total_users: int
    total_active_user: int
    new_user_in_last_one_day: int
    new_user_in_last_one_month: int

class PostStat(BaseModel):
    total_posts: int
    total_active_post: int
    total_inactive_post: int
    new_post_in_last_one_day: int
    new_post_in_last_one_month: int

class StatResponse(BaseModel):
    user: UserStat
    post: PostStat
    total_comments: int
    model_config= {"from_attributes": True}