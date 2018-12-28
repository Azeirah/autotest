import sublime
import sublime_plugin
import sqlite3
import os.path
from pprint import pprint
from collections import Counter
import html

settings = sublime.load_settings('MethodUsages.sublime-settings')

db_name = settings.get("db_path")
conn = sqlite3.connect(db_name)


class ComputedProperty:
    def __init__(self, conn, word, filename, linenum):
        self.conn = conn
        self.word = word
        self.filename = filename
        self.linenum = linenum

    def compute(self):
        raise NotImplementedError

    def render_html(self):
        raise NotImplementedError


class IsDeterministicProperty(ComputedProperty):
    def compute(self):
        """
        Returns an estimate on whether a given function is
        deterministic or not.
        0 means certainty that the function is _not_ deterministic
        >= 0 is uncertain, but the higher the number, the higher the probability that it is non-deterministic
        """
        query = """
        SELECT
            group_concat(coalesce(v.value, '{{void}}'), ', ') as params,
            v2.value as returnval
        FROM
            function_invocations f
            LEFT JOIN `invocation_parameters` parameter on parameter.function_invocation_hash=f.hash
            LEFT JOIN `values` v on parameter.value_id = v.rowid
            LEFT JOIN `values` v2 on f.returnval = v2.rowid
        WHERE f.name =
            (SELECT fn.rowid
             FROM function_names fn
             WHERE
                fn.name = :word)
        GROUP BY f.hash
        """

        c = self.conn.cursor()
        c.execute(query, { 'word': self.word })

        hashtable = {}

        for params, returnval in c.fetchall():
            if params in hashtable:
                hashtable[params].append(returnval)
            else:
                hashtable[params] = [returnval]

        certainty = 0
        for key, return_values in hashtable.items():
            uniq_retvals = set(return_values)
            if len(uniq_retvals) > 1:
                return 0
            else:
                certainty += len(return_values)

        return certainty

    def render_html(self):
        certainty = self.compute()

        if certainty == 0:
            return """<div><b>Deterministic</b>: <var>No</var></div>"""
        else:
            return """<div><b>Deterministic</b>: Maybe <var class="certainty">({certainty})</var></div>""".format(certainty=certainty)

class ArityProperty(ComputedProperty):
    def compute(self):
        query = """
        SELECT
            COUNT(v.value)
        FROM
            function_invocations f
            LEFT JOIN `invocation_parameters` parameter on parameter.function_invocation_hash=f.hash
            LEFT JOIN `values` v on parameter.value_id = v.rowid
        WHERE f.name =
            (SELECT fn.rowid
             FROM function_names fn
             WHERE
                fn.name = :word)
        GROUP BY f.hash"""

        c = self.conn.cursor()
        c.execute(query, { 'word': self.word })

        return c.fetchall()

    def render_html(self):
        arities = [x[0] for x in self.compute()]
        num_samples = len(arities)

        counts = Counter(arities)

        print(counts)

        # split
        # substr
        # __constructor
        #

        if len(counts) == 0:
            print("...0")
            value = "void <var class='certainty'>({samples})</var>".format(samples=num_samples)
        else:
            if len(counts) == 1:
                value = "{v} <var class='certainty'>({samples})</var>".format(samples=num_samples, v=list(counts.keys())[0])
            else:
                print("...2")
                value = "<i>varying</i>"
                for k, v in counts.items():
                    value += "<br /><code class='invisible'>....</code>{k}: {v}".format(k=k, v=v)

        return "<div><b>Arity</b>: {value}</div>".format(value=value)

class ReturnTypeProperty(ComputedProperty):
    def compute(self):
        query = """
        SELECT DISTINCT
            `vt`.`php_type`
        FROM
            `function_invocations` `f`
            LEFT JOIN `values` `v` ON `f`.`returnval`=`v`.`rowid`
            LEFT JOIN `value_types` `vt` ON `v`.`php_type`=`vt`.`rowid`
        WHERE f.name =
            (SELECT f4.rowid
             FROM function_names f4
             WHERE
                f4.name = :word)
        """

        c = self.conn.cursor()
        c.execute(query, { 'word': self.word })

        return c.fetchall()

    def render_html(self):
        types = self.compute()

        if len(types) == 1:
            return types[0][0]
        else:
            return "<" + " | ".join([t[0] for t in types]) + ">"

        return types

