import asyncio
import websockets
import json
from PySide6.QtCore import QObject, Signal


class WebSocketBridge(QObject):
    """WebSocket桥接器：将TCP接收的算法数据转发给Web客户端"""
    
    # 信号：发送数据到WebSocket客户端
    send_to_websocket = Signal(str)
    
    def __init__(self, host='localhost', port=8765):
        super().__init__()
        self.host = host
        self.port = port
        self.clients = set()
        self.server = None
        self.loop = None
        
    async def handler(self, websocket):
        """处理WebSocket连接（新版websockets API）"""
        self.clients.add(websocket)
        print(f"[WebSocket] client connected, total: {len(self.clients)}")
        
        try:
            # 保持连接活跃
            async for message in websocket:
                # 如果需要接收客户端消息，在这里处理
                pass
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.clients.discard(websocket)
            print(f"[WebSocket] client disconnected, total: {len(self.clients)}")
    
    async def broadcast(self, message):
        """向所有连接的客户端广播消息"""
        if self.clients:
            # 使用websockets.broadcast进行并发发送
            await asyncio.gather(
                *[client.send(message) for client in self.clients],
                return_exceptions=True
            )
    
    def start_server(self):
        """启动WebSocket服务器（在新的事件循环中）"""
        import threading
        
        def run_server():
            # 创建新的事件循环
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            
            # 在事件循环中创建并运行服务器
            async def start_and_run():
                # 先创建服务器
                self.server = await websockets.serve(self.handler, self.host, self.port)
                print(f"[WebSocket] server started at ws://{self.host}:{self.port}")
                
                # 保持服务器运行
                try:
                    await self.server.wait_closed()
                except KeyboardInterrupt:
                    pass
                finally:
                    self.server.close()
                    await self.server.wait_closed()
            
            # 运行直到完成
            try:
                self.loop.run_until_complete(start_and_run())
            finally:
                self.loop.close()
        
        # 在后台线程中运行
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
    
    def stop_server(self):
        """停止WebSocket服务器"""
        if self.loop and self.loop.is_running():
            self.loop.call_soon_threadsafe(self.loop.stop)
    
    def send_algorithm_data(self, data_dict):
        """发送算法数据到所有WebSocket客户端"""
        if self.clients:
            json_str = json.dumps(data_dict)
            asyncio.run_coroutine_threadsafe(
                self.broadcast(json_str),
                self.loop
            )
