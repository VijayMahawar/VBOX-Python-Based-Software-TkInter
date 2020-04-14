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
from matplotlib import colors
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


def load_data():
    FILEOPENOPTIONS = dict(defaultextension='.VBO', filetypes=[('VBox File','*.VBO')])
    filename = askopenfilenames(**FILEOPENOPTIONS, title='Choose a file')

    try:
        curr_dir =(pd.Series(filename[0].split('/')[0:-1])+'/').sum()
        file_selection = [f.split('/')[-1] for f in filename]
        vbo_data = ut.gps.load_vbox_data(folder_path = curr_dir,
                              file_selection = file_selection)
    except:
        vbo_data = pd.DataFrame()
        filename = ''
    return vbo_data, filename   
def clean_data(vbo_data, trip_distance_threshold, data_count_threshold):
    # remove unloaded file
    files_invalid = list((vbo_data['filename'].value_counts()==1).replace(False, np.nan).dropna().index)
    vbo_data = vbo_data.set_index('filename').drop(files_invalid).reset_index()

    # correcting columns
    vbo_data = vbo_data.rename(columns={'datetime':'timestamp', 'sats':'satellitesUsed', 'velocity':'speed',
                                       'height':'altitude'})
    vbo_data['satellitesUsed'] = vbo_data['satellitesUsed'].astype(int)


    trip_distance_threshold = trip_distance_threshold
    data_count_threshold = data_count_threshold
    
    data_check = vbo_data.groupby('filename').apply(lambda x: {'Distance':pd.Series(ut.gps.compute_distance_from_speed(x.speed, x.reset_index()['timestamp'].diff())).sum(),
                                                       'DataCount':x.shape[0]}).apply(pd.Series)
    files_to_drop = data_check.apply(lambda x: (x['DataCount']>data_count_threshold) & (x['Distance']>trip_distance_threshold), axis=1).replace(True, np.nan).dropna().index
    vbo_data = vbo_data.set_index('filename').drop(files_to_drop).reset_index()
    vbo_data = vbo_data.set_index('timestamp').drop((vbo_data['timestamp'].value_counts()>1).replace(False, np.nan).dropna().index)

    total_files = len(files_invalid) + len(files_to_drop) + vbo_data['filename'].nunique()
    total_files_dropped = len(files_invalid) + len(files_to_drop)        
    drop_summary = pd.concat([pd.Series({x:'Invalid File' for x in files_invalid}), pd.Series({x:'Threshold conditions do not match'.format(trip_distance_threshold) for x in files_to_drop})]).to_frame('File_Status')    
    
    
    
    

    return vbo_data, total_files, total_files_dropped, drop_summary, files_invalid
  
import utm 
def get_xy_cordinates_withcorrect_latlon(lat, lon):
    try:
        xy = utm.from_latlon(lat, lon)[0:2]
        return xy[0], xy[1], lat, lon
    except:
        xy = utm.from_latlon(lat/60, lon/60)[0:2]
        return xy[0], xy[1], lat/60, lon/60
def data_process(vbo_data):
    #vbo_data = vbo_data.groupby('filename').progress_apply(lambda x: ut.gps.process_gps_data(x)).reset_index().set_index('timestamp').sort_index()
    vbo_data = vbo_data.groupby('filename').apply(lambda x: ut.gps.process_gps_data(x)).reset_index().set_index('timestamp').sort_index()
    #xy_cord = vbo_data.progress_apply(lambda x: get_xy_cordinates_withcorrect_latlon(x['lat'], x['long']), axis=1)
    xy_cord = vbo_data.apply(lambda x: get_xy_cordinates_withcorrect_latlon(x['lat'], x['long']), axis=1)
    vbo_data[['x', 'y', 'lat_corr', 'lon_corr']] = pd.DataFrame([[x[0], x[1], x[2], x[3]] for x in xy_cord.values], index=vbo_data.index)

    if vbo_data['filename'].nunique()>1:
        vbo_data['roc'] = vbo_data.groupby('filename').apply(lambda x: pd.Series(ut.gps.compute_radius_3p(x['x'], x['y']), index=x.index)).reset_index().set_index('timestamp')[0]
    else:
        vbo_data['roc'] = vbo_data.groupby('filename').apply(lambda x: pd.Series(ut.gps.compute_radius_3p(x['x'], x['y']), index=x.index)).stack().reset_index().set_index('timestamp')[0]
    vbo_data['roc_abs'] = vbo_data['roc'].apply(lambda x: 1000 if np.abs(x)>1000 else abs(x))
    
    return vbo_data
