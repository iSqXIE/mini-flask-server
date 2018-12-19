from flask import request
from wtforms import Form

from app.libs.error_code import ParameterException


class BaseValidator(Form):
    def __init__(self):
        data = request.get_json(silent=True)
        view_args = request.view_args  # 获取view中的args
        args = dict(request.args.to_dict(), **view_args)
        super(BaseValidator, self).__init__(data=data, **args)

    def validate_for_api(self):
        valid = super(BaseValidator, self).validate()
        if not valid:
            raise ParameterException(msg=self.errors)
        return self

    def isPositiveInteger(self, value):
        try:
            value = int(value)
        except ValueError:
            return False
        return True if (isinstance(value, int) and value >= 0) else False

    def isPositivePrice(self, value):
        try:
            value = float(value)
        except ValueError:
            return False
        return True if (isinstance(value, (int, float)) and value > 0) else False

