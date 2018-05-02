# -*- coding=UTF-8 -*-

import json
import grpc
from hornbill4p import hornbill_pb2_grpc, hornbill_pb2

"""
GRPC transport has a limitation of message length as following:
    https://github.com/grpc/grpc/blob/master/include/grpc/impl/codegen/grpc_types.h
    #define GRPC_DEFAULT_MAX_RECV_MESSAGE_LENGTH (4 * 1024 * 1024) => 4194304

"""


class HornbillRpcClient:
    def __init__(self, host, port):
        self.channel = grpc.insecure_channel("%s:%s" % (host, port))
        self.stub = hornbill_pb2_grpc.ClassifierStub(self.channel)

    def classify(self, content, workflows):
        """
        hornbill classification
        :param content: content to analysis, string
        :param workflows: list of string, hornbill classifier id
        :return: hornbill result ADTWT$1|SNTTWT$1
        """

        doc = {"id": "", "data": {"Text": content}, "documentType": "WEIBO"}
        doc = json.dumps(doc, ensure_ascii=True)
        doc_bytes = bytes(doc, "utf8")

        if len(doc_bytes) >= 4 * 1024 * 1024:
            raise Exception("contents too long, 你这是搞事情")
        else:
            response = self.stub.Classify(hornbill_pb2.BytesRequest(document=doc_bytes, workflows=workflows))
            return json.loads(response.hornbillResult.decode("utf-8"))

    def batch_classify(self, contents, workflows):
        """
        hornbill batch classification
        :param contents:
        :param workflows:
        :return:
        """

        docs = []
        for content in contents:
            doc = {"id": "", "data": {"Text": content}, "documentType": "WEIBO"}
            docs.append(doc)
        docs = json.dumps(docs, ensure_ascii=True)
        docs_bytes = bytes(docs, "utf8")

        if len(docs_bytes) >= 4 * 1024 * 1024:
            raise Exception("contents too long, please split into smaller batch")
        else:
            response = self.stub.BatchClassify(hornbill_pb2.BytesRequest(document=docs_bytes, workflows=workflows))
            return json.loads(response.hornbillResult.decode("utf-8"))

