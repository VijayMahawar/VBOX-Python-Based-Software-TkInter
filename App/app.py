import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
#import matplotlib.animation as animation
#from matplotlib import style

import tkinter as tk
from tkinter import ttk
from pandastable import Table, TableModel

LARGE_FONT = ('Verdana', 12)
NORM_FONT = ('Verdana', 10)
SMALL_FONT = ('Verdana', 8)

import numpy as np 
import matplotlib.pyplot as plt
import pandas as pd
import os, glob
import folium as f
import seaborn as sns
import ulabtools as ut
plt.style.use('classic')

from tkinter.filedialog import askopenfilenames
from tkinter.filedialog import asksaveasfile
from tkinter import messagebox

LARGE_FONT = ('Verdana', 12)
NORM_FONT = ('Verdana', 10)
SMALL_FONT = ('Verdana', 8)       

from tkinter import *  
from PIL import ImageTk,Image  

#from vbox_app_scripts.functions import *
from Scripts.functions import *

class vbox_procesing:
    def __init__(self, master):
        master.iconbitmap(r'favicon_transparent.ico')    
        master.wm_title('Vbox App - v1.2')
        
        width = master.winfo_screenwidth()
        height = master.winfo_screenheight()
        master.geometry('%sx%s' % (width, height))
        
        menubar = Menu(master, tearoff=0)
        master.config(menu=menubar)
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label='Open', command = lambda: self.load_project(master))
        filemenu.add_command(label='Save', command = lambda: self.save_project(master))
        filemenu.add_command(label='Save As', command = lambda: self.save_as_project(master))
        filemenu.add_separator()
        filemenu.add_command(label='Export Report to HTML', command = lambda: popupmsg('Not yet supported!'))
        filemenu.add_command(label='Export Report to PDF', command = lambda: popupmsg('Not yet supported!'))
        filemenu.add_separator()
        filemenu.add_command(label='Exit', command = lambda: on_closing(master))
        menubar.add_cascade(label="File", menu=filemenu)
        self.menubar_object = menubar
        self.make_navigation_menu = True
        
        frame = ttk.Frame(master)        
        self.frame_check = frame                
        self.start_page(master)
            
    def start_page(self, master):
        self.destroy_frame()
        
        frame = ttk.Frame(master)        
        frame.pack(side='top', padx=400, ipadx=10, ipady=10)
        frame.grid_columnconfigure(0, weight=1)
        
        canvas = Canvas(frame, width = 700, height = 400)   
        canvas.pack(padx=200, pady=50)
        canvas.grid_columnconfigure(0, weight=1)
        img = ImageTk.PhotoImage(Image.open(r"Vbox_Tool_Logo-removebg-removebg.png"),
                                master=frame)  
        self.img_store=img
        canvas.create_image(5,5, anchor=NW, image=img)       
        
        
        frame1 = ttk.Frame(master)
        frame1.pack(side='top')
        discrip = 'Vbox Data Processing Application. Designed and Developed at Michelin CTIN. All Rights Reserved'
        label = ttk.Label(frame1, text=discrip,  font=LARGE_FONT)
        label.pack()        
        button1 = ttk.Button(frame1, text = 'Agree and Start Loading Data', command= lambda: self.page_one(master))
        button1.pack()        
        button2 = ttk.Button(frame1, text = 'Disagree', command=lambda: close_tkinter_app(master))
        button2.pack()
        
        self.frame_check = [frame, frame1]        
        return frame    
    def destroy_frame(self):
        if isinstance(self.frame_check, list):
            [f.destroy() for f in self.frame_check]
        else:
            self.frame_check.destroy()    
    def page_one(self, master):  
        self.destroy_frame()
        
        frame = ttk.Frame(master)      
        frame.pack()
        
        label = tk.Label(frame, text='Data Loading Wizard',  font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        button1 = ttk.Button(frame, text = 'Load Data', command = lambda: self.data_loading(master))
        button1.pack()
        button2 = ttk.Button(frame, text = 'Back to Home', command = lambda: self.start_page(master))
        button2.pack()
        
        self.frame_check = frame    
    def data_loading(self, master):                
        self.data, self.file_list, curr_dir = load_data_with_progress_bar()
        self.curr_dir = curr_dir
        self.is_already_exist = False
        
        file_size = pd.Series({fn:round(os.stat(curr_dir+'//'+fn).st_size/1000,2) for fn in self.file_list}).to_frame('filesize(kb)')
        self.file_size = file_size.sort_values(by='filesize(kb)', ascending=True)
        

            
            
     
        self.frame_check.destroy()
        frame = ttk.Frame(master)
        frame.pack(side='top', fill='both', expand=True)
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(1, weight=1)
        #         frame.pack()
        self.frame_check = frame            

        label = tk.Label(frame, text='Data Loading Done!',  font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        button1 = ttk.Button(frame, text = 'Proceed to Data Process Page',
                            command = lambda: self.data_clean_status_page(master))
        button1.pack()

        button2 = ttk.Button(frame, text = 'Home',
                            command = lambda: self.start_page(master))
        button2.pack()
        
    def data_clean_status_page(self, master):
        self.frame_check.destroy()
        frame = ttk.Frame(master)        
        frame.pack()
        self.frame_check = frame
    
        label = tk.Label(frame, text='Data Cleaning Step',  font=LARGE_FONT)
        label.grid(row=0, column=1)
        
        label1 = ttk.Label(frame, text='Set Distanc(kms) per VboxFile to filter data')
        label1.grid(row=1, column=0, sticky='w')
        entry1_var = tk.DoubleVar(frame)
        entry1_var.set(1)
        entry1 = ttk.Entry(frame, textvariable=entry1_var)
        entry1.grid(row=1, column=1)
        self.trip_distance_threshold = entry1_var
        
        label2 = ttk.Label(frame, text='Set DataCount (Number of Data Points) per VboxFile to filter data')
        label2.grid(row=2, column=0, sticky='w')
        entry2_var = tk.DoubleVar(frame)
        entry2_var.set(100)
        entry2 = ttk.Entry(frame, textvariable=entry2_var)
        entry2.grid(row=2, column=1)
        self.data_count_threshold = entry2_var
        
        button1 = ttk.Button(frame, text = 'Clean Data',
                            command = lambda: self.clean_data_page(master))
        button1.grid(row=3, column=1)

        button2 = ttk.Button(frame, text = 'Home',
                            command = lambda: self.start_page(master))
        button2.grid(row=4, column=1)           
    def clean_data_page(self, master):        
        inf_pb = indeterminant_progress_bar('Data Cleaning', 'Data is being cleaned...')
        self.clean_data, self.total_files, self.total_files_dropped, self.drop_summary, self.files_invalid = clean_data(self.data, self.trip_distance_threshold.get(), self.data_count_threshold.get())        
        
        if self.clean_data.empty:
            inf_pb.destroy()
            popupmsg('No data to process. Try again loading more data or adjust clean data parameters')            
        else:
            self.sampling_frequency = ut.generic.get_sampling_frequency(self.clean_data.reset_index()['timestamp'].diff().dropna().apply(lambda x: x.total_seconds()))[1]
            inf_pb.destroy()
            self.frame_check.destroy()
            frame = ttk.Frame(master)
            frame.pack()      
            self.frame_check = frame        


            label = tk.Label(frame, text='Data Process Step',  font=LARGE_FONT)
            label.grid(row=0, column=1, sticky='w')

            label = tk.Label(frame, text='Data Sampling Frequency')
            label.grid(row=1, column=0, sticky='w')

            label_fr = tk.Label(frame, text='{} Hz'.format(str(self.sampling_frequency)))
            label_fr.grid(row=1, column=1)

            label1 = ttk.Label(frame, text='Set Cut of Frequency (in Hz)')
            label1.grid(row=2, column=0, sticky='w')
            entry1_var = tk.DoubleVar(frame)
            entry1_var.set(0.1)
            entry1 = ttk.Entry(frame, textvariable=entry1_var)
            entry1.grid(row=2, column=1)
            self.cut_off_frequency = entry1_var

            button1 = ttk.Button(frame, text = 'Data Process', command = lambda: self.data_process_page(master))
            button1.grid(row=3, column=1)
            button2 = ttk.Button(frame, text = 'Back', command = lambda: self.data_clean_status_page(master))
            button2.grid(row=4, column=1)
    def data_process_page(self, master):
        if self.clean_data.empty:
            popupmsg('No data to process. Try again loading more data or adjust clean data parameters')
        else:
            self.process_data, self.unprocessed_files = data_process_with_progress_bar(self.clean_data, fs=self.cut_off_frequency.get())
            
            inf_pb = indeterminant_progress_bar('Data Summary', 'Data is being summarized.....')
            self.summary_vbox_files, self.summary, self.roc_table, self.vel_distance, self.straight_road = data_statistics(self.process_data)
            inf_pb.destroy()
            
            self.drop_summary = pd.concat([self.unprocessed_files, self.drop_summary])
            
            self.frame_check.destroy()
            frame = ttk.Frame(master)
            frame.pack(side='top', fill='both', expand=True)
            frame.grid_rowconfigure(1, weight=1)
            frame.grid_columnconfigure(1, weight=1)        

            self.frame_check = frame        

            label = tk.Label(frame, text='Data Process Done!',  font=LARGE_FONT)
            label.pack(pady=10, padx=10)
            button1 = ttk.Button(frame, text = 'Go to Dashboard', command = lambda: self.DashBoardPage(master))
            button1.pack()
            button2 = ttk.Button(frame, text = 'Back', command = lambda: self.data_clean_status_page(master))
            button2.pack()
            
    def Dashboard_page_map(self, master):
        self.frame_check.destroy()
        frame = ttk.Frame(master)
        frame.pack(side='top', fill='both', expand=True)
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(1, weight=1)        
        self.frame_check = frame
    
        label = tk.Label(frame, text='Track Truck',  font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        
        entry2_var = tk.IntVar(frame)
        entry2_var.set(10)
        entry2 = ttk.Entry(frame, textvariable=entry2_var)
        entry2.pack()
        self.track_data_cut = entry2_var
        
        myOptList = ['roc_abs', 'roc_abs', 'altitude_filt', 'speed_filt', 'long_accel_vbox_filt_corrected',
                     'lat_accel_vbox_filt', 'roc']
        var = tk.StringVar(frame)
        om = ttk.OptionMenu(frame, var, *myOptList)
        var.set(myOptList[0])
        om.pack()
        
        button1 = ttk.Button(frame, text = 'Track Truck',
                                command = lambda: draw_map(self.process_data, self.track_data_cut.get(), var.get()))
        button1.pack()
        button2 = ttk.Button(frame, text = 'Home', command = lambda: self.start_page(master))
        button2.pack()
        
    def DashBoardPage(self, master):       
        self.destroy_frame()
        inf_pb = indeterminant_progress_bar('Dash Board', 'Dashboard is being prepared.....')
      #Navigation Menu-------------------------------------------------------------------------------------------------         
        if self.make_navigation_menu:
            menubar = self.menubar_object
            navigation_menu = Menu(menubar, tearoff=0)
            navigation_menu.add_command(label='To Home Page', command = lambda: self.start_page(master))
            navigation_menu.add_command(label='To Data Loading Page', command = lambda: self.page_one(master))
            navigation_menu.add_command(label='To Data Cleaning Page', command = lambda: self.data_clean_status_page(master))
            #navigation_menu.add_command(label='To Data Process Page', command = lambda: self.clean_data_page(master))
            navigation_menu.add_command(label='To Dashboard Page', command = lambda: self.DashBoardPage(master))
            menubar.add_cascade(label="Navigation", menu=navigation_menu)
            self.menubar_object_from_dashboad_page = menubar
            self.make_navigation_menu = False
        else:
            None
      #Frames Creation------------------------------------------------------------------------------------------------- 
        note = ttk.Notebook(master, height=5000, width=5000)
        
        data_frame = ttk.Frame(master)
        note.add(data_frame, text='  Data  \n')
        
        ds_frame = ttk.Frame(master)   # first page, which would get widgets gridded into it
        note.add(ds_frame, text='  Data Summary  \n')        
        
        loading_status = ttk.Frame(master)
        note.add(loading_status, text='  Data Loading  \n  Status')
        
        RoC = ttk.Frame(master)
        note.add(RoC, text='  Radius of Curvature  \n  Summary')
        
        graph_frame = ttk.Frame(master)   # second page
        note.add(graph_frame, text='  Graphs  \n')
        
        graph_frame_speed = ttk.Frame(master)   # second page
        note.add(graph_frame_speed, text='  Speed \n  Distribution  ')
        
        graph_frame_bihist = ttk.Frame(master)   # second page
        note.add(graph_frame_bihist, text='  Accelerations  \n  BiHistogram  ')
        
        map_frame = ttk.Frame(master)
        note.add(map_frame, text='  Map  \n')
        
        note.pack(padx=10, pady=10)
      #Raw data show up---------------------------------------------------------------------------------------------------
        pt = Table(data_frame, dataframe=self.process_data.reset_index(),
                                showtoolbar=False, showstatusbar=False)
        pt.show()
        
      #Summary tables show up------------------------------------------------------------------------------------------------------
        #ds_frame.grid_rowconfigure(0, weight=1) # For row 0
        ds_frame.grid_columnconfigure(0, weight=1) # For column 0
        #ds_frame.grid_columnconfigure(1, weight=1) # For column 1
        
        ds_frame_1 = ttk.Frame(ds_frame)
        ds_frame_1.grid(padx=500, sticky='nsew')
        ds_frame_1.grid_columnconfigure(0, weight=1)
        label1 = ttk.Label(ds_frame_1, text='Usage Summary', font=LARGE_FONT)
        label1.grid(row=0, column=0)
        make_table(self.summary.reset_index(), ds_frame_1, col_width=400,
                  row_tree=1, column_tree=0,
                      row_scrollx=2, column_scrollx=0,              
                      row_scrolly=1, column_scrolly=1)

        ds_frame_2 = ttk.Frame(ds_frame)
        ds_frame_2.grid(pady=10)

        ds_frame_3 = ttk.Frame(ds_frame)
        ds_frame_3.grid()
        ds_frame_3.grid_columnconfigure(0, weight=1) 
        label2 = ttk.Label(ds_frame_3, text='Usage Summary per Vbox File', font=LARGE_FONT)
        label2.grid(row=0, column=0)
        make_table(self.summary_vbox_files.reset_index(), ds_frame_3, col_width=200, 
                   row_tree=1, column_tree=0, 
                   row_scrollx=2, column_scrollx=0, 
                   row_scrolly=1, column_scrolly=1)
      #Loading tables show up------------------------------------------------------------------------------------------------------
        
        loading_status_1 = ttk.Frame(loading_status)
        #loading_status_1.grid(padx=5, sticky='nsew')
        loading_status_1.pack(side = 'left', padx=50, fill='both', pady=50)
        loading_status_1.grid_columnconfigure(0, weight=1)
        label1 = ttk.Label(loading_status_1, text='Total Files = {}'.format(self.total_files), font=LARGE_FONT)
        label1.grid(row=0, column=0)
        make_table(self.file_size.reset_index().rename(columns={'index':'files'}), loading_status_1, col_width=200,
                  row_tree=1, column_tree=0,
                      row_scrollx=2, column_scrollx=0,              
                      row_scrolly=1, column_scrolly=1)


        loading_status_2 = ttk.Frame(loading_status)
        #loading_status_2.grid()
        #loading_status_2.grid_columnconfigure(0, weight=1)
        loading_status_2.pack(side='left', padx=50, fill='both', pady=50)
        loading_status_2.grid_columnconfigure(0, weight=1)
        label2 = ttk.Label(loading_status_2, text='Files Dropped = {}'.format(self.total_files_dropped), font=LARGE_FONT)
        label2.grid(row=0, column=0)
        make_table(self.drop_summary.reset_index().rename(columns={'index':'files'}), loading_status_2, col_width=200, 
                   row_tree=1, column_tree=0, 
                   row_scrollx=2, column_scrollx=0, 
                   row_scrolly=1, column_scrolly=1)
      #RoC tables show up------------------------------------------------------------------------------------------------------
       #Building Frames for RoC Table and Entry Table------------------------------------
        RoC_1 = ttk.Frame(RoC, borderwidth=10)
        #loading_status_1.grid(padx=5, sticky='nsew')
        RoC_1.pack(side = 'top', padx=50, expand=True)
        RoC_1.grid_columnconfigure(0, weight=1)
        
        entry_frame = ttk.Frame(RoC_1)
        entry_frame.pack(side = 'left', padx=50, expand=True)
  
        table_frame = ttk.Frame(RoC_1)
        table_frame.pack(side = 'left', padx=50, expand=True)
        table_frame.grid_columnconfigure(0, weight=1)        
        label1 = ttk.Label(table_frame, text='RoC Summary (% Distance Travelled)', font=LARGE_FONT)
        label1.grid(row=0, column=0)
        
        roc_table = self.roc_table.reset_index()
        roc_table = pd.concat([pd.Series(['' for x in range(self.roc_table.shape[1]+1)], index = roc_table.columns).to_frame().T,
                               roc_table]).reset_index()
        roc_table.loc[0, 'Velocity(km/h)']='Velocity(km/h)'
        roc_table.rename(columns={'Velocity(km/h)':'RoC(m)'}, inplace=True)
        roc_table = roc_table.drop('index', axis=1)
        
        make_table(roc_table, table_frame, col_width=100,
                  row_tree=1, column_tree=0,
                      row_scrollx=2, column_scrollx=0,              
                      row_scrolly=1, column_scrolly=1)        
       #Pie Chart--------------------------------------------------------------
        pie_frame = ttk.Frame(RoC)
        pie_frame.pack(side = 'left', padx=2, pady=20, expand=True)
        pie_frame.grid_columnconfigure(0, weight=1)
        
        pie_option = ttk.Frame(pie_frame)
        pie_option.pack(side = 'left', padx=10, pady=20, expand=True)
        pie_option.grid_columnconfigure(0, weight=1)
        pie_chart = ttk.Frame(pie_frame)
        pie_chart.pack(side = 'left', padx=10, pady=20, expand=True)
        pie_chart.grid_columnconfigure(0, weight=1)
        
        label1 = ttk.Label(pie_option, text='Road Conditions\nRoC Range (meters)')
        label1.grid(row=0, column=0, sticky='w', pady=(0,15))
        
        label1 = ttk.Label(pie_option, text='Very Tight')    
        label1.grid(row=1, column=0, sticky='w')
        entry1_var = tk.StringVar(pie_option)
        entry1_var.set('0-20')
        entry1 = ttk.Entry(pie_option, textvariable=entry1_var, width=10)
        entry1.grid(row=1, column=1)
        vt = entry1_var

        label1 = ttk.Label(pie_option, text='Tight')
        label1.grid(row=2, column=0, sticky='w')
        entry1_var = tk.StringVar(pie_option)
        entry1_var.set('20-50')
        entry1 = ttk.Entry(pie_option, textvariable=entry1_var, width=10)
        entry1.grid(row=2, column=1)
        t = entry1_var
        
        label1 = ttk.Label(pie_option, text='Moderate')
        label1.grid(row=3, column=0, sticky='w')
        entry1_var = tk.StringVar(pie_option)
        entry1_var.set('50-100')
        entry1 = ttk.Entry(pie_option, textvariable=entry1_var, width=10)
        entry1.grid(row=3, column=1)
        m = entry1_var
        
        label1 = ttk.Label(pie_option, text='Large Curve')
        label1.grid(row=4, column=0, sticky='w')
        entry1_var = tk.StringVar(pie_option)
        entry1_var.set('100-500')
        entry1 = ttk.Entry(pie_option, textvariable=entry1_var, width=10)
        entry1.grid(row=4, column=1)
        lc = entry1_var
        
        label1 = ttk.Label(pie_option, text='Straight')
        label1.grid(row=5, column=0, sticky='w')
        entry1_var = tk.StringVar(pie_option)
        entry1_var.set('500-1000')
        entry1 = ttk.Entry(pie_option, textvariable=entry1_var, width=10)
        entry1.grid(row=5, column=1)
        s = entry1_var       
        
        button1 = ttk.Button(pie_option, text = 'Pie Chart',
                                command = lambda: draw_pie_chart(self.process_data, vt.get(), t.get(), m.get(), lc.get(), s.get(), pie_chart))
        button1.grid(row=6, column=1, sticky='w', pady=(10,0))
                
        draw_pie_chart(self.process_data, vt.get(), t.get(), m.get(), lc.get(), s.get(), pie_chart)
        
       #Speed Disciption Frame-----------------------------------------------------------------------------
        RoC_2 = ttk.Frame(RoC)
        #loading_status_1.grid(padx=5, sticky='nsew')
        RoC_2.pack(side = 'top', padx=(10,50), pady=20, expand=True)
        RoC_2.grid_columnconfigure(0, weight=1)
        label2 = ttk.Label(RoC_2, text='Distance(%) vs Velocity', font=LARGE_FONT)
        label2.grid(row=0, column=0)
        make_table(self.vel_distance.reset_index(), RoC_2, col_width=200,
                  row_tree=1, column_tree=0,
                      row_scrollx=2, column_scrollx=0,              
                      row_scrolly=1, column_scrolly=1)
        
        label2 = ttk.Label(RoC_2, text='% Straight Roads = {}%'.format(round(self.straight_road,2)), font=LARGE_FONT)
        label2.grid(row=5, column=0, pady=20)
        
       #Building RoC Table------------------------------------------------------------------------------
        customize_roc_table_intervels(self.process_data, entry_frame, table_frame, RoC_2)        
                  
      #Figure show up--------------------------------------------------------------------------------------------------------------
       #Time Series Graph------------------------------------------
        fig = plot_graph(self.process_data) 
        canvas = FigureCanvasTkAgg(fig, graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=10, padx=10)
        #canvas.get_tk_widget().pack(side=tk.TOP, fill='x', expand=False)

        # toolbar = NavigationToolbar2TkAgg(canvas, frame)
        toolbar = NavigationToolbar2Tk(canvas, graph_frame)

        # toolbar.update()
        canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=10, padx=10)
        #canvas.get_tk_widget().pack(side=tk.TOP, fill='x', expand=False)
        
       #Distribution Graph------------------------------------------        
        def describe_parameter(parameter):
            for widget in graph_frame.winfo_children()+des_frame.winfo_children():
                widget.destroy()

            fig_speed = plot_speed_distribution(self.process_data, parameter)       
            canvas1 = FigureCanvasTkAgg(fig_speed, graph_frame)
            canvas1.draw()
            canvas1.get_tk_widget().pack(side=tk.TOP, expand=False, pady=20)

            toolbar1 = NavigationToolbar2Tk(canvas1, graph_frame)
            # toolbar.update()
            canvas1._tkcanvas.pack(side=tk.TOP, expand=False, pady=20)

            rename_dict = {'Speed(km/hr)':'speed_filt', 'Altitude(m)':'altitude_filt',
                   'Long_Acc(m/sec2)':'long_accel_gps_filt',
                   'Lat_Acc(m/sec2)':'lat_accel_gps_filt', 'RoC-abs(m)':'roc_abs'}
            data = self.process_data.rename(columns={rename_dict[parameter]:parameter})[parameter].describe(percentiles=[0.1,0.5,0.9]).to_frame().T.reset_index().rename(columns={'index':'parameter', '10%':'D10', '50%':'D50', '90%':'D90'}).round(4)
            data_enter = data.values
            tree = ttk.Treeview(des_frame, columns = tuple(range(len(data.columns))), height = 1, show = "headings", padding=10)
            tree.grid(row=1, column=0, sticky='nsew')
            [tree.heading(x, text=y, anchor='w') for x,y in zip(range(len(data.columns)), data.columns)]
            [tree.column(x, width = 100+len(list(c))) for x,c in zip(range(len(data.columns)), data.columns)]
            for val in data_enter:
                tree.insert('', 'end', values = [x for x in val] )        
        
        option_frame = ttk.Frame(graph_frame_speed)
        #option_frame.pack(side = 'left', expand=True)
        option_frame.grid(row=0, column=0, padx=50)
        
        graph_frame = ttk.Frame(graph_frame_speed)
        #graph_frame.pack(side = 'left', expand=True)
        graph_frame.grid(row=0, column=1)
        
        des_frame = ttk.Frame(graph_frame_speed)
        #des_frame.pack(side = 'bottom', expand=True)
        des_frame.grid(row=1, column=1, pady=50)
        des_frame.grid_columnconfigure(0, weight=1)
        
        label3 = tk.Label(option_frame, text = 'Parameter to Describe ->')
        label3.grid(row=0, column=0, pady=10, sticky='w')
        myOptList = ['Speed(km/hr)', 'Speed(km/hr)', 'Altitude(m)', 'Long_Acc(m/sec2)', 'Lat_Acc(m/sec2)']
        var = tk.StringVar(graph_frame_speed)
        var.set(myOptList[0])
        om = ttk.OptionMenu(option_frame, var, *myOptList, command = describe_parameter)        
        om.grid(row=0, column=1, pady=10, sticky='w')
        
        rename_dict = {'Speed(km/hr)':'speed_filt', 'Altitude(m)':'altitude_filt',
                   'Long_Acc(m/sec2)':'long_accel_gps_filt',
                   'Lat_Acc(m/sec2)':'lat_accel_gps_filt', 'RoC-abs(m)':'roc_abs'}
        describe_parameter('Speed(km/hr)')
        
        
       #BiHistogram--------------------------------------------------------
        
        fig_bihist = plot_bihistogram(self.process_data)       
        canvas2 = FigureCanvasTkAgg(fig_bihist, graph_frame_bihist)
        canvas2.draw()
        canvas2.get_tk_widget().pack(side=tk.TOP, expand=False, pady=20)
        #canvas.get_tk_widget().pack(side=tk.TOP, fill='x', expand=False)

        toolbar2 = NavigationToolbar2Tk(canvas2, graph_frame_bihist)

        # toolbar.update()
        canvas2._tkcanvas.pack(side=tk.TOP, expand=False, pady=20)
                
                
      #Map show up-------------------------------------------------------------------------------------------------------------
        map_frame = ttk.Frame(map_frame)
        map_frame.pack(padx=70, pady=20)
        map_frame.grid_columnconfigure(0, weight=1)
        
        label = tk.Label(map_frame, text='Track Truck',  font=LARGE_FONT)
        label.grid(row=0, column=1)

        label2 = tk.Label(map_frame, text='Data Cut Count\n(Higher the Value, Faster it plots)       ')
        label2.grid(row=1, column=0, sticky='w')
        entry2_var = tk.IntVar(map_frame)
        entry2_var.set(10)
        entry2 = ttk.Entry(map_frame, textvariable=entry2_var)
        entry2.grid(row=1, column=1, sticky='w', padx=0)
        self.track_data_cut = entry2_var

        label3 = tk.Label(map_frame, text = 'Parameter to Map with Route')
        label3.grid(row=2, column=0, pady=10, sticky='w')
        myOptList = ['None', 'None', 'Speed(km/hr)', 'Altitude(m)', 'Long_Acc(m/sec2)',
                     'Lat_Acc(m/sec2)', 'RoC-abs(m)']
        var = tk.StringVar(map_frame)
        om = ttk.OptionMenu(map_frame, var, *myOptList)
        var.set(myOptList[0])
        om.grid(row=2, column=1, pady=10, sticky='w')

        button1 = ttk.Button(map_frame, text = 'Track Truck',
                                command = lambda: draw_map(self.process_data, self.track_data_cut.get(), var.get()))
        button1.grid(row=3, column=1, sticky='w')
        button2 = ttk.Button(map_frame, text = 'Home', command = lambda: self.start_page(master))
        button2.grid(row=4, column=1, sticky='w')
        
        note.pack()
        self.frame_check = note
        
        inf_pb.destroy()

        
                
    def save_as_project(self, master):
        try:
            tosave = {'raw_data' : self.data,
                      'clean_data':self.clean_data,
                      'process_data':self.process_data,
                      'summary':self.summary,
                      'summary_vbox':self.summary_vbox_files,
                      'file_size_df':self.file_size,
                      'total_files':self.total_files,
                      'file_dropped_df':self.drop_summary,
                      'total_files_dropped':self.total_files_dropped,
                      'perc_straight_road':self.straight_road,
                      'roc_table':self.roc_table,
                      'vel_dist':self.vel_distance}
            options = {'defaultextension':".vb",
                       'filetypes':[('vbox processed file', '.vb')],
                       'initialfile':self.original_project_path.split('/')[-1] if self.is_already_exist else 'my_vbox_project',
                       'initialdir': (pd.Series(self.original_project_path.split('/')[0:-1])+'//').sum() if self.is_already_exist else self.curr_dir}
            path = asksaveasfile(mode='w', **options)
            inf_pb = indeterminant_progress_bar('Save Project', 'Study is being saved.....')
            if path is None:
                pass
                inf_pb.destroy()
            else:
                self.is_already_exist=True
                self.original_project_path = path.name
                pd.Series(tosave).to_pickle(path.name)
                inf_pb.destroy()
                popupmsg('Project has been successfully saved!')
        except:
            popupmsg('It seems there is no data to save yet. Try loading data or import from saved projects')
    def save_project(self, master):
        try:
            if not self.is_already_exist :
                self.save_as_project(master)
            else:
                inf_pb = indeterminant_progress_bar('Save Project', 'Study is being saved....')
                tosave = {'raw_data' : self.data,
                          'clean_data':self.clean_data,
                          'process_data':self.process_data,
                          'summary':self.summary,
                          'summary_vbox':self.summary_vbox_files,
                          'file_size_df':self.file_size,
                          'total_files':self.total_files,
                          'file_dropped_df':self.drop_summary,
                          'total_files_dropped':self.total_files_dropped,
                          'perc_straight_road':self.straight_road,
                          'roc_table':self.roc_table,
                          'vel_dist':self.vel_distance}
                pd.Series(tosave).to_pickle(self.original_project_path)
                inf_pb.destroy()
                popupmsg('Project has been successfully saved!')
        except:
            popupmsg('It seems there is no data to save yet. Try loading data or import from saved projects')
    def load_project(self, master):
        FILEOPENOPTIONS = dict(defaultextension='.vb', filetypes=[('vbox processed file','*.vb')])
        filename = askopenfilenames(**FILEOPENOPTIONS, title='Choose a file')
        if not isinstance(filename, str):
            if len(filename)>1:
                popupmsg('You can load only one project file at a time')
            else:
                inf_pb = indeterminant_progress_bar('Load Project', 'Project is being loaded...')
                loaded = pd.read_pickle(filename[0]).to_dict()
                self.data = loaded['raw_data']
                self.clean_data = loaded['clean_data']
                self.process_data = loaded['process_data']
                self.summary = loaded['summary']
                self.summary_vbox_files = loaded['summary_vbox']
                self.file_size = loaded['file_size_df']
                self.total_files = loaded['total_files']
                self.total_files_dropped = loaded['total_files_dropped']
                self.drop_summary = loaded['file_dropped_df']
                self.roc_table = loaded['roc_table']
                self.straight_road = loaded['perc_straight_road']
                self.vel_distance = loaded['vel_dist']
                self.original_project_path = filename[0]
                self.is_already_exist = True
                inf_pb.destroy()
                popupmsg('Project has been successfully loaded!')                
                self.DashBoardPage(master)                
        else:
            None
        
            
    def check(self, master):
        self.destroy_frame()
        
        frame_nav = ttk.Frame(master, height=1000)
        #frame_nav.pack(side='top')
        frame_nav.grid(row=0, column=0, padx=5, pady=5, sticky='n')
        
        
        
        data_button = ttk.Button(frame_nav, text = 'Data', command = lambda: show_raw_data(self, master))
        data_button.grid(row=0, column=0)
        summary_button = ttk.Button(frame_nav, text = 'Summary', command= lambda: show_summary(self, master))
        summary_button.grid(row=1, column=0)
        graph_button = ttk.Button(frame_nav, text = 'Graph')
        graph_button.grid(row=2, column=0)
        map_button = ttk.Button(frame_nav, text = 'Map', command = lambda: draw_map_within_frame(self, master))
        map_button.grid(row=3, column=0)
        
        sep = ttk.Separator(master, orient=tk.VERTICAL)
        #sep.pack(side='left')
        sep.grid(row=0, column=1, padx=5, pady=5, sticky='ns')
        
        frame = ttk.Frame(master)
        frame.grid(row=0, column=2, padx=5, pady=5, sticky='n')
        self._frame_within_frame = frame
        
        def show_raw_data(self, master):
            self._frame_within_frame.destroy()
            
            frame = ttk.Frame(master, height=1000)
            frame.grid(row=0, column=2, padx=5, pady=5, sticky='n')
            
            label = ttk.Label(frame, text='DataSet', font=LARGE_FONT)
            label.grid(row=0, column=0)
            
            pt = Table(frame, dataframe=self.process_data.reset_index(),
                                showtoolbar=False, showstatusbar=False)
            pt.show()
            self._frame_within_frame = frame        
        def draw_map_within_frame(self, master):
            self._frame_within_frame.destroy()
            
            map_frame = ttk.Frame(master, height=1000)
            map_frame.grid(row=0, column=2, padx=500, pady=5, sticky='n')
            
            label = tk.Label(map_frame, text='Track Truck',  font=LARGE_FONT)
            label.grid(row=0, column=1)

            label2 = tk.Label(map_frame, text='Data Cut Count\n(Higher the Value, Faster it plots)       ')
            label2.grid(row=1, column=0, sticky='w')
            entry2_var = tk.IntVar(map_frame)
            entry2_var.set(10)
            entry2 = ttk.Entry(map_frame, textvariable=entry2_var)
            entry2.grid(row=1, column=1, sticky='w', padx=0)
            self.track_data_cut = entry2_var

            label3 = tk.Label(map_frame, text = 'Parameter to Map with Route')
            label3.grid(row=2, column=0, pady=10, sticky='w')
            myOptList = ['None', 'None', 'roc_abs', 'altitude_filt', 'speed_filt', 'long_accel_vbox_filt_corrected',
                         'lat_accel_vbox_filt', 'roc']
            var = tk.StringVar(map_frame)
            om = ttk.OptionMenu(map_frame, var, *myOptList)
            var.set(myOptList[0])
            om.grid(row=2, column=1, pady=10, sticky='w')

            button1 = ttk.Button(map_frame, text = 'Track Truck',
                                    command = lambda: draw_map(self.process_data, self.track_data_cut.get(), var.get()))
            button1.grid(row=3, column=1, sticky='w')
            button2 = ttk.Button(map_frame, text = 'Home', command = lambda: self.start_page(master))
            button2.grid(row=4, column=1, sticky='w')
            
            self._frame_within_frame = map_frame
            
        def show_summary(self, master):
            self._frame_within_frame.destroy()
            
            ds_frame = ttk.Frame(master, height=1000)
            ds_frame.grid(row=0, column=2, padx=5, pady=5, sticky='n')
            
            label1 = ttk.Label(ds_frame, text='Usage Summary', font=LARGE_FONT)
            label1.grid(row=0, column=0)
            make_table(self.summary.reset_index(), ds_frame, col_width=20,
                      row_tree=1, column_tree=0,
                          row_scrollx=2, column_scrollx=0,              
                          row_scrolly=1, column_scrolly=1)

            label = ttk.Label(ds_frame)
            label.grid(row=5, column=0)

            label2 = ttk.Label(ds_frame, text='Usage Summary per Vbox File', font=LARGE_FONT)
            label2.grid(row=7, column=0)
            make_table(self.summary_vbox_files.reset_index(), ds_frame, col_width=70,
              row_tree=8, column_tree=0,
                  row_scrollx=9, column_scrollx=0,              
                  row_scrolly=8, column_scrolly=1)
            
            self._frame_within_frame = ds_frame
