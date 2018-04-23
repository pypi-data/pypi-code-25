# -*- coding: utf-8 -*-

from pywe_utils import to_text
from pywe_xml import pair_to_xml
from TimeConvert import TimeConvert as tc


class Reply(object):
    def text(self, touser=None, fromuser=None, content=None):
        """
        <xml>
            <ToUserName>< ![CDATA[toUser] ]></ToUserName>
            <FromUserName>< ![CDATA[fromUser] ]></FromUserName>
            <CreateTime>12345678</CreateTime>
            <MsgType>< ![CDATA[text] ]></MsgType>
            <Content>< ![CDATA[你好] ]></Content>
        </xml>
        """
        return pair_to_xml([
            ('ToUserName', touser),
            ('FromUserName', fromuser),
            ('CreateTime', tc.utc_timestamp()),
            ('MsgType', 'text'),
            ('Content', content)
        ])

    def image(self, touser=None, fromuser=None, media_id=None):
        """
        <xml>
            <ToUserName>< ![CDATA[toUser] ]></ToUserName>
            <FromUserName>< ![CDATA[fromUser] ]></FromUserName>
            <CreateTime>12345678</CreateTime>
            <MsgType>< ![CDATA[image] ]></MsgType>
            <Image>
                <MediaId>< ![CDATA[media_id] ]></MediaId>
            </Image>
        </xml>
        """
        return pair_to_xml([
            ('ToUserName', touser),
            ('FromUserName', fromuser),
            ('CreateTime', tc.utc_timestamp()),
            ('MsgType', 'image'),
            ('Image', [
                ('MediaId', media_id)
            ])
        ])

    def voice(self, touser=None, fromuser=None, media_id=None):
        """
        <xml>
            <ToUserName>< ![CDATA[toUser] ]></ToUserName>
            <FromUserName>< ![CDATA[fromUser] ]></FromUserName>
            <CreateTime>12345678</CreateTime>
            <MsgType>< ![CDATA[voice] ]></MsgType>
            <Voice>
                <MediaId>< ![CDATA[media_id] ]></MediaId>
            </Voice>
        </xml>
        """
        return pair_to_xml([
            ('ToUserName', touser),
            ('FromUserName', fromuser),
            ('CreateTime', tc.utc_timestamp()),
            ('MsgType', 'voice'),
            ('Voice', [
                ('MediaId', media_id)
            ])
        ])

    def video(self, touser=None, fromuser=None, media_id=None, title=None, description=None):
        """
        <xml>
            <ToUserName>< ![CDATA[toUser] ]></ToUserName>
            <FromUserName>< ![CDATA[fromUser] ]></FromUserName>
            <CreateTime>12345678</CreateTime>
            <MsgType>< ![CDATA[video] ]></MsgType>
            <Video>
                <MediaId>< ![CDATA[media_id] ]></MediaId>
                <Title>< ![CDATA[title] ]></Title>
                <Description>< ![CDATA[description] ]></Description>
            </Video>
        </xml>
        """
        return pair_to_xml([
            ('ToUserName', touser),
            ('FromUserName', fromuser),
            ('CreateTime', tc.utc_timestamp()),
            ('MsgType', 'video'),
            ('Video', [
                ('MediaId', media_id),
                ('Title', title),
                ('Description', description)
            ])
        ])

    def music(self, touser=None, fromuser=None, title=None, description=None, music_url=None, hq_music_url=None, media_id=None):
        """
        <xml>
            <ToUserName>< ![CDATA[toUser] ]></ToUserName>
            <FromUserName>< ![CDATA[fromUser] ]></FromUserName>
            <CreateTime>12345678</CreateTime>
            <MsgType>< ![CDATA[music] ]></MsgType>
            <Music>
                <Title>< ![CDATA[TITLE] ]></Title>
                <Description>< ![CDATA[DESCRIPTION] ]></Description>
                <MusicUrl>< ![CDATA[MUSIC_Url] ]></MusicUrl>
                <HQMusicUrl>< ![CDATA[HQ_MUSIC_Url] ]></HQMusicUrl>
                <ThumbMediaId>< ![CDATA[media_id] ]></ThumbMediaId>
            </Music>
        </xml>
        """
        return pair_to_xml([
            ('ToUserName', touser),
            ('FromUserName', fromuser),
            ('CreateTime', tc.utc_timestamp()),
            ('MsgType', 'music'),
            ('Music', [
                ('Title', title),
                ('Description', description),
                ('MusicUrl', music_url),
                ('HQMusicUrl', hq_music_url),
                ('ThumbMediaId', media_id),
            ])
        ])

    def news(self, touser=None, fromuser=None, items=[]):
        """
        <xml>
            <ToUserName>< ![CDATA[toUser] ]></ToUserName>
            <FromUserName>< ![CDATA[fromUser] ]></FromUserName>
            <CreateTime>12345678</CreateTime>
            <MsgType>< ![CDATA[news] ]></MsgType>
            <ArticleCount>2</ArticleCount>
            <Articles>
                <item>
                    <Title>< ![CDATA[title1] ]></Title>
                    <Description>< ![CDATA[description1] ]></Description>
                    <PicUrl>< ![CDATA[picurl] ]></PicUrl>
                    <Url>< ![CDATA[url] ]></Url>
                </item>
                <item>
                    <Title>< ![CDATA[title] ]></Title>
                    <Description>< ![CDATA[description] ]></Description>
                    <PicUrl>< ![CDATA[picurl] ]></PicUrl>
                    <Url>< ![CDATA[url] ]></Url>
                </item>
            </Articles>
        </xml>
        """
        articleCount = len(items)

        if not 0 < articleCount < 8:
            return

        return pair_to_xml([
            ('ToUserName', touser),
            ('FromUserName', fromuser),
            ('CreateTime', tc.utc_timestamp()),
            ('MsgType', 'news'),
            ('ArticleCount', articleCount),
            ('Articles', [
                [
                    ('Title', item.get('title', '')),
                    ('Description', item.get('description', '')),
                    ('PicUrl', item.get('picurl', '')),
                    ('Url', item.get('url', ''))
                ] for item in items
            ])
        ])


reply = Reply()
reply_text = reply.text
reply_image = reply.image
reply_voice = reply.voice
reply_video = reply.video
reply_music = reply.music
reply_news = reply.news
