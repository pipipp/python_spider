"""
This is a quick download tool for CCC website test logs（https://cesium.cisco.com/）
After running, a GUI window opens and you can select the test log within the specified date for batch download
"""
# -*- coding:utf-8 -*-
# @Time     : 2020/03/21
# @Author   : Evan Liu

import os
import re
import json
import time
import html
import base64
import requests
import threading
import calendar
import tkinter as tk
import tkinter.font as tkFont

from tkinter import ttk
from tkinter import messagebox

# global
spider = None
datetime = calendar.datetime.datetime
timedelta = calendar.datetime.timedelta


class CCCSpider(object):

    def __init__(self, login_account, thread_pool_max=10):
        self.login_account = login_account
        self.download_results = []
        self.thread_pool = threading.Semaphore(value=thread_pool_max)
        self.root_url = 'https://cesium.cisco.com/apps/cesiumhome/overview'
        self.verification_source_url = 'https://api-dbbfec7f.duosecurity.com'
        self.verification_prompt_url = self.verification_source_url + '/frame/prompt'
        self.verification_status_url = self.verification_source_url + '/frame/status'
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                          ' Chrome/80.0.3987.132 Safari/537.36'
        })

    def login(self, authentication_code=''):
        """
        Login to the CCC website
        :param authentication_code: Fill in the Mobile pass code
        :return:
        """
        resp = self.session.get(self.root_url)
        if '302' in str(resp.history):  # Redirect to the account login interface
            login_url = re.search('name="login-form" action="(.+?)"', resp.text)
            data = {
                'pf.username': self.login_account[0],
                'pf.pass': self.login_account[1],
                'pf.userType': 'cco',
                'pf.TargetResource': '?'
            }
            resp = self.session.post(login_url.group(1), data=data)
            if resp.status_code == 200:
                # Enter the authentication interface "Two-Factor Authentication"
                sig_request = re.search("'sig_request': '(.+?)(:APP.+?)'", resp.text)
                post_action = re.search("'post_action': '(.+?)'", resp.text)
                referer = 'https://cloudsso.cisco.com/' + post_action.group(1)
                duo_security_url = 'https://api-dbbfec7f.duosecurity.com/frame/web/v1/auth?'
                authentication_url = '{}tx={}&parent={}&v={}'.format(duo_security_url, sig_request.group(1),
                                                                     referer, '2.6')
                data = {
                    'tx': sig_request.group(1),
                    'parent': referer,
                    'referer': referer,
                    'screen_resolution_width': '1920',
                    'screen_resolution_height': '1080',
                    'color_depth': '24',
                    'is_cef_browser': 'false',
                    'is_ipad_os': 'false',
                    'react_support': 'True'
                }
                # Request for certification --> https://api-dbbfec7f.duosecurity.com/frame/web/v1/auth?
                resp = self.session.post(authentication_url, data=data)

                # 2020/11/12 update，Due to authentication interface upgrade
                if resp.status_code == 200:  # Gets multiple authentication parameters to start authentication
                    capture_params = ['sid', 'akey', 'txid', 'response_timeout', 'parent',
                                      'duo_app_url', 'eh_service_url', 'eh_download_link', 'is_silent_collection']
                    verify_param_dict = {}
                    for param in capture_params:
                        regex = r'type="hidden" name="{}" value="?(.+?)"?\s?/?>'.format(param)
                        matched = html.unescape(re.search(regex, resp.text).group(1))  # Unescape HTML
                        verify_param_dict[param] = matched

                    resp = self.session.post(authentication_url, data=verify_param_dict)
                    if '302' in str(resp.history):  # Redirect into the mobile phone verification interface
                        data = {
                            'sid': verify_param_dict['sid'],
                            'device': 'phone1',
                            'factor': 'Passcode',  # Use mobile pass code login
                            'passcode': authentication_code,
                            'out_of_date': 'False',
                            'days_out_of_date': '0',
                            'days_to_block': 'None'
                        }
                        # data = {
                        #     'sid': verify_param_dict['sid'],
                        #     'device': 'phone1',
                        #     'factor': 'Duo Push',  # Use mobile phone to push login
                        #     'dampen_choice': 'true',
                        #     'out_of_date': 'False',
                        #     'days_out_of_date': '0',
                        #     'days_to_block': 'None'
                        # }
                        # Start validation
                        resp = self.session.post(self.verification_prompt_url, data=data)
                        if resp.status_code == 200:
                            # input('Please use your mobile phone to verify the login request'
                            #       ' [Press enter to continue after verification]: ')
                            data = {
                                'sid': verify_param_dict['sid'],
                                'txid': resp.json()['response']['txid']
                            }
                            # Get validation results
                            resp = self.session.post(self.verification_status_url, data=data)
                            if resp.status_code == 200:
                                status_result_url = self.verification_source_url + resp.json()['response']['result_url']
                                data = {
                                    'sid': verify_param_dict['sid'],
                                }
                                # Gets the cookie for the validation result
                                resp = self.session.post(status_result_url, data=data)
                                if resp.status_code == 200:
                                    authentication_url = resp.json()['response']['parent']
                                    sig_response = resp.json()['response']['cookie']
                                    data = {
                                        'sig_response': sig_response + sig_request.group(2)
                                    }
                                    # Retrieve the cookie and re-enter the authentication interface
                                    self.session.post(authentication_url, data=data)
                                    # Carry the authenticated cookie acquisition Token
                                    token_url = 'https://cesium.cisco.com/apps/machineservices/MachineDetails.svc/getToken'
                                    resp = self.session.get(token_url)
                                    token = resp.json()['session']
                                    # Adds a token to the crawler
                                    self.session.headers.update({
                                        'csession': token,
                                        '_csession': token
                                    })

    def set_ccc_login_cookies(self, login_cookie, login_session):
        """
        Manually add cookie and session to the crawler
        :param login_cookie: Manually enter the CCC website and copy the cookie to here
        :param login_session: Manually enter the CCC website and copy the session to here
        :return:
        """
        self.session.headers.update({
            'cookie': login_cookie,
            'csession': login_session,
            '_csession': login_session
        })

    def login_ccc(self, automatic_login=True, authentication_code=''):
        """
        Login to the CCC website
        :param bool automatic_login: If the value is False, you need to manually add cookie and cession to crawler
        :param str authentication_code: Fill in the Mobile pass code
        :return:
        """
        if automatic_login:
            try:
                self.login(authentication_code=authentication_code)
            except Exception as ex:
                raise ValueError(f'Please check whether the login account and mobile pass code are correct'
                                 f' or website may be upgraded\nRaise info: {ex}')
        else:
            print('You need to login the CCC website and press F12 to open the "developer tools" '
                  'and manually copy the cookie and csession values to start the crawler')
            while True:
                cookie = input('cookie: ')
                session = input('csession: ')
                if not cookie or not session:
                    print('Cookie and csession are empty, please fill in again')
                    continue
                break
            self.set_ccc_login_cookies(login_cookie=cookie, login_session=session)

        # Login token double check
        if not self.session.headers.get('csession') or not self.session.headers.get('_csession'):
            raise ValueError('The mobile pass code expires or website may be upgraded\nPlease fill in again!')
        print('Login CCC website successfully')

    def get_all_test_data(self, data={}):
        """
        Gets all crawl results after the request
        :param data: Fill in the request data for spider
        :return:
        """
        multi_search_url = 'https://cesium.cisco.com/polarissvcs/central_data/multi_search'
        resp = self.session.post(multi_search_url, data=json.dumps(data))
        if resp.status_code == 200:
            return resp.json()
        else:
            return None

    def get_measurement_data(self, serial_number='', download_file_list=['sequence_log'], request_params={}):
        """
        Gets the specified measurement file for the specified serial number
        :param str serial_number: Test serial number
        :param list download_file_list: Fill in the specified file type to download
        :param dict request_params: Fill in the request params for spider
        :return: (measurement type, measurement id)
        """
        measures_url = 'https://cesium.cisco.com/svclnx/cgi-bin/central_cs/services.py/meas/{}'.format(serial_number)
        resp = self.session.get(measures_url, params=request_params)
        if resp.status_code == 200:
            measures_data = resp.json()
            for each_data in measures_data['measurements']:  # Walk through each measurement file
                for file_type in download_file_list:
                    if file_type in each_data['limit_id']:  # Matches the specified file type
                        yield (file_type, each_data['measurement'])  # return the measurement type and id for download
            else:
                yield None

    def download_measurement_log(self, file_name='measurement.log', binary_id=''):
        """
        Download the measurement log to local
        :param file_name: Log file name
        :param binary_id: Measurement log id
        :return:
        """
        download_url = 'https://cesium.cisco.com/svclnx/cgi-bin/central_cs/services.py/binarymeas_data/run'
        data = {
            'binary_id': binary_id,
            'source': 'Apollo'
        }
        flag = False
        resp = self.session.post(download_url, data=json.dumps(data))
        if resp.status_code == 200:
            content = base64.b64decode(resp.text)  # Base64 decode
            with open(file_name, 'wb') as wf:
                wf.write(content)  # Write measurement log
            flag = True
        return flag

    def get_measurement_log_file(self, measurement_data, download_file_list=[]):
        """
        Get measurement log file
        :param dict measurement_data: Measurement data
        :param list download_file_list: Fill in the specified file type to download
        :return:
        """
        with self.thread_pool:  # Controls the number of thread pools
            serial_number = measurement_data['sernum']
            params = {
                'area': measurement_data['area'],
                'server': 'prod',
                'timeid': measurement_data['tst_id'],
                'uuttype': measurement_data['uuttype']
            }
            for measures in self.get_measurement_data(serial_number=serial_number,
                                                      download_file_list=download_file_list,
                                                      request_params=params):
                if measures:
                    test_time = measurement_data['rectime'].replace(' ', '_').replace(':', '-')
                    test_status = measurement_data['attributes'].get('TEST') or 'PASS'
                    if ':' in test_status:
                        test_status = test_status.split(':')[0]
                    # Log name = 'ApolloServer - SN - TestTime - TestStatus - MeasuresType.log'
                    log_name = '{}_{}_{}_{}_{}.log'.format(measurement_data['machine'], serial_number,
                                                           test_time, test_status, measures[0])
                    # Skip duplicate test logs
                    if log_name in self.download_results:
                        continue
                    # Download the test log file
                    flag = self.download_measurement_log(file_name=log_name, binary_id=measures[1])
                    if flag:
                        self.download_results.append(log_name)
                        print('Download the file << {} >> succeeded'.format(log_name))
                    else:
                        # If download the test log fail, try again
                        time.sleep(1)
                        flag = self.download_measurement_log(file_name=log_name, binary_id=measures[1])
                        if flag:
                            self.download_results.append(log_name)
                            print('Download the file << {} >> succeeded'.format(log_name))
                        else:
                            print('Download the file << {} >> failed !!!')

    def start_crawl(self, first_request_data={}, download_file_list=[]):
        """
        Start the CCC crawler
        :param dict first_request_data: Fill in the first request data for spider
        :param list download_file_list: Fill in the specified file type to download
        :return:
        """
        all_data = self.get_all_test_data(data=first_request_data)
        if not all_data or not all_data['results']:
            raise ValueError('No data was found, Please check that the information you entered is correct!')
        print('Crawling all test data is completed, Total: {}'.format(len(all_data['results'])))

        self.download_results = []
        threads = []
        print('Start multi-threading to download the measurement file')
        for each_data in all_data['results']:
            t = threading.Thread(target=self.get_measurement_log_file, args=(each_data, download_file_list))
            t.daemon = True
            threads.append(t)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()
        print('All the measurement files have been downloaded')


