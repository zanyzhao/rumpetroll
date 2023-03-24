"""
# Copyright 2016 Tencent
# Author: 蓝鲸智云
"""
import json
import logging

from tornado import gen

from auth.mp_tencent import constants
from common.retrying import Retrying
from common.utils import http_get
from settings import RD, REGION

LOG = logging.getLogger(__name__)


@gen.coroutine
def get_access_token(use_cache=True):
    """获取调用接口凭证，有频率限制，最好有缓存"""
    if use_cache:
        access_token = REGION.get('access_token')
        LOG.debug(f'get_access_token use cache: {access_token}')
    else:
        access_token = None

    if not access_token:
        params = {'app_code': constants.APP_CODE, 'uin': constants.QQ_UIN, 'app_secret': constants.SECRET_KEY}
        result = yield http_get(constants.WECHAT_ACCESS_TOKEN_URL, params)
        # 错误日志
        if not result.get('result'):
            LOG.error('get_access_token error: %s' % result)
            access_token = None
        else:
            access_token = result['data'].get('access_token')
            REGION.set('access_token', access_token)
    raise gen.Return(access_token)


@gen.coroutine
def get_userid(code):
    """获取openid"""
    params = {
        'appid': constants.WECHAT_APPID,
        'secret': constants.WECHAT_APPSECRET,
        'code': code,
        'grant_type': 'authorization_code',
    }
    result = yield http_get(constants.WECHAT_USERID_URL, params)
    if result.get('errcode'):
        LOG.error(u"获取用户userid错误: %s" % result)
    else:
        LOG.debug('get_userid success %s', result)
    user_id = result.get('openid', '')
    raise gen.Return({'user_id': user_id})


@gen.coroutine
def get_userinfo(user_id, access_token=None, use_cache=True):
    """获取用户RTX信息"""
    if not access_token:
        access_token = yield get_access_token(use_cache=use_cache)
        if not access_token and use_cache is True:
            raise Retrying
    params = {'access_token': access_token, 'openid': user_id, 'lang': 'zh_CN'}

    cache_key = 'get_userinfo::%s' % user_id

    if use_cache:
        result = REGION.get(cache_key)
        LOG.debug('get_userinfo[%s] use cache: %s', user_id, result)
    else:
        result = None

    if not result:
        result = yield http_get(constants.WECHAT_USERINFO_URL, params)
        if result.get('errcode'):
            LOG.error(f"获取用户微信信息失败: {result}")
            if use_cache is True:
                raise Retrying
        else:
            REGION.set(cache_key, result)
            RD.hset('WEIXIN_OPEN_INFO', result['openid'], json.dumps(result))

    raise gen.Return((result.get('nickname', 'Guest'), result.get('sex', '1')))
