from . import config as memba_config
from . import misc as memba_misc

import sqlalchemy
import sqlalchemy.dialects.sqlite
import databases
import sqlite3

class ForeignKeyConnection(sqlite3.Connection):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.execute("PRAGMA foreign_keys = ON")

def make_table(name, *cols):
	meta = sqlalchemy.MetaData()
	return sqlalchemy.Table(name, meta, *cols)

# [TODO] DB path is temporary
DATA_DB = databases.Database("sqlite+aiosqlite:///data.db", factory=ForeignKeyConnection)

# Reference old code

# import sqlalchemy as s
# import sqlalchemy.dialects.sqlite as sq
# import databases as d
# import sqlite3 as sl

# wordle_game_table = base.make_table(
# 	"wordle_game",
# 	base.s.Column("game_id", base.s.String(length=36), primary_key=True, nullable=False),
# 	base.s.Column("username", base.s.Text, primary_key=True, nullable=False),
# 	base.s.Column("word", base.s.Text, nullable=False) # The answer for the word
# 	# s.Column("count", s.BigInteger, nullable=False) # Total guesses so far (Probably not needed)
# )

# wordle_guess_table = base.make_table(
# 	"wordle_guess",
# 	base.s.Column("game_id", base.s.String(length=36), base.s.ForeignKey("wordle_game.game_id", ondelete="CASCADE"), primary_key=True, nullable=False),
# 	base.s.Column("word", base.s.Text, nullable=False), # The guess for the word
# 	base.s.Column("order", base.s.BigInteger, primary_key=True, nullable=False) # Order of the guesses (higher = later)
# )

# wordle_word_table = base.make_table(
# 	"wordle_word",
# 	base.s.Column("valid", base.s.Integer, nullable=False),
# 	base.s.Column("word", base.s.Text, nullable=False)
# )