class Calendar(object):

    def __init__(s, point=None, position=None):
        s.master = tk.Toplevel()
        s.master.withdraw()
        fwday = calendar.SUNDAY
        year = datetime.now().year
        month = datetime.now().month
        locale = None
        sel_bg = '#ecffc4'
        sel_fg = '#05640e'
        s._date = datetime(year, month, 1)
        s._selection = None
        s.G_Frame = ttk.Frame(s.master)
        s._cal = s.__get_calendar(locale, fwday)
        s.__setup_styles()
        s.__place_widgets()
        s.__config_calendar()
        s.__setup_selection(sel_bg, sel_fg)
        s._items = [s._calendar.insert('', 'end', values='') for _ in range(6)]
        s._update()
        s.G_Frame.pack(expand=1, fill='both')
        s.master.overrideredirect(1)
        s.master.update_idletasks()
        width, height = s.master.winfo_reqwidth(), s.master.winfo_reqheight()
        if point and position:
            if position == 'ur':
                x, y = point[0], point[1] - height
            elif position == 'lr':
                x, y = point[0], point[1]
            elif position == 'ul':
                x, y = point[0] - width, point[1] - height
            elif position == 'll':
                x, y = point[0] - width, point[1]
            else:
                x = y = None
        else:
            x, y = (s.master.winfo_screenwidth() - width) / 2, (s.master.winfo_screenheight() - height) / 2
        s.master.geometry('%dx%d+%d+%d' % (width, height, x, y))
        s.master.after(300, s._main_judge)
        s.master.deiconify()
        s.master.focus_set()
        s.master.wait_window()

    def __get_calendar(s, locale, fwday):
        if locale is None:
            return calendar.TextCalendar(fwday)
        else:
            return calendar.LocaleTextCalendar(fwday, locale)

    def __setitem__(s, item, value):
        if item in ('year', 'month'):
            raise AttributeError("attribute '%s' is not writeable" % item)
        elif item == 'selectbackground':
            s._canvas['background'] = value
        elif item == 'selectforeground':
            s._canvas.itemconfigure(s._canvas.text, item=value)
        else:
            s.G_Frame.__setitem__(s, item, value)

    def __getitem__(s, item):
        if item in ('year', 'month'):
            return getattr(s._date, item)
        elif item == 'selectbackground':
            return s._canvas['background']
        elif item == 'selectforeground':
            return s._canvas.itemcget(s._canvas.text, 'fill')
        else:
            r = ttk.tclobjs_to_py({item: ttk.Frame.__getitem__(s, item)})
            return r[item]

    def __setup_styles(s):
        style = ttk.Style(s.master)
        arrow_layout = lambda dir: (
            [('Button.focus', {'children': [('Button.%sarrow' % dir, None)]})]
        )
        style.layout('L.TButton', arrow_layout('left'))
        style.layout('R.TButton', arrow_layout('right'))

    def __place_widgets(s):
        input_judgment_num = s.master.register(s.input_judgment)
        hframe = ttk.Frame(s.G_Frame)
        gframe = ttk.Frame(s.G_Frame)
        bframe = ttk.Frame(s.G_Frame)
        hframe.pack(in_=s.G_Frame, side='top', pady=5, anchor='center')
        gframe.pack(in_=s.G_Frame, fill=tk.X, pady=5)
        bframe.pack(in_=s.G_Frame, side='bottom', pady=5)
        lbtn = ttk.Button(hframe, style='L.TButton', command=s._prev_month)
        lbtn.grid(in_=hframe, column=0, row=0, padx=12)
        rbtn = ttk.Button(hframe, style='R.TButton', command=s._next_month)
        rbtn.grid(in_=hframe, column=5, row=0, padx=12)
        s.CB_year = ttk.Combobox(hframe, width=5, values=[str(year) for year in
                                                          range(datetime.now().year, datetime.now().year - 11, -1)],
                                 validate='key', validatecommand=(input_judgment_num, '%P'))
        s.CB_year.current(0)
        s.CB_year.grid(in_=hframe, column=1, row=0)
        s.CB_year.bind('<KeyPress>', lambda event: s._update(event, True))
        s.CB_year.bind("<<ComboboxSelected>>", s._update)
        tk.Label(hframe, text='Year', justify='left').grid(in_=hframe, column=2, row=0, padx=(0, 5))
        s.CB_month = ttk.Combobox(hframe, width=3, values=['%02d' % month for month in range(1, 13)], state='readonly')
        s.CB_month.current(datetime.now().month - 1)
        s.CB_month.grid(in_=hframe, column=3, row=0)
        s.CB_month.bind("<<ComboboxSelected>>", s._update)
        tk.Label(hframe, text='Month', justify='left').grid(in_=hframe, column=4, row=0)
        s._calendar = ttk.Treeview(gframe, show='', selectmode='none', height=7)
        s._calendar.pack(expand=1, fill='both', side='bottom', padx=5)
        ttk.Button(bframe, text="Confirm", width=7, command=lambda: s._exit(True))\
            .grid(row=0, column=0, sticky='ns', padx=20)
        ttk.Button(bframe, text="Cancel", width=7, command=s._exit).grid(row=0, column=1, sticky='ne', padx=20)
        tk.Frame(s.G_Frame, bg='#565656').place(x=0, y=0, relx=0, rely=0, relwidth=1, relheigh=2 / 200)
        tk.Frame(s.G_Frame, bg='#565656').place(x=0, y=0, relx=0, rely=198 / 200, relwidth=1, relheigh=2 / 200)
        tk.Frame(s.G_Frame, bg='#565656').place(x=0, y=0, relx=0, rely=0, relwidth=2 / 200, relheigh=1)
        tk.Frame(s.G_Frame, bg='#565656').place(x=0, y=0, relx=198 / 200, rely=0, relwidth=2 / 200, relheigh=1)

    def __config_calendar(s):
        cols = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
        s._calendar['columns'] = cols
        s._calendar.tag_configure('header', background='grey90')
        s._calendar.insert('', 'end', values=cols, tag='header')
        font = tkFont.Font()
        maxwidth = max(font.measure(col) for col in cols)
        for col in cols:
            s._calendar.column(col, width=maxwidth, minwidth=maxwidth,
                               anchor='center')

    def __setup_selection(s, sel_bg, sel_fg):
        def __canvas_forget(evt):
            canvas.place_forget()
            s._selection = None
        s._font = tkFont.Font()
        s._canvas = canvas = tk.Canvas(s._calendar, background=sel_bg, borderwidth=0, highlightthickness=0)
        canvas.text = canvas.create_text(0, 0, fill=sel_fg, anchor='w')
        canvas.bind('<Button-1>', __canvas_forget)
        s._calendar.bind('<Configure>', __canvas_forget)
        s._calendar.bind('<Button-1>', s._pressed)

    def _build_calendar(s):
        year, month = s._date.year, s._date.month
        cal = s._cal.monthdayscalendar(year, month)
        for indx, item in enumerate(s._items):
            week = cal[indx] if indx < len(cal) else []
            fmt_week = [('%02d' % day) if day else '' for day in week]
            s._calendar.item(item, values=fmt_week)

    def _show_select(s, text, bbox):
        x, y, width, height = bbox
        textw = s._font.measure(text)
        canvas = s._canvas
        canvas.configure(width=width, height=height)
        canvas.coords(canvas.text, (width - textw) / 2, height / 2 - 1)
        canvas.itemconfigure(canvas.text, text=text)
        canvas.place(in_=s._calendar, x=x, y=y)

    def _pressed(s, evt=None, item=None, column=None, widget=None):
        if not item:
            x, y, widget = evt.x, evt.y, evt.widget
            item = widget.identify_row(y)
            column = widget.identify_column(x)
        if not column or not item in s._items:
            return
        item_values = widget.item(item)['values']
        if not len(item_values):
            return
        text = item_values[int(column[1]) - 1]
        if not text:
            return
        bbox = widget.bbox(item, column)
        if not bbox:
            s.master.after(20, lambda: s._pressed(item=item, column=column, widget=widget))
            return
        text = '%02d' % text
        s._selection = (text, item, column)
        s._show_select(text, bbox)

    def _prev_month(s):
        s._canvas.place_forget()
        s._selection = None
        s._date = s._date - timedelta(days=1)
        s._date = datetime(s._date.year, s._date.month, 1)
        s.CB_year.set(s._date.year)
        s.CB_month.set(s._date.month)
        s._update()

    def _next_month(s):
        s._canvas.place_forget()
        s._selection = None
        year, month = s._date.year, s._date.month
        s._date = s._date + timedelta(
            days=calendar.monthrange(year, month)[1] + 1)
        s._date = datetime(s._date.year, s._date.month, 1)
        s.CB_year.set(s._date.year)
        s.CB_month.set(s._date.month)
        s._update()

    def _update(s, event=None, key=None):
        if key and event.keysym != 'Return': return
        year = int(s.CB_year.get())
        month = int(s.CB_month.get())
        if year == 0 or year > 9999: return
        s._canvas.place_forget()
        s._date = datetime(year, month, 1)
        s._build_calendar()
        if year == datetime.now().year and month == datetime.now().month:
            day = datetime.now().day
            for _item, day_list in enumerate(s._cal.monthdayscalendar(year, month)):
                if day in day_list:
                    item = 'I00' + str(_item + 2)
                    column = '#' + str(day_list.index(day) + 1)
                    s.master.after(100, lambda: s._pressed(item=item, column=column, widget=s._calendar))

    def _exit(s, confirm=False):
        if not confirm: s._selection = None
        s.master.destroy()

    def _main_judge(s):
        try:
            if s.master.focus_displayof() == None or 'toplevel' not in str(s.master.focus_displayof()):
                s._exit()
            else:
                s.master.after(10, s._main_judge)
        except Exception:
            s.master.after(10, s._main_judge)

    def selection(s):
        if not s._selection: return None
        year, month = s._date.year, s._date.month
        return str(datetime(year, month, int(s._selection[0])))[:10]

    @staticmethod
    def input_judgment(content):
        if content.isdigit() or content == "":
            return True
        else:
            return False


