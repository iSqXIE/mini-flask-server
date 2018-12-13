from flask import g, jsonify, request
from app.libs.error_code import Success, UserException
from app.libs.redprint import RedPrint
from app.libs.token_auth import auth
from app.models.base import db
from app.models.order import Order
from app.models.user import User
from app.service.wxpay import UnifiedOrder, OrderQuery, CloseOrder, Base
from app.validators.params import CreateOrderValidator

api = RedPrint('order')


@api.route('/<string:oid>', methods=['GET'])
def get_one_order(oid):
    order = Order.get_one_order(oid)
    return jsonify(order)


@api.route('', methods=['GET'])
@auth.login_required
def get_my_order():
    uid = g.user.uid
    order = Order.get_user_order(uid)
    return jsonify(order)


@api.route('/pay/<string:oid>', methods=['GET'])
@auth.login_required
def get_pay_order(oid):
    uid = g.user.uid
    user = User.query.filter_by(id=uid).first().append('openid')
    order = Order.get_one_order(oid)
    wx_pay = UnifiedOrder(oid, user.openid, order.pay_price)
    pay_info = wx_pay.get_pay_info()
    return jsonify(pay_info)


@api.route('/pay/query/<string:oid>', methods=['GET', 'POST'])
def get_pay_query(oid):
    pay_info = OrderQuery(oid).get_order_info()
    if pay_info['result_code'] == 'FAIL':
        return UserException(msg=pay_info['err_code'])
    elif pay_info['trade_state'] == 'SUCCESS':
        with db.auto_commit():
            order = Order.get_one_order(oid)
            order.transaction_id = pay_info['transaction_id']
            order.status = 2
        return Success(msg=pay_info['trade_state_desc'])
    return UserException(msg=pay_info['trade_state_desc'])


@api.route('/pay/close/<string:oid>', methods=['GET', 'POST'])
def get_pay_close(oid):
    order_info = OrderQuery(oid).get_order_info()
    if order_info['result_code'] == 'FAIL':
        return UserException(msg=order_info['err_code'])
    elif order_info['trade_state'] == 'CLOSED':
        return Success(msg=order_info['trade_state_desc'])
    pay_info = CloseOrder(oid).get_close_info()
    if pay_info['result_code'] == 'FAIL':
        return UserException(msg=pay_info['err_code'])
    order = dict(Order.get_one_order(oid))
    Order.restore_product_stock(order['snap_product'])
    return Success(msg='订单已关闭')


@api.route('/pay/notify', methods=['POST'])
def get_pay_notify():
    if request.method == 'POST':
        pay_info = Base.xml_to_dict(request.data)
        if pay_info['return_code'] == 'SUCCESS':
            if pay_info['result_code'] == 'SUCCESS':
                if pay_info['trade_state'] == 'SUCCESS':
                    with db.auto_commit():
                        order = Order.get_one_order(pay_info['out_trade_no'])
                        if int(order.pay_price * 100) == pay_info['settlement_total_fee']:
                            order.transaction_id = pay_info['transaction_id']
                            order.status = 2
                            result_data = {
                                'return_code': 'SUCCESS',
                                'return_msg': 'OK'
                            }
                            return Base.dict_to_xml(result_data), {'Content-Type': 'application/xml'}


@api.route('/create', methods=['POST'])
@auth.login_required
def create_order():
    uid = g.user.uid
    form = CreateOrderValidator().validate_for_api()
    order_no = Order.create_order(form.product_ids.data, form.address_id.data,
                                  form.user_coupon_id.data, form.remark.data, uid)
    return jsonify(order_no)
