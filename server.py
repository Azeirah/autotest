from flask import Flask
import sqlite3
import settings

def get_paths_for_text_in_trace(text, trace):
    query = """
    SELECT f2.name,
           f4.name as `definition file`,
           f3.name as `calling file`,
           f.linenum,
           group_concat(coalesce(v.value, '{{void}}'), ', ') as params
    FROM function_invocations f
           LEFT JOIN function_names f2 ON f.name = f2.rowid
           LEFT JOIN file_names f3 on f.calling_filename = f3.rowid
           LEFT JOIN file_names f4 on f.definition_filename = f4.rowid
           LEFT JOIN invocation_parameters parameter on parameter.function_invocation_hash = cast(f.hash as text)
           LEFT JOIN "values" v on parameter.value_id = v.rowid
           LEFT JOIN "values" v2 on f.returnval = v2.rowid
    WHERE f.requestname='XDS29awTEVEAABfUVOEAAAA-'
    GROUP BY f.hash HAVING (params LIKE '%DAF Tru%' OR returnval LIKE '%DAF Tru%') AND `definition file` != 'php:internal'
    """
    conn = sqlite3.connect('function-calls.db')

    c = conn.cursor()
    c.execute(query)

    paths = c.fetchall()

    content = ""

    for p in paths:
        fn = p[0]
        linenum = p[3]
        filepath = p[2].replace('\\', '/')
        filename = filepath.split('/')[-1]
        url = "phpstorm://open?url=file://{filename}&line={linenum}".format(filename=filepath, linenum=linenum)
        content += "<a href='{url}'>{function}@{filename}:{linenum}</a><br />".format(url=url, function=fn, filename=filename, linenum=linenum)

    return content

app = Flask(__name__)

@app.route("/")
def hello():
    paths = get_paths_for_text_in_trace("TODO", "TODO")

    return paths

if __name__ == "__main__":
    app.run()
