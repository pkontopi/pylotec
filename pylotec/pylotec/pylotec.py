import numpy as np
# from scipy.signal import find_peaks, peak_prominences
import pyuff
import os                       # OS stuff
from tqdm import tqdm               #progressbar

import plotly.express as px
import plotly.graph_objects as go

import matplotlib.image as mgimg
from PIL import Image
from scipy.fft import fft

import cmath

import matplotlib.image as mpimg
from PIL import Image

from scipy.signal import find_peaks
import pandas as pd

import Functions.PlotFunctions as plFKT

meas = os.getcwd()+"/Data/"

def show_records(meas): 
    records = os.listdir(meas+'uff')
    if records[0] == ".DS_Store":
        records.pop(0)
    return records

def make_dirs(): 
    ordnerpfad = os.getcwd()+"/Data"

    if not os.path.exists(ordnerpfad):
        os.makedirs(ordnerpfad)
        os.makedirs(ordnerpfad+"/uff")
        os.makedirs(ordnerpfad+"/NumPyArrays")
        os.makedirs(ordnerpfad+"/img")

        input("The /Data directory didn't exist. I made it. Please save your uff files under Data/uff. Press any key to continue")
        contents = os.listdir(ordnerpfad+"/uff")
        if len(contents)==0: 
            input("The Data/uff directory is empty. Please save your uff files there. Press any key to continue")
    else: 
        contents = os.listdir(ordnerpfad+"/uff")
        if len(contents)==0: 
            input("The Data/uff directory is empty. Please save your uff files there. Press any key to continue")

def found_uffs(records):
    print(str(len(records))+" files found in the Data Directory. Please type: \n")
    
    for i in range(len(records)): 
        print(str(i)+" for "+str(records[i]))

    decision = input()
    decision = int(decision)

    if decision > len(records)-1: 
       print('Error: No valid input.')
    
    return decision

def load_uff(): 
    make_dirs()
    records = show_records(meas)
    decision = found_uffs(records)

    mess=records[decision][:-4]

    path=meas+'uff/'+mess+".uff"
    uff_file = pyuff.UFF(path)

    # geometrie auslesen (type 15 bzw. 2411 (double) )
    IDs = np.where(uff_file.get_set_types() == 2411)

    if len(IDs[0])==1:
        Nodes=uff_file.read_sets(IDs[0][0])
    else:
        print("Error")

    # get recording date
    IDs = np.where(uff_file.get_set_types() == 151)
    uff_file.read_sets(IDs[0][0])['date_db_created']

    # Laser- und Hammer-signal suchen und speichern
    veloIDs=[]
    forceIDs=[]

    for i in tqdm(range(len(uff_file.get_set_types()))):
        if uff_file.get_set_types()[i]==58: #daten suchen
            if uff_file.read_sets(i)['id1']=='Response Time Trace': 
                if uff_file.read_sets(i)['id2']=='Vib  Geschwindigkeit': 
                    veloIDs.append(i)
            if uff_file.read_sets(i)['id1']=='Reference Time Trace':             
                if uff_file.read_sets(i)['id2']=='Ref1  Kraft': 
                    forceIDs.append(i)
            
    velocities = uff_file.read_sets(veloIDs)
    forces = uff_file.read_sets(forceIDs)

    LL=len(velocities)

    #messwerte und Positionen in NumPy-Array schreiben

    X=np.zeros(LL)
    Y=np.zeros(LL)
    Z=np.zeros(LL)

    Vel=np.zeros((LL,len(velocities[1]['x'])))
    Force=np.zeros((LL,len(velocities[1]['x'])))
    for i in range(LL):
        Force[i]=(forces[i]['data']) 
        Vel[i]=(velocities[i]['data']) 
        node_id=velocities[i]['rsp_node']
        id=np.where(Nodes['node_nums']==node_id)[0][0] 
        X[i]=Nodes['x'][id]
        Y[i]=Nodes['y'][id]
        Z[i]=Nodes['z'][id]

    np.save(meas + 'NumPyArrays/'+ mess + '_Xnodes', X)
    np.save(meas + 'NumPyArrays/'+ mess + '_Ynodes', Y)
    np.save(meas + 'NumPyArrays/'+ mess + '_Znodes', Z)
    np.save(meas + 'NumPyArrays/'+ mess + '_velocities', Vel)
    np.save(meas + 'NumPyArrays/'+ mess + '_forces', Force)

    print("\nThe X, Y, Z nodes, forces and velocities are now saved under Data/NumPyArrays.")