def on_closing(root):
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        root.quit()
        root.destroy()
def close_tkinter_app(master):
    master.quit()
    master.destroy()
def popupmsg(msg):
    popup = tk.Tk()
    popup.wm_title('Message')
    popup.iconbitmap(r'favicon_transparent.ico')
    label = ttk.Label(popup, text=msg, font=NORM_FONT)
    label.pack(side='top', fill='x', pady=10)
    B1 = ttk.Button(popup, text = 'Okay', command = lambda: close_tkinter_app(popup))
    B1.pack()
    popup.mainloop()
import folium as f
import webbrowser
def draw_map(vbo_data, cut_data, colormap):
    rename_dict = {'Speed(km/hr)':'speed_filt', 'Altitude(m)':'altitude_filt',
                   'Long_Acc(m/sec2)':'long_accel_gps_filt',
                   'Lat_Acc(m/sec2)':'lat_accel_gps_filt', 'RoC-abs(m)':'roc_abs', 'None':'None'}
    colormap_label = colormap
    colormap = rename_dict[colormap]
    try:
        inf_pb = indeterminant_progress_bar('Track Truck', 'Truck is being tracked....')
        big_map = f.Map(tiles='cartodbpositron')
        [ut.gps.track_truck('lat_corr', 'lon_corr', data = grp[1][::cut_data][['lat_corr', 'lon_corr']].dropna() if colormap.startswith('None') else grp[1][::cut_data][['lat_corr', 'lon_corr', colormap]].dropna(),
                     colormap_data=eval(colormap) if colormap.startswith('None') else colormap, map_toadd=big_map) for grp in vbo_data.groupby('filename')]
        if not colormap.startswith('None'):
            map_legend = big_map._children[[x for x in big_map._children.keys() if x.startswith('color')][0]]
            map_legend.vmin = vbo_data[colormap].dropna().min()
            map_legend.vmax = vbo_data[colormap].dropna().max()
            map_legend.caption = colormap_label
            for key in [x for x in big_map._children.keys() if x.startswith('color')][1:]:
                del(big_map._children[key])
        else:
            None    
        big_map.save(r'Map.html')
        webbrowser.open(r'Map.html')
        inf_pb.destroy()
    except:
        inf_pb.destroy()
        popupmsg('Ops! Something went wrong. \nTry again with some other (Data Cut Count) parameter or clean your data again to drop false Vbox files from the project')
    
    
def data_statistics(vbo_data):
    vbo_data = vbo_data.dropna(subset=['gap'])
    vbo_data['gap'] = vbo_data['gap'].astype(bool)
        
    summary_vbox_files = vbo_data.groupby('filename').apply(lambda x: pd.Series(ut.gps.summarize_gps_data(x)).to_frame('values').dropna().round(4))['values'].unstack().sort_values('distance', ascending=False)
    summary_vbox_files = summary_vbox_files[['distance', 'duration', 'spdAvg', 'spdStd', 'lonAccAvg_gps', 'lonAccStd_gps', 'latAccAvg_gps', 'latAccStd_gps']].rename(columns={'distance':'Distance(km)',
                                                                                                                                            'duration':'Duration(hrs)',
                                                                                                                                            'spdAvg':'Speed Avg(km/hr)',
                                                                                                                                            'spdStd':'Speed Std(km/h)',
                                                                                                                                            'lonAccAvg_gps':'Lon Acc Avg(m/sec2)',
                                                                                                                                            'lonAccStd_gps':'Lon Acc Std(m/sec2)',
                                                                                                                                            'latAccAvg_gps':'Lat Acc Avg(m/sec2)',
                                                                                                                                            'latAccStd_gps':'Lat Acc Std(m/sec2)'})
    
    
    
    
    summary = pd.Series(ut.gps.summarize_gps_data(vbo_data)).to_frame('values').dropna().round(4)
    summary = summary.T[['distance', 'duration', 'spdAvg', 'spdStd', 'lonAccAvg_gps', 'lonAccStd_gps', 'latAccAvg_gps', 'latAccStd_gps']].rename(columns={'distance':'Distance(km)',
                                                                                                                                            'duration':'Duration(hrs)',
                                                                                                                                            'spdAvg':'Speed Avg(km/hr)',
                                                                                                                                            'spdStd':'Speed Std(km/h)',
                                                                                                                                            'lonAccAvg_gps':'Lon Acc Avg(m/sec2)',
                                                                                                                                            'lonAccStd_gps':'Lon Acc Std(m/sec2)',
                                                                                                                                            'latAccAvg_gps':'Lat Acc Avg(m/sec2)',
                                                                                                                                            'latAccStd_gps':'Lat Acc Std(m/sec2)'}).T

    vbo_data['vel_bin'] = pd.cut(vbo_data['speed'], [0,15,25, 35, 45, 55, 65, 75, 85, 95, 105, np.inf])
    vbo_data['roc_abs_bins'] = pd.cut(vbo_data['roc_abs'], [0,10, 15,25,50,100,200,300, 500, 1000,2000,np.inf])

    roc_table = vbo_data.groupby(['vel_bin', 'roc_abs_bins']).apply(lambda x: x['distance_delta'].sum()*100/vbo_data['distance_delta'].sum()).unstack()
    roc_table.index = [str(x) for x in list(roc_table.index)]
    roc_table.columns = [str(x) for x in list(roc_table.columns)]
    roc_table.index.name = 'Velocity(km/h)'
    roc_table.columns.name = 'RoC(m)'
    
    straight_road =roc_table[['(500.0, 1000.0]']].sum().sum()
    vel_distance = roc_table.sum(axis=1).to_frame('% Distance').round(4)
    
    roc_table = roc_table.round(4).replace(np.nan, '') 
    
    return summary_vbox_files, summary, roc_table, vel_distance, straight_road
