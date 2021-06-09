from sanic.response import json, HTTPResponse
from sanic.request import Request
from sanic.views import HTTPMethodView
from sanic_openapi import doc
from ...decorators.checkjsonschema import checkjsonschema
from ...models import User
from .schema import post_query_schema


class ListSource(HTTPMethodView):

    @doc.summary("user接口总览")
    async def get(self, _: Request) -> HTTPResponse:
        cnt = await User.all().count()
        result = {
            "Description": "测试api,User总览",
            "UserCount": cnt,
            "Links": [
                {
                    "uri": "/user",
                    "method": "POST",
                    "description": "创建一个新用户"
                },
                {
                    "uri": "/user/<int:uid>",
                    "method": "GET",
                    "description": "用户号为<id>的用户信息"
                },
                {
                    "uri": "/user/<int:uid>",
                    "method": "PUT",
                    "description": "更新用户号为<id>用户信息"
                },
                {
                    "uri": "/user/<int:uid>",
                    "method": "DELETE",
                    "description": "删除用户号为<id>用户"
                },
            ]
        }

        return json(result, ensure_ascii=False)

    @staticmethod
    @doc.summary("创建新用户")
    @checkjsonschema(post_query_schema)
    async def post(request: Request) -> HTTPResponse:
        query_json = request.json
        try:
            u = await User.create(name=query_json.get("name", ""))
        except Exception as e:
            return json({
                "msg": "执行错误",
            }, status=500, ensure_ascii=False)
        else:
            return json({
                "msg": "插入成功",
                "uid": u.id
            }, ensure_ascii=False)
