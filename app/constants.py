default_tags = ['Python', 'Java', 'C++', 'C#', 'F#', 'Ruby', 'Tornado', 'Flask', 'Django']
jobs = ['互联网/IT', '电子/微电子', '制造业', '广告/公关', '房地产', '贸易/出口/零售批发', '消费品',
        '交通运输', '教育培训', '艺术/休闲/运动', '农林牧副渔', '通讯', '电气/电力', '石化/石油',
        '服务/中介', '餐饮/酒店', '金融/银行', '文化/传媒/出版/印刷', '生物/医疗/保健', '咨询', '政府']

types = ['post', 'answer', 'question', 'topic']

topics = ['游戏', '运动', '互联网', '艺术', '阅读', '美食', '动漫', '汽车', '生活方式', '教育', '摄影', '历史', '文化', '旅行']

import enum


class MessageStatus(enum.Enum):
    read = 'read'
    unread = 'unread'


class MessageType(enum.Enum):
    standard = 'standard'
    system = 'system'


class DeleteStatus(enum.Enum):
    standard = 'standard'
    user_delete = 'user_delete'
    author_delete = 'author_delete'