def data_process_with_progress_bar(vbo_data, fs = 0.5):
    
    popup1 = tk.Tk()    
    popup1.wm_title('Data Processing')
    popup1.iconbitmap(r'favicon_transparent.ico')
    label = ttk.Label(popup1, text='Data is being processed.....', font=NORM_FONT)
    label.pack(side='top', fill='x', pady=10)

    pb = ttk.Progressbar(popup1,orient ="horizontal",length = 500, mode ="determinate")
    pb["maximum"] = vbo_data['filename'].nunique()
    pb["value"] = 0
    pb.pack()
    pb.update()
        
    process_data = []
    unprocessed_file = []
    for pb_update, dt in zip(np.arange(0, vbo_data['filename'].nunique()), list(vbo_data.groupby('filename'))):
        try:
            data = ut.gps.process_gps_data(dt[1], fs=fs)
            data['filename'] = dt[0]
            xy_cord = data.apply(lambda x: get_xy_cordinates_withcorrect_latlon(x['lat'], x['long']), axis=1)
            data[['x', 'y', 'lat_corr', 'lon_corr']] = pd.DataFrame([[x[0], x[1], x[2], x[3]] for x in xy_cord.values],
                                                                    index=data.index)

            data['roc'] = pd.Series(ut.gps.compute_radius_3p(data['x'], data['y']), index=data.index)
            data['roc_abs'] = data['roc'].apply(lambda x: 1000 if np.abs(x)>1000 else abs(x))

            data = data.reset_index()
            data.set_index('timestamp', inplace=True)      


            process_data.append(data)
            pb["value"] = pb_update+1 
            pb.update()
        except:
            unprocessed_file.append(dt[0])
            pb["value"] = pb_update+1 
            pb.update()
    popup1.destroy()
        
    return pd.concat(process_data).sort_index(), pd.Series({x:'processing error' for x in unprocessed_file}).to_frame('File_Status')
    
def load_data_with_progress_bar():    
    FILEOPENOPTIONS = dict(defaultextension='.VBO', filetypes=[('VBox File','*.VBO')])
    filename = askopenfilenames(**FILEOPENOPTIONS, title='Choose a file')
    curr_dir =(pd.Series(filename[0].split('/')[0:-1])+'/').sum()
    file_selection = [f.split('/')[-1] for f in filename]

    popup = tk.Tk()    
    popup.wm_title('Data Loading')
    popup.iconbitmap(r'favicon_transparent.ico')
    label = ttk.Label(popup, text='Data is being loaded.....', font=NORM_FONT)
    label.pack(side='top', fill='x', pady=10)

    mpb = ttk.Progressbar(popup,orient ="horizontal",length = 500, mode ="determinate")
    mpb["maximum"] = len(file_selection)
    mpb["value"] = 0
    mpb.pack()
    mpb.update()
    vbo_data = []
    for pb_update, file in zip(np.arange(0,len(file_selection),1), file_selection):
        data = load_vbox_file(curr_dir, file)
        vbo_data.append(data)
        mpb["value"] = pb_update+1 
        mpb.update()        
        #update_perc = ttk.Label(popup, text='{}'.format(pb_update+1), font=NORM_FONT)
        #update_perc.pack(side = 'right')
        #update_perc.destroy()

    popup.destroy()
    vbo_data = pd.concat(vbo_data).reset_index(drop = True)
    return vbo_data, file_selection, curr_dir
