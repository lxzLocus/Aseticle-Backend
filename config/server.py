import grpc
from concurrent import futures
from api.pkg import service_pb2
from api.pkg import service_pb2_grpc

# サービサーの実装クラス
class SearchScholarServicer(service_pb2_grpc.SearchScholarServicer):
    def Search(self, request, context):
        # ここにサービスのロジックを実装
        results = [
            service_pb2.SearchResult(
                url="https://example.com",
                title="Sample Paper",
                author="John Doe",
                conference="Sample Conference",
                pages=10,
                date="240922",
                abstract="This is a sample abstract.",
                cite_num=5,
                submitted=True,
                relevant_no=1,
                tier=3
            )
        ]
        return service_pb2.SearchScholarResponse(results=results)

# サーバーの起動とサービスの登録
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service_pb2_grpc.add_SearchScholarServicer_to_server(SearchScholarServicer(), server)
    server.add_insecure_port('[::]:8080')
    server.start()
    print("gRPC Server started on port 8080")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
