import logging
from concurrent import futures

import grpc

import kvstore_pb2_grpc as pb2grpc
from kvstore_service import KVStoreService

logger = logging.getLogger(__name__)

logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


PORT = 8000


def main() -> None:
    grpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    pb2grpc.add_KeyValueStoreServicer_to_server(
        servicer=KVStoreService(),
        server=grpc_server,
    )

    grpc_server.add_insecure_port(f"[::]:{PORT}")
    grpc_server.start()

    logger.info("gRPC server started on port %s", PORT)

    grpc_server.wait_for_termination()


if __name__ == "__main__":
    main()