def plot_graph(vbo_data):    
    index_to_put_nan = (vbo_data.sort_index().reset_index(drop=False).set_index('timestamp', drop=False)['timestamp'].diff().apply(lambda x: x.total_seconds())>1*60).replace(False, np.nan).dropna().index
    index_to_put_nan = pd.concat([pd.Series(index_to_put_nan)-pd.Timedelta('0.0000001s'),
                                    pd.Series(index_to_put_nan),
                                    pd.Series(index_to_put_nan)+pd.Timedelta('0.0000001s')]).values
    vbo_data_to_plot = pd.concat([vbo_data, pd.Series(index=index_to_put_nan)]).sort_index()
    
    ax = vbo_data_to_plot[['speed_filt', 'altitude_filt', 'lat_accel_gps_filt', 'long_accel_gps_filt']].plot(subplots=True, figsize=(10,8), sharex=True, color='b', lw=1)
    vbo_data_to_plot[['speed', 'altitude', 'lat_accel_gps', 'long_accel_gps']].plot(subplots=True, ax=ax, color='b', alpha=0.2, ls='-')
    [a.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize=12) for a in ax]
    [a.grid() for a in ax]
    [a.set_ylabel(lab, fontsize=15) for a, lab in zip(ax,['Speed(km/h)', 'Altitude(m)', 'LatAcc\n(m/sec^2)', 'LonAcc\n(m/sec^2)'])]
    ax[-1].set_xlabel('timstamp', fontsize=15)
    fig = plt.gcf()
    fig.set_facecolor('w')
    fig.tight_layout()
    return fig
def plot_speed_distribution(vbo_data, toplot):
    rename_dict = {'Speed(km/hr)':'speed_filt', 'Altitude(m)':'altitude_filt',
                   'Long_Acc(m/sec2)':'long_accel_gps_filt',
                   'Lat_Acc(m/sec2)':'lat_accel_gps_filt', 'RoC-abs(m)':'roc_abs'}
    fig, ax = plt.subplots(figsize=(12,5))
    sns.distplot(vbo_data[rename_dict[toplot]].dropna(), ax=ax,
                kde_kws={"color": "b", "lw": 1, 'ls':'--', 'alpha':0.5},
                hist_kws={"linewidth": 1, "alpha": 1, "color": "b", 'alpha':0.5, 'edgecolor':'w'})
    ax.set_yticklabels('')
    #ax.set_xlim(0,None)
    ax.set_ylabel('Probablity', fontsize=15)
    ax.set_xlabel(toplot, fontsize=15)
    fig.set_facecolor('w')
    fig.set_size_inches(15,7)
    return fig
from matplotlib import colors
def plot_bihistogram(vbo_data):
    #ax = ut.gps.draw_acceleration_bihistogram(vbo_data, ax='long_accel_gps_filt', ay='lat_accel_gps_filt',
    #                                   weighting=True, log=True, figsize=(10, 10), bgcolor='w', grid=True, binsize=201)
    #ax.set_xlim(-2,2)
    #ax.set_ylim(-2,2)
    #ax.grid(c='k', ls='--', alpha=0.2)
    #plt.gcf().set_facecolor('w')
    
    fig, ax = plt.subplots()
    ax.hist2d(vbo_data['lat_accel_gps_filt'], vbo_data['long_accel_gps_filt'],
             bins=500, norm=colors.LogNorm(), normed=True);
    ax.grid(c='k', ls='--', alpha=0.2)
    ax.set_xlabel('Lat Acc (m/sec2)', fontsize=15)
    ax.set_ylabel('Lon Acc (m/sec2)', fontsize=15)
    ax.set_facecolor('navy')
    fig.set_facecolor('w')
    
    
    return fig