class MethodUsageExamplesProperty(ComputedProperty):
    def compute(self):
        query = """
        SELECT DISTINCT
            COALESCE(f2.name, '{{missing fn}}') || '(' || substr(group_concat(coalesce(v.value, '{{void}}'), ', '), 1, 80) || ') -> ' || coalesce(v2.value, '{{void}}') as `function invocation`,
            f3.name LIKE :name as file_sorter,
            ABS(f.linenum - :linenum) as distance,
            printf("%f", t.value) as time,
            m.value as memory
        FROM
             function_invocations f
               LEFT JOIN `function_names` f2 ON f.name = f2.rowid
               LEFT JOIN `file_names` f3 on f.calling_filename = f3.rowid
               LEFT JOIN `file_names` f4 on f.definition_filename = f4.rowid
               LEFT JOIN `invocation_parameters` parameter on parameter.function_invocation_hash=f.hash
               LEFT JOIN `values` v on parameter.value_id = v.rowid
               LEFT JOIN `values` v2 on f.returnval = v2.rowid
               LEFT JOIN `values` m on f.memory=m.rowid
               LEFT JOIN `values` t on f.time=t.rowid
        WHERE f.name =
              (SELECT f4.rowid
               FROM function_names f4
               WHERE
                   f4.name = :word)
        GROUP BY f.hash
        ORDER BY file_sorter DESC, distance ASC
        LIMIT 15
        ;"""

        c = self.conn.cursor()
        c.execute(query, { 'word': self.word, 'name': '%' + self.filename + '%', 'linenum': self.linenum })

        return c.fetchall()

    def render_html(self):
        result = self.compute()

        content = """<h2>Examples</h2>
                <code><b>Memory</b><b class="invisible">..........</b><b>Time</b><b class="invisible">............</b><b>Code</b></code>"""
        # substr

        content += "<code>"

        for item in result:
            memory = (str(item[4]) + "b").ljust(16, " ")
            time = (str(item[3]) + "s").ljust(16, " ")
            call = item[0]

            content += "<br />"
            content += "{mem}{time}{call}".format(mem=memory, time=time, call=call)

        content += "</code>"

        return content

class MethodUsagesCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        point = self.view.sel()[0]
        word = self.view.substr(self.view.word(point))
        linenum = self.view.rowcol(point.a)[0] + 1
        filename = os.path.split(self.view.file_name() or '')[1]

        self.render_html(word, filename, linenum)

    def render_html(self, word, filename, linenum):
        deterministic_html = IsDeterministicProperty(conn, word, filename, linenum).render_html()
        method_usage_examples = MethodUsageExamplesProperty(conn, word, filename, linenum).render_html()
        types = ReturnTypeProperty(conn, word, filename, linenum).render_html()
        arity = ArityProperty(conn, word, filename, linenum).render_html()

        content = """
        <html>
            <body id="method-usages-function-popup">
                <style>
                    .certainty {{
                        color: rgb(170, 170, 170);
                        font-size: 0.8rem;
                    }}

                    .invisible {{
                        color: transparent;
                    }}

                    var {{
                        font-style: normal;
                    }}

                    h1, h2, h3, h4, h5, h6, div {{
                        font-family: sans-serif;
                    }}
                </style>
                <h1>{name} ⇒ {types}</h1>
                <h2>Properties</h2>
                <div class="properties">
                    {deterministic_html}
                    {arity}
                </div>

                {method_usage_examples}
                <br />
            </body>
        </html>
        """.format(
            name=word,
            types=types,
            deterministic_html=deterministic_html,
            method_usage_examples=method_usage_examples,
            arity=arity)

        # content = content.replace(r"\\0", r"\\\\0")

        # substr
        # split
        # __construct
        # count

        self.view.show_popup(content, max_width=1280, max_height=800)

    def render_itemlist(self, result):
        """Renders the results as a selectable list of items using sublime's popup_menu API"""

        content = []

        for item in result:
            content.append(str(item[0]))

        self.view.show_popup_menu(content, on_select=lambda x: sublime.set_clipboard(content[x]) if x != -1 else x)
