import sys
import asyncio
from dotenv import load_dotenv

sys.path.append('/app/app')
from grpc_server import serve as grpc_serve  # gRPC サーバーをインポート

load_dotenv()

if __name__ == "__main__":
    # gRPC サーバーのみを実行
    grpc_serve()