def load_vbox_file(folder_path,filename):
    try:            
        try:
            vb = pd.read_csv(folder_path+  '\\' + filename, header=None, sep=None, engine='python')
            date = pd.to_datetime((vb.iloc[0]+' ').dropna().sum().split('@')[0].split('on')[1].replace(' ', ''), dayfirst = True)
            tocut = vb[0].apply(lambda x: x if x.startswith('sats') else np.nan).dropna().index[0]
            vb = vb.iloc[tocut:].dropna(how='all', axis=1).dropna().T.set_index(tocut).T.reset_index(drop=True)
            vb.columns.name=''
        except:
            vb = pd.read_csv(folder_path+  '\\' + filename, header=None)
            date = pd.to_datetime(vb[0].iloc[0].split('@')[0].split('on')[1].replace(' ', ''), dayfirst = True)
            tocut = vb[0].apply(lambda x: x if x.startswith('sats') else np.nan).dropna().index[0]
            vb[0].iloc[tocut] = vb[0].iloc[tocut].replace('  ', ' ')
            vb = vb.iloc[tocut:][0].apply(lambda x: x.split(' ')[:-1]).drop(tocut+1)
            try:
                vb = pd.DataFrame(np.stack(vb[tocut+1:].values), columns=vb[tocut])
            except:
                vb = vb.drop((vb.apply(lambda x: len(x))!=10).replace(False, np.nan).dropna().index)
                vb = pd.DataFrame(np.stack(vb[tocut+1:].values), columns=vb[tocut])

        vb['date'] = date
        vb['time'] = vb['time'].apply(lambda x: '000000.00' if x=='240000.00' else x)
        vb['time_str'] = vb['time'].copy()
        vb['time'] = vb['time'].astype(float)
        vb['timediff'] = vb['time'].diff()
        vb['time'] = vb['time_str'].copy()
        vb['increment'] = (vb['timediff']<0).astype(int)
        vb['day'] = vb['increment'].cumsum()
        vb['date_correct'] = vb.apply(lambda x: x['date'] + pd.DateOffset(x['day']), axis=1)
        vb['time'] = vb['time'].astype('str').apply(lambda x: x.zfill(8))
        vb['datetime'] = vb.apply(lambda x: pd.to_datetime(pd.datetime.combine(x['date_correct'].date(), pd.to_datetime(x['time'][:2]+':'+x['time'][2:4]+':'+x['time'][4:6] + ':' + x['time'][7:], format='%H:%M:%S:%f').time())), axis=1)
        vb.drop(['timediff','increment','day','date_correct', 'time_str'], axis=1, inplace = True)
        try:
            vb[['lat','long','velocity','heading','height','vert-vel','Longacc','Latacc']] = vb[['lat','long','velocity','heading','height','vert-vel','Longacc','Latacc']].astype(float)
        except:
            vb[['lat','long','velocity','heading','height','vert-vel']] = vb[['lat','long','velocity','heading','height','vert-vel']].astype(float)
            vb['Longacc'] = 0.0
            vb['Latacc'] = 0.0        
        vb['filename']=filename		
        return vb
    except:
        return pd.DataFrame([filename], columns=['filename'])
    
def make_table(data, frame, col_width = 100,
              row_tree=0, column_tree=0,
              row_scrollx=0, column_scrollx=0,              
              row_scrolly=0, column_scrolly=0):
    data_enter = data.values
    tree = ttk.Treeview(frame, columns = tuple(range(len(data.columns))), height = 15, show = "headings", padding=10)
    tree.grid(row=row_tree, column=column_tree, sticky='nsew')
    [tree.heading(x, text=y, anchor='w') for x,y in zip(range(len(data.columns)), data.columns)]
    [tree.column(x, width = col_width+len(list(c))) for x,c in zip(range(len(data.columns)), data.columns)]

    scrolly = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    scrolly.grid(row=row_scrolly, column=column_scrolly, sticky='nse')
    scrollx = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
    scrollx.grid(row=row_scrollx, column=column_scrollx, sticky='sew')
    tree.configure(yscrollcommand=scrolly.set)
    tree.configure(xscrollcommand=scrollx.set)
    
    for val in data_enter:
        tree.insert('', 'end', values = [x for x in val] )
def indeterminant_progress_bar(title, content):    
    popup1 = tk.Tk()    
    popup1.wm_title(title)
    popup1.iconbitmap(r'favicon_transparent.ico')
    label = ttk.Label(popup1, text=content, font=NORM_FONT)
    label.pack(side='top', fill='x', pady=10)
    pb = ttk.Progressbar(popup1,orient ="horizontal",length = 500, mode ="indeterminate")    
    pb.pack()
    
    pb.start(25)
    pb["value"] = 0
    pb.update()
    return popup1
	