def calculate_IRFs(): 
    records=os.listdir(os.getcwd()+"/Data/uff/")
    recordsnp=os.listdir(os.getcwd()+"/Data/NumPyArrays/")

    records = show_records(meas)

    if len(recordsnp)==0: 
        return "Error: No NumPyArrays to analyze. Please call pylotec.load_uff() first."


    for i in range(len(records)): 
        messID=i
        measD=os.getcwd()+"/Data/"
        print(records[messID][:-4])

        mess=records[messID][:-4]

        velocities = np.load(measD + 'NumPyArrays/'+ mess + '_velocities.npy')
        forces = np.load(measD + 'NumPyArrays/'+ mess + '_forces.npy')

        #IRF
        nPoints = len(velocities)

        IRFs = np.zeros(np.shape(velocities),dtype=np.complex_)

        veloSpec = np.zeros(np.shape(velocities),dtype=np.complex_)
        forceSpec = np.zeros(np.shape(velocities),dtype=np.complex_)

        for i in range(nPoints):
            veloSpec[i] = fft(velocities[i])
            forceSpec[i] = fft(forces[i])
            IRFs[i] = np.divide(veloSpec[i], forceSpec[i])
        np.save(measD + 'NumPyArrays/'+ mess + '_IRFs', IRFs)

    return "All IRFs were saved to Data/NumPyArrays."

def meanspec(**kwargs): 

    thresh = -9   # min. Höhe der peaks in dB_FS
    minProm= 0.1 # min Prominence eines peaks (Abstand zwischen peak maximum und dem nächsten minimum), stdmäßig so 1.7

    thresh = kwargs.get('thresh', -9)
    minProm = kwargs.get('prom', 0.1)
    save = kwargs.get('saveToFile', False)
    
    records=show_records(meas)
    messID = found_uffs(records)

    mess=records[messID][:-4]

    nPoints=np.zeros(len(records),int)
    fmax=5000

    Peaks=[]

    MeanSpecS=np.zeros((len(records),fmax))

    # Daten laden
    X = np.load(meas + 'NumPyArrays/'+ mess + '_Xnodes.npy')
    IRFs = np.load(meas + 'NumPyArrays/'  + mess + '_IRFs.npy')


    #Fs=len(IRFs[1]) #Messzeit beträgt 1sec. Ansonsten gibt es Fehler!!!
    nPoints[messID]=len(X)

    MeanSpec=np.zeros(len(IRFs[1]),dtype=np.complex_)

    for i in range(nPoints[messID]):
        MeanSpec += np.abs(IRFs[i])

    #mittleres Spektrum
    MeanSpec/=nPoints[messID]

    spec=np.abs(MeanSpec)[0:fmax]

    spec=np.log(np.divide(spec,max(spec)))

    MeanSpecS[messID,:]=spec

    Peaks=[]
    peaks,location= find_peaks(spec, distance=1, prominence=minProm, height=thresh)
    Peaks=np.append(Peaks,peaks)
    Peaks2=np.int32(np.unique(Peaks))

    fig = go.Figure()
    trace = go.Scatter(x=np.arange(fmax+1), y=spec, name=str(records[messID])+" Mean Spectrum")
    trace_peaks = go.Scatter(x=Peaks, y=location['peak_heights'], name=str(records[messID])+" Peaks", mode='markers')

    fig.add_trace(trace)
    fig.add_trace(trace_peaks)

    fig.update_layout(
        title=str(records[messID][:-4]),
        xaxis_title="Frequency (Hz)",
        yaxis_title="Mobility (dBFS)",
        #legend_title="Legend Title",
        font=dict(
            family="Courier New, monospace",
            size=10,
            color="RebeccaPurple"
        )
    )

    fig.show()
    if save:
        fig.write_html(str(records[messID][:-4])+".html")

    return IRFs, Peaks2

def plot_modes(IRFs, Peaks2, **kwargs): 
    records = show_records(meas)
    decision = found_uffs(records)

    mess = records[int(decision)][:-4]
    fmin=kwargs.get('fmin', 200) 
    
    Peaks2=Peaks2[Peaks2>=fmin]
            # Daten laden
    X = np.load(meas + 'NumPyArrays/' + mess + '_Xnodes.npy')
    Y = np.load(meas + 'NumPyArrays/'+ mess + '_Ynodes.npy')

    Xn=X
    Yn=Y

    x1 = 1000
    y1 = 1000
    for i in range(len(Peaks2)): 
        f=Peaks2[i]

        Amp=IRFs[:,f]
        plotData=plFKT.PlotModeRe(Xn, Yn,Amp, (x1/ 50,y1/50))
        plotData.savefig(meas+'img/'  + mess +'_Re_' + str(f).zfill(4) + 'Hz.png')
        plotData=plFKT.PlotModeIm(Xn, Yn,Amp, (x1/ 50,y1/50))
        plotData.savefig(meas+'img/'  + mess +'_Im_' + str(f).zfill(4) + 'Hz.png')

    return 'Modes saved!'