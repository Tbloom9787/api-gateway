.PHONY: clean

schema.db:
	sqlite3 schema.db < schema.sql

clean:
	rm -f schema.db