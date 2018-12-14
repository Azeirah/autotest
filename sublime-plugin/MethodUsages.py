import sublime
import sublime_plugin
import sqlite3
import os.path

db_name = r'C:\Users\Marvin\Documents\autotest\function-calls.db'
conn = sqlite3.connect(db_name)

class MethodUsagesCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        point = self.view.sel()[0]
        word = self.view.substr(self.view.word(point))


        query = """
        SELECT DISTINCT
            COALESCE(f2.name, '{{missing fn}}') || '(' || substr(group_concat(coalesce(v.value, '{{void}}'), ', '), 1, 80) || ') -> ' || coalesce(v2.value, '{{void}}') as `function invocation`,
            f3.name LIKE :name as file_sorter
        FROM
             function_invocations f
               LEFT JOIN function_names f2 ON f.name = f2.rowid
               LEFT JOIN file_names f3 on f.calling_filename = f3.rowid
               LEFT JOIN file_names f4 on f.definition_filename = f4.rowid
               LEFT JOIN invocation_parameters parameter on parameter.function_invocation_hash = cast(f.hash as text)
               LEFT JOIN "values" v on parameter.value_id = v.rowid
               LEFT JOIN "values" v2 on f.returnval = v2.rowid
        WHERE f.name =
              (SELECT f4.rowid
               FROM function_names f4
               WHERE
                   f4.name = :word)
        GROUP BY f.hash
        ORDER BY file_sorter DESC
        LIMIT 15
        ;"""

        filename = os.path.split(self.view.file_name())[1]

        c = conn.cursor()
        c.execute(query, {'word': word, 'name': '%' + filename + '%'})
        result = c.fetchall()

        content = []

        for item in result:
            content.append(str(item[0]))

        print(word)
        self.view.show_popup_menu(content, on_select=lambda x: sublime.set_clipboard(content[x]) if x != -1 else x)
        print("```")
        print(content)
        print("```")