def draw_roc_table(vbo_data, frame_table, frame_vel,
                   min_roc, max_roc, int_roc, min_vel, max_vel, int_vel, sr_roc,
                   by_bins=True, roc_bin='0,100,500,1000', vel_bin='0,20,50,100'):
    if not by_bins:
        try:
            vbo_data['vel_bin'] = pd.cut(vbo_data['speed'], np.append(np.arange(min_vel,max_vel,int_vel), np.inf))
            vbo_data['roc_abs_bins'] = pd.cut(vbo_data['roc_abs'], np.append(np.arange(min_roc,max_roc,int_roc), np.inf))
        except:
            popupmsg('Make sure the bins are in correct format. For eg: x1, x2, x3, x4.....(Monotonic Increasing)')
            return None
    else:
        try:
            vbo_data['vel_bin'] = pd.cut(vbo_data['speed'], [float(x) for x in vel_bin.replace(' ', '').split(',')] + [np.inf])
            vbo_data['roc_abs_bins'] = pd.cut(vbo_data['roc_abs'], [float(x) for x in roc_bin.replace(' ', '').split(',')] + [np.inf])
        except:
            popupmsg('Make sure the bins are in correct format. For eg: x1, x2, x3, x4.....(Monotonic Increasing)')
            return None

    roc_table = vbo_data.groupby(['vel_bin', 'roc_abs_bins']).apply(lambda x: x['distance_delta'].sum()*100/vbo_data['distance_delta'].sum()).unstack()
    roc_table.index = [str(x) for x in list(roc_table.index)]
    roc_table.columns = [str(x) for x in list(roc_table.columns)]
    roc_table.index.name = 'Velocity(km/h)'
    roc_table.columns.name = 'RoC(m)'
    
    vbo_data['roc_abs_bins'] = pd.cut(vbo_data['roc_abs'], [sr_roc, np.inf])
    straight_road = vbo_data.groupby('roc_abs_bins').apply(lambda x: x['distance_delta'].sum()*100/vbo_data['distance_delta'].sum()).sum()    
    vel_distance = roc_table.sum(axis=1).to_frame('% Distance').round(4)    
    roc_table = roc_table.round(4).replace(np.nan, '')
    
    roc_table_1 = roc_table.reset_index()
    roc_table = pd.concat([pd.Series(['' for x in range(roc_table.shape[1]+1)], index = roc_table_1.columns).to_frame().T,
                       roc_table_1]).reset_index()
    roc_table.loc[0, 'Velocity(km/h)']='Velocity(km/h)'
    roc_table.rename(columns={'Velocity(km/h)':'RoC(m)'}, inplace=True)
    roc_table = roc_table.drop('index', axis=1)

    make_table(roc_table, frame_table, col_width=100,
              row_tree=1, column_tree=0,
                  row_scrollx=2, column_scrollx=0,              
                  row_scrolly=1, column_scrolly=1)
    
    make_table(vel_distance.reset_index(), frame_vel, col_width=200,
                  row_tree=1, column_tree=0,
                      row_scrollx=2, column_scrollx=0,              
                      row_scrolly=1, column_scrolly=1)
    label2 = ttk.Label(frame_vel, text='% Straight Roads = {}%'.format(round(straight_road,2)), font=LARGE_FONT)
    label2.grid(row=5, column=0, pady=20)
    
def customize_roc_table_bins(vbo_data, entry_frame, table_frame, RoC_2):    
    for widget in entry_frame.winfo_children():
        widget.destroy()
    
    label1 = ttk.Label(entry_frame, text='User defined\nRoC & Velocity Bins')
    label1.grid(row=0, column=0, sticky='w', pady=(0,15))
    
    label1 = ttk.Label(entry_frame, text='RoC Bins (meteres)')    
    label1.grid(row=1, column=0, sticky='w')
    entry1_var = tk.StringVar(entry_frame)
    entry1_var.set('0, 50, 100, 1000')
    entry1 = ttk.Entry(entry_frame, textvariable=entry1_var, width=25)
    entry1.grid(row=1, column=1)
    roc_bin = entry1_var

    label1 = ttk.Label(entry_frame, text='Velocity Bins (km/hr)')
    label1.grid(row=2, column=0, sticky='w')
    entry1_var = tk.StringVar(entry_frame)
    entry1_var.set('0, 20, 40, 80, 120')
    entry1 = ttk.Entry(entry_frame, textvariable=entry1_var, width=25)
    entry1.grid(row=2, column=1)
    vel_bin = entry1_var
    
    label1 = ttk.Label(entry_frame, text='Straight Road (>RoC(m))')
    label1.grid(row=3, column=0, sticky='w', pady=(0,10))
    entry1_var = tk.DoubleVar(entry_frame)
    entry1_var.set(500)
    entry1 = ttk.Entry(entry_frame, textvariable=entry1_var, width=10)
    entry1.grid(row=3, column=1, pady=(0,10))
    sr_roc = entry1_var
    
    button1 = ttk.Button(entry_frame, text = 'Update Table',
                                command = lambda: draw_roc_table(vbo_data, table_frame, RoC_2, None, None,
                                                                None, None, None, None,
                                                                sr_roc.get(),
                                                                by_bins=True, roc_bin=roc_bin.get(), vel_bin=vel_bin.get()))
    button1.grid(row=4, column=1, sticky='w', pady=(10,0))

    button2 = ttk.Button(entry_frame, text = 'Customize RoC Table',
                            command = lambda: customize_roc_table_intervels(vbo_data, entry_frame, table_frame, RoC_2))
    button2.grid(row=5, column=0, sticky='w', pady=(20,0))    	

	
	
