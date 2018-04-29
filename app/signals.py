from blinker import Namespace
signals=Namespace()



"""
通过信号来更新,数据库字段
"""

# user_follow=signals.signal('user_follow')
# user_unfollow=signals.signal('user_unfollow')

question_answer_add = signals.signal('question_answer_add')
question_follow = signals.signal('question_follow')
question_unfollow = signals.signal('question_unfollow')
question_comment_add = signals.signal('question_comment_add')
question_comment_delete = signals.signal('question_comment_delete')

answer_comment_add = signals.signal('answer_comment_add')
answer_comment_delete = signals.signal('answer_comment_delete')
answer_voteup = signals.signal('answer_voteup')
answer_cancel_vote = signals.signal('answer_cancel_vote')

comment_voteup = signals.signal('comment_voteup')
comment_cancel_vote = signals.signal('comment_cancel_vote')

favorite_answer_add = signals.signal('favorite_answer_add')
favorite_answer_delete = signals.signal('favorite_answer_delete')
favorite_question_add=signals.signal('favorite_question_add')
favorite_question_delete=signals.signal('favorite_question_delete')
favorite_post_add=signals.signal('favorite_post_add')
favorite_post_delete=signals.signal('favorite_post_delete')
favorite_comment_add=signals.signal('favorite_comment_add')
favorite_comment_delete=signals.signal('favorite_comment_delete')
favorite_follow = signals.signal('favorite_follow')
favorite_unfollow = signals.signal('favorite_unfollow')

post_comment_add = signals.signal('post_comment_add')
post_comment_delete = signals.signal('post_comment_delete')
post_voteup = signals.signal('post_voteup')
post_cancel_vote = signals.signal('post_cancel_vote')
post_tag_add=signals.signal('post_tag_add')

topic_question_add=signals.signal('topic_question_add')
topic_question_delete=signals.signal('topic_question_delete')