class SpiderGui(object):

    def __init__(self):
        self.build_storage_folder()
        self.root = tk.Tk()
        self.root.geometry('640x410')
        self.root.title('Download CCC Test Log Tool                         @Author: Evan Liu | @Version: 2.0')

        self.build_date_frame()
        self.build_request_data_frame()
        self.build_select_status_frame()
        self.build_display_board_frame()
        self.build_button_frame()
        self.set_gui_center(window=self.root, x=2.5, y=4)
        self.logined_flag = False

    def build_display_board_frame(self):
        frames = tk.Frame(relief='ridge', borderwidth=1)
        tk.Label(frames, text='Display Board').grid(row=0, column=0)
        self.board = tk.Text(frames, width=50, height=20)
        self.board.grid(row=1, column=0)
        frames.grid(row=0, column=1, rowspan=2, sticky=tk.NSEW)

    def build_button_frame(self):
        self.button_frame = tk.Frame(relief='ridge', borderwidth=1)
        tk.Label(self.button_frame, text='Login User: ', bg='Wheat').grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        self.login_laber = tk.Label(self.button_frame, text='Unknown', bg='Gold')
        self.login_laber.grid(row=0, column=1, sticky=tk.W, pady=5)
        self.login_button = tk.Button(self.button_frame, text='Login', command=self.build_login_window, bg='aqua')
        self.login_button.grid(row=0, column=2, sticky=tk.W, padx=10, pady=5)

        self.running_label_1 = tk.Label(self.button_frame, text='Running Status: ', bg='Wheat')
        self.running_label_1.grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        self.running_label_2 = tk.Label(self.button_frame, text='Idle', bg='Gold')
        self.running_label_2.grid(row=1, column=1, sticky=tk.W, pady=5)

        tk.Button(self.button_frame, text='Cleanup', command=self.cleanup, bg='#AFEEEE') \
            .grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        self.execute_button = tk.Button(self.button_frame, text='Execute', command=self.start_crawl, bg='#98FB98')
        self.execute_button.grid(row=2, column=1, sticky=tk.W, pady=5)
        tk.Button(self.button_frame, text='Quit', command=self.tk_quit, bg='LightSkyBlue')\
            .grid(row=2, column=2, sticky=tk.W, padx=45, pady=5)
        self.button_frame.grid(row=2, column=1, sticky=tk.NSEW, rowspan=2, columnspan=3)

    def tk_quit(self):
        try:
            os.system('taskkill /im download_ccc_test_log_tool.exe /f')  # Force kill process
        except Exception:
            pass
        self.root.destroy()
        self.root.quit()

    def cleanup(self):
        for text in [self.uut_type, self.serial_number, self.area, self.machine]:
            text.delete(1.0, tk.END)

    def build_select_status_frame(self):
        frames = tk.Frame(relief='ridge', borderwidth=5)
        tk.Label(frames, text='Select Download Log').grid(row=0, column=0)
        self.seq_log = tk.StringVar()
        self.uut_buffer = tk.StringVar()
        enable_check2 = tk.Checkbutton(frames, text="Sequence_log", variable=self.seq_log,
                                       offvalue='', onvalue='sequence_log')
        enable_check2.select()
        enable_check2.grid(row=1, column=0, sticky=tk.W)
        enable_check3 = tk.Checkbutton(frames, text="UUT_buffer", variable=self.uut_buffer,
                                       offvalue='', onvalue='UUT_buffer')
        enable_check3.select()
        enable_check3.grid(row=2, column=0, sticky=tk.W)
        self.use_debug = tk.StringVar()
        tk.Checkbutton(frames, text="Use Debug DB", variable=self.use_debug,
                       offvalue='', onvalue='dev').grid(row=3, column=0, sticky=tk.W)

        tk.Label(frames, text='Select Status').grid(row=0, column=1, sticky=tk.W, padx=30)
        self.fail_status = tk.StringVar()
        self.pass_status = tk.StringVar()
        self.about_status = tk.StringVar()
        enable_check1 = tk.Checkbutton(frames, text="Failed", variable=self.fail_status,
                                       offvalue='', onvalue='F')
        enable_check1.select()
        enable_check1.grid(row=1, column=1, sticky=tk.W, padx=30)
        tk.Checkbutton(frames, text="Passed", variable=self.pass_status,
                       offvalue='', onvalue='P').grid(row=2, column=1, sticky=tk.W, padx=30)
        tk.Checkbutton(frames, text="Aborted", variable=self.about_status,
                       offvalue='', onvalue='A').grid(row=3, column=1, sticky=tk.W, padx=30)
        frames.grid(row=2, column=0, sticky=tk.NSEW)

    def build_request_data_frame(self):
        frames = tk.Frame(relief='ridge', borderwidth=5)
        tk.Label(frames, text='UUT Type').grid(row=0, column=0)
        self.uut_type = tk.Text(frames, width=18, height=5)
        self.uut_type.grid(row=1, column=0)

        tk.Label(frames, text='Serial Number').grid(row=0, column=1)
        self.serial_number = tk.Text(frames, width=18, height=5)
        self.serial_number.grid(row=1, column=1)

        tk.Label(frames, text='Area').grid(row=2, column=0)
        self.area = tk.Text(frames, width=18, height=5)
        self.area.grid(row=3, column=0)

        tk.Label(frames, text='Machine').grid(row=2, column=1)
        self.machine = tk.Text(frames, width=18, height=5)
        self.machine.grid(row=3, column=1)
        frames.grid(row=1, column=0, sticky=tk.NSEW)

    def build_date_frame(self):
        frames = tk.Frame(relief='ridge', borderwidth=1)
        tk.Label(frames, text='StartDate: ').grid(row=0, column=0, sticky=tk.W)
        self.start_time = tk.StringVar()
        entry1 = tk.Entry(frames, textvariable=self.start_time)
        self.start_time.set(self.get_start_date())
        entry1.grid(row=0, column=1, sticky=tk.W)
        tk.Button(frames, text='Select', bg='Tan', command=self.select_start_date) \
            .grid(row=0, column=2)

        tk.Label(frames, text='EndDate: ').grid(row=1, column=0, sticky=tk.W)
        self.end_time = tk.StringVar()
        entry2 = tk.Entry(frames, textvariable=self.end_time)
        self.end_time.set(datetime.now().strftime('%Y-%m-%d') + ' 00:00:00')
        entry2.grid(row=1, column=1)
        tk.Button(frames, text='Select', bg='PeachPuff', command=self.select_end_date) \
            .grid(row=1, column=2)
        frames.grid(row=0, column=0, sticky=tk.NSEW)

    def select_start_date(self):
        width, height = self.root.winfo_reqwidth() + 50, 50
        x, y = (self.root.winfo_screenwidth() - width) / 1.5, (self.root.winfo_screenheight() - height) / 2
        for date in [Calendar((x, y), 'ur').selection()]:
            if date:
                self.start_time.set(date + ' 00:00:00')

    def select_end_date(self):
        width, height = self.root.winfo_reqwidth() + 50, 50
        x, y = (self.root.winfo_screenwidth() - width) / 1.5, (self.root.winfo_screenheight() - height) / 2
        for date in [Calendar((x, y), 'ur').selection()]:
            if date:
                self.end_time.set(date + ' 00:00:00')

    @staticmethod
    def get_start_date():
        year, month, day = datetime.now().strftime('%Y-%m-%d').split('-')
        months = [i for i in range(1, 13)]
        for index, value in enumerate(months):
            if int(month) == value:
                month = index
                break
        return '-'.join([year, '{:02}'.format(months[month - 1]), day]) + ' 00:00:00'

    def build_login_window(self):
        self.window = tk.Toplevel(self.root)
        self.window.title('Login Window')
        self.window.wm_attributes("-topmost", True)
        tk.Label(self.window, text='CEC Username').grid(row=0, column=0)

        self.username = tk.StringVar()
        tk.Entry(self.window, textvariable=self.username).grid(row=1, column=0)
        tk.Label(self.window, text='CEC Password').grid(row=0, column=1)

        self.password = tk.StringVar()
        tk.Entry(self.window, textvariable=self.password, show='*').grid(row=1, column=1)
        tk.Label(self.window, text='Mobile Pass Code').grid(row=2, column=0)

        self.pass_code = tk.StringVar()
        tk.Entry(self.window, textvariable=self.pass_code).grid(row=3, column=0, sticky=tk.NSEW)

        self.login_confirm = tk.Button(self.window, text='Login', command=self.start_login, bg='MediumSpringGreen')
        self.login_confirm.grid(row=3, column=1)
        self.set_gui_center(window=self.window, x=1.4, y=3)

    @staticmethod
    def build_storage_folder():
        # Create a folder to store all the download results
        if not os.path.isdir('download_results'):
            os.mkdir('download_results')
        os.chdir('download_results')

    @staticmethod
    def set_gui_center(window, x=None, y=None):
        window.update_idletasks()
        x_info = (window.winfo_screenwidth() - window.winfo_reqwidth()) / x
        y_info = (window.winfo_screenwidth() - window.winfo_reqwidth()) / y
        window.geometry('+%d+%d' % (x_info, y_info))

    def input_info_check(self):
        # Format input parameter (uut_type & serial_number & area & machine)
        uut_type = self.uut_type.get(1.0, tk.END).strip()
        serial_number = self.serial_number.get(1.0, tk.END).strip()
        area = self.area.get(1.0, tk.END).strip()
        machine = self.machine.get(1.0, tk.END).strip()
        input_result = []
        for input_info in [uut_type, serial_number, area, machine]:
            if input_info:
                if len(input_info.splitlines()) > 1:
                    _uut_type = []
                    for value in input_info.splitlines():
                        if value:
                            _uut_type.append(value)
                    _uut_type = ','.join(_uut_type)
                else:
                    _uut_type = input_info
            else:
                _uut_type = ''
            input_result.append(_uut_type)

        # Format input parameter (test status)
        select_status = []
        for status in [self.fail_status.get(), self.pass_status.get(), self.about_status.get()]:
            if status:
                select_status.append(status)
        select_status = ','.join(select_status)

        # Format input parameter (download log type)
        select_download_log = []
        for status in [self.seq_log.get(), self.uut_buffer.get()]:
            if status:
                select_download_log.append(status)

        # Check use_debug
        if not self.use_debug.get():
            use_debug = None
        else:
            use_debug = self.use_debug.get()

        final_result = {
            'start_time': self.start_time.get(),
            'end_time': self.end_time.get(),
            'uut_type': input_result[0],
            'serial_number': input_result[1],
            'area': input_result[2],
            'machine': input_result[3],
            'select_status': select_status,
            'select_download_log': select_download_log,
            'use_debug': use_debug,
        }

        # Check start time and end time
        if final_result['start_time'] and final_result['end_time']:
            time_format = re.compile(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$')
            for i in [final_result['start_time'], final_result['end_time']]:
                matched = re.match(time_format, i)
                if not matched:
                    messagebox.showwarning('Warning', 'Wrong start date or end date format. Please enter again!')
                    return None
        else:
            messagebox.showwarning('Warning', 'Start time or end time is null. Please enter again!')
            return None

        # Check download log type
        if not final_result['select_download_log']:
            messagebox.showwarning('Warning', 'Select download log is null. Please enter again!')
            return None

        # Check test status
        if not final_result['select_status']:
            messagebox.showwarning('Warning', 'Select status is null. Please enter again!')
            return None

        # Check uut_type & serial_number & area & machine
        if not final_result['uut_type'] and not final_result['serial_number'] and \
                not final_result['area'] and not final_result['machine']:
            messagebox.showwarning('Warning', 'Search information cannot be empty. Please enter again!')
            return None

        return final_result

    def show_running_bar(self):
        self.running_label_1.config(text='In Progress: ')
        self.running_label_2.destroy()
        self.bar = ttk.Progressbar(self.button_frame, mode="indeterminate", orient=tk.HORIZONTAL)
        self.bar.start(8)
        self.bar.grid(row=1, column=1, sticky=tk.W, pady=5)

    def show_idle_status(self):
        self.running_label_1.config(text='Running Status: ')
        self.bar.destroy()
        self.running_label_2 = tk.Label(self.button_frame, text='Idle', bg='Gold')
        self.running_label_2.grid(row=1, column=1, sticky=tk.W, pady=5)

    def start_login(self):
        threading.Thread(target=self._start_login, args=()).start()

    def _start_login(self):
        if not self.username.get():
            messagebox.showwarning('Warning', 'CEC username is null. Please enter again!')
            return
        if not self.password.get():
            messagebox.showwarning('Warning', 'CEC password is null. Please enter again!')
            return
        if not self.pass_code.get():
            messagebox.showwarning('Warning', 'Mobile pass code is null. Please enter again!')
            return
        global spider
        spider = CCCSpider(login_account=(self.username.get(), self.password.get()))
        try:
            self.show_running_bar()
            self.login_confirm.config(text='Logining', state='disable')
            self.login_button.config(text='Logining', state='disable')
            spider.login_ccc(authentication_code=self.pass_code.get())
        except Exception as es:
            self.login_confirm.config(text='Login', state='active')
            self.login_button.config(text='Login', state='active')
            messagebox.showerror('Error', 'Login failure\nError msg: {}'.format(es))
            return
        else:
            self.window.destroy()
            self.login_button.config(text='Logined', state='disable')
            self.login_laber.config(text=self.username.get())
            self.logined_flag = True
        finally:
            self.show_idle_status()

    def show_download_results(self, results):
        self.board.delete(1.0, tk.END)
        if results:
            self.board.insert(tk.END, 'The total number of downloaded test logs is {}\n\n'.format(len(results)))
            for index, each_result in enumerate(results):
                self.board.insert(tk.END, '{}. << {} >>\n\n'.format(index + 1, each_result))
        else:
            self.board.insert(tk.END, 'The download result is empty!')

    def start_crawl(self):
        threading.Thread(target=self._start_crawl, args=()).start()

    def _start_crawl(self):
        if not self.logined_flag:
            messagebox.showwarning('Warning', 'Please login first')
            return

        all_input_info = self.input_info_check()
        if not all_input_info:
            return

        request_data = {
            'sernum': all_input_info['serial_number'],
            'uuttype': all_input_info['uut_type'],
            'area': all_input_info['area'],
            'machine': all_input_info['machine'],
            'location': '',
            'test': '',
            'passfail': all_input_info['select_status'],
            'start_time': all_input_info['start_time'],
            'end_time': all_input_info['end_time'],
            'dataset': 'test_results',
            'database': all_input_info['use_debug'],
            'start': 0,
            'limit': '5000',
            'user': '',
            'attribute': '',
            'fttd': 0,
            'lttd': 0,
            'ftta': 0,
            'passedsampling': 0,
        }
        print('-' * 40)
        print('request_data:\n{}'.format(request_data))
        print('-' * 40)
        try:
            self.board.delete(1.0, tk.END)
            self.board.insert(tk.END, 'Please Wait...')
            self.show_running_bar()
            self.execute_button.config(text='Executing', state='disable')
            spider.start_crawl(first_request_data=request_data,
                               download_file_list=all_input_info['select_download_log'])
        except Exception as es:
            messagebox.showerror('Error', 'Crawl failure\nError msg: {}'.format(es))
            return
        else:
            messagebox.showinfo('Info', 'Crawl successful, All the test log have been downloaded')
        finally:
            self.show_idle_status()
            self.execute_button.config(text='Execute', state='active')
        self.show_download_results(results=spider.download_results)


if __name__ == '__main__':
    spider_gui = SpiderGui()
    spider_gui.root.mainloop()
