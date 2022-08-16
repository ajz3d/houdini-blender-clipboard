# coding=utf8

import bpy
import threading
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler


class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2')


def server_create():
    with SimpleXMLRPCServer(('localhost', 8000),
                            requestHandler=RequestHandler) as server:
        server.register_introspection_functions()
        def import_alembic(path):
            # BUG: Wrong context.
            # How to change it with RPC client?
            bpy.ops.wm.alembic_import(
                bpy.context.copy(),
                filepath=path,
                set_frame_range=False
            )
            return "DONE"

        server.register_function(import_alembic)
        server.serve_forever()


def server_start():
    t = threading.Thread(target=server_create)
    t.daemon = True
    t.start()


if __name__ == '__main__':
    server_start()
