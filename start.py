from aiohttp import web

async def hello(request):
    return web.Response(text='hello!')

app=web.Application()
app.router.add_get('/hello',hello)
web.run_app(app,port=6800)