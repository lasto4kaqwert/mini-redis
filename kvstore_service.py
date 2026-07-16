import grpc

import kvstore_pb2 as pb2
import kvstore_pb2_grpc as pb2grpc
from kvstore import KeyNotFoundError, KVStore


class KVStoreService(pb2grpc.KeyValueStoreServicer):
    def __init__(self):
        self.store = KVStore()

    def Put(self, request, context):
        self.store.put(
            key=request.key,
            value=request.value,
            ttl_seconds=request.ttl_seconds
        )

        return pb2.PutResponse()

    def Get(self, request, context):
        try:
            value = self.store.get(request.key)
        except KeyNotFoundError:
            context.abort(grpc.StatusCode.NOT_FOUND, "Key not found")

        return pb2.GetResponse(value=value)

    def Delete(self, request, context):
        self.store.delete(request.key)
        return pb2.DeleteResponse()

    def List(self, request, context):
        items = [
            pb2.KeyValue(key=key, value=value)
            for key, value in self.store.list(request.prefix)
        ]

        return pb2.ListResponse(items=items)
