import sqlite3
import time
import logging
import os

class Records:
    """持久化游戏分数"""
    def __init__(self):
        # 打开数据库
        if os.path.exists('score_record.sqlite3'):
            uri = 'file:score_record.sqlite3?mode=rw'
        else:
            uri = 'file:score_record.sqlite3?mode=rwc'
        self.connection = sqlite3.connect(uri, uri=True)
        self.connection.execute('''create table if not exists scores (
            timestamp string,
            level bigint,
            score bigint
        );''')

    def __del__(self):
        # 需要提交并关闭链接才可以正常持久化
        self.connection.commit()
        self.connection.close()

    def highest_score(self):
        """从数据库中找到最大的分数"""
        itr = self.connection.execute('select ifnull(max(score), 0) from scores')
        scores = [v for v in itr]
        return max([int(v[0]) for v in scores] + [0])

    def record_new_entries(self, *args):
        """传入任意多的分数与其等级，即可记录"""
        for arg in args:
            ctime = time.strftime('%Y%m%d-%H:%M:%S')
            print('Recorded new score:', (ctime, ) + arg)
            self.connection.execute(
                '''insert into scores values (?, ?, ?)''',
                (ctime, ) + arg)

