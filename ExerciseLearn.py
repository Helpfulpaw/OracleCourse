
# -*- coding: utf-8 -*-
import Tkinter
import random
import copy
import hashlib
import cx_Oracle
__author__ = 'Alex'


class SimpleTable(Tkinter.Frame):
    def __init__(self, parent, rows=10, columns=2):
        # use black background so it "peeks through" to
        # form grid lines
        Tkinter.Frame.__init__(self, parent, background="black")
        self._widgets = []
        self.command_line=[]
        self.output=''
        for row in range(rows):
            current_row = []
            for column in range(columns):
                label = Tkinter.Button(self, text="",
                                 borderwidth=0, width=10)
                label.grid(row=row, column=column, sticky="nsew", padx=1, pady=1)
                current_row.append(label)
            self._widgets.append(current_row)

        for column in range(columns):
            self.grid_columnconfigure(column, weight=1)

    def set(self, row, column, value):
        widget = self._widgets[row][column]
        widget.configure(text=value)

    def set_constructor(self, row, column, value):
        widget = self._widgets[row][column]
        widget.configure(text=value)

        def command():
            self.command_line.append(widget.config('text')[-1])
            try:
                self.show_command_line(row+1)
            except:
                pass
        widget.configure(command=command)

    def show_command_line(self,row):
        i=0
        for widget in self._widgets[row]:
            widget.configure(text=self.command_line[i])
            i+=1

    def restart(self,row=1):
        del self.command_line[:]

        for widget in self._widgets[row]:
            widget.configure(text='')

    def output_command_line(self):

        try:
            sentence=self.command_line[0]
        except:
            sentence=''
        for command in self.command_line[1:]:
            sentence+=' '+command
        self.output=sentence
        return self.output

    def get_command_line(self):

        return self.command_line


class Exercise(Tkinter.Frame):

    def __init__(self,master=None,exercise_id='1',mode='learn'):
        Tkinter.Frame.__init__(self,master)
        self.answer='God Knows'
        self.task='Who?'
        self.mode=mode
        self.tags=[]
        self.exercise_id=exercise_id
        self.student_answer=''
        self.answer=None
        self.create_answer()
    def create_task(self,task):
        Exercise=Tkinter.Text(self)
        Exercise.config(state=Tkinter.DISABLED)
        Exercise.config(text=task)
        Exercise.config(relief=Tkinter.RIDGE)
        Exercise.config(background='black')
        Exercise.pack(side="top", fill=Tkinter.BOTH)
        return Exercise

    def create_hint(self,tags):
        hint_frame=Tkinter.Frame(self)
        i=0
        result_table = SimpleTable(hint_frame,len(tags),2)
        random.shuffle(tags)

        for tag in tags:
            result_table.set(0,i,tag) #создает строку для выбора
            i+=1                                   #переход на новую строку

        result_table .pack({"side": "right"}, fill="x")
        hint_frame.pack()
        return result_table

    def create_answer(self):
        self.answer=Tkinter.Text(self)
        self.answer .pack(side="bottom", fill=Tkinter.BOTH)
        self.answer.insert(Tkinter.END,'')

    def set_answer(self, answer):
        answer.insert(Tkinter.END, answer)


class Constructor(Tkinter.Frame):

        def __init__(self, master=None, answer='select * from hr.employees', tags=['*', 'print', 'commit'], odds=3):
            Tkinter.Frame.__init__(self, master)
            self.inputing = ''
            i = 0
            parts = answer.split(' ')

            random.shuffle(parts)
            random.shuffle(tags)

            for tag in tags[odds:]:
                if parts.count(tag) == 0:
                    parts.append(tag)
            self.result_table = SimpleTable(self, 2, len(parts))
            for part in parts:

                self.result_table.set_constructor(0, i, part) #создает строку для выбора
                i += 1                                   #переход на новую строку

            self.create_widgets()

        def create_widgets(self):
                restart_button = Tkinter.Button(self, command=self.result_table.restart, text='Restart')
                parse_button = Tkinter.Button(self, command=self.run, text='Go!')

                self.result_table .pack({"side": "right"}, fill="x")
                restart_button.pack()
                parse_button.pack()
                self.pack()

        def run(self):
            inputing = self.result_table.output_command_line()

            self.create_answer(inputing)
            self.inputing = inputing

        def create_answer(self, inputing='', master=None):
            try:
                self.answer.destroy()
            except:
                pass
            try:
                self.answer = Tkinter.Text(master)
            except:
                self.answer = Tkinter.Text(self)
            self.answer.tag_config("a", foreground="black",font='42')
            self.answer .pack(side="bottom", fill=Tkinter.BOTH)
            self.answer.insert(Tkinter.END, inputing, 'a')


def show_table(result, master=None):                         # На входе результат запроса, на выходе фрейм с таблицей
    i = 0
    j = 0
    result_show = Tkinter.Frame(master)
    #try:
    result_table = SimpleTable(result_show, len(result)+1, len(result[0])+1)
    #except:
    #    return 0

    for row in result:
        for col in row:
            result_table .set(i, j, col)
            j += 1
        j = 0
        i += 1
    result_table.pack()
    result_show.pack()
    return result_show


def database_connection(user='user1', password='USER1', ip='@10.1.75.168', sd='orcl'):

    connect_string = user+'/'+password+ip+'/'+sd
    db = cx_Oracle.connect(connect_string)

    return db