def customize_roc_table_intervels(vbo_data, entry_frame, table_frame, RoC_2):
    
    for widget in entry_frame.winfo_children():
        widget.destroy()
        
    label1 = ttk.Label(entry_frame, text='User defined RoC & Velocity Bins\n(equal intervals)')
    label1.grid(row=0, column=0, sticky='w', pady=(0,15))    
    
    label1 = ttk.Label(entry_frame, text='RoC Minimum (meters)')
    label1.grid(row=1, column=0, sticky='w')
    entry1_var = tk.DoubleVar(entry_frame)
    entry1_var.set(0)
    entry1 = ttk.Entry(entry_frame, textvariable=entry1_var, width=10)
    entry1.grid(row=1, column=1)
    roc_min = entry1_var

    label1 = ttk.Label(entry_frame, text='RoC Maximum (meters)')
    label1.grid(row=2, column=0, sticky='w')
    entry1_var = tk.DoubleVar(entry_frame)
    entry1_var.set(1000)
    entry1 = ttk.Entry(entry_frame, textvariable=entry1_var, width=10)
    entry1.grid(row=2, column=1)
    roc_max = entry1_var

    label1 = ttk.Label(entry_frame, text='RoC Intervel (meters)')
    label1.grid(row=3, column=0, sticky='w', pady=(0,10))
    entry1_var = tk.DoubleVar(entry_frame)
    entry1_var.set(200)
    entry1 = ttk.Entry(entry_frame, textvariable=entry1_var, width=10)
    entry1.grid(row=3, column=1, pady=(0,10))
    roc_int = entry1_var

    label1 = ttk.Label(entry_frame, text='Velocity Minimum (km/hr)')
    label1.grid(row=4, column=0, sticky='w')
    entry1_var = tk.DoubleVar(entry_frame)
    entry1_var.set(0)
    entry1 = ttk.Entry(entry_frame, textvariable=entry1_var, width=10)
    entry1.grid(row=4, column=1)
    vel_min = entry1_var

    label1 = ttk.Label(entry_frame, text='Velocity Maximum (km/hr)')
    label1.grid(row=5, column=0, sticky='w')
    entry1_var = tk.DoubleVar(entry_frame)
    entry1_var.set(150)
    entry1 = ttk.Entry(entry_frame, textvariable=entry1_var, width=10)
    entry1.grid(row=5, column=1)
    vel_max = entry1_var

    label1 = ttk.Label(entry_frame, text='Velocity Intervel (km/hr)')
    label1.grid(row=6, column=0, sticky='w', pady=(0,10))
    entry1_var = tk.DoubleVar(entry_frame)
    entry1_var.set(20)
    entry1 = ttk.Entry(entry_frame, textvariable=entry1_var, width=10)
    entry1.grid(row=6, column=1, pady=(0,10))
    vel_int = entry1_var

    label1 = ttk.Label(entry_frame, text='Straight Road (>RoC(m))')
    label1.grid(row=7, column=0, sticky='w', pady=(0,10))
    entry1_var = tk.DoubleVar(entry_frame)
    entry1_var.set(500)
    entry1 = ttk.Entry(entry_frame, textvariable=entry1_var, width=10)
    entry1.grid(row=7, column=1, pady=(0,10))
    sr_roc = entry1_var

    button1 = ttk.Button(entry_frame, text = 'Update Table',
                            command = lambda: draw_roc_table(vbo_data, table_frame, RoC_2, roc_min.get(), roc_max.get(),
                                                            roc_int.get(), vel_min.get(), vel_max.get(), vel_int.get(),
                                                            sr_roc.get(), by_bins=False))
    button1.grid(row=8, column=1, sticky='w')

    button2 = ttk.Button(entry_frame, text = 'Customize RoC Table',
                            command = lambda: customize_roc_table_bins(vbo_data, entry_frame, table_frame, RoC_2))
    button2.grid(row=9, column=0, sticky='w', pady=(20,0))	
	
