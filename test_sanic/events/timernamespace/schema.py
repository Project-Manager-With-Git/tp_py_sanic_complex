post_query_schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "additionalProperties": False,
    "required": ["seconds"],
    "properties": {
        "seconds": {
            "type": "integer",
            "description": "倒计时多少秒"
        }
    }
}
