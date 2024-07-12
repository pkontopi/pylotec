# funktion zum mode-shape plotten
import numpy as np
import matplotlib.pyplot as plt #plotten


#### Moden

def PlotModeIm(X, Y,Amp,size):

    data = np.divide(np.imag(Amp),np.amax(np.imag(Amp)))

    fac=0.66

    data[data>fac]=fac
    data[data<fac*(-1)]=fac*(-1)

    fig, ax = plt.subplots(1, 1, figsize=size)
    

    ax.tricontourf(X, Y, data,cmap="RdBu_r",vmin=-fac,vmax=fac)
    ax.tricontour(X, Y, data, colors='k', linewidths=.5)
    # ax.title.set_text('Im')

    ax.set_aspect('equal')
    ax.axis('off')

    plt.close()
    return fig

def PlotModeRe(X, Y,Amp,size):
    data= np.divide(np.real(Amp),np.amax(np.real(Amp)))

    fac=0.66

    data[data>fac]=fac
    data[data<fac*(-1)]=fac*(-1)

    fig, ax = plt.subplots(1, 1, figsize=size)
    

    ax.tricontourf(X, Y, data,cmap="RdBu_r",vmin=-fac,vmax=fac)
    ax.tricontour(X, Y, data, colors='k', linewidths=.5)
    # ax.title.set_text('Re')

    ax.set_aspect('equal')
    ax.axis('off')

    plt.close()

    return fig

def PlotModeAbs(X, Y,Amp,size):
    data= np.divide(np.abs(Amp),np.amax(np.abs(Amp)))

    fac=0.66

    data[data>fac]=fac
    # data[data<fac*(-1)]=fac*(-1)

    fig, ax = plt.subplots(1, 1, figsize=size)
    

    ax.tricontourf(X, Y, data,cmap="gray_r",vmin=0,vmax=fac)
    ax.tricontour(X, Y, data, colors='k', linewidths=.5)
    # ax.title.set_text('Re')

    ax.set_aspect('equal')
    ax.axis('off')

    plt.close()

    return fig

# transparenz

def transparencyMode(img):
    
    amp=6 #Verstärkung der Deckkraft 
    maxAlpha=0.7 #maximale Deckkraft

    datas = img.getdata()
    newData = []
    for item in datas:
        fac=int(amp*item[3]*(1-sum(item[:3])/(255*3)))
        if fac>int(maxAlpha*item[3]):
            fac=int(maxAlpha*item[3])
        newData.append(item[0:3]+ (fac,))

    img.putdata(newData)
    return img

#### Video

def plotFrame(Amp,X,Y,size,maxA ):

    # fac=.66
    fac=.9

    Amp[Amp>maxA*fac]=maxA*fac
    Amp[Amp<maxA*fac*(-1)]=maxA*fac*(-1)
 
    # k=1000*t/Fs
    
    #plotten
    fig, ax = plt.subplots(1, 1, figsize=size)

    cs = ax.tricontourf(X, Y, Amp,cmap="RdBu",levels=np.linspace(-maxA*(fac+0.01),maxA*(fac+0.01),60))
   
    ax.set_aspect('equal')
    ax.axis('off')
    plt.close()
    return fig

# transparenz

def transparency(img):
    
    amp=3.5 #Verstärkung der Deckkraft 
    maxAlpha=0.7 #maximale Deckkraft

    datas = img.getdata()
    newData = []
    for item in datas:
        fac=int(amp*item[3]*(1-sum(item[:3])/(255*3)))
        if fac>int(maxAlpha*item[3]):
            fac=int(maxAlpha*item[3])
        newData.append(item[0:3]+ (fac,))

    img.putdata(newData)
    return img