def draw_pie_chart(vbo_data, vt, t, m, lc, s, pie_chart):
    
    try:
        rc_dict = {}
        for cond, b_ in zip(['Very Tight', 'Tight', 'Moderate', 'Large Curve', 'Straight'],
                           [vt, t, m, lc, s]):
            vbo_data['roc_abs_bins'] = pd.cut(vbo_data['roc_abs'], [float(x) for x in b_.replace(' ','').split('-')])    
            rc_dict[cond] = vbo_data.groupby('roc_abs_bins').apply(lambda x: 100*x['distance_delta'].sum()/vbo_data['distance_delta'].sum()).values[0]
        rc = pd.Series(rc_dict).to_frame('%').reset_index()
        rc['label'] = rc['index']+' - '+rc['%'].round(2).astype(str)+'%'
        if not round(100-rc['%'].sum())==0:
            rc = pd.concat([rc, pd.DataFrame([['NA', 100-rc['%'].sum(), 'RoC(Not Defined)'+' - '+str(round(100-rc['%'].sum(),2))+'%']], columns=['index', '%', 'label'])])

        ax = rc.plot.pie(y = '%', startangle=90, shadow=False, labels=rc['label'], legend = True,
                         wedgeprops={'linewidth': 0.5, 'linestyle': 'solid', 'antialiased': True, "edgecolor":"w"},
                         colors=['red', 'orange','gold','yellowgreen', 'green', 'grey'])
        [x.set_fontsize(0) for x in ax.texts]
        ax.legend(loc='center left', bbox_to_anchor=(0.9, 0.5), fontsize=12)
        plt.gcf().set_facecolor('w')
        plt.gca().set_ylabel('')
        plt.tight_layout()
        fig = plt.gcf() 

        for widget in pie_chart.winfo_children():
            widget.destroy()
        canvas1 = FigureCanvasTkAgg(fig, pie_chart)
        canvas1.draw()
        canvas1.get_tk_widget().pack(side=tk.LEFT, expand=False, pady=20)
    except:
        popupmsg('Make sure the bins are in correct format.\nFor example: x1-x2, x3-x4..etc. (Monotonic Increasing)\nMake sure one entry is provided with one set of range (x1-x2)')
		
def describe_parameter(vbo_data, parameter):

    for widget in graph_frame.winfo_children()+des_frame.winfo_children():
        widget.destroy()

    fig_speed = plot_speed_distribution(vbo_data, parameter)       
    canvas1 = FigureCanvasTkAgg(fig_speed, graph_frame)
    canvas1.draw()
    canvas1.get_tk_widget().pack(side=tk.TOP, expand=False, pady=20)

    toolbar1 = NavigationToolbar2Tk(canvas1, graph_frame)
    # toolbar.update()
    canvas1._tkcanvas.pack(side=tk.TOP, expand=False, pady=20)

    rename_dict = {'Speed(km/hr)':'speed_filt', 'Altitude(m)':'altitude_filt',
           'Long_Acc(m/sec2)':'long_accel_gps_filt',
           'Lat_Acc(m/sec2)':'lat_accel_gps_filt', 'RoC-abs(m)':'roc_abs'}
    data = vbo_data.rename(columns={rename_dict[parameter]:parameter})[parameter].describe(percentiles=[0.1,0.5,0.9]).to_frame().T.reset_index().rename(columns={'index':'parameter', '10%':'D10', '50%':'D50', '90%':'D90'}).round(4)
    data_enter = data.values
    tree = ttk.Treeview(des_frame, columns = tuple(range(len(data.columns))), height = 1, show = "headings", padding=10)
    tree.grid(row=1, column=0, sticky='nsew')
    [tree.heading(x, text=y, anchor='w') for x,y in zip(range(len(data.columns)), data.columns)]
    [tree.column(x, width = 100+len(list(c))) for x,c in zip(range(len(data.columns)), data.columns)]
    for val in data_enter:
        tree.insert('', 'end', values = [x for x in val] )		