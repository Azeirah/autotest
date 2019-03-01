from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import sqlite3
import settings
import sqlparse

def get_requests():
    conn = sqlite3.connect('R:/Temp/function-calls.db')

    query = """SELECT requestname, strftime('%d-%m %H:%M:%S', timestamp) FROM traces ORDER BY timestamp DESC"""

    c = conn.cursor()
    c.execute(query)
    return c.fetchall()

def get_paths_for_text_in_trace(conn, requestHash, text):
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
    WHERE f.requestname=:requestHash
    GROUP BY f.hash HAVING (params LIKE ('%' || :text || '%') OR returnval LIKE ('%' || :text || '%'))
    """



    c = conn.cursor()
    c.execute(query, { 'requestHash': requestHash, 'text': text })

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
CORS(app)

@app.route("/queryLinks/<requestHash>")
def queryLinks(requestHash):
    conn = sqlite3.connect('function-calls.db')
    paths = get_paths_for_text_in_trace(conn, requestHash, request.args.get('text'))

    return paths

@app.route("/json/requests")
def requests():
    return jsonify(get_requests())

@app.route("/sqlColumnsInRequest/<requestHash>")
def sqlColumnsInRequest(requestHash):
    """Fetches info about the sql tables, statements and columns accessed
    in a specified request based on the trace data."""
    conn = sqlite3.connect('function-calls.db')

    query = """SELECT
      f2.name,
      v.value,
      f3.name,
      f.linenum,
      m.value,
      t.value
    FROM function_invocations f
        LEFT JOIN function_names f2 ON f.name = f2.rowid
        LEFT JOIN invocation_parameters parameter on parameter.function_invocation_hash = f.hash
        LEFT JOIN "values" v on parameter.value_id = v.rowid
        LEFT JOIN file_names f3 on f.calling_filename = f3.rowid
        LEFT JOIN `values` m on f.memory=m.rowid
        LEFT JOIN `values` t on f.time=t.rowid
    WHERE f.requestname = :requestHash
      AND (f2.name = 'mysqli_query'
      OR f2.name = 'createQuery'
      OR f2.name = 'mysql_query'
      OR f2.name = 'executeDelete'
      OR f2.name = 'executeQuery'
      OR f2.name = 'executeUpdate'
      OR f2.name = 'fetchAll'
      OR f2.name = 'fetchColumn'
      OR f2.name = 'fetchAssoc')
    GROUP BY
      f.hash HAVING
        (v.value LIKE '%SELECT%' OR
         v.value LIKE '%UPDATE%' OR
         v.value LIKE '%DELETE FROM%' OR
         v.value LIKE '%INSERT INTO%')
        AND parameter.rowid=MIN(parameter.ROWID)"""

    c = conn.cursor()
    c.execute(query, { 'requestHash': requestHash })

    sqlCalls = c.fetchall()

    content = ""

    for p in sqlCalls:
        fn = p[0]
        linenum = p[3]
        memory = p[4]
        time = p[5]
        filepath = p[2].replace('\\', '/')
        filename = filepath.split('/')[-1]
        url = "phpstorm://open?url=file://{filename}&line={linenum}".format(filename=filepath, linenum=linenum)
        rawQuery=p[1].replace("\\r\\n", "\n").replace("\\n", "\n")
        rawQuery=rawQuery[1:]
        rawQuery=rawQuery[:-1]
        htmlQuery = sqlparse.format(rawQuery, reindent=True)
        print("-"*80)
        print("-"*80)
        parsed = sqlparse.parse(rawQuery)

        print(type(parsed))
        print(type(parsed[0]))
        print(type(parsed[0].tokens))
        print(type(parsed[0].flatten()))

        # for t in parsed[0].flatten():
        #     if t.ttype is sqlparse.tokens.Name:
        #         print(t)
        #         nextToken = parsed[0].token_next(parsed[0].token_index(t), skip_cm=True)
        #         nextNextToken = parsed[0].token_next(parsed[0].token_index(nextToken), skip_cm=True)
        #         if nextToken.ttype is sqlparse.tokens.punctuation and nextNextToken.ttype is sqlparse.tokens.Name:
        #             print(t + nextToken + nextNextToken)
            # print('..')

        # for token in parsed.tokens.flatten():
            # for t in token.flatten():
            # print(token.ttype)
            # print(token.flatten())
        # print(parsed)
        print("-"*80)
        print("-"*80)

        content += "<div>"
        content += "<a href='{url}'>{function}@{filename}:{linenum}</a> -- time: <b>{time:.5f}</b> -- memory: <b>{memory}</b><br />".format(
            url=url,
            function=fn,
            filename=filename,
            linenum=linenum,
            memory=memory,
            time=float(time))
        content += "<code>{query}</code>".format(query=htmlQuery)
        content += "</div>"
        content += "<br/>"

    return content


@app.route('/overview', defaults={'request_hash': None})
@app.route('/overview/<request_hash>')
def overview(request_hash):
    request_hashes = get_requests()

    return render_template('overview.html', request_hashes=request_hashes, request_hash=request_hash)

if __name__ == "__main__":
    app.run()
