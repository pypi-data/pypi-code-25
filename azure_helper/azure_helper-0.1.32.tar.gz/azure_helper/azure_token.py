import datetime
import hmac
import hashlib
import base64


def getAccessKey(apimId, apimKey, expiryDate=None):
    if expiryDate is None:
        expiryDate = datetime.datetime.utcnow() + datetime.timedelta(hours=1)

    strExpiry = expiryDate.strftime("%Y-%m-%dT%H:%M:00.0000000Z")

    dataToSign = apimId + "\n" + strExpiry

    hasher = hmac.new(bytes(apimKey, 'latin-1'), digestmod=hashlib.sha512)

    hasher.update(dataToSign.encode('UTF-8'))
    digest = hasher.digest()

    hash = base64.b64encode(digest)

    accessKey = "SharedAccessSignature uid=%s&ex=%s&sn=%s" % (apimId, strExpiry, str(hash, 'UTF-8'))

    return accessKey