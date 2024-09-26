import grpc
import sys
from concurrent import futures

from api.pkg import service_pb2
from api.pkg import service_pb2_grpc

import asyncio
sys.path.append('/app/app')  
from googlescholar_searcher import scraping_main # type: ignore

# サービサーの実装クラス
class SearchScholarServicer(service_pb2_grpc.SearchScholarServicer):
    def Search(self, request, context):
        
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
        
        # query = request.query  # request からクエリを取得
        
        # if not query:
        #     context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Bad request: missing parameters")

        # # scraping_main 関数を呼び出して検索処理を実行
        # try:
        #     results = asyncio.run(scraping_main(query))
        # except Exception as e:
        #     context.abort(grpc.StatusCode.INTERNAL, f"Error during scraping: {str(e)}")

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
