





# import paypalrestsdk
#
# paypalrestsdk.configure({
#  "mode": "sandbox", # sandbox or live
#  "client_id": "AS3RJDVf-1yowanwVAcJoSw6oGd1MD4AHBasuUS4j0e9pZSSwf4NwRaMX_r0B0KMtcHQ1-_lIUegXBwk",
#  "client_secret": "EOMOaDYiZlXPWv-IPGtGehpFg3Whu9KK3qTcAsPaKjBckWy_cApJTjT2E_DBSFkzDhPvClx-OLy2HBst" })
#
# payment = paypalrestsdk.Payment({
#  "intent": "sale",
#  "payer": {
#      "payment_method": "paypal"},
#  "redirect_urls": {
#      "return_url": "http://w2w.test/continue_rest/",
#      "cancel_url": "http://w2w.test/"},
#  "transactions": [{
#      "item_list": {
#          "items": [{
#              "name": "item",
#              "sku": "item",
#              "price": "15.00",
#              "currency": "PLN",
#              "quantity": 1}]},
#      "amount": {
#          "total": "15.00",
#          "currency": "PLN"},
#      "description": "This is the payment transaction description."}]})
#
# if payment.create():
#    print("Payment created successfully")
#    
#    for link in payment.links:
#        print link.href, link.method
# else:
#   print(payment.error)
#
# # ?paymentId=PAY-4V813520YW776611VLKZ26XA&token=EC-9CA31462RP712590V&PayerID=HEVJP549N7QXG
#
# sale = paypalrestsdk.Sale.find('9J356305AE789734D')
# print sale
#
payment = paypalrestsdk.Payment.find("PAY-4V813520YW776611VLKZ26XA")

a = payment.execute({"payer_id": "HEVJP549N7QXG"})
if a:
   print("Payment execute successfully")
   print a
else:
   print(payment.error) # Error Hash
#
# # payment = paypalrestsdk.Payment.find("PAY-61E659464R113151ELKZY3UY")
# # a = "" + repr(payment)
# # print a.replace("'", '"')
# # # HEVJP549N7QXG
