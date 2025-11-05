from pathlib import Path

from sdx_base.server.server import RouterConfig

from app.routes import router
from app.settings import Settings
from sdx_base.run import run


async def dummy_tx_id_getter(request):
    return "NA"

if __name__ == '__main__':
    proj_root = Path(__file__).parent

    routers = [
        RouterConfig(router=router, prefix="", tx_id_getter=dummy_tx_id_getter)
    ]

    run(Settings, proj_root=proj_root, routers=routers)