def pass_query(cursor=database_connection().cursor(), answer=None):  # Передает запрос в базу данных, возвращает таблицу и её параметры
    i = 0
    j = 0

    cursor.execute(answer)
    result_set = cursor.fetchall()
    i = len(result_set)

    try:
        j = len(result_set[0])
    except BaseException:
        j = 0
    output = {"rows": i, "cols": j, "result": result_set}

    return output


def smiled_string(tuple_variables):
    result = '('
    i = 1
    for var in tuple_variables:
        result += (var+',')
    result = result[:-1]
    result += ') values('
    for var in tuple_variables:
        result += (':'+str(i)+',')
        i += 1
    result = result[:-1]+')'
    return result


def insert(table, columns, values, connection=database_connection()):

    cursor = connection.cursor()

    statement = 'insert into '+table+smiled_string(columns)
    print statement
    print values
    cursor.execute(statement, values)
    connection.commit()
    cursor.close()


def select(query='select * from hr.employees', connection=database_connection(), params=None):
    cursor = connection.cursor()
    try:
        for p in params:
            print p
    except:
        cursor.execute(query, params)
    else:
        cursor.execute(query, params)
    result = []
    for row in cursor:
        result.append(row)

    cursor.close()

    return result


def insert_input_label(master, name, **options):

                                label = Tkinter.Label(master,text=name)
                                label.pack()
                                var = Tkinter.StringVar(master)
                                combo = Tkinter.Entry(master, textvariable=var, **options)
                                combo.pack()
                                return var


class Login (Tkinter.Frame):
    def __init__(self, master=None, cursor = database_connection().cursor()):
        Tkinter.Frame.__init__(self, master)

        self.email_entry = insert_input_label(self,    u'Email')
        self.password_entry = insert_input_label(self, u'Пароль', show='*')
        self.id = 0
        self.email = ''
        self.password = ''
        self.max_user = 0

        reg_button = Tkinter.Button(self, borderwidth=4, text="Register", width=10, pady=8, command=self.registration)
        login_button = Tkinter.Button(self, borderwidth=4, text="Login", width=10, pady=8, command=self.login_pass)

        reg_button .pack(side=Tkinter.BOTTOM, fill=Tkinter.BOTH, expand=1)
        login_button.pack(side=Tkinter.BOTTOM, fill=Tkinter.BOTH, expand=1)

        self.pack()

    def login_pass(self):
        self.email = self.email_entry.get()
        self.password = self.password_entry.get()
        self.password = hashlib.md5(self.password).hexdigest()

        try:
            user = select(query='select (StudentId) from student where student.email=:1 and student.password=:2',
                params=[self.email, self.password])
        except:
            user = 0
        self.id = user
        if self.id != 0:
            self.pack_forget()

    def registration(self):

        self.RegForm = Tkinter.Toplevel(self)
        self.FirstNameEntry = insert_input_label(self.RegForm, u'Имя')
        self.LastNameEntry = insert_input_label(self.RegForm, u'Фамилия')
        self.SurNameEntry = insert_input_label(self.RegForm, u'Отчество')
        self.EmailEntry = insert_input_label(self.RegForm, u'Email')
        self.PasswordEntry = insert_input_label(self.RegForm, u'Пароль')
        ###################################################
        Reging = Tkinter.Button(self.RegForm, borderwidth=4, text="Login", width=10, pady=8, command=self.registration_enter)
        Reging.pack(side=Tkinter.BOTTOM)
        ##################################################
        #self.RegForm.pack()

    def registration_enter(self):

        print self.registration_pass()

    def registration_pass(self):

        first_name = self.FirstNameEntry.get()
        last_name = self.LastNameEntry.get()
        sur_name = self.SurNameEntry.get()
        email = self.EmailEntry.get()
        password = self.EmailEntry.get()
        password = hashlib.md5(password).hexdigest()

        max_user = select('select max(StudentId)+1 from student')[0]
        if self.max_user != 0:
            self.RegForm.destroy()
            print((max_user+1, first_name, last_name, sur_name, email, password))
        insert('USER1.student', columns=('STUDENTID', 'FIRSTNAME', 'LASTNAME', 'SURNAME', 'EMAIL',
                                         'DATE_REG', 'ROLE', 'PASSWORD'),
               values=(max_user+1, first_name, last_name, sur_name, email, password))


class Tester(Tkinter.Tk):

    def __init__(self):
        Tkinter.Tk.__init__(self)
        self.level = 0
        self.mode = 0
        self.mistakes = []
        self.new_tags = []
        self.score = 0
        self.log_in = Login(self)

    def get_new_tags(self):
        pass

    def get_mistakes(self):
        pass

    def get_exercise(self):
        if self.mode == 0:
            self.get_learn_exercise()
        else:
            if self.score > 5 and self.get_mistakes() is None:
                self.get_mistake_exercise()
            elif self.score < 5:
                self.get_new_exercise()
            else:
                self.next_mode()

    def get_new_exercise(self):
        pass

    def get_mistake_exercise(self):
        pass

    def get_learn_exercise(self):
        pass

    def next_mode(self):
        self.mode += 1

    def level_up(self):
        self.mode = 0
        self.level += 1




app = Tkinter.Tk()

# Con1 = Constructor(app)
# Con1.create_answer(master=app)
# Con1.pack()
# Log1 = Login(app)
# Log1.pack()



app.mainloop()
