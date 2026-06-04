from app.BE.database.connection import fetchrow, fetch, execute, executemany

class BaseRepository:
    _fetchrow    = staticmethod(fetchrow)
    _fetchall    = staticmethod(fetch)
    _fetch       = staticmethod(fetch)
    _execute     = staticmethod(execute)
    _executemany = staticmethod(executemany)