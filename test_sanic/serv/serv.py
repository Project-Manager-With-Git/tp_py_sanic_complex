
import ssl
import json
from pathlib import Path
from typing import Any, Dict
from pyloggerhelper import log
from schema_entry import EntryPoint
from sanic import Sanic
from sanic.log import logger, error_logger, access_logger
from sanic_openapi import openapi2_blueprint
from test_sanic.apis import init_api
from test_sanic.downloads import init_downloads
from test_sanic.events import init_channels
from test_sanic.listeners import init_listeners
from test_sanic.middlewares import init_middleware
from test_sanic.models import init_models


class Serv(EntryPoint):
    _name = "test_sanic_sender"
    default_config_file_paths = [
        "config.json",
        "config.yml",
    ]
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "required": [
            "app_version",
            "app_name",
            "log_level",
            "address",
        ],
        "properties": {
            "app_version": {
                "type": "string",
                "title": "v",
                "description": "应用版本",
                "default": "0.0.0"
            },
            "app_name": {
                "type": "string",
                "title": "n",
                "description": "应用名",
                "default": "test_sanic_sender"
            },

            "log_level": {
                "type": "string",
                "title": "l",
                "description": "log等级",
                "enum": ["DEBUG", "INFO", "WARN", "ERROR"],
                "default": "DEBUG"
            },
            "address": {
                "type": "string",
                "title": "a",
                "description": "启动地址",
                "default": "0.0.0.0:5000"
            },
            "workers": {
                "type": "integer",
                "title": "w",
                "description": "启动进程数",
                "default": 1
            },
            "published_address": {
                "type": "string",
                "title": "p",
                "description": "外部访问地址"
            },
            "cros_allow_origins": {
                "type": "array",
                "description": "跨域允许的域名",
                "items": {
                    "type": "string"
                }
            },
            "cros_allow_credentials": {
                "type": "boolean",
                "description": "跨域是否需要证书"
            },
            "cors_allow_headers": {
                "type": "array",
                "description": "跨域允许的头",
                "items": {
                    "type": "string"
                }
            },
            "cors_expose_headers": {
                "type": "array",
                "description": "跨域暴露的头",
                "items": {
                    "type": "string"
                }
            },
            "static_page_dir": {
                "type": "string",
                "description": "静态页面存放的文件夹"
            },
            "static_source_dir": {
                "type": "string",
                "description": "静态资源存放的文件夹"
            },
            "serv_cert_path": {
                "type": "string",
                "description": "服务端证书位置"
            },
            "serv_key_path": {
                "type": "string",
                "description": "服务端证书的私钥位置"
            },
            "ca_cert_path": {
                "type": "string",
                "description": "根证书位置"
            },
            "client_crl_path": {
                "type": "string",
                "description": "客户端证书黑名单"
            }
        }
    }

    def _run_serv(self, app: Sanic) -> None:
        address = self.config.get("address", "0.0.0.0:5000")
        host, port = address.split(":")
        log_level = self.config.get("log_level")
        if log_level == "DEBUG":
            debug = True
            access_log = True
        else:
            debug = False
            access_log = False
        conf = {
            "host": host,
            "port": int(port),
            "workers": self.config.get("workers", 1),
            "debug": debug,
            "access_log": access_log,
        }
        # ssl相关配置
        if self.config.get.get("serv_cert_path") and self.config.get.get("serv_key_path"):
            context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
            context.load_cert_chain(self.config["serv_cert_path"], keyfile=self.config["serv_key_path"])
            if self.config.get("ca_cert_path"):
                context.load_verify_locations(self.config["ca_cert_path"])
                context.verify_mode = ssl.CERT_REQUIRED
                if self.config.get('client_crl_path'):
                    context.load_verify_locations(self.config['client_crl_path'])
                    context.verify_flags = ssl.VERIFY_CRL_CHECK_LEAF
                log.info("use TLS with client auth")
            else:
                log.info("use TLS")
            conf["ssl"] = context
        log.info("server start", config=conf)
        app.run(**conf)

    def do_main(self) -> None:
        app_name = self.config.get("app_name")
        log_level = self.config.get("log_level")
        app = Sanic(app_name)
        logger.setLevel(log_level)
        error_logger.setLevel(log_level)
        access_logger.setLevel(log_level)
        log.initialize_for_app(
            app_name=app_name,
            log_level=log_level
        )
        log.info("获取配置", config=self.config)
        # 注册测试
        if log_level == "DEBUG":
            from sanic_testing import TestManager
            TestManager(app)
            app.blueprint(openapi2_blueprint)

        

        # 注册静态文件
        if self.config.get("static_page_dir"):
            app.static("/", self.config["static_page_dir"])
        if self.config.get("static_source_dir"):
            app.static("/static", self.config["static_source_dir"])

        # 注册数据模型
        init_models(app)
        # 注册listeners
        init_listeners(app)
        # 注册中间件
        init_middleware(app)
        # 注册restful接口
        init_api(app)
        # 注册下载接口
        init_downloads(app)
        # 注册基于sse的channels
        init_channels(app)
        self._run_serv(